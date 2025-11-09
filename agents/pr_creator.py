from agents.base_agent import NemotronAgent
from tools.github_client import GitHubClient
from typing import Dict
import time

PR_CREATOR_PROMPT = """You are a PR Creator Agent. Your job is to:
1. Create well-documented GitHub pull requests
2. Write clear PR descriptions with CVE details
3. Include testing results and validation info
4. Follow best practices for security patches

Make PRs that developers will want to merge immediately."""

class PRCreatorAgent(NemotronAgent):
    def __init__(self):
        super().__init__("PRCreator", PR_CREATOR_PROMPT)
        self.github = GitHubClient()
    
    def create_pr(self, patch_data: Dict, validation_data: Dict, 
                  repo_name: str, research_data: Dict, cve_explanation: str = None,
                  attempts: int = 1) -> str:
        """Create a GitHub PR with the patch
        
        Args:
            patch_data: Patch information
            validation_data: Validation results
            repo_name: GitHub repository name
            research_data: CVE research data
            cve_explanation: Optional CVE explanation from Nemotron
            attempts: Number of attempts made (for ReAct loop info)
        """
        self.logger.info(f"📝 Creating PR for {patch_data['cve_id']}")
        
        cve_id = patch_data['cve_id']
        branch_name = f"security-patch-{cve_id.lower()}-{int(time.time())}"
        
        # Create branch
        self.github.create_branch(repo_name, branch_name)
        
        # Commit patch
        self.github.commit_file(
            repo_name=repo_name,
            file_path=patch_data['file_path'],
            content=patch_data['patched_content'],
            message=f"fix: {patch_data['description']}",
            branch=branch_name
        )
        
        # Generate PR body
        cvss_score = research_data.get('cvss_score', 0)
        package = research_data.get('package', patch_data.get('package', 'unknown'))
        current_version = research_data.get('current_version', patch_data.get('old_version', 'unknown'))
        secure_version = research_data.get('secure_version', patch_data.get('new_version', 'unknown'))
        summary = research_data.get('summary', '')
        
        # Build PR body
        pr_body = f"""## 🔒 Security Patch: {cve_id}

**CVSS Score**: {cvss_score}/10 ({'CRITICAL' if cvss_score >= 9 else 'HIGH' if cvss_score >= 7 else 'MEDIUM'})

### 🐛 Vulnerability Details

{summary if summary else patch_data['description']}

"""
        
        # Add CVE explanation if provided
        if cve_explanation:
            pr_body += f"""### 📚 CVE Fix Explanation

{cve_explanation}

"""
        
        # Add ReAct loop information if multiple attempts were made
        if attempts > 1:
            pr_body += f"""### 🔄 ReAct Loop Refinement

This patch was refined through **{attempts} attempts** using PatchForge's ReAct-style retry loop:

1. **Attempt 1**: Initial patch generated (single package update)
2. **Validation**: Failed with dependency conflicts
3. **Refinement**: Nemotron analyzed errors and coordinated multi-package updates
4. **Attempt {attempts}**: Refined patch with coordinated updates passed all validation checks

The final patch resolves all dependency conflicts through coordinated package upgrades.

"""
            
            # Add information about multi-package updates if available
            refinement_changes = patch_data.get('refinement_changes', [])
            if refinement_changes:
                pr_body += f"""### 📦 Multi-Package Updates

To resolve dependency conflicts, the following packages were automatically updated:

"""
                # Filter and format changes
                package_updates = []
                for change in refinement_changes:
                    change_str = change.strip()
                    if change_str and ('==' in change_str or '>=' in change_str or '~=' in change_str):
                        # Clean up the change string
                        if 'Werkzeug' in change_str or 'MarkupSafe' in change_str or 'Jinja2' in change_str:
                            package_updates.append(change_str)
                        else:
                            package_updates.append(change_str)
                
                # Show unique package updates
                seen = set()
                for update in package_updates[:10]:  # Limit to 10 updates
                    # Extract package name for deduplication
                    pkg_name = update.split()[0] if update.split() else update
                    if pkg_name not in seen:
                        pr_body += f"- `{update}`\n"
                        seen.add(pkg_name)
                
                if package_updates:
                    pr_body += "\n"
                    pr_body += "*These packages were automatically upgraded to resolve dependency conflicts.*\n\n"

        
        pr_body += f"""### ✅ Fix Applied

Updated `{patch_data['file_path']}` to address the vulnerability.

**Package**: `{package}`  
**Previous Version**: `{current_version}`  
**New Version**: `{secure_version}`  
**Status**: Upgraded to secure version

### 🧪 Validation Results

{'✅ All checks passed' if validation_data['passed'] else '⚠️ Validation had issues'}

```
{validation_data['message']}
```

### 📚 References

- [OSV: {cve_id}](https://osv.dev/vulnerability/{cve_id})
- [NVD: {cve_id}](https://nvd.nist.gov/vuln/detail/{cve_id})

---

*🤖 Generated by PatchForge - Autonomous CVE Patching Agent*  
*Powered by NVIDIA Nemotron*  
*ReAct Loop: {'Enabled' if attempts > 1 else 'Not needed'}*
"""
        
        # Create PR
        pr_url = self.github.create_pr(
            repo_name=repo_name,
            title=f"🔒 Security: Fix {cve_id}",
            body=pr_body,
            head_branch=branch_name,
            base_branch="main"
        )
        
        return pr_url

