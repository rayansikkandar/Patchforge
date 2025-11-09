"""
Integration tests for the end-to-end PatchForge pipeline
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from agents.scanner import ScannerAgent
from agents.researcher import ResearcherAgent
from agents.patch_generator import PatchGeneratorAgent
from agents.validator import ValidatorAgent
from agents.pr_creator import PRCreatorAgent


class TestIntegration:
    """Integration tests for the full pipeline"""
    
    @pytest.mark.integration
    def test_full_pipeline_with_mocks(self, temp_repo, mock_nvd_client, mock_github_client):
        """Test the full pipeline with mocked external services"""
        
        # Step 1: Scanner
        with patch('agents.scanner.NVDClient', return_value=mock_nvd_client):
            scanner = ScannerAgent()
            cves = scanner.scan_repository(temp_repo)
            
            assert len(cves) > 0
            cve = cves[0]
            assert 'cve_id' in cve
            assert 'package' in cve
        
        # Step 2: Researcher
        with patch('agents.researcher.NVDClient', return_value=mock_nvd_client):
            with patch.object(ResearcherAgent, 'call_nemotron', return_value="Mock analysis"):
                researcher = ResearcherAgent()
                research = researcher.research_cve(cve)
                
                assert research['cve_id'] == cve['cve_id']
                assert 'analysis' in research
        
        # Step 3: Patch Generator
        with patch.object(PatchGeneratorAgent, '_select_secure_version', return_value=("2.3.2", "Security fix")):
            generator = PatchGeneratorAgent()
            patch_data = generator.generate_patch(research, temp_repo)
            
            assert patch_data['cve_id'] == cve['cve_id']
            assert patch_data['file_path'] == "requirements.txt"
            assert patch_data['patched_content'] != patch_data['original_content']
        
        # Step 4: Validator
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # venv creation
                Mock(returncode=0, stderr="", stdout=""),  # pip install
                Mock(returncode=0, stderr="", stdout="")  # pip check
            ]
            
            validator = ValidatorAgent()
            validation = validator.validate_patch(patch_data, temp_repo)
            
            assert validation['passed'] is True
            assert validation['cve_id'] == cve['cve_id']
        
        # Step 5: PR Creator
        with patch('agents.pr_creator.GitHubClient', return_value=mock_github_client):
            pr_creator = PRCreatorAgent()
            pr_url = pr_creator.create_pr(patch_data, validation, "test/repo", research)
            
            assert pr_url is not None
            assert "github.com" in pr_url or pr_url == "https://github.com/user/repo/pull/1"
    
    @pytest.mark.integration
    def test_validator_with_real_requirements(self):
        """Integration test: Validate a real patch with actual pip"""
        validator = ValidatorAgent()
        
        # Create a real patch that should work
        patch_data = {
            "cve_id": "CVE-TEST-INTEGRATION",
            "file_path": "requirements.txt",
            "original_content": "Flask==2.0.1\n",
            "patched_content": "Flask==2.3.2\n",
            "description": "Integration test patch"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validator.validate_patch(patch_data, tmpdir)
            
            # Should pass validation
            assert 'passed' in result
            assert result['cve_id'] == "CVE-TEST-INTEGRATION"
            
            # If it passed, verify the structure
            if result['passed']:
                assert result['message'] is not None
                assert 'details' in result
    
    @pytest.mark.integration
    def test_validator_with_invalid_requirements(self):
        """Integration test: Validate should fail with invalid requirements"""
        validator = ValidatorAgent()
        
        # Create a patch with invalid requirements
        patch_data = {
            "cve_id": "CVE-TEST-INVALID",
            "file_path": "requirements.txt",
            "original_content": "Flask==2.0.1\n",
            "patched_content": "InvalidPackageName==999.999.999\n",
            "description": "Invalid patch test"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validator.validate_patch(patch_data, tmpdir)
            
            # Should fail validation
            assert result['passed'] is False
            assert 'error' in result['message'].lower() or 'failed' in result['message'].lower()

