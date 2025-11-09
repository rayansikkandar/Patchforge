from agents.base_agent import NemotronAgent
import re
import json
import os

PATCH_GENERATOR_PROMPT = """You are a Dependency Update Agent.

Your job is surgical:
1. Read the dependency file
2. Find the line with the vulnerable package
3. Replace the old version with the secure version
4. Return the updated file content

Be precise. Change ONLY the vulnerable package line. Nothing else."""

class PatchGeneratorAgent(NemotronAgent):
    def __init__(self):
        super().__init__("PatchGenerator", PATCH_GENERATOR_PROMPT)
    
    def generate_patch(self, research_data: dict, repo_path: str, feedback: str = None, attempt: int = 1) -> dict:
        """Generate a patch by updating the dependency version
        
        Args:
            research_data: CVE research data with package and version info
            repo_path: Path to the repository
            feedback: Optional feedback from previous validation attempts
            attempt: Attempt number (for refinement tracking)
        
        Returns:
            Dictionary with patch data
        """
        self.logger.info(f"🔧 Generating patch for {research_data['package']} (attempt {attempt})")
        
        if feedback:
            self.logger.info(f"🔁 Refining patch based on feedback: {feedback[:200]}...")
        
        # Get file path - prefer full_file_path if available, otherwise use file_path
        file_path = research_data.get('full_file_path') or research_data.get('file_path', 'requirements.txt')
        package = research_data['package']
        old_version = research_data['current_version']
        new_version = research_data['secure_version']
        ecosystem = research_data['ecosystem']
        
        # Handle file path - could be absolute or relative
        if os.path.isabs(file_path):
            # Absolute path - use as is
            full_path = file_path
        else:
            # Relative path - join with repo_path
            full_path = os.path.join(repo_path, os.path.basename(file_path))
        
        # Fallback: try just the filename in repo_path
        if not os.path.exists(full_path):
            full_path = os.path.join(repo_path, os.path.basename(file_path))
        
        if not os.path.exists(full_path):
            raise ValueError(f"Could not find dependency file: {file_path} (tried: {full_path})")
        
        # Read the file
        with open(full_path, 'r') as f:
            original_content = f.read()
        
        # If this is a retry with feedback, use Nemotron to refine with multi-package updates
        if feedback and attempt > 1:
            # Create initial patch first
            if ecosystem == 'PyPI':
                patched_content = self._update_requirements_txt(
                    original_content, package, old_version, new_version
                )
            elif ecosystem == 'npm':
                patched_content = self._update_package_json(
                    original_content, package, old_version, new_version
                )
            else:
                self.logger.error(f"Unsupported ecosystem: {ecosystem}")
                return None
            
            # Now refine with Nemotron for multi-package updates
            temp_patch = {
                'cve_id': research_data['cve_id'],
                'file_path': full_path,
                'original_content': original_content,
                'patched_content': patched_content,
                'package': package,
                'old_version': old_version,
                'new_version': new_version,
                'ecosystem': ecosystem
            }
            
            refined_patch = self._refine_patch_with_nemotron(temp_patch, feedback, attempt)
            
            # Determine relative file path for GitHub (just the filename)
            github_file_path = os.path.basename(file_path)
            refined_patch['file_path'] = github_file_path
            refined_patch['description'] = f"Security: Upgrade {package} from {old_version} to {new_version} to fix {research_data['cve_id']}"
            
            return refined_patch
        
        # First attempt - standard single-package update
        if ecosystem == 'PyPI':
            patched_content = self._update_requirements_txt(
                original_content, package, old_version, new_version
            )
        elif ecosystem == 'npm':
            patched_content = self._update_package_json(
                original_content, package, old_version, new_version
            )
        else:
            self.logger.error(f"Unsupported ecosystem: {ecosystem}")
            return None
        
        self.logger.info(f"✅ Updated {package}: {old_version} → {new_version}")
        
        # Determine relative file path for GitHub (just the filename)
        github_file_path = os.path.basename(file_path)
        
        return {
            'cve_id': research_data['cve_id'],
            'file_path': github_file_path,  # Store relative path for GitHub
            'original_content': original_content,
            'patched_content': patched_content,
            'package': package,
            'old_version': old_version,
            'new_version': new_version,
            'ecosystem': ecosystem,
            'description': f"Security: Upgrade {package} from {old_version} to {new_version} to fix {research_data['cve_id']}"
        }
    
    def _refine_patch_with_nemotron(self, patch_data: dict, feedback: str, attempt: int) -> dict:
        """Use Nemotron to intelligently refine the patch based on validation feedback
        
        Args:
            patch_data: Current patch data with patched_content
            feedback: Validation error feedback
            attempt: Current attempt number
        
        Returns:
            Refined patch data dictionary
        """
        self.logger.info(f"🔁 Refining patch based on feedback: {feedback[:100]}...")
        self.logger.info("🧠 Using Nemotron to resolve dependency conflicts")
        
        package = patch_data['package']
        old_version = patch_data['old_version']
        new_version = patch_data['new_version']
        patched_content = patch_data['patched_content']
        
        # Ask Nemotron to analyze the conflict and suggest a fix
        prompt = f"""You are a Python dependency resolution expert. You have deep, specific knowledge of package version compatibility.

A security patch failed validation with this error:
{feedback}

Current patch attempt {attempt}:
- Target Package: {package}
- Upgrading from: {old_version}
- Upgrading to: {new_version}

Current requirements.txt to be fixed:
{patched_content}

Your task is to resolve the dependency conflicts. Use the following precise compatibility rules:

CRITICAL COMPATIBILITY RULES:
- For Flask: If upgrading to 2.3.x, you MUST upgrade Werkzeug to 2.3.3.
- For Flask: If upgrading to 2.2.x, you MUST upgrade Werkzeug to 2.2.3.
- For Werkzeug: If upgrading, ensure MarkupSafe is >= 2.1.1.
- For cryptography: If upgrading, ensure requests and urllib3 are compatible.

Your goal is to produce a COMPLETE and VALID requirements.txt that will pass pip's dependency resolver.

Return ONLY the corrected requirements.txt content. No explanation, no markdown.
Update ALL necessary packages to resolve conflicts based on the rules above."""
        
        try:
            response = self.call_nemotron(prompt, temperature=0.2)  # Lower temperature for more deterministic output
            
            if not response:
                self.logger.warning("⚠️  Nemotron returned empty response, using fallback")
                return self._fallback_multi_package_update(patch_data)
            
            # Clean up the response
            refined_content = response.strip()
            
            # Remove markdown code blocks if present
            if '```' in refined_content:
                parts = refined_content.split('```')
                # Find the part that looks like requirements.txt
                for part in parts:
                    if part.strip() and not part.strip().startswith('txt') and not part.strip().startswith('python'):
                        refined_content = part.strip()
                        # Remove language identifier if present
                        if refined_content.startswith('txt') or refined_content.startswith('python'):
                            lines = refined_content.split('\n')
                            refined_content = '\n'.join(lines[1:]) if len(lines) > 1 else refined_content
                        break
            
            refined_content = refined_content.strip()
            
            if not refined_content or len(refined_content) < 50:
                self.logger.warning("⚠️  Refined content seems invalid, using fallback")
                return self._fallback_multi_package_update(patch_data)
            
            self.logger.info("✅ Refined patch generated by Nemotron")
            
            # Log what changed - compare package lines
            original_lines = patch_data['patched_content'].split('\n')
            refined_lines = refined_content.split('\n')
            
            # Extract package lines (non-comment, non-empty)
            original_packages = {}
            refined_packages = {}
            
            for line in original_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name and version
                    parts = line.split()
                    if parts and ('==' in line or '>=' in line or '~=' in line or '>' in line or '<' in line):
                        pkg_name = parts[0].lower()
                        original_packages[pkg_name] = line
            
            for line in refined_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name and version
                    parts = line.split()
                    if parts and ('==' in line or '>=' in line or '~=' in line or '>' in line or '<' in line):
                        pkg_name = parts[0].lower()
                        refined_packages[pkg_name] = line
            
            # Find changed packages
            changes = []
            for pkg_name in refined_packages:
                if pkg_name not in original_packages:
                    changes.append(refined_packages[pkg_name])
                elif refined_packages[pkg_name] != original_packages[pkg_name]:
                    changes.append(refined_packages[pkg_name])
            
            if changes:
                self.logger.info(f"📝 Additional changes detected: {len(changes)} package updates")
                for change in changes[:5]:  # Log first 5 changes
                    self.logger.info(f"   • {change}")
            
            return {
                **patch_data,
                'patched_content': refined_content,
                'refinement_attempt': attempt,
                'refinement_changes': list(changes) if changes else []
            }
            
        except Exception as e:
            self.logger.error(f"Nemotron refinement failed: {e}")
            self.logger.info("Falling back to coordinated package updates")
            # Fallback: manually update related packages
            return self._fallback_multi_package_update(patch_data)
    
    def _fallback_multi_package_update(self, patch_data: dict) -> dict:
        """Fallback: Manually update related packages if Nemotron fails
        
        Args:
            patch_data: Current patch data
        
        Returns:
            Updated patch data with coordinated package updates
        """
        self.logger.info("🔧 Using fallback: coordinated package updates")
        
        content = patch_data['patched_content']
        package = patch_data['package'].lower()
        changes = []
        
        # If upgrading Flask, also upgrade Werkzeug and MarkupSafe
        if package == 'flask':
            self.logger.info("🔗 Flask upgrade detected - updating Werkzeug and MarkupSafe")
            
            # Determine Flask version to decide Werkzeug version (using precise compatibility rules)
            flask_new_version = patch_data.get('new_version', '')
            
            # Update Werkzeug based on Flask version (using precise compatibility rules)
            werkzeug_pattern = r'^(Werkzeug\s*[=><~!]+\s*)[\d.]+'
            if re.search(werkzeug_pattern, content, re.MULTILINE | re.IGNORECASE):
                # Flask 2.3.x requires Werkzeug 2.3.3 (exact version)
                if flask_new_version.startswith('2.3.'):
                    werkzeug_version = '2.3.3'
                # Flask 2.2.x requires Werkzeug 2.2.3 (exact version)
                elif flask_new_version.startswith('2.2.'):
                    werkzeug_version = '2.2.3'
                else:
                    # Default to 2.3.3 for safety
                    werkzeug_version = '2.3.3'
                
                content = re.sub(
                    werkzeug_pattern,
                    rf'\g<1>{werkzeug_version}',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                changes.append(f"Werkzeug=={werkzeug_version}")
                self.logger.info(f"   ✓ Updated Werkzeug to {werkzeug_version} (for Flask {flask_new_version})")
            
            # Update MarkupSafe if present (Flask 2.3.x works better with MarkupSafe >=2.1.1)
            markupsafe_pattern = r'^(MarkupSafe\s*[=><~!]+\s*)[\d.]+'
            if re.search(markupsafe_pattern, content, re.MULTILINE | re.IGNORECASE):
                content = re.sub(
                    markupsafe_pattern,
                    r'\g<1>2.1.3',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                changes.append("MarkupSafe==2.1.3")
                self.logger.info("   ✓ Updated MarkupSafe to 2.1.3")
            
            # Update Jinja2 if present and old (Flask 2.3.x works with Jinja2 >=3.0)
            jinja2_pattern = r'^(Jinja2\s*[=><~!]+\s*)[\d.]+'
            if re.search(jinja2_pattern, content, re.MULTILINE | re.IGNORECASE):
                # Check if version is < 3.0
                match = re.search(jinja2_pattern, content, re.MULTILINE | re.IGNORECASE)
                if match:
                    # Update to 3.1.2 for compatibility
                    content = re.sub(
                        jinja2_pattern,
                        r'\g<1>3.1.2',
                        content,
                        flags=re.MULTILINE | re.IGNORECASE
                    )
                    changes.append("Jinja2==3.1.2")
                    self.logger.info("   ✓ Updated Jinja2 to 3.1.2")
        
        # If upgrading Werkzeug, ensure Flask is compatible
        elif package == 'werkzeug':
            self.logger.info("🔗 Werkzeug upgrade detected - checking Flask compatibility")
            # Flask 2.0.x should work with Werkzeug 2.3.x, but let's ensure compatibility
            flask_pattern = r'^(Flask\s*[=><~!]+\s*)[\d.]+'
            if re.search(flask_pattern, content, re.MULTILINE | re.IGNORECASE):
                # If Flask is very old (< 2.0), suggest upgrade
                # For now, just log it
                self.logger.info("   ℹ️  Flask version should be compatible")
        
        if changes:
            self.logger.info(f"✅ Updated related packages: {', '.join(changes)}")
        else:
            self.logger.info("✅ No additional package updates needed")
        
        return {
            **patch_data,
            'patched_content': content,
            'refinement_attempt': 'fallback',
            'fallback_used': True,
            'refinement_changes': changes
        }
    
    def _update_requirements_txt(self, content: str, package: str, old_ver: str, new_ver: str) -> str:
        """Update a package version in requirements.txt"""
        lines = content.splitlines()
        updated_lines = []
        updated = False
        
        package_lower = package.lower()
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                updated_lines.append(line)
                continue
            
            # Check if this line contains the package (case-insensitive)
            # Pattern: package==version, package>=version, package~=version, etc.
            # Match the package name (case-insensitive) and version
            pattern = re.compile(
                rf'^({re.escape(package)})\s*([=><~!]+)\s*{re.escape(old_ver)}\b',
                re.IGNORECASE
            )
            
            if pattern.search(stripped) and not updated:
                # Replace the version - use \1 and \2 for groups
                new_line = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}{new_ver}", stripped)
                # Preserve leading whitespace and comments
                leading_ws = len(line) - len(line.lstrip())
                if '#' in line:
                    comment_part = line.split('#', 1)[1]
                    new_line = f"{' ' * leading_ws}{new_line}  # {comment_part.strip()}"
                else:
                    new_line = f"{' ' * leading_ws}{new_line}"
                updated_lines.append(new_line)
                updated = True
                self.logger.info(f"Updated line: {line.strip()} → {new_line.strip()}")
            else:
                updated_lines.append(line)
        
        if not updated:
            # Try a more flexible match (package name only, any version)
            for i, line in enumerate(updated_lines):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Match package name with any operator and any version
                match = re.match(rf'^({re.escape(package)})\s*([=><~!]+)\s*(\S+)', stripped, re.IGNORECASE)
                if match:
                    pkg_name = match.group(1)
                    operator = match.group(2)
                    new_line = f"{pkg_name}{operator}{new_ver}"
                    
                    # Preserve comments and whitespace
                    leading_ws = len(line) - len(line.lstrip())
                    if '#' in line:
                        comment = line.split('#', 1)[1]
                        new_line = f"{' ' * leading_ws}{new_line}  # {comment.strip()}"
                    else:
                        new_line = f"{' ' * leading_ws}{new_line}"
                    
                    updated_lines[i] = new_line
                    updated = True
                    self.logger.info(f"Updated line (flexible match): {line.strip()} → {new_line.strip()}")
                    break
        
        if not updated:
            raise ValueError(f"Could not find package {package}=={old_ver} in requirements.txt")
        
        result = '\n'.join(updated_lines)
        if content.endswith('\n'):
            result += '\n'
        
        return result
    
    def _update_package_json(self, content: str, package: str, old_ver: str, new_ver: str) -> str:
        """Update a package version in package.json"""
        try:
            data = json.loads(content)
            
            # Check both dependencies and devDependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data and package in data[dep_type]:
                    # Update to use ^new_version (standard npm format)
                    data[dep_type][package] = f"^{new_ver}"
                    self.logger.info(f"Updated {dep_type}.{package}: {old_ver} → ^{new_ver}")
            
            return json.dumps(data, indent=2) + '\n'
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in package.json: {e}")
            return content
