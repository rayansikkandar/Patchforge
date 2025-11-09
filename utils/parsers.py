from typing import List, Dict
import re
from packaging import version

def parse_requirements(content: str) -> List[Dict[str, str]]:
    """Parse requirements.txt file"""
    packages = []
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Handle different formats: package==1.0.0, package>=1.0.0, etc.
        match = re.match(r'([a-zA-Z0-9\-_]+)([>=<]+)?([\d.]+)?', line)
        if match:
            name, operator, ver = match.groups()
            packages.append({
                "name": name.lower(),
                "version": ver or "unknown",
                "operator": operator or "==",
                "raw": line
            })
    
    return packages

def parse_package_json(content: str) -> List[Dict[str, str]]:
    """Parse package.json dependencies"""
    import json
    packages = []
    data = json.loads(content)
    
    for dep_type in ["dependencies", "devDependencies"]:
        deps = data.get(dep_type, {})
        for name, ver in deps.items():
            # Remove ^, ~, etc.
            clean_ver = re.sub(r'[\^~>=<]', '', ver)
            packages.append({
                "name": name,
                "version": clean_ver,
                "operator": "==",
                "raw": f"{name}@{ver}"
            })
    
    return packages

