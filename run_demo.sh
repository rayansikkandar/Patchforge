#!/bin/bash
# Demo runner for PatchForge
# Runs the full pipeline against the bundled vulnerable app

set -e

echo "🚀 PatchForge Demo Runner"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run: ./setup_env.sh"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    echo ""
elif ! python3 -c "import openai" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if API keys are set
if [ -z "$NVIDIA_API_KEY" ] || [ "$NVIDIA_API_KEY" = "your_nvidia_api_key_here" ]; then
    echo "⚠️  WARNING: NVIDIA_API_KEY not set or still has placeholder value"
    echo "   Please edit .env with your actual NVIDIA API key"
    echo ""
fi

if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    echo "⚠️  WARNING: GITHUB_TOKEN not set or still has placeholder value"
    echo "   Please edit .env with your actual GitHub token"
    echo ""
fi

# Check if demo app exists
if [ ! -f "demo/vulnerable_app/requirements.txt" ]; then
    echo "❌ Demo app not found at demo/vulnerable_app/requirements.txt"
    exit 1
fi

echo "📋 Demo Configuration:"
echo "   Repository path: demo/vulnerable_app"
echo "   Vulnerable packages: Flask==2.0.1, requests==2.25.0, Jinja2==2.11.0"
echo ""

# Get GitHub repo name from user or use default
if [ -z "$1" ]; then
    echo "⚠️  GitHub repository not specified!"
    echo ""
    echo "Usage: ./run_demo.sh <github-username>/<repo-name>"
    echo ""
    echo "Example:"
    echo "   ./run_demo.sh yourusername/vulnerable-app"
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "   - This will create a REAL GitHub PR in the specified repo"
    echo "   - Make sure the repo exists and you have write access"
    echo "   - Use a test/throwaway repo if you're unsure"
    echo ""
    read -p "Enter GitHub repo (username/repo-name) or press Ctrl+C to cancel: " repo_name
else
    repo_name=$1
fi

echo ""
echo "🚀 Starting PatchForge pipeline..."
echo "   This will:"
echo "   1. Scan for CVEs in Flask 2.0.1, requests 2.25.0, Jinja2 2.11.0"
echo "   2. Research vulnerabilities using Nemotron"
echo "   3. Generate security patches"
echo "   4. Validate patches in isolated environment"
echo "   5. Create GitHub PR with fixes"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Running PatchForge..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python main.py demo/vulnerable_app "$repo_name"

