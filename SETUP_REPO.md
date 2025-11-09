# Setting Up PatchForge Repository on GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `PatchForge` (or `patchforge`)
3. Description: "Autonomous multi-agent system for scanning codebases for CVEs, researching fixes, generating patches, validating them, and creating GitHub PRs automatically"
4. Visibility: **Public** (so teammates can see it) or **Private** (if you prefer)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Push Code to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /Users/rayansikkandar/PatchForge

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/PatchForge.git

# Rename branch to main if needed
git branch -M main

# Push the code
git push -u origin main
```

## Step 3: Verify

1. Go to your GitHub repository page
2. Verify all files are there
3. Check that `.env` is NOT in the repository (it should be git-ignored)
4. Verify `README.md` displays correctly

## Step 4: Share with Teammates

1. Go to repository settings
2. Click "Collaborators"
3. Add your teammates by their GitHub usernames
4. They will receive an invitation email

## Important Notes

### Security
- ✅ `.env` is git-ignored (secrets are safe)
- ✅ `.env.example` is included (template for teammates)
- ✅ `venv/` is git-ignored (virtual environment)
- ✅ API keys should be in `.env` (not committed)

### Setup for Teammates
Teammates should:
1. Clone the repository
2. Copy `.env.example` to `.env`
3. Add their own API keys to `.env`
4. Create and activate virtual environment
5. Install dependencies: `pip install -r requirements.txt`

## Repository Structure

```
PatchForge/
├── agents/           # Agent implementations
├── tools/            # API clients (OSV, GitHub, NVD)
├── utils/            # Utilities (logging, parsers)
├── tests/            # Test suite
├── demo_mode.py      # Demo scenario creation
├── main.py           # Main orchestration script
├── config.py         # Configuration
├── requirements.txt  # Dependencies
├── README.md         # Project documentation
├── .env.example      # Environment variable template
└── .gitignore        # Git ignore rules
```

## Next Steps

1. Create the GitHub repository
2. Push the code
3. Add teammates as collaborators
4. Share the repository URL with your team

---

**Ready to push?** Follow the steps above! 🚀
