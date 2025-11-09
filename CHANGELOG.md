# Changelog

All notable changes to PatchForge will be documented in this file.

## [Unreleased]

### Added
- **ReAct-style retry loop**: Automatic patch refinement when validation fails
  - Up to 3 retry attempts
  - Nemotron-powered patch refinement based on validation feedback
  - Automatic dependency conflict resolution
  - Detailed logging of retry attempts and feedback
- **Enhanced PR descriptions**: PRs now include ReAct loop information when multiple attempts were made
- **Improved error handling**: Better detection of dependency conflicts vs build errors
- **Python 3.13 compatibility**: Special handling for Python 3.13 build errors
- **--explain flag**: Generate detailed CVE fix explanations using Nemotron

### Changed
- **PatchGenerator**: Now accepts `feedback` parameter for iterative refinement
- **Validator**: Returns structured feedback including conflicting packages
- **Main pipeline**: Integrated retry loop between patch generation and validation
- **PR Creator**: Includes retry attempt information in PR descriptions

### Fixed
- **CVSS score extraction**: Fixed type errors when sorting vulnerabilities
- **OSV integration**: Better handling of CVSS vector strings and severity mappings
- **Version selection**: Prefer same major version to avoid breaking changes
- **npm validation**: Increased timeout and better error handling for large packages

## [Previous Versions]

See git history for previous changes.
