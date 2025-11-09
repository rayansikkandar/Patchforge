# PatchForge - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

**Option A: Use .env file (recommended)**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your keys:
# - NVIDIA_API_KEY=your_nvidia_api_key
# - GITHUB_TOKEN=your_github_token
# - NVD_API_KEY=your_nvd_api_key (optional)
```

**Option B: Export environment variables**

```bash
export NVIDIA_API_KEY="your_nvidia_api_key"
export GITHUB_TOKEN="your_github_token"
export NVD_API_KEY="your_nvd_api_key"  # Optional
```

### Step 3: Setup RAG Database (Optional but Recommended)

For professional PR descriptions with NVD context:

```bash
# Option A: Use local JSON files (fastest)
# Place CVE JSON files in data/ directory, then:
python setup_rag.py

# Option B: Download from NVD API
python setup_rag.py
```

### Step 4: Run PatchForge!

## 🎯 Running PatchForge

### Interactive Mode (Recommended)

```bash
python main.py
```

This will:
1. Ask for your GitHub username
2. List your repositories
3. Let you select a repository
4. Run the full pipeline with visual feedback

### Non-Interactive Mode

```bash
python main.py <repo_path> <github_repo_name>
```

**Example:**
```bash
python main.py ../pathforge-demo rayansikkandar/pathforge-demo
```

### With CVE Explanations

```bash
python main.py --explain
```

Adds detailed CVE explanations to PR descriptions using Nemotron.

### Demo Mode (Showcase ReAct Loop)

```bash
python main.py --demo-react
```

Creates intentional conflicts to showcase the ReAct retry loop. Perfect for demonstrations!

### Combined Flags

```bash
# Interactive mode with explanations
python main.py --explain

# Non-interactive with explanations
python main.py ../pathforge-demo rayansikkandar/pathforge-demo --explain

# Demo mode with explanations
python main.py --demo-react --explain
```

## 📋 Complete Example

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Setup RAG (optional)
python setup_rag.py

# 4. Run
python main.py
```

## 🎬 Demo Workflow

### For Judges Demo:

```bash
# 1. Interactive mode (shows repository selection)
python main.py --explain

# 2. Or demo mode (showcases ReAct loop)
python main.py --demo-react --explain
```

### What Happens:

1. **Scanner**: Finds CVEs in dependencies
2. **Researcher**: Finds secure versions using OSV
3. **Patch Generator**: Creates patches (with ReAct retry if needed)
4. **Validator**: Tests patches in isolated environment
5. **PR Creator**: Creates GitHub PR with professional description

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'utils'"

Make sure you're in the PatchForge directory:
```bash
cd /path/to/PatchForge
python main.py
```

### "NVIDIA API key not found"

Check your `.env` file or export the environment variable:
```bash
export NVIDIA_API_KEY="your_key"
```

### "GitHub token not found"

Check your `.env` file or export the environment variable:
```bash
export GITHUB_TOKEN="your_token"
```

### "RAG database not found"

This is optional, but if you want RAG features:
```bash
python setup_rag.py
```

### "No CVEs found"

Make sure your repository has dependency files:
- `requirements.txt` (Python)
- `package.json` (Node.js)

## 📚 More Information

- Full documentation: See `README.md`
- Architecture: See `README.md` Architecture section
- Testing: See `README.md` Testing section

## 🎯 Next Steps

1. Run PatchForge on your repository
2. Review the generated PRs
3. Merge and deploy!

---

**Ready to patch! 🚀**

