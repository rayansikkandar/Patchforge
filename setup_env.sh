#!/bin/bash
# Setup script for PatchForge environment variables

set -e

echo "🔐 PatchForge Environment Setup"
echo "================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Copy template
cp .env.example .env

echo "✅ Created .env from template"
echo ""
echo "📝 Please edit .env with your actual API keys:"
echo ""
echo "   NVIDIA_API_KEY=your_actual_nvidia_key"
echo "   GITHUB_TOKEN=your_actual_github_token"
echo "   NVD_API_KEY=your_actual_nvd_key  # Optional"
echo ""
echo "You can edit it with:"
echo "   nano .env"
echo "   # or"
echo "   vim .env"
echo "   # or"
echo "   code .env"
echo ""
echo "⚠️  Remember: .env is git-ignored and should never be committed!"

