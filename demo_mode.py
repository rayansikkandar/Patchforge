"""
Demo mode utilities for showcasing PatchForge features
"""

import os
from utils.logger import setup_logger

logger = setup_logger("DemoMode")

def create_react_test_scenario(repo_path: str):
    """
    Create a scenario that will trigger multiple ReAct iterations
    This creates dependency conflicts that require refinement
    """
    logger.info("🎭 Creating ReAct demo scenario with intentional conflicts")
    
    # Create a requirements.txt with a known conflict pattern
    # This will trigger multi-package updates when Flask is upgraded
    conflict_requirements = """# ReAct Loop Demo - Intentional dependency conflicts
# This scenario is designed to showcase PatchForge's multi-package update capability

# Flask ecosystem with known vulnerabilities
Flask==2.0.1          # CVE-2023-30861 (CVSS: 9.8) - Will upgrade to 2.3.3
                       # INTENTIONAL: Flask 2.3.3 requires Werkzeug>=2.2.2 and MarkupSafe>=2.1.1
Werkzeug==2.0.0       # CVE-2023-25577 (CVSS: 7.5) - TOO OLD for Flask 2.3.3
                       # This will trigger coordinated upgrade in ReAct loop

# INTENTIONAL CONFLICT: MarkupSafe is too old for Flask 2.3.3+
MarkupSafe==2.0.0     # Flask 2.3.3 requires MarkupSafe>=2.1.1
                       # This will cause a conflict that triggers multi-package update

# Jinja2 also has dependencies on MarkupSafe
Jinja2==3.0.0         # Should be compatible, but may need update

# Other vulnerable packages
requests==2.25.1      # CVE-2023-32681 (CVSS: 6.1)
urllib3==1.26.4       # CVE-2023-43804 (CVSS: 5.9)

# PyYAML for serialization vulnerabilities
PyYAML==5.3.1         # CVE-2020-14343 (CVSS: 9.8)

# Testing
pytest>=7.0.0

# DEMO EXPECTATION:
# Attempt 1: Upgrade Flask 2.0.1 → 2.3.3 → FAIL (Werkzeug 2.0.0 incompatible)
# Attempt 2: Nemotron refines → Upgrades Flask + Werkzeug + MarkupSafe → PASS ✓
"""
    
    req_file = os.path.join(repo_path, "requirements.txt")
    
    # Backup original if it exists
    if os.path.exists(req_file):
        backup_file = os.path.join(repo_path, "requirements.txt.backup")
        with open(req_file, 'r') as f:
            original = f.read()
        with open(backup_file, 'w') as f:
            f.write(original)
        logger.info(f"📦 Backed up original requirements.txt to requirements.txt.backup")
    
    # Write new requirements with conflicts
    with open(req_file, 'w') as f:
        f.write(conflict_requirements)
    
    logger.info("✅ Created ReAct test scenario")
    logger.info("  - Flask upgrade will conflict with MarkupSafe 2.0.0")
    logger.info("  - Agent will need multiple iterations to resolve")
    logger.info("  - This showcases intelligent conflict resolution")
    
    return req_file

def restore_original_requirements(repo_path: str):
    """Restore the original requirements.txt from backup"""
    backup_file = os.path.join(repo_path, "requirements.txt.backup")
    req_file = os.path.join(repo_path, "requirements.txt")
    
    if os.path.exists(backup_file):
        with open(backup_file, 'r') as f:
            original = f.read()
        with open(req_file, 'w') as f:
            f.write(original)
        os.remove(backup_file)
        logger.info("✅ Restored original requirements.txt")
        return True
    
    return False

def create_complex_scenario(repo_path: str):
    """
    Create a more complex scenario with multiple conflicts
    """
    logger.info("🎭 Creating complex multi-conflict scenario")
    
    complex_requirements = """# Complex Multi-Conflict Scenario
# Multiple packages need upgrades, creating cascade of conflicts

Flask==2.0.1          # Needs upgrade, but conflicts with MarkupSafe
MarkupSafe==2.0.0     # Too old for Flask 2.3.3+
Jinja2==3.0.0         # Needs compatible MarkupSafe
Werkzeug==2.0.0       # Part of Flask ecosystem
PyYAML==5.3.1         # Has its own vulnerabilities
requests==2.25.1      # Multiple conflicts possible
urllib3==1.26.4       # Related to requests

pytest>=7.0.0
"""
    
    req_file = os.path.join(repo_path, "requirements.txt")
    
    if os.path.exists(req_file):
        backup_file = os.path.join(repo_path, "requirements.txt.backup")
        with open(req_file, 'r') as f:
            original = f.read()
        with open(backup_file, 'w') as f:
            f.write(original)
    
    with open(req_file, 'w') as f:
        f.write(complex_requirements)
    
    logger.info("✅ Created complex scenario with multiple conflicts")
    return req_file

