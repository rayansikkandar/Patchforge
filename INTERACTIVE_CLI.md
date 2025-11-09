# PatchForge Interactive CLI Guide

## 🎉 New Interactive Interface!

PatchForge now has a beautiful, interactive CLI that makes it easy to scan your repositories!

## 🚀 Quick Start

### Interactive Mode (Recommended)

Simply run:

```bash
cd /Users/rayansikkandar/PatchForge
source venv/bin/activate
python main.py
```

**What happens:**
1. Shows the PatchForge banner
2. Asks for your GitHub username
3. Fetches and displays your repositories
4. Lets you select a repository
5. Clones the repo (if needed)
6. Runs the full pipeline with visual feedback

### Non-Interactive Mode (Command Line)

You can still use command-line arguments:

```bash
python main.py <repo_path> <github_repo_name>
```

**Example:**
```bash
python main.py ../pathforge-demo rayansikkandar/pathforge-demo
```

## 📋 Features

### ✨ Interactive Repository Selection

- Lists all your GitHub repositories
- Shows repository details (public/private, stars, description)
- Easy selection by number
- Automatically clones repositories to `./temp_repos/`

### 🎨 Beautiful Visual Feedback

- Color-coded output
- Animated progress indicators
- Step-by-step progress tracking
- Clear success/error messages

### 🔍 Step-by-Step Pipeline

1. **🔍 Scanning** - Analyzes dependencies for CVEs
2. **🔬 Researching** - Queries NVD and analyzes vulnerabilities
3. **🔧 Generating** - Creates security patches
4. **🧪 Validating** - Tests patches in isolated environment
5. **📝 Creating PR** - Opens GitHub pull request

## 🎯 Example Flow

```
╔═══════════════════════════════════════════════════════════════╗
║                    PATCHFORGE                                 ║
║         Autonomous CVE Patching Agent                         ║
║         Powered by NVIDIA Nemotron 70B                        ║
╚═══════════════════════════════════════════════════════════════╝

Enter your GitHub username: rayansikkandar

⠹ Fetching repositories for rayansikkandar
✓ Fetching repositories for rayansikkandar

Found 12 repositories:

   1. pathforge-demo (public) ⭐ 5
      Demo repository for PatchForge testing
   2. my-web-app (public) ⭐ 45
      A full-stack web application
   3. data-project (private)
      Data science experiments
   ...

Select repository number (1-12): 1

✓ Selected: rayansikkandar/pathforge-demo

⠹ Cloning pathforge-demo
✓ Repository cloned successfully

────────────────────────────────────────────────────────────
Ready to scan: rayansikkandar/pathforge-demo
────────────────────────────────────────────────────────────

Press ENTER to start autonomous security scan, or Ctrl+C to cancel

[1/5] 🔍 SCANNING FOR VULNERABILITIES
────────────────────────────────────────────────────────────
⠹ Analyzing dependencies
✓ Analyzing dependencies

⚠️  Found 2 high-severity CVE(s):
  • CVE-2025-23211 - CVSS: 9.9/10
    Package: jinja2 v2.11.0
  • CVE-2023-30861 - CVSS: 8.1/10
    Package: flask v2.0.1

→ Targeting: CVE-2025-23211

[2/5] 🔬 RESEARCHING VULNERABILITY
────────────────────────────────────────────────────────────
⠹ Querying NVD database
✓ Querying NVD database
⠹ Analyzing fix strategies
✓ Analyzing fix strategies

✓ Research complete
Root cause identified and fix strategy developed

[3/5] 🔧 GENERATING SECURITY PATCH
────────────────────────────────────────────────────────────
⠹ Reading vulnerable files
✓ Reading vulnerable files
⠹ Crafting patch
✓ Crafting patch

✓ Patch generated
File: requirements.txt
Changes: Upgrade jinja2 (2.11.0 -> 3.0.3), Flask (2.0.1 -> 2.0.2) to fix CVE-2025-23211 and resolve dependency conflicts

[4/5] 🧪 VALIDATING PATCH
────────────────────────────────────────────────────────────
⠹ Creating test environment
✓ Creating test environment
⠹ Running dependency checks
✓ Running dependency checks
⠹ Testing installation
✓ Testing installation

✓ VALIDATION PASSED
All tests successful - patch is safe to deploy

[5/5] 📝 CREATING PULL REQUEST
────────────────────────────────────────────────────────────
⠹ Preparing commit
✓ Preparing commit
⠹ Creating branch
✓ Creating branch
⠹ Opening pull request
✓ Opening pull request

════════════════════════════════════════════════════════════
✓ PIPELINE COMPLETE
════════════════════════════════════════════════════════════

📊 Summary:
  • CVE Fixed: CVE-2025-23211
  • Severity: CVSS 9.9/10
  • Package: jinja2
  • Validation: PASSED ✓

🔗 Pull Request:
  https://github.com/rayansikkandar/pathforge-demo/pull/2

The security patch is ready for review and merge!
Check your GitHub notifications 📬
```

## 🛠️ Configuration

### Repository Storage

Repositories are cloned to `./temp_repos/` directory:
- Already cloned repos are reused
- Shallow clones (--depth 1) for speed
- Automatically created if it doesn't exist

### GitHub Authentication

Uses your `GITHUB_TOKEN` from `.env`:
- Fetches your repositories
- Creates branches and PRs
- Requires repo read/write permissions

## 🎨 Color Scheme

- **Blue**: Information and headers
- **Green**: Success messages
- **Yellow**: Warnings and selections
- **Red**: Errors and critical issues
- **Cyan**: Highlights and emphasis

## 💡 Tips

1. **Quick Selection**: Just type the number and press Enter
2. **Cancel Anytime**: Press Ctrl+C to cancel
3. **Reuse Clones**: Already cloned repos are reused automatically
4. **Non-Interactive**: Use command-line args for scripts/CI

## 🔧 Troubleshooting

### "No repositories found"
- Check your GitHub token has correct permissions
- Verify your username is correct
- Check token hasn't expired

### "Clone failed"
- Check internet connection
- Verify repository exists and is accessible
- Check git is installed

### "Repository already exists"
- The repo will be reused from `./temp_repos/`
- Delete `./temp_repos/<repo-name>` to force re-clone

## 🚀 Next Steps

1. Run `python main.py` to start interactive mode
2. Select a repository to scan
3. Watch PatchForge automatically patch CVEs
4. Review and merge the PR on GitHub

Enjoy the new interactive experience! 🎉

