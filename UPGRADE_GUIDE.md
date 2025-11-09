# PatchForge Architecture Upgrade Guide

## What Changed

PatchForge has been upgraded to use OSV (Open Source Vulnerabilities) API and a simplified architecture.

## Key Improvements

### 1. OSV API Integration

**Before (v1.0):**
- Used NVD API for CVE lookup
- Keyword-based searching
- Less accurate for package+version matching

**After (v2.0):**
- Uses OSV API for exact package+version matching
- Faster and more accurate
- Better support for multiple ecosystems

### 2. Simplified Researcher

**Before (v1.0):**
- Used Nemotron AI to analyze and recommend versions
- Complex prompts and parsing
- Slower and less reliable

**After (v2.0):**
- Direct queries to package registries (PyPI, npm)
- No AI needed for version finding
- Faster and more reliable

### 3. Enhanced Scanner

**Before (v1.0):**
- Only supported requirements.txt
- Limited package parsing
- NVD keyword search

**After (v2.0):**
- Supports multiple file types (requirements.txt, package.json, etc.)
- Better package parsing
- OSV exact version matching

### 4. Improved Patch Generator

**Before (v1.0):**
- Used AI to generate patches
- Complex conflict resolution
- Sometimes unreliable

**After (v2.0):**
- Direct version replacement
- Precise file updates
- More reliable

## Migration

### No Breaking Changes for Users

The API remains the same:
```python
python main.py <repo_path> <github_repo_name>
```

### Internal Changes

1. **Scanner Output**: Now includes `ecosystem` and `full_file_path` fields
2. **Researcher Output**: Returns `secure_version` directly (not in `analysis`)
3. **Patch Data**: Includes `ecosystem` field

### Configuration

No configuration changes needed. Existing `.env` file works as-is.

## Benefits

1. **Faster**: OSV API is faster than NVD
2. **More Accurate**: Exact package+version matching
3. **More Reliable**: Less dependency on AI
4. **Better Support**: Multiple ecosystems (PyPI, npm, etc.)
5. **Simpler**: Cleaner code architecture

## Testing

Run the demo to verify everything works:

```bash
python main.py ../pathforge-demo rayansikkandar/pathforge-demo
```

## Rollback

If you need to rollback to v1.0:
1. Checkout the previous git commit
2. Or manually revert the changes to agents/

## Support

See `ARCHITECTURE.md` for detailed architecture documentation.

