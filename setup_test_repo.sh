#!/bin/bash
# Setup script for creating a test GitHub repository for PatchForge demo

set -e

echo "🔧 PatchForge Test Repository Setup"
echo "===================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "This script will help you create a test repository for the PatchForge demo."
echo ""
echo "Steps:"
echo "  1. Create a new repository on GitHub (we'll guide you)"
echo "  2. Initialize the local repo with the demo app"
echo "  3. Push to GitHub"
echo ""

# Get GitHub username and repo name
read -p "Enter your GitHub username: " github_username
read -p "Enter repository name (e.g., 'patchforge-test' or 'vulnerable-app'): " repo_name

repo_full_name="${github_username}/${repo_name}"

echo ""
echo "📋 Repository: ${repo_full_name}"
echo ""

# Check if repo directory already exists
if [ -d "../${repo_name}" ]; then
    echo "⚠️  Directory ../${repo_name} already exists!"
    read -p "Do you want to use it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please choose a different repository name or remove the existing directory."
        exit 1
    fi
    repo_dir="../${repo_name}"
else
    repo_dir="../${repo_name}"
    mkdir -p "$repo_dir"
fi

# Check if it's already a git repo
if [ -d "$repo_dir/.git" ]; then
    echo "✅ Git repository already initialized"
else
    echo "📦 Initializing git repository..."
    cd "$repo_dir"
    git init
    git branch -M main
    cd - > /dev/null
fi

# Copy demo app files
echo "📁 Copying demo app files..."
cd "$repo_dir"

# Copy requirements.txt
cp "../PatchForge/demo/vulnerable_app/requirements.txt" .

# Create a simple README
cat > README.md << EOF
# PatchForge Test Repository

This is a test repository for PatchForge demo.

## Vulnerable Packages

- Flask==2.0.1
- requests==2.25.0
- Jinja2==2.11.0

This repository contains vulnerable packages for testing PatchForge's CVE patching capabilities.

## Purpose

This repo is used to test PatchForge's automated CVE scanning, patch generation, and PR creation.

EOF

# Create a simple Python file to make it a valid repo
cat > app.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Flask app for testing PatchForge
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, PatchForge!"

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Stage files
git add requirements.txt README.md app.py

# Check if there are any commits
if git log -1 &> /dev/null; then
    echo "✅ Repository already has commits"
else
    echo "💾 Making initial commit..."
    git commit -m "Initial commit: Vulnerable app for PatchForge demo"
fi

echo ""
echo "✅ Local repository setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create the repository on GitHub:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: ${repo_name}"
echo "   - Description: PatchForge test repository"
echo "   - Choose: Public or Private"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo "   - Click 'Create repository'"
echo ""
echo "2. After creating on GitHub, press Enter to continue..."
read -p "Press Enter when the repository is created on GitHub..."

echo ""
echo "🔗 Setting up remote..."
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin "https://github.com/${repo_full_name}.git"
else
    git remote add origin "https://github.com/${repo_full_name}.git"
fi

echo "✅ Remote configured: https://github.com/${repo_full_name}.git"
echo ""

# Check GitHub token for authentication
if [ -f "../PatchForge/.env" ]; then
    source ../PatchForge/.env
    if [ -n "$GITHUB_TOKEN" ] && [ "$GITHUB_TOKEN" != "your_github_token_here" ]; then
        echo "🔐 Using GitHub token for authentication..."
        git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${repo_full_name}.git"
    fi
fi

echo "📤 Pushing to GitHub..."
echo ""

# Try to push
if git push -u origin main 2>&1; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
else
    echo ""
    echo "⚠️  Push failed. This might be because:"
    echo "   - The repository doesn't exist on GitHub yet"
    echo "   - Authentication failed"
    echo "   - You need to set up SSH keys or use token authentication"
    echo ""
    echo "You can push manually with:"
    echo "   cd ${repo_dir}"
    echo "   git push -u origin main"
    echo ""
    echo "Or if you need to authenticate:"
    echo "   git remote set-url origin https://YOUR_TOKEN@github.com/${repo_full_name}.git"
    echo "   git push -u origin main"
fi

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "📋 Repository details:"
echo "   Local path: ${repo_dir}"
echo "   GitHub: https://github.com/${repo_full_name}"
echo ""
echo "🚀 Now you can run the PatchForge demo:"
echo "   cd ../PatchForge"
echo "   ./run_demo.sh ${repo_full_name}"
echo ""
echo "Or run directly:"
echo "   cd ../PatchForge"
echo "   source venv/bin/activate"
echo "   python main.py ${repo_dir} ${repo_full_name}"
echo ""

