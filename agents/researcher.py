from agents.base_agent import NemotronAgent
from tools.osv_client import OSVClient
from tools.rag_nvd import rag_nvd
import requests
from packaging import version as pkg_version
from utils.logger import setup_logger

logger = setup_logger("Researcher")

RESEARCHER_PROMPT = """You are a Version Research Agent.

Your job is crystal clear:
Given a vulnerable package and version, find the latest SECURE version.

Process:
1. Query the package registry (PyPI, npm, etc.)
2. Get list of all available versions
3. Check which versions have the CVE fixed
4. Return the latest secure version

Be precise. Return ONLY the version number, nothing else."""

class ResearcherAgent(NemotronAgent):
    def __init__(self):
        super().__init__("Researcher", RESEARCHER_PROMPT)
        self.osv_client = OSVClient()
    
    def research_cve(self, cve_data: dict) -> dict:
        """Find the latest secure version for a vulnerable package"""
        self.logger.info(f"🔬 Researching fix for {cve_data['cve_id']}")
        
        package = cve_data['package']
        current_version = cve_data['current_version']
        ecosystem = cve_data['ecosystem']
        cve_id = cve_data.get('cve_id', '')
        
        # 1. Get rich context from NVD via RAG (NEW: Grounded intelligence)
        nvd_context = ""
        try:
            nvd_context = rag_nvd(cve_id)
            self.logger.info(f"📚 Retrieved NVD context for {cve_id}")
            if "Error" in nvd_context or "No detailed information" in nvd_context:
                self.logger.warning(f"⚠️  Limited NVD context for {cve_id}")
                nvd_context = ""  # Don't use invalid context
        except Exception as e:
            self.logger.warning(f"⚠️  Could not retrieve NVD context: {e}")
            nvd_context = ""
        
        # 2. Get latest secure version from registry
        if ecosystem == 'PyPI':
            # Try to get CVE fix information from OSV first
            fixed_version = self._get_fixed_version_from_osv(package, cve_id, current_version, ecosystem)
            if fixed_version:
                secure_version = self._get_best_compatible_version(package, current_version, fixed_version)
            else:
                secure_version = self._get_latest_pypi_version(package, current_version)
        elif ecosystem == 'npm':
            secure_version = self._get_latest_npm_version(package, current_version)
        else:
            secure_version = None
        
        if not secure_version:
            self.logger.error("Could not find secure version")
            return None
        
        self.logger.info(f"✅ Found secure version: {secure_version}")
        
        # Store NVD context for later use in PR descriptions
        research_result = {
            'cve_id': cve_data['cve_id'],
            'package': package,
            'current_version': current_version,
            'secure_version': secure_version,
            'ecosystem': ecosystem,
            'cvss_score': cve_data.get('cvss_score', 0),
            'file_path': cve_data.get('file_path', 'requirements.txt'),  # Relative path
            'full_file_path': cve_data.get('full_file_path', cve_data.get('file_path', 'requirements.txt')),  # Full path
            'summary': cve_data.get('summary', ''),
            'nvd_context': nvd_context  # Store NVD context for PR generation
        }
        
        return research_result
    
    def explain_cve_fix(self, cve_data: dict, research_data: dict) -> str:
        """Generate a detailed explanation of the CVE fix using Nemotron with NVD context"""
        self.logger.info(f"📚 Generating CVE fix explanation for {cve_data['cve_id']}")
        
        # Get NVD context if available
        nvd_context = research_data.get('nvd_context', '')
        
        # Build prompt with NVD context
        if nvd_context and "Error" not in nvd_context and "No detailed information" not in nvd_context:
            prompt = f"""You are a cybersecurity expert explaining a CVE fix to developers.

CVE ID: {cve_data['cve_id']}
Package: {research_data['package']}
Current Version: {research_data['current_version']}
Secure Version: {research_data['secure_version']}
CVSS Score: {research_data.get('cvss_score', 0)}/10

Full NVD (National Vulnerability Database) Context:
---
{nvd_context}
---

Based on the official NVD data above, provide a clear, concise explanation that covers:

1. **What is the vulnerability?** - Explain what the CVE allows attackers to do (use NVD details)
2. **Why is this version secure?** - Explain what was fixed in the secure version
3. **What should developers know?** - Any important notes about the upgrade, breaking changes, or compatibility

Keep it technical but accessible. Aim for 3-4 paragraphs. Be specific about the security impact.
Reference the NVD data to make your explanation authoritative and grounded in official sources.

Explanation:"""
        else:
            # Fallback to basic explanation without NVD context
            prompt = f"""You are a cybersecurity expert explaining a CVE fix to developers.

CVE ID: {cve_data['cve_id']}
Package: {research_data['package']}
Current Version: {research_data['current_version']}
Secure Version: {research_data['secure_version']}
CVSS Score: {research_data.get('cvss_score', 0)}/10
Vulnerability Summary: {cve_data.get('summary', 'No summary available')}

Please provide a clear, concise explanation that covers:

1. **What is the vulnerability?** - Explain what the CVE allows attackers to do
2. **Why is this version secure?** - Explain what was fixed in the secure version
3. **What should developers know?** - Any important notes about the upgrade

Keep it technical but accessible. Aim for 3-4 paragraphs. Be specific about the security impact.

Explanation:"""
        
        try:
            response = self.call_nemotron(prompt)
            if response:
                explanation = response.strip()
                self.logger.info("✅ CVE explanation generated")
                return explanation
            else:
                self.logger.warning("⚠️  Could not generate explanation")
                return None
        except Exception as e:
            self.logger.error(f"Error generating explanation: {e}")
            return None
    
    def _get_fixed_version_from_osv(self, package: str, cve_id: str, current_version: str, ecosystem: str) -> str:
        """Get the minimum version that fixes the CVE from OSV"""
        try:
            # First, query the package to find vulnerabilities
            vulns = self.osv_client.query_package(package, current_version, ecosystem)
            vuln_details = None
            
            # Find the vulnerability that matches the CVE ID
            for vuln in vulns:
                aliases = vuln.get('aliases', [])
                vuln_id = str(vuln.get('id', ''))
                # Check if CVE ID matches
                if cve_id in aliases or cve_id in vuln_id:
                    # Get detailed information
                    osv_id = vuln.get('id')
                    if osv_id:
                        vuln_details = self.osv_client.get_vulnerability_details(osv_id)
                    if not vuln_details:
                        vuln_details = vuln  # Use the summary if details not available
                    break
            
            # If not found in query, try getting details directly (might work for some CVE formats)
            if not vuln_details:
                try:
                    vuln_details = self.osv_client.get_vulnerability_details(cve_id)
                except:
                    pass
            
            if vuln_details and 'affected' in vuln_details:
                # Find the fixed version in affected ranges
                for affected in vuln_details['affected']:
                    pkg_info = affected.get('package', {})
                    pkg_name = pkg_info.get('name', '').lower()
                    # Check if this affects our package
                    if pkg_name == package.lower() or pkg_name.replace('-', '_') == package.lower().replace('-', '_'):
                        ranges = affected.get('ranges', [])
                        for range_info in ranges:
                            events = range_info.get('events', [])
                            for event in events:
                                if 'fixed' in event:
                                    fixed_ver = event['fixed']
                                    logger.info(f"OSV indicates {cve_id} fixed in version: {fixed_ver}")
                                    return fixed_ver
        except Exception as e:
            logger.warning(f"Could not get OSV fix version for {cve_id}: {e}")
        return None
    
    def _get_best_compatible_version(self, package: str, current_version: str, min_fixed_version: str) -> str:
        """Get the best version that fixes the CVE but maintains compatibility"""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
            response.raise_for_status()
            data = response.json()
            versions = list(data['releases'].keys())
            
            # Parse versions
            try:
                current_parsed = pkg_version.parse(current_version)
                min_fixed_parsed = pkg_version.parse(min_fixed_version)
                current_major = current_parsed.major
            except:
                return None
            
            # Filter to stable versions that fix the CVE
            stable_versions = [
                v for v in versions 
                if not any(x in v for x in ['a', 'b', 'rc', 'dev']) and
                   not v.endswith('.dev0')
            ]
            
            # Get versions that are >= min_fixed_version
            fixed_versions = []
            for v in stable_versions:
                try:
                    v_parsed = pkg_version.parse(v)
                    if v_parsed >= min_fixed_parsed:
                        fixed_versions.append(v)
                except:
                    continue
            
            if not fixed_versions:
                return None
            
            # Sort versions
            try:
                fixed_versions.sort(key=lambda v: pkg_version.parse(v), reverse=True)
            except:
                fixed_versions.sort(reverse=True)
            
            # Prefer same major version, but skip very old versions that might not build
            same_major = [v for v in fixed_versions 
                         if pkg_version.parse(v).major == current_major]
            
            if same_major:
                # Prefer newer versions in same major (better Python support)
                # Skip versions that are too old (before 2021)
                try:
                    # Filter to versions that are likely to have better Python support
                    # Prefer versions from 2021 onwards if available
                    recent_same_major = [v for v in same_major 
                                        if pkg_version.parse(v) >= pkg_version.parse('5.4.1')]
                    if recent_same_major:
                        best = recent_same_major[-1]  # Latest in same major
                    else:
                        best = same_major[-1]  # Latest available
                    logger.info(f"Best compatible version (major {current_major}): {best}")
                    return best
                except:
                    best = same_major[0]
                    logger.info(f"Best compatible version (major {current_major}): {best}")
                    return best
            
            # Fall back to minimum version that fixes the CVE, but prefer slightly newer
            # to avoid build issues with very old packages
            fixed_versions_sorted = sorted(fixed_versions, key=lambda v: pkg_version.parse(v))
            # Try to get a version that's not the absolute minimum (better compatibility)
            if len(fixed_versions_sorted) > 1:
                # Use second or later version if available (better Python support)
                best = fixed_versions_sorted[min(1, len(fixed_versions_sorted)-1)]
            else:
                best = fixed_versions_sorted[0]
            logger.info(f"Minimum version that fixes CVE: {best}")
            return best
            
        except Exception as e:
            logger.error(f"Error finding compatible version: {e}")
            return None
    
    def _get_latest_pypi_version(self, package: str, current_version: str) -> str:
        """Get latest version from PyPI, preferring same major version"""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get all versions
            versions = list(data['releases'].keys())
            
            # Parse current version to get major version
            try:
                current_parsed = pkg_version.parse(current_version)
                current_major = current_parsed.major
            except:
                current_major = None
            
            # Filter out pre-releases and sort
            stable_versions = [
                v for v in versions 
                if not any(x in v for x in ['a', 'b', 'rc', 'dev']) and
                   not v.endswith('.dev0')
            ]
            
            if not stable_versions:
                # Fall back to all versions if no stable versions
                stable_versions = versions
            
            # Sort versions
            try:
                stable_versions.sort(key=lambda v: pkg_version.parse(v), reverse=True)
            except:
                # Fallback to string sort if version parsing fails
                stable_versions.sort(reverse=True)
            
            # Prefer same major version to avoid breaking changes
            if current_major is not None:
                same_major = [v for v in stable_versions 
                             if pkg_version.parse(v).major == current_major]
                if same_major:
                    latest_same_major = same_major[0]
                    logger.info(f"PyPI latest (same major {current_major}): {latest_same_major}")
                    return latest_same_major
            
            # Fall back to absolute latest if no same major version
            if stable_versions:
                latest = stable_versions[0]
                logger.info(f"PyPI latest: {latest}")
                return latest
            
            return None
            
        except Exception as e:
            logger.error(f"PyPI API error: {e}")
            return None
    
    def _get_latest_npm_version(self, package: str, current_version: str) -> str:
        """Get latest version from npm"""
        try:
            response = requests.get(f"https://registry.npmjs.org/{package}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            latest = data.get('dist-tags', {}).get('latest')
            logger.info(f"npm latest: {latest}")
            return latest
            
        except Exception as e:
            logger.error(f"npm API error: {e}")
            return None
