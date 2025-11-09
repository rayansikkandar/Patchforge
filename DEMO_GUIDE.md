# PatchForge Demo Guide

## Overview

This guide provides two demo paths for showcasing PatchForge:

1. **Production Demo**: Fast, reliable, shows real-world usage
2. **Intelligence Demo**: Showcases ReAct loop and agent reasoning

## Demo Path 1: Production Demo (Fast & Reliable)

### What It Shows
- Automatic CVE scanning
- Smart PR checking (skips CVEs with existing PRs)
- Efficient patch generation
- Validation and PR creation

### How to Run
```bash
cd /Users/rayansikkandar/PatchForge
source venv/bin/activate
python main.py
```

### Steps
1. Enter GitHub username
2. Select repository (e.g., `pathforge-demo`)
3. Watch it scan, patch, validate, and create PR
4. **Key Point**: If a CVE already has a PR, it's automatically skipped!

### Talking Points
- "PatchForge automatically checks for existing PRs"
- "It won't create duplicate patches"
- "The system is intelligent enough to know what's already fixed"
- "End-to-end automation from scan to PR"

### Expected Output
```
🔍 SCANNING FOR VULNERABILITIES
Found 5 high-severity CVEs

⏭️  Skipping CVE-2020-14343 - PR already exists
⏭️  Skipping CVE-2023-30861 - PR already exists

→ Targeting: CVE-2023-25577
✅ Patch generated
✅ Validation passed
✅ PR created
```

---

## Demo Path 2: Intelligence Demo (ReAct Loop Showcase)

### What It Shows
- Intentional conflict creation
- Agent reasoning and analysis
- Multi-iteration refinement
- Intelligent conflict resolution

### How to Run
```bash
cd /Users/rayansikkandar/PatchForge
source venv/bin/activate
python main.py --demo-react
```

### Steps
1. Enter GitHub username
2. Select repository
3. Demo mode creates intentional conflicts
4. Watch the agent reason through conflicts
5. See multiple retry attempts
6. Observe intelligent refinement

### Talking Points
- "Watch the agent think through the problem"
- "It detects conflicts and reasons about solutions"
- "Multiple iterations show learning and adaptation"
- "The system can fix its own mistakes"

### Expected Output
```
🎭 DEMO MODE: ReAct Loop Showcase

🔧 GENERATING & VALIDATING PATCH (Attempt 1/3)
✓ Patch generated
⚠️  VALIDATION FAILED

💡 Agent Analysis:
   • MarkupSafe needs upgrading to >=2.1.1 for Flask 2.3.3+
   • Flask upgrade requires MarkupSafe upgrade for compatibility

🤔 Agent Reasoning:
   Analyzing conflict and refining approach...
   Using Nemotron to resolve dependency conflicts

🔁 Retrying with refined approach...

🔧 GENERATING & VALIDATING PATCH (Attempt 2/3)
✓ Refined patch generated
✅ VALIDATION PASSED
✨ Patch refined successfully after 2 attempts
```

---

## Demo Path 3: Full Feature Showcase

### What It Shows
- All features combined
- CVE explanations
- ReAct loop
- PR checking

### How to Run
```bash
python main.py --explain --demo-react
```

### Talking Points
- "Comprehensive security patching"
- "Intelligent conflict resolution"
- "Detailed explanations for developers"
- "Autonomous end-to-end process"

---

## For Judges: Key Points to Emphasize

### 1. Intelligence
- **PR Checking**: "It knows what's already fixed"
- **Conflict Resolution**: "It can fix its own mistakes"
- **Reasoning**: "Watch it think through problems"

### 2. Autonomy
- **End-to-End**: "From scan to PR, fully automated"
- **Self-Correction**: "Multiple attempts with learning"
- **Decision Making**: "Chooses optimal solutions"

### 3. Reliability
- **Validation**: "Tests before committing"
- **Error Handling**: "Graceful failure and retry"
- **Production Ready**: "Handles real-world scenarios"

### 4. Developer Experience
- **Clear PRs**: "Well-documented patches"
- **Explanations**: "Understands why fixes are needed"
- **Transparency**: "Shows reasoning process"

---

## Troubleshooting

### Demo Mode Doesn't Trigger Conflicts
- Check Python version (3.13 has special handling)
- Verify requirements.txt has conflicts
- Look for "needs_retry" in validation results

### PR Checking Doesn't Work
- Verify GITHUB_TOKEN is set
- Check repository name format (owner/repo)
- Ensure PR titles contain "CVE-"

### ReAct Loop Doesn't Engage
- Check validation errors (must be conflicts, not build errors)
- Verify Nemotron API is accessible
- Look for "needs_retry: True" in validation

---

## Quick Reference

| Mode | Command | Best For |
|------|---------|----------|
| Production | `python main.py` | Real-world usage |
| Intelligence | `python main.py --demo-react` | Showcasing ReAct loop |
| Explanations | `python main.py --explain` | Detailed CVE info |
| Full Demo | `python main.py --explain --demo-react` | Complete showcase |

---

**Choose the demo path that best fits your audience!** 🚀

