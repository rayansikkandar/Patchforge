# RAG Setup Guide

## Quick Setup for Demo

### Step 1: Get CVE JSON Files

Download CVE data from NVD in JSON format and place in `data/` directory:

```
data/
  ├── cve-2024.json
  └── cve-2023.json
```

**Where to get the files:**
- NVD Data Feeds: https://nvd.nist.gov/feeds/json/cve/1.1/
- Or use the NVD API to download (see `tools/rag_nvd.py`)

### Step 2: Build Vector Database

```bash
python setup_rag.py
```

This will:
1. Load CVEs from `data/*.json` files (fast!)
2. Build ChromaDB vector database in `.chroma/`
3. Test with a sample query

### Step 3: Verify

```bash
python tools/rag_nvd.py
```

Expected output:
```
✅ Loaded 18000 CVEs from cve-2024.json
✅ Indexed 18000 CVEs total into ChromaDB
🧪 Testing RAG query...
{'ids': [['CVE-2023-30861', ...]], 'documents': [['Flask ...']]}
```

## Alternative: Download from API

If you don't have local JSON files, the script will automatically download from NVD API:

```bash
python setup_rag.py
```

This is slower (10-30 minutes) but doesn't require local files.

## Usage in PatchForge

Once the database is built, PatchForge will automatically use RAG for:
- CVE explanations (with `--explain` flag)
- Professional PR descriptions
- Grounded, authoritative security analysis

## Troubleshooting

### "chromadb not installed"
```bash
pip install chromadb
```

### "No local files found"
- Create `data/` directory
- Add CVE JSON files (cve-2024.json, etc.)
- Or let the script download from API

### "Database not found"
Run `python setup_rag.py` to build the database.

## For Judges Demo

**Recommended:** Use local JSON files for fastest, most reliable demo:
1. Pre-download CVE data
2. Place in `data/` directory
3. Run `python setup_rag.py`
4. Demo works instantly with no API calls!

---

**This setup ensures your RAG system works flawlessly for the demo!** 🚀

