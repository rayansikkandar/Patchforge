from agents.base_agent import NemotronAgent
from tools.osv_client import OSVClient
from utils.parsers import parse_requirements, parse_package_json
from config import GITHUB_TOKEN
import os
import json
import re

SCANNER_PROMPT = """You are a Dependency Scanner Agent.

Your job is simple and precise:
1. Find dependency files (requirements.txt, package.json, pom.xml, Gemfile)
2. Parse them to extract package names and versions
3. Check each package+version against vulnerability databases (OSV, NVD)
4. Return a list of vulnerable dependencies with their CVEs

Be systematic and thorough. Every dependency must be checked."""

class ScannerAgent(NemotronAgent):
    def __init__(self):
        super().__init__("Scanner", SCANNER_PROMPT)
        self.osv_client = OSVClient()
    
    def _get_existing_prs(self, repo_name: str) -> set:
        """Get CVE IDs that already have open PRs"""
        try:
            from github import Github
            
            if not GITHUB_TOKEN:
                self.logger.warning("GITHUB_TOKEN not available, skipping PR check")
                return set()
            
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(repo_name)
            
            # Get all open PRs
            open_prs = repo.get_pulls(state='open')
            
            # Extract CVE IDs from PR titles
            existing_cves = set()
            for pr in open_prs:
                # Match pattern: "Security: Fix CVE-2023-12345" or "Fix CVE-2023-12345"
                if 'CVE-' in pr.title:
                    match = re.search(r'CVE-\d{4}-\d+', pr.title)
                    if match:
                        existing_cves.add(match.group())
            
            if existing_cves:
                self.logger.info(f"📋 Found {len(existing_cves)} CVEs with existing PRs: {existing_cves}")
            
            return existing_cves
            
        except Exception as e:
            self.logger.warning(f"Could not check existing PRs: {e}")
            return set()
    
    def scan_repository(self, repo_path: str, repo_name: str = None) -> list:
        """Scan repository dependencies for known CVEs
        
        Args:
            repo_path: Path to the repository
            repo_name: GitHub repository name (e.g., 'owner/repo') for PR checking
        
        Returns:
            List of vulnerable dependencies
        """
        self.logger.info(f"🔍 Scanning dependencies in {repo_path}")
        
        # Get existing PRs if repo_name provided
        existing_cves = set()
        if repo_name:
            existing_cves = self._get_existing_prs(repo_name)
            if existing_cves:
                self.logger.info(f"⏭️  Will skip {len(existing_cves)} CVEs with existing PRs")
        
        vulnerable_deps = []
        
        # 1. Find and parse dependency files
        dependency_files = self._find_dependency_files(repo_path)
        
        if not dependency_files:
            self.logger.warning("No dependency files found")
            return []
        
        # 2. Parse each file
        all_packages = []
        for file_info in dependency_files:
            packages = self._parse_dependency_file(file_info)
            all_packages.extend(packages)
        
        self.logger.info(f"Found {len(all_packages)} dependencies to check")
        
        # 3. Check each package+version for CVEs
        for pkg in all_packages:
            self.logger.info(f"Checking {pkg['name']}=={pkg['version']}")
            
            # Query OSV for this specific package+version
            vulns = self.osv_client.query_package(
                package_name=pkg['name'],
                version=pkg['version'],
                ecosystem=pkg['ecosystem']  # "PyPI", "npm", etc.
            )
            
            if vulns:
                for vuln in vulns:
                    # Extract CVSS score from database_specific or severity
                    # Ensure it's always a float for consistent sorting
                    cvss_score = 0.0
                    
                    # Try database_specific first (often has numeric CVSS score or severity string)
                    if 'database_specific' in vuln:
                        db_specific = vuln['database_specific']
                        if isinstance(db_specific, dict):
                            # Check for numeric CVSS score
                            db_score = db_specific.get('cvss_score') or db_specific.get('CVSS_score') or db_specific.get('cvss')
                            if db_score:
                                try:
                                    cvss_score = float(db_score)
                                except (ValueError, TypeError):
                                    cvss_score = 0.0
                            
                            # If no numeric score, check for severity string (HIGH, CRITICAL, etc.)
                            if cvss_score == 0.0:
                                severity_str = db_specific.get('severity', '').upper()
                                if 'CRITICAL' in severity_str:
                                    cvss_score = 9.5
                                elif 'HIGH' in severity_str:
                                    cvss_score = 7.5
                                elif 'MEDIUM' in severity_str or 'MODERATE' in severity_str:
                                    cvss_score = 5.0
                                elif 'LOW' in severity_str:
                                    cvss_score = 3.0
                    
                    # Try severity array - OSV returns CVSS vector strings, not numeric scores
                    # We'll parse the vector or use a default based on type
                    if cvss_score == 0.0 and 'severity' in vuln:
                        severity_list = vuln.get('severity', [])
                        if severity_list and isinstance(severity_list, list):
                            # Look for CVSS_V3 or CVSS_V4 entries
                            for severity_item in severity_list:
                                if isinstance(severity_item, dict):
                                    score_val = severity_item.get('score', '')
                                    score_type = severity_item.get('type', '')
                                    
                                    # If score is already numeric, use it
                                    if score_val:
                                        try:
                                            cvss_score = float(score_val)
                                            break
                                        except (ValueError, TypeError):
                                            # Score is a CVSS vector string, estimate severity
                                            # CVSS vectors like "CVSS:3.1/AV:N/AC:L/..." indicate high severity
                                            if 'CVSS' in str(score_val):
                                                # For CVSS vectors, we can't easily parse without a library
                                                # Default to a high score if CVSS vector exists (indicates critical/high)
                                                if 'CVSS_V3' in score_type or 'CVSS_V4' in score_type:
                                                    cvss_score = 7.5  # Default high severity for CVSS vectors
                                                    break
                                            continue
                    
                    # Get CVE ID or use OSV ID
                    cve_id = vuln.get('id', 'UNKNOWN')
                    if 'aliases' in vuln:
                        for alias in vuln['aliases']:
                            if alias.startswith('CVE-'):
                                cve_id = alias
                                break
                    
                    # Skip if PR already exists for this CVE
                    if cve_id in existing_cves:
                        self.logger.info(f"⏭️  Skipping {cve_id} - PR already exists")
                        continue
                    
                    # Also check OSV ID format (GHSA-*, PYSEC-*, etc.)
                    osv_id = vuln.get('id', '')
                    if osv_id in existing_cves:
                        self.logger.info(f"⏭️  Skipping {osv_id} - PR already exists")
                        continue
                    
                    # Store both relative path (for GitHub) and full path (for file access)
                    full_file_path = pkg['file_path']
                    relative_file_path = os.path.basename(full_file_path)
                    
                    vulnerable_deps.append({
                        'cve_id': cve_id,
                        'package': pkg['name'],
                        'current_version': pkg['version'],
                        'ecosystem': pkg['ecosystem'],
                        'cvss_score': cvss_score,  # Now guaranteed to be float
                        'summary': vuln.get('summary', ''),
                        'file_path': relative_file_path,  # Relative path for GitHub
                        'full_file_path': full_file_path,  # Full path for file access
                        'osv_id': osv_id
                    })
        
        # 4. Sort by severity (CVSS score) - ensure all scores are numeric
        vulnerable_deps.sort(key=lambda x: float(x.get('cvss_score', 0) or 0), reverse=True)
        
        # 5. Filter to recent CVEs (2020+)
        recent_vulns = [v for v in vulnerable_deps if self._is_recent_cve(v['cve_id'])]
        if recent_vulns:
            self.logger.info(f"🚨 Found {len(recent_vulns)} recent vulnerable dependencies (2020+)")
            return recent_vulns[:10]  # Return top 10
        
        self.logger.info(f"🚨 Found {len(vulnerable_deps)} vulnerable dependencies")
        return vulnerable_deps[:10]  # Return top 10
    
    def _is_recent_cve(self, cve_id: str) -> bool:
        """Check if CVE is from 2020 or later"""
        if not cve_id or not cve_id.startswith('CVE-'):
            return True  # Non-CVE IDs are considered recent
        
        try:
            parts = cve_id.split('-')
            if len(parts) >= 2:
                year = int(parts[1])
                return year >= 2020
        except (ValueError, IndexError):
            pass
        
        return True  # Default to recent if we can't parse
    
    def _find_dependency_files(self, repo_path: str) -> list:
        """Find all dependency files in the repository"""
        dependency_files = []
        
        # Common dependency file patterns
        patterns = {
            'requirements.txt': 'PyPI',
            'package.json': 'npm',
            'pom.xml': 'Maven',
            'Gemfile': 'RubyGems',
            'go.mod': 'Go',
            'Cargo.toml': 'crates.io'
        }
        
        for filename, ecosystem in patterns.items():
            file_path = os.path.join(repo_path, filename)
            if os.path.exists(file_path):
                dependency_files.append({
                    'path': file_path,
                    'type': filename,
                    'ecosystem': ecosystem
                })
                self.logger.info(f"Found: {filename} ({ecosystem})")
        
        return dependency_files
    
    def _parse_dependency_file(self, file_info: dict) -> list:
        """Parse a dependency file and extract packages"""
        packages = []
        
        try:
            with open(file_info['path'], 'r') as f:
                content = f.read()
            
            if file_info['type'] == 'requirements.txt':
                parsed = parse_requirements(content)
                for pkg in parsed:
                    # Skip packages without versions
                    if pkg.get('version') and pkg['version'] != 'unknown':
                        packages.append({
                            'name': pkg['name'],
                            'version': pkg['version'],
                            'ecosystem': 'PyPI',
                            'file_path': file_info['path'],
                            'raw_line': pkg.get('raw', '')
                        })
            
            elif file_info['type'] == 'package.json':
                parsed = parse_package_json(content)
                for pkg in parsed:
                    # Skip packages without versions
                    if pkg.get('version') and pkg['version'] != 'unknown':
                        packages.append({
                            'name': pkg['name'],
                            'version': pkg['version'],
                            'ecosystem': 'npm',
                            'file_path': file_info['path'],
                            'raw_line': f"{pkg['name']}@{pkg['version']}"
                        })
            
            # Add more parsers as needed for pom.xml, Gemfile, etc.
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_info['path']}: {e}")
        
        return packages
