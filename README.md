# PatchForge

**Autonomous CVE Patching Agent** powered by NVIDIA Nemotron

PatchForge is a multi-agent system that automatically:
1. 🔍 **Scans** codebases for CVEs
2. 🔬 **Researches** vulnerabilities and fixes
3. 🔧 **Generates** security patches
4. 🔄 **Refines** patches using ReAct-style retry loop (up to 3 attempts)
5. 🧪 **Validates** patches before deployment
6. 📝 **Creates** GitHub PRs automatically

## 🆕 Key Features

### 🤖 RAG-Powered CVE Analysis with Vector Database

PatchForge uses **Retrieval-Augmented Generation (RAG)** over the National Vulnerability Database (NVD) with a **ChromaDB vector database** to provide grounded, authoritative CVE analysis:

- **Vector Database**: ChromaDB stores 38,000+ CVEs as vector embeddings for fast semantic search
- **Grounded Intelligence**: Queries official NVD data via vector database (not just API calls)
- **Professional PRs**: Generates CISO-ready PR descriptions using NVD context from vector search
- **Authoritative Explanations**: CVE fixes are based on official NVD advisories retrieved via vector similarity
- **Vector Search**: Semantic search over CVE descriptions enables accurate, context-aware retrieval
- **Demo Ready**: Vector database uses local JSON files for fast, reliable demos without API rate limits

### 🔄 ReAct-Style Retry Loop

PatchForge includes a **ReAct-style retry loop** that automatically refines patches when validation fails:

- **First attempt**: Fast regex-based patch generation
- **Validation fails**: Error feedback captured
- **Retry with AI**: Nemotron analyzes errors and refines the patch
- **Up to 3 attempts**: Intelligent conflict resolution with multi-package coordination
- **Success**: Only creates PR when validation passes

### 📦 Multi-Package Updates

When dependency conflicts are detected, PatchForge automatically coordinates updates across multiple packages:

- Analyzes dependency conflicts
- Uses precise compatibility rules (e.g., Flask 2.3.x → Werkzeug 2.3.3)
- Updates all necessary packages together
- Ensures compatibility across the dependency tree

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

**Option A: Use the setup script (recommended)**
```bash
./setup_env.sh
# Then edit .env with your actual API keys
```

**Option B: Manual setup**
```bash
cp .env.example .env
# Edit .env with your actual API keys:
# - NVIDIA_API_KEY (required)
# - GITHUB_TOKEN (required)
# - NVD_API_KEY (optional, but recommended)
```

**Option C: Use shell environment variables**
```bash
# Add to ~/.zshrc or ~/.bashrc:
export NVIDIA_API_KEY="your_actual_key"
export GITHUB_TOKEN="your_actual_token"
export NVD_API_KEY="your_actual_key"  # Optional
```

**⚠️ Security Note:** `.env` is git-ignored and should never be committed. Always use `.env.example` as a template and keep your actual API keys secure.

### 3. Setup RAG Vector Database (Optional but Recommended)

For RAG-powered CVE analysis with professional PR descriptions, PatchForge uses a **ChromaDB vector database**:

**Option A: Use Local JSON Files (Fastest - Recommended for Demos)**
```bash
# Place CVE JSON files in data/ directory:
# - data/cve-2024.json
# - data/cve-2023.json
python setup_rag.py
```

**Option B: Download from NVD API**
```bash
python setup_rag.py
# Will automatically download if local files not found
```

This will:
- Load CVEs from local JSON files (if available) or download from NVD API
- **Build a ChromaDB vector database** (`.chroma/` directory) with vector embeddings
- Index 38,000+ CVEs for fast semantic search
- Enable grounded, authoritative CVE explanations via vector similarity search

**Vector Database Benefits:**
- **Fast Semantic Search**: Vector embeddings enable fast, accurate CVE retrieval
- **No API Rate Limits**: Local vector database eliminates API dependency
- **Demo Ready**: Works offline, perfect for demonstrations
- **Scalable**: Can index millions of CVEs with fast query performance

**Note**: This step is optional. PatchForge will work without it, but PR descriptions will be simpler. **The vector database is recommended for demos** to showcase RAG functionality.

### 4. Run PatchForge

**Interactive Mode (Recommended):**
```bash
python main.py
```
This will:
- Ask for your GitHub username
- List your repositories
- Let you select a repository to scan
- Run the full pipeline with visual feedback

**Non-Interactive Mode:**
```bash
python main.py <repo_path> <github_repo_name>
```

**Example:**
```bash
python main.py ../pathforge-demo rayansikkandar/pathforge-demo
```

**With CVE Explanations:**
```bash
python main.py --explain
# Adds detailed CVE explanations to PR descriptions using Nemotron + RAG
```

**Demo Mode (Showcase ReAct Loop):**
```bash
python main.py --demo-react
# Creates intentional conflicts to showcase the ReAct retry loop
```

**Combined Flags:**
```bash
python main.py --explain --demo-react
# Interactive mode with explanations and ReAct loop demo
```

**See `QUICK_START.md` for a complete step-by-step guide.**

## Architecture

### Agents

- **ScannerAgent**: Scans repositories for CVEs using NVD database
- **ResearcherAgent**: Analyzes vulnerabilities and recommends fixes
- **PatchGeneratorAgent**: Generates actual code patches
- **ValidatorAgent**: Tests patches in isolated environments
- **PRCreatorAgent**: Creates GitHub pull requests

### Tools

- **NVDClient**: Interfaces with NIST NVD API
- **GitHubClient**: Manages GitHub operations (branches, commits, PRs)
- **Sandbox**: Isolated testing environment (future)

## Testing

### Run Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all unit tests
pytest tests/ -v

# Run integration tests
pytest tests/ -v -m integration

# Run dry-run pipeline test (no API keys needed)
python tests/test_pipeline_dry_run.py

# Run test suite
python tests/run_tests.py
```

### Test Coverage

The test suite includes:
- **Unit tests** for all agents and utilities
- **Integration tests** for the end-to-end pipeline
- **Validator flow tests** specifically exercising the new isolated venv validation
- **Mock utilities** for testing without API keys

See `tests/README.md` for detailed testing documentation.

## Demo

**Quick Demo:**
```bash
./run_demo.sh your-github-username/vulnerable-app
```

**Full Demo Guide:**
See `DEMO.md` for complete instructions on running the demo against the bundled vulnerable app.

The demo uses `demo/vulnerable_app` which contains vulnerable packages (Flask 2.0.1, requests 2.25.0, Jinja2 2.11.0) and exercises the full pipeline end-to-end.

## Requirements

- Python 3.8+
- NVIDIA API key (for Nemotron)
- GitHub token (for PR creation)
- NVD API key (optional, but recommended for rate limits)
- ChromaDB (for vector database - installed via `requirements.txt`)
- CVE JSON files (optional, for local vector database - recommended for demos)

## License

MIT

