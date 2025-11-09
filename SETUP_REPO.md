# Setting Up a Test Repository for PatchForge Demo

## Quick Setup

Run the setup script:

```bash
./setup_test_repo.sh
```

The script will guide you through:
1. Creating a GitHub repository
2. Initializing the local repo with the demo app
3. Pushing to GitHub

## Manual Setup

If you prefer to set up manually:

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `patchforge-test` (or any name you prefer)
3. Description: "PatchForge test repository"
4. Choose: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 2: Initialize Local Repository

```bash
# Create directory (outside PatchForge)
cd ..
mkdir patchforge-test
cd patchforge-test

# Initialize git
git init
git branch -M main

# Copy demo app
cp ../PatchForge/demo/vulnerable_app/requirements.txt .

# Create README
cat > README.md << 'EOF'
# PatchForge Test Repository

Vulnerable app for testing PatchForge's CVE patching capabilities.
EOF

# Create a simple app file
cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, PatchForge!"
EOF

# Commit
git add .
git commit -m "Initial commit: Vulnerable app for PatchForge demo"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/patchforge-test.git

# Push
git push -u origin main
```

### Step 3: Run PatchForge Demo

```bash
cd PatchForge
source venv/bin/activate
python main.py ../patchforge-test YOUR_USERNAME/patchforge-test
```

## Repository Contents

The test repository will contain:

- `requirements.txt` - Vulnerable packages:
  - Flask==2.0.1 (has CVEs)
  - requests==2.25.0 (has CVEs)
  - Jinja2==2.11.0 (has CVEs)

- `README.md` - Repository description
- `app.py` - Simple Flask app (optional)

## Authentication

If you encounter authentication issues:

### Option 1: Use GitHub Token in URL

```bash
git remote set-url origin https://YOUR_TOKEN@github.com/username/repo.git
```

### Option 2: Use SSH

```bash
git remote set-url origin git@github.com:username/repo.git
```

### Option 3: Configure Git Credential Helper

```bash
git config --global credential.helper osxkeychain  # macOS
# or
git config --global credential.helper store        # Linux
```

## Troubleshooting

### "Repository not found"
- Make sure the repository exists on GitHub
- Check that you have the correct username and repo name
- Verify your GitHub token has access

### "Authentication failed"
- Check your GitHub token in `.env`
- Make sure the token has `repo` scope
- Try using SSH instead of HTTPS

### "Push rejected"
- The repository might have different commits
- Try: `git push -u origin main --force` (use with caution)

## Next Steps

After the repository is set up:

1. Run the PatchForge demo:
   ```bash
   ./run_demo.sh YOUR_USERNAME/patchforge-test
   ```

2. PatchForge will:
   - Scan for CVEs
   - Research vulnerabilities
   - Generate patches
   - Validate patches
   - Create a GitHub PR

3. Check the PR on GitHub and merge it if everything looks good!

