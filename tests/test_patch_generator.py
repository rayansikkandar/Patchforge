"""
Tests for PatchGeneratorAgent
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.patch_generator import PatchGeneratorAgent


class TestPatchGeneratorAgent:
    """Test suite for PatchGeneratorAgent"""
    
    def test_patch_generator_initialization(self):
        """Test patch generator initializes correctly"""
        generator = PatchGeneratorAgent()
        assert generator.name == "PatchGenerator"
    
    def test_update_requirement_line_simple(self):
        """Test updating a simple requirement line"""
        generator = PatchGeneratorAgent()
        
        content = "Flask==2.0.1\nrequests==2.25.0\n"
        result = generator._update_requirement_line(content, "flask", "2.3.2")
        
        assert "Flask==2.3.2" in result
        assert "requests==2.25.0" in result
        assert "Flask==2.0.1" not in result
    
    def test_update_requirement_line_preserves_formatting(self):
        """Test that formatting is preserved when updating"""
        generator = PatchGeneratorAgent()
        
        content = "  Flask==2.0.1  # web framework\nrequests==2.25.0\n"
        result = generator._update_requirement_line(content, "flask", "2.3.2")
        
        assert "  Flask==2.3.2  # web framework" in result
        assert "requests==2.25.0" in result
    
    def test_update_requirement_line_preserves_operator(self):
        """Test that version operator is preserved"""
        generator = PatchGeneratorAgent()
        
        content = "Flask>=2.0.1\nrequests==2.25.0\n"
        result = generator._update_requirement_line(content, "flask", "2.3.2")
        
        assert "Flask>=2.3.2" in result
    
    def test_update_requirement_line_case_insensitive(self):
        """Test that package name matching is case insensitive"""
        generator = PatchGeneratorAgent()
        
        content = "flask==2.0.1\n"
        result = generator._update_requirement_line(content, "Flask", "2.3.2")
        
        assert "flask==2.3.2" in result
    
    def test_update_requirement_line_not_found(self):
        """Test error when package not found"""
        generator = PatchGeneratorAgent()
        
        content = "requests==2.25.0\n"
        
        with pytest.raises(ValueError, match="not found"):
            generator._update_requirement_line(content, "flask", "2.3.2")
    
    def test_update_requirement_line_preserves_newline(self):
        """Test that trailing newline is preserved"""
        generator = PatchGeneratorAgent()
        
        content = "Flask==2.0.1\n"
        result = generator._update_requirement_line(content, "flask", "2.3.2")
        
        assert result.endswith("\n")
    
    @patch('agents.patch_generator.PatchGeneratorAgent.call_nemotron')
    def test_select_secure_version(self, mock_call_nemotron, sample_research_data):
        """Test selecting secure version from Nemotron"""
        generator = PatchGeneratorAgent()
        
        mock_call_nemotron.return_value = '{"secure_version": "2.3.2", "justification": "Security fix"}'
        
        version, justification = generator._select_secure_version(
            sample_research_data,
            "Flask==2.0.1\n"
        )
        
        assert version == "2.3.2"
        assert justification == "Security fix"
        assert mock_call_nemotron.called
    
    @patch('agents.patch_generator.PatchGeneratorAgent._select_secure_version')
    @patch('agents.patch_generator.PatchGeneratorAgent._update_requirement_line')
    def test_generate_patch(
        self, mock_update, mock_select, sample_research_data, temp_repo
    ):
        """Test patch generation end-to-end"""
        generator = PatchGeneratorAgent()
        
        mock_select.return_value = ("2.3.2", "Security fix")
        mock_update.return_value = "Flask==2.3.2\nrequests==2.25.0\n"
        
        patch_data = generator.generate_patch(sample_research_data, temp_repo)
        
        assert patch_data['cve_id'] == sample_research_data['cve_id']
        assert patch_data['file_path'] == "requirements.txt"
        assert "2.3.2" in patch_data['description']
        assert mock_select.called
        assert mock_update.called
    
    def test_generate_patch_package_not_found(self, sample_research_data, temp_repo):
        """Test error when package not in requirements.txt"""
        generator = PatchGeneratorAgent()
        
        # Modify research data to use non-existent package
        sample_research_data['package'] = "nonexistent"
        
        with patch.object(generator, '_select_secure_version', return_value=("1.0.0", "")):
            with pytest.raises(ValueError, match="not found"):
                generator.generate_patch(sample_research_data, temp_repo)

