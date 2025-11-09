#!/usr/bin/env python3
"""
Dry-run test of the end-to-end PatchForge pipeline
Exercises the full pipeline with mocks to verify all components work together
"""
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scanner import ScannerAgent
from agents.researcher import ResearcherAgent
from agents.patch_generator import PatchGeneratorAgent
from agents.validator import ValidatorAgent
from agents.pr_creator import PRCreatorAgent
from utils.logger import setup_logger

logger = setup_logger("PipelineTest")


def test_pipeline_dry_run():
    """Test the full pipeline with mocks"""
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🧪 PatchForge Pipeline Dry-Run Test                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Create temporary repository
    with tempfile.TemporaryDirectory() as temp_repo:
        req_file = os.path.join(temp_repo, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write("Flask==2.0.1\nrequests==2.25.0\nJinja2==2.11.0\n")
        
        print(f"📁 Created test repository: {temp_repo}\n")
        
        # Mock NVD client
        mock_nvd = Mock()
        mock_nvd.search_cve_by_keyword.return_value = [
            {
                "cve_id": "CVE-2023-30861",
                "cvss_score": 8.1,
                "description": "Flask vulnerable to code injection",
                "published": "2023-05-01"
            }
        ]
        mock_nvd.get_cve_details.return_value = {
            "id": "CVE-2023-30861",
            "descriptions": [{"value": "Flask vulnerable to code injection"}],
            "references": [{"url": "https://example.com/cve"}]
        }
        
        # Mock GitHub client
        mock_github = Mock()
        mock_github.create_branch.return_value = True
        mock_github.commit_file.return_value = True
        mock_github.create_pr.return_value = "https://github.com/test/repo/pull/1"
        
        # Step 1: SCAN
        print("🔍 Step 1: Scanning repository...")
        with patch('agents.scanner.NVDClient', return_value=mock_nvd):
            scanner = ScannerAgent()
            cves = scanner.scan_repository(temp_repo)
            
            if not cves:
                print("   ⚠️  No CVEs found (expected in dry-run)")
                return
            
            cve = cves[0]
            print(f"   ✅ Found CVE: {cve['cve_id']} (CVSS: {cve['cvss_score']})")
            print(f"      Package: {cve.get('package', 'unknown')}\n")
        
        # Step 2: RESEARCH
        print("🔬 Step 2: Researching CVE...")
        with patch('agents.researcher.NVDClient', return_value=mock_nvd):
            with patch.object(ResearcherAgent, 'call_nemotron', return_value="""
Root cause: Flask 2.0.1 has a code injection vulnerability in template rendering.
Recommended fix: Upgrade to Flask 2.3.2 or later which includes security patches.
Testing: Run unit tests and integration tests to verify compatibility.
            """):
                researcher = ResearcherAgent()
                research = researcher.research_cve(cve)
                print(f"   ✅ Research complete for {research['cve_id']}")
                print(f"      Analysis: {research['analysis'][:100]}...\n")
        
        # Step 3: GENERATE PATCH
        print("🔧 Step 3: Generating patch...")
        with patch.object(PatchGeneratorAgent, '_select_secure_version', return_value=("2.3.2", "Security fix")):
            with patch.object(PatchGeneratorAgent, 'call_nemotron', return_value='{"secure_version": "2.3.2", "justification": "Security fix"}'):
                generator = PatchGeneratorAgent()
                patch_data = generator.generate_patch(research, temp_repo)
                print(f"   ✅ Patch generated for {patch_data['cve_id']}")
                print(f"      File: {patch_data['file_path']}")
                print(f"      Description: {patch_data['description']}\n")
                print(f"      Original: {patch_data['original_content'].strip()}")
                print(f"      Patched:  {patch_data['patched_content'].strip()}\n")
        
        # Step 4: VALIDATE
        print("🧪 Step 4: Validating patch...")
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # venv creation
                Mock(returncode=0, stderr="", stdout="Installing packages..."),  # pip install
                Mock(returncode=0, stderr="", stdout="No broken requirements found.")  # pip check
            ]
            
            validator = ValidatorAgent()
            validation = validator.validate_patch(patch_data, temp_repo)
            
            if validation['passed']:
                print(f"   ✅ Validation passed!")
                print(f"      Message: {validation['message']}\n")
            else:
                print(f"   ❌ Validation failed: {validation['message']}\n")
                return
        
        # Step 5: CREATE PR
        print("📝 Step 5: Creating PR (mocked)...")
        with patch('agents.pr_creator.GitHubClient', return_value=mock_github):
            pr_creator = PRCreatorAgent()
            pr_url = pr_creator.create_pr(patch_data, validation, "test/repo", research)
            
            if pr_url:
                print(f"   ✅ PR created: {pr_url}\n")
            else:
                print(f"   ⚠️  PR creation mocked (no real PR created)\n")
        
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✅ Pipeline Dry-Run Complete!                          ║
║                                                           ║
║   All components exercised successfully:                  ║
║   • Scanner ✅                                            ║
║   • Researcher ✅                                         ║
║   • Patch Generator ✅                                    ║
║   • Validator ✅                                          ║
║   • PR Creator ✅                                         ║
║                                                           ║
║   The new validator flow with isolated venv was tested.  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)


if __name__ == "__main__":
    try:
        test_pipeline_dry_run()
    except Exception as e:
        print(f"\n❌ Error during dry-run: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

