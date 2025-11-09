# PatchForge Demo Guide

## Quick Start

Run the demo against the bundled vulnerable app:

```bash
./run_demo.sh your-github-username/vulnerable-app
```

Or manually:

```bash
python main.py demo/vulnerable_app your-github-username/vulnerable-app
```

## What the Demo Does

The demo uses the bundled `demo/vulnerable_app` which contains:

```
Flask==2.0.1      # Has known CVEs (e.g., CVE-2023-30861)
requests==2.25.0  # Has known CVEs
Jinja2==2.11.0    # Has known CVEs
```

### Pipeline Steps

1. **🔍 Scanner**: Scans `requirements.txt` and queries NVD for CVEs
2. **🔬 Researcher**: Uses Nemotron to analyze vulnerabilities and recommend fixes
3. **🔧 Patch Generator**: Generates patches (updates vulnerable packages)
4. **🧪 Validator**: Tests patches in isolated venv (validates dependency installation)
5. **📝 PR Creator**: Creates GitHub PR with security fixes

## Prerequisites

### 1. API Keys

Make sure your `.env` file has real API keys:

```bash
# Edit .env
nano .env

# Should contain:
NVIDIA_API_KEY=your_actual_nvidia_key
GITHUB_TOKEN=your_actual_github_token
NVD_API_KEY=your_actual_nvd_key  # Optional but recommended
```

### 2. GitHub Repository

You need a GitHub repository to create the PR. Options:

**Option A: Use existing repo**
```bash
./run_demo.sh yourusername/existing-repo
```

**Option B: Create a test repo**
1. Go to GitHub and create a new repository (e.g., `vulnerable-app`)
2. Initialize it with the demo app:
   ```bash
   cd demo/vulnerable_app
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/vulnerable-app.git
   git push -u origin main
   ```
3. Run the demo:
   ```bash
   cd ../..
   ./run_demo.sh yourusername/vulnerable-app
   ```

### 3. Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

## What Happens

### Expected Output

```
╔═══════════════════════════════════════════════════════════╗
║   PatchForge - Autonomous CVE Patching Agent            ║
╚═══════════════════════════════════════════════════════════╝

🚀 Starting PatchForge pipeline...
🔍 Scanning repository: demo/vulnerable_app
Found 3 packages
🚨 Found X high-severity CVEs

Processing: CVE-2023-30861 (CVSS: 8.1)
🔬 Researching CVE-2023-30861
✅ Research complete
🔧 Generating patch for CVE-2023-30861
✅ Patch generated
🧪 Validating patch for CVE-2023-30861
✅ Dependencies validated successfully
✅ Validation passed!
📝 Creating PR for CVE-2023-30861
✅ PR created: https://github.com/yourusername/repo/pull/1

╔═══════════════════════════════════════════════════════════╗
║   ✅ SUCCESS! Pull Request Created                       ║
╚═══════════════════════════════════════════════════════════╝
```

### What Gets Created

1. **GitHub Branch**: `security-patch-cve-2023-30861-<timestamp>`
2. **Updated requirements.txt**: With secure package versions
3. **GitHub PR**: With CVE details, fix description, and validation results

## Troubleshooting

### "No high-severity CVEs found"
- The NVD API might not return results for demo packages
- Try running with real vulnerable packages in a real repo

### "NVD API error"
- Check your `NVD_API_KEY` in `.env`
- NVD API has rate limits; wait and retry

### "GitHub API error"
- Verify your `GITHUB_TOKEN` has repo write permissions
- Check that the repository exists and you have access

### "Nemotron API error"
- Verify your `NVIDIA_API_KEY` is correct
- Check your NVIDIA API quota/limits

### "Validation failed"
- The patch might have dependency conflicts
- Check the validation details in the error message

## Testing Without Creating PRs

If you want to test without creating GitHub PRs, you can:

1. Use the dry-run test:
   ```bash
   python tests/test_pipeline_dry_run.py
   ```

2. Modify `main.py` to skip PR creation (comment out the PR creator step)

3. Use a throwaway test repository

## Next Steps

After the demo works:

1. Point PatchForge at your real repositories
2. Customize CVSS score threshold in `config.py`
3. Add more dependency file parsers (package.json, etc.)
4. Extend validation with unit tests
5. Add more agents for additional functionality

## Support

See `README.md` for general usage and `SECURITY.md` for security best practices.

