"""
Pytest configuration and shared fixtures
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock
from typing import Dict, List


@pytest.fixture
def mock_nemotron_response():
    """Mock Nemotron API response"""
    def _create_response(content: str):
        mock_message = Mock()
        mock_message.content = content
        mock_message.tool_calls = None
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        return mock_response
    return _create_response


@pytest.fixture
def sample_cve_data():
    """Sample CVE data for testing"""
    return {
        "cve_id": "CVE-2023-30861",
        "cvss_score": 8.1,
        "description": "Flask vulnerable to code injection",
        "published": "2023-05-01",
        "package": "flask",
        "current_version": "2.0.1"
    }


@pytest.fixture
def sample_research_data():
    """Sample research data for testing"""
    return {
        "cve_id": "CVE-2023-30861",
        "package": "flask",
        "current_version": "2.0.1",
        "cvss_score": 8.1,
        "analysis": """Root cause: Flask 2.0.1 has a code injection vulnerability.
Recommended fix: Upgrade to Flask 2.3.2 or later.
Testing: Run unit tests and integration tests."""
    }


@pytest.fixture
def sample_patch_data():
    """Sample patch data for testing"""
    return {
        "cve_id": "CVE-2023-30861",
        "file_path": "requirements.txt",
        "original_content": "Flask==2.0.1\nrequests==2.25.0\n",
        "patched_content": "Flask==2.3.2\nrequests==2.25.0\n",
        "description": "Upgrade flask from 2.0.1 to 2.3.2 to fix CVE-2023-30861"
    }


@pytest.fixture
def temp_repo():
    """Create a temporary repository with requirements.txt"""
    with tempfile.TemporaryDirectory() as tmpdir:
        req_file = os.path.join(tmpdir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write("Flask==2.0.1\nrequests==2.25.0\nJinja2==2.11.0\n")
        yield tmpdir


@pytest.fixture
def mock_nvd_client():
    """Mock NVD client"""
    mock = Mock()
    mock.search_cve_by_keyword.return_value = [
        {
            "cve_id": "CVE-2023-30861",
            "cvss_score": 8.1,
            "description": "Flask vulnerable to code injection",
            "published": "2023-05-01"
        }
    ]
    mock.get_cve_details.return_value = {
        "id": "CVE-2023-30861",
        "descriptions": [{"value": "Flask vulnerable to code injection"}],
        "references": [{"url": "https://example.com/cve"}]
    }
    return mock


@pytest.fixture
def mock_github_client():
    """Mock GitHub client"""
    mock = Mock()
    mock.create_branch.return_value = True
    mock.commit_file.return_value = True
    mock.create_pr.return_value = "https://github.com/user/repo/pull/1"
    return mock


@pytest.fixture
def mock_openai_client(mock_nemotron_response):
    """Mock OpenAI client for Nemotron"""
    mock_client = Mock()
    
    def create_completion(**kwargs):
        # Extract the user message to generate a response
        messages = kwargs.get('messages', [])
        user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '')
        
        # Generate mock response based on prompt
        if 'secure_version' in user_msg.lower():
            response = mock_nemotron_response('{"secure_version": "2.3.2", "justification": "Security fix"}')
        elif 'analyze' in user_msg.lower() or 'cve' in user_msg.lower():
            response = mock_nemotron_response("Root cause: Vulnerability in Flask. Fix: Upgrade to 2.3.2")
        else:
            response = mock_nemotron_response("Mock response")
        
        return response
    
    mock_client.chat.completions.create = Mock(side_effect=create_completion)
    return mock_client

