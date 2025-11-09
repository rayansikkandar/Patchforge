# Quick Start: Running PatchForge Demo

## Prerequisites

1. ✅ NVIDIA API key configured in `.env`
2. ✅ GitHub token configured in `.env`
3. ✅ Demo repository created on GitHub

## Step 1: Create Demo Repository

If you haven't already, create the demo repository:

```bash
cd /Users/rayansikkandar/patchforge-demo

# Follow SETUP_GITHUB.md to push to GitHub
# Or run: ./setup_github.sh
```

## Step 2: Run PatchForge

```bash
cd /Users/rayansikkandar/PatchForge

# Activate virtual environment
source venv/bin/activate

# Run PatchForge
python main.py
```

## Step 3: Interactive Flow

1. **Enter GitHub username** when prompted
2. **Select repository** from the list (use arrow keys, Enter to select)
3. **Press Enter** to start the scan
4. **Watch the agents work**:
   - 🔍 Scanner finds vulnerabilities
   - 🔬 Researcher finds secure versions
   - 🔧 Patch Generator creates fixes
   - 🧪 Validator tests the patch
   - 📝 PR Creator submits pull request

## Step 4: Review the PR

1. Check the terminal for the PR URL
2. Visit the GitHub repository
3. Review the pull request with:
   - CVE details
   - Version upgrades
   - Validation results
   - Professional description

## Expected Results

- **Vulnerabilities found**: 7+ CVEs
- **Packages updated**: Flask, PyYAML, Werkzeug, etc.
- **Validation**: All checks passed
- **PR created**: Ready for review

## Troubleshooting

### "No repositories found"
- Check your GitHub token has `repo` permissions
- Verify the username is correct

### "Validation failed"
- Check npm/pip are installed
- Large packages may timeout (this is handled gracefully)

### "PR creation failed"
- Verify GitHub token has write permissions
- Check repository exists and is accessible

## Demo Script

For judges/demo purposes, see `DEMO_SCRIPT.md` for a complete presentation guide.

## Before & After Comparison

See `BEFORE_AFTER.md` for a detailed comparison of manual vs. automated patching.
