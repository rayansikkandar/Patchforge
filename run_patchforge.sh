#!/bin/bash
# PatchForge Runner - Easy way to specify repository to check

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 PatchForge - Repository Configuration${NC}"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "   Run: ./setup_env.sh"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
set -a
source .env
set +a

# Get repository path
if [ -z "$1" ]; then
    echo "Usage: ./run_patchforge.sh <repo_path> <github_repo_name>"
    echo ""
    echo "Examples:"
    echo "  ./run_patchforge.sh ../my-app myusername/my-app"
    echo "  ./run_patchforge.sh ./demo/vulnerable_app myusername/vulnerable-app"
    echo "  ./run_patchforge.sh /path/to/repo myusername/repo-name"
    echo ""
    echo "Or specify via environment variables:"
    echo "  export PATCHFORGE_REPO_PATH=../my-app"
    echo "  export PATCHFORGE_REPO_NAME=myusername/my-app"
    echo "  ./run_patchforge.sh"
    echo ""
    exit 1
fi

REPO_PATH="$1"
REPO_NAME="${2:-${PATCHFORGE_REPO_NAME}}"

if [ -z "$REPO_NAME" ]; then
    echo -e "${YELLOW}⚠️  GitHub repository name not specified!${NC}"
    echo ""
    read -p "Enter GitHub repo (username/repo-name): " REPO_NAME
    if [ -z "$REPO_NAME" ]; then
        echo "GitHub repo name is required!"
        exit 1
    fi
fi

# Check if repository path exists
if [ ! -d "$REPO_PATH" ]; then
    echo -e "${YELLOW}⚠️  Repository path not found: $REPO_PATH${NC}"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$REPO_PATH/requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  No requirements.txt found in $REPO_PATH${NC}"
    echo "   PatchForge requires a requirements.txt file"
    exit 1
fi

echo -e "${GREEN}✅ Repository Configuration:${NC}"
echo "   Local Path: $REPO_PATH"
echo "   GitHub Repo: $REPO_NAME"
echo ""

# Show what will be scanned
echo "📋 Packages to scan:"
python3 -c "
import os
import sys
sys.path.insert(0, '.')
from utils.parsers import parse_requirements

req_file = os.path.join('$REPO_PATH', 'requirements.txt')
with open(req_file, 'r') as f:
    content = f.read()
packages = parse_requirements(content)
for pkg in packages[:10]:
    print(f'   - {pkg[\"name\"]} ({pkg[\"version\"]})')
if len(packages) > 10:
    print(f'   ... and {len(packages) - 10} more')
"

echo ""
echo -e "${BLUE}🚀 Starting PatchForge...${NC}"
echo ""

# Run PatchForge
python main.py "$REPO_PATH" "$REPO_NAME"

