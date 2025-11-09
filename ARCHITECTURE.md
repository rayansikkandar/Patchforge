# PatchForge Architecture

## Overview

PatchForge uses a streamlined, multi-agent architecture powered by NVIDIA Nemotron and OSV (Open Source Vulnerabilities) API.

## Architecture Components

### 1. Scanner Agent (`agents/scanner.py`)

**Purpose**: Find and scan dependency files for vulnerabilities

**Process**:
1. Finds dependency files (requirements.txt, package.json, etc.)
2. Parses packages and versions from each file
3. Queries OSV API for each package+version combination
4. Returns list of vulnerable dependencies with CVEs

**Key Features**:
- Supports multiple ecosystems (PyPI, npm, Maven, etc.)
- Uses OSV API for fast, accurate version matching
- Filters to recent CVEs (2020+)
- Sorts by CVSS score

**OSV Advantages**:
- Faster than NVD
- Better for exact package+version matching
- Supports multiple package ecosystems
- More accurate vulnerability detection

### 2. Researcher Agent (`agents/researcher.py`)

**Purpose**: Find the latest secure version for a vulnerable package

**Process**:
1. Queries package registry (PyPI, npm, etc.)
2. Gets list of all available versions
3. Filters out pre-releases
4. Returns the latest stable version

**Key Features**:
- Direct registry queries (no AI needed)
- Fast and reliable
- Supports PyPI and npm
- Filters pre-releases automatically

### 3. Patch Generator Agent (`agents/patch_generator.py`)

**Purpose**: Generate patches by updating dependency versions

**Process**:
1. Reads the dependency file
2. Finds the vulnerable package line
3. Replaces old version with secure version
4. Returns updated file content

**Key Features**:
- Precise version replacement
- Preserves file formatting
- Supports requirements.txt and package.json
- Maintains comments and formatting

### 4. Validator Agent (`agents/validator.py`)

**Purpose**: Validate patches in isolated environment

**Process**:
1. Creates isolated virtual environment
2. Installs patched dependencies
3. Tests package import
4. Runs dependency conflict checks

**Key Features**:
- Isolated testing environment
- Real dependency installation
- Import testing
- Conflict detection

### 5. PR Creator Agent (`agents/pr_creator.py`)

**Purpose**: Create GitHub pull requests with patches

**Process**:
1. Creates GitHub branch
2. Commits patched file
3. Creates pull request
4. Includes CVE details and validation results

**Key Features**:
- Automated PR creation
- Detailed PR descriptions
- Validation results included
- CVE references and links

## Data Flow

```
Repository
    ↓
Scanner Agent
    ↓ (finds vulnerable packages)
Researcher Agent
    ↓ (finds secure version)
Patch Generator Agent
    ↓ (creates patch)
Validator Agent
    ↓ (validates patch)
PR Creator Agent
    ↓ (creates PR)
GitHub PR
```

## Key Technologies

### OSV API
- **URL**: https://api.osv.dev/v1
- **Purpose**: Vulnerability database optimized for package+version matching
- **Advantages**: Fast, accurate, multi-ecosystem support

### Package Registries
- **PyPI**: https://pypi.org/pypi/{package}/json
- **npm**: https://registry.npmjs.org/{package}
- **Purpose**: Get latest package versions

### NVIDIA Nemotron
- **Model**: meta/llama-3.1-70b-instruct
- **Purpose**: AI-powered analysis (currently minimal usage)
- **Future**: Could be used for complex fix strategies

## Ecosystem Support

Currently Supported:
- **PyPI** (Python): requirements.txt
- **npm** (JavaScript): package.json

Planned:
- **Maven** (Java): pom.xml
- **RubyGems** (Ruby): Gemfile
- **Go**: go.mod
- **Rust**: Cargo.toml

## Configuration

### Key Settings (`config.py`)

- `MIN_CVSS_SCORE`: Minimum CVSS score to patch (default: 7.0)
- `MIN_CVE_YEAR`: Minimum CVE year to process (default: 2015)
- `NEMOTRON_MODEL`: AI model to use (default: meta/llama-3.1-70b-instruct)

## Advantages of New Architecture

1. **Faster**: OSV API is faster than NVD for package queries
2. **More Accurate**: Exact package+version matching
3. **Simpler**: Direct registry queries instead of AI for version finding
4. **More Reliable**: Less dependency on AI for critical decisions
5. **Multi-Ecosystem**: Supports multiple package managers
6. **Better Validation**: Real dependency installation testing

## Future Enhancements

1. **Multi-CVE Processing**: Process multiple CVEs in one run
2. **Dependency Conflict Resolution**: Automatically resolve conflicts
3. **Test Suite Integration**: Run project tests after patching
4. **CI/CD Integration**: Automated runs on schedule
5. **More Ecosystems**: Support for Maven, Gemfile, go.mod, etc.
6. **AI-Powered Fixes**: Use Nemotron for complex code changes

