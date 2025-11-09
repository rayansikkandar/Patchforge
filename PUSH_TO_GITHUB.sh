#!/bin/bash
# Script to push PatchForge to GitHub

echo "🚀 PatchForge GitHub Setup"
echo "=========================="
echo ""

# Check if remote already exists
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    git remote remove origin
fi

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

# Repository name
REPO_NAME="PatchForge"

echo ""
echo "📋 Repository Details:"
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo ""

# Check if repository exists
echo "⚠️  Make sure you've created the repository on GitHub first!"
echo "   Go to: https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Description: Autonomous CVE Patching Agent powered by NVIDIA Nemotron"
echo "   Visibility: Public or Private"
echo "   DO NOT initialize with README, .gitignore, or license"
echo ""
read -p "Have you created the repository? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please create the repository first, then run this script again."
    exit 1
fi

# Add remote
echo "🔗 Adding remote repository..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Verify remote
echo ""
echo "✅ Remote added:"
git remote -v

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Rename branch to main if needed
git branch -M main

# Push
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Your code is now on GitHub:"
    echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "🎉 Next steps:"
    echo "   1. Go to your repository settings"
    echo "   2. Add teammates as collaborators"
    echo "   3. Share the repository URL with your team"
    echo ""
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. Repository exists on GitHub"
    echo "   2. You have push access"
    echo "   3. Your GitHub credentials are correct"
    echo ""
fi

