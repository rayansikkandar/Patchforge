"""
Tests for utility parsers
"""
import pytest
from utils.parsers import parse_requirements, parse_package_json


class TestParsers:
    """Test suite for parsers"""
    
    def test_parse_requirements_simple(self):
        """Test parsing simple requirements.txt"""
        content = "Flask==2.0.1\nrequests==2.25.0\n"
        packages = parse_requirements(content)
        
        assert len(packages) == 2
        assert packages[0]['name'] == 'flask'
        assert packages[0]['version'] == '2.0.1'
        assert packages[1]['name'] == 'requests'
    
    def test_parse_requirements_with_comments(self):
        """Test parsing requirements with comments"""
        content = "# Web framework\nFlask==2.0.1\n# HTTP library\nrequests==2.25.0\n"
        packages = parse_requirements(content)
        
        assert len(packages) == 2
        assert all(pkg['name'] in ['flask', 'requests'] for pkg in packages)
    
    def test_parse_requirements_with_operators(self):
        """Test parsing requirements with different operators"""
        content = "Flask>=2.0.1\nrequests<3.0.0\nJinja2~=2.11.0\n"
        packages = parse_requirements(content)
        
        assert len(packages) == 3
        flask = next(p for p in packages if p['name'] == 'flask')
        assert flask['operator'] == '>='
    
    def test_parse_requirements_empty(self):
        """Test parsing empty requirements.txt"""
        packages = parse_requirements("")
        assert packages == []
    
    def test_parse_requirements_blank_lines(self):
        """Test parsing requirements with blank lines"""
        content = "Flask==2.0.1\n\nrequests==2.25.0\n"
        packages = parse_requirements(content)
        
        assert len(packages) == 2
    
    def test_parse_package_json(self):
        """Test parsing package.json"""
        content = '''{
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "~4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }'''
        
        packages = parse_package_json(content)
        
        assert len(packages) == 3
        assert any(p['name'] == 'express' for p in packages)
        assert any(p['name'] == 'jest' for p in packages)

