"""
Tests for ValidatorAgent - Focus on the new isolated venv validation flow
"""
import pytest
import tempfile
import os
import subprocess
from unittest.mock import Mock, patch, MagicMock
from agents.validator import ValidatorAgent


class TestValidatorAgent:
    """Test suite for ValidatorAgent"""
    
    def test_validator_initialization(self):
        """Test validator agent initializes correctly"""
        validator = ValidatorAgent()
        assert validator.name == "Validator"
        assert validator.logger is not None
    
    @pytest.mark.parametrize("install_success,check_success,expected_pass", [
        (True, True, True),
        (True, False, False),
        (False, None, False),
    ])
    def test_validate_patch_with_mocked_subprocess(
        self, sample_patch_data, temp_repo, install_success, check_success, expected_pass
    ):
        """Test patch validation with mocked subprocess calls"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            # Mock venv creation
            mock_run.side_effect = [
                # venv creation
                Mock(returncode=0),
                # pip install
                Mock(returncode=0 if install_success else 1, stderr="", stdout=""),
                # pip check (only if install succeeded)
                *([Mock(returncode=0 if check_success else 1, stderr="", stdout="")] if install_success else [])
            ]
            
            result = validator.validate_patch(sample_patch_data, temp_repo)
            
            assert result['passed'] == expected_pass
            assert result['cve_id'] == sample_patch_data['cve_id']
            
            # Verify venv was created
            assert mock_run.call_count >= 2
    
    def test_validate_patch_creates_temp_directory(self, sample_patch_data, temp_repo):
        """Test that validation creates a temporary directory"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # venv creation
                Mock(returncode=0, stderr="", stdout=""),  # pip install
                Mock(returncode=0, stderr="", stdout="")  # pip check
            ]
            
            result = validator.validate_patch(sample_patch_data, temp_repo)
            
            # Verify subprocess was called (indicating temp dir was used)
            assert mock_run.called
    
    def test_validate_patch_handles_timeout(self, sample_patch_data, temp_repo):
        """Test that validation handles timeout gracefully"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pip", 30)
            
            result = validator.validate_patch(sample_patch_data, temp_repo)
            
            assert result['passed'] is False
            assert 'timeout' in result['message'].lower() or 'timed out' in result['message'].lower()
    
    def test_validate_patch_handles_venv_creation_failure(self, sample_patch_data, temp_repo):
        """Test that validation handles venv creation failure"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            # First call (venv creation) fails
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, "venv"),
            ]
            
            result = validator.validate_patch(sample_patch_data, temp_repo)
            
            assert result['passed'] is False
            assert 'error' in result['message'].lower()
    
    def test_validate_patch_writes_patched_content(self, sample_patch_data, temp_repo):
        """Test that validation writes the patched content to temp file"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # venv creation
                Mock(returncode=0, stderr="", stdout=""),  # pip install
                Mock(returncode=0, stderr="", stdout="")  # pip check
            ]
            
            with patch('builtins.open', create=True) as mock_open:
                result = validator.validate_patch(sample_patch_data, temp_repo)
                
                # Verify file was written
                assert mock_open.called
                # Check that patched content was written
                write_calls = [call for call in mock_open.call_args_list if 'w' in str(call)]
                assert len(write_calls) > 0
    
    def test_validate_patch_uses_isolated_venv(self, sample_patch_data, temp_repo):
        """Test that validation uses isolated venv (not system pip)"""
        validator = ValidatorAgent()
        
        with patch('agents.validator.subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # venv creation
                Mock(returncode=0, stderr="", stdout=""),  # pip install
                Mock(returncode=0, stderr="", stdout="")  # pip check
            ]
            
            result = validator.validate_patch(sample_patch_data, temp_repo)
            
            # Verify pip was called from venv (not system)
            pip_calls = [call for call in mock_run.call_args_list 
                        if len(call[0]) > 0 and 'pip' in str(call[0][0])]
            assert len(pip_calls) > 0
            
            # Check that pip path contains 'venv' or 'bin' or 'Scripts'
            for call in pip_calls:
                pip_path = call[0][0]
                assert any(part in pip_path for part in ['venv', 'bin', 'Scripts'])
    
    @pytest.mark.integration
    def test_validate_patch_real_installation(self, sample_patch_data):
        """Integration test: Actually test patch validation with real pip"""
        validator = ValidatorAgent()
        
        # Use a real patch that should work
        real_patch = {
            "cve_id": "CVE-TEST-001",
            "file_path": "requirements.txt",
            "original_content": "Flask==2.0.1\n",
            "patched_content": "Flask==2.3.2\n",
            "description": "Test patch"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validator.validate_patch(real_patch, tmpdir)
            
            # Should pass with a valid upgrade
            assert 'passed' in result
            assert result['cve_id'] == "CVE-TEST-001"

