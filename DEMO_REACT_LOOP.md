# Demo: ReAct Loop Feature

## Overview

This demo showcases PatchForge's **ReAct-style retry loop** that automatically refines patches when validation fails.

## Demo Scenario

The `patchforge-demo` repository is configured to trigger the ReAct loop:

### Initial State
- **PyYAML**: 5.3.1 (vulnerable - CVE-2020-14343)
- **Jinja2**: 2.11.3 (vulnerable - CVE-2024-22195)
- **Conflict**: PyYAML 5.4.1+ requires Jinja2 3.0+

### What Happens

1. **First Attempt**:
   - PatchForge upgrades PyYAML: 5.3.1 → 5.4.1
   - Validation fails: "Jinja2==2.11.3 conflicts with PyYAML 5.4.1"

2. **ReAct Loop Engages**:
   - Nemotron analyzes the error
   - Identifies the dependency conflict
   - Refines the patch to upgrade both packages

3. **Second Attempt**:
   - PyYAML: 5.3.1 → 5.4.1 (security fix)
   - Jinja2: 2.11.3 → 3.1.2 (compatibility fix)
   - Validation passes: All dependencies compatible

4. **PR Created**:
   - Includes both upgrades
   - Documents the refinement process
   - Shows ReAct loop was used

## Running the Demo

```bash
cd /Users/rayansikkandar/PatchForge
source venv/bin/activate
python main.py
```

When prompted:
1. Enter GitHub username: `rayansikkandar`
2. Select repository: `pathforge-demo`
3. Watch the ReAct loop in action!

## Expected Output

```
[3/5] 🔧 GENERATING & VALIDATING PATCH
────────────────────────────────────────────────────────────
✓ Reading dependency file
✓ Updating package version

✓ Patch generated
File: requirements.txt
Changes: Security: Upgrade pyyaml from 5.3.1 to 5.4.1 to fix CVE-2020-14343

✓ Creating test environment
✓ Running dependency checks
✓ Testing installation

⚠️  VALIDATION FAILED (Attempt 1/3)
Dependency installation failed: ERROR: Cannot install ... Jinja2==2.11.3 because these package versions have conflicting dependencies.

🔁 Retrying with refined approach...

🔄 Retry 2/3
Refining patch based on previous feedback...
✓ Analyzing feedback
✓ Refining patch

✓ Refined patch generated

✓ Re-validating refined patch

✓ VALIDATION PASSED
All tests successful - patch is safe to deploy
✨ Patch refined successfully after 2 attempts
```

## What to Look For

1. **First Attempt**: Simple patch (PyYAML only)
2. **Validation Failure**: Clear error message about conflict
3. **Retry Message**: "🔄 Retry 2/3" appears
4. **Refinement**: Nemotron analyzes and refines
5. **Success**: Patch passes with both upgrades
6. **Summary**: Shows "Total Attempts: 2" and "ReAct Loop: Used"

## PR Description

The created PR will include:

```markdown
### 🔄 ReAct Loop Refinement

This patch was refined through **2 attempts** using PatchForge's ReAct-style retry loop:

1. **Attempt 1**: Initial patch generated
2. **Validation**: Failed with dependency conflicts
3. **Refinement**: Nemotron analyzed errors and refined the patch
4. **Attempt 2**: Refined patch passed all validation checks

The final patch resolves all dependency conflicts and ensures compatibility.
```

## Key Features Demonstrated

✅ **Automatic conflict detection**
✅ **Intelligent patch refinement**
✅ **Multi-package upgrades**
✅ **Transparent retry process**
✅ **Detailed PR documentation**

## Troubleshooting

If the demo doesn't trigger the retry loop:

1. **Check Python version**: Python 3.13 build errors are handled specially
2. **Check dependencies**: Ensure Jinja2 conflict exists
3. **Check logs**: Look for "ReAct Loop - Attempt" messages
4. **Manual test**: Try upgrading PyYAML manually to see the conflict

## Success Criteria

- ✅ First attempt fails with dependency conflict
- ✅ Second attempt refines patch with both upgrades
- ✅ Validation passes on second attempt
- ✅ PR includes ReAct loop documentation
- ✅ Summary shows "Total Attempts: 2"

---

**This demo proves PatchForge can fix its own mistakes!** 🚀

