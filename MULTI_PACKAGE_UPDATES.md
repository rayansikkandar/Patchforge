# Multi-Package Update Feature

## Overview

PatchForge now supports **intelligent multi-package updates** that coordinate related dependency upgrades to resolve conflicts. This is a key feature of the ReAct loop that demonstrates true agentic reasoning.

## How It Works

### 1. Initial Single-Package Update
- First attempt updates only the vulnerable package
- Fast and efficient for simple cases
- Most patches pass on first try

### 2. Conflict Detection
- Validator detects dependency conflicts
- Extracts conflicting package names
- Provides suggestions for resolution

### 3. Multi-Package Refinement
- Nemotron analyzes the conflict
- Identifies related packages that need updates
- Coordinates upgrades across multiple packages
- Preserves file formatting and comments

### 4. Coordinated Updates
- Updates all necessary packages together
- Ensures compatibility across the dependency tree
- Validates the complete solution

## Example: Flask Ecosystem

### Scenario
- **Flask**: 2.0.1 → 2.3.3 (security fix)
- **Werkzeug**: 2.0.0 (too old for Flask 2.3.3)
- **MarkupSafe**: 2.0.0 (too old for Flask 2.3.3)

### Attempt 1: Single Package
```
Flask==2.0.1 → Flask==2.3.3
❌ FAIL: Werkzeug 2.0.0 incompatible with Flask 2.3.3
```

### Attempt 2: Multi-Package (Nemotron Refinement)
```
Flask==2.0.1 → Flask==2.3.3
Werkzeug==2.0.0 → Werkzeug==2.3.0  (auto-updated)
MarkupSafe==2.0.0 → MarkupSafe==2.1.3  (auto-updated)
✅ PASS: All packages compatible
```

## Implementation

### Nemotron-Powered Refinement
- Analyzes validation errors
- Uses precise compatibility rules:
  - Flask 2.3.x → Werkzeug 2.3.3
  - Flask 2.2.x → Werkzeug 2.2.3
  - Werkzeug upgrade → MarkupSafe >= 2.1.1
  - Cryptography → requests/urllib3 compatibility
- Coordinates multi-package updates
- Preserves file structure

### Fallback Mechanism
- Manual coordination if Nemotron fails
- Uses precise version matching:
  - Flask 2.3.x → Werkzeug 2.3.3
  - Flask 2.2.x → Werkzeug 2.2.3
- Knows common dependency patterns
- Flask → Werkzeug + MarkupSafe
- Ensures reliability

### Change Tracking
- Tracks which packages were updated
- Logs coordination decisions
- Documents in PR descriptions
- Shows reasoning process

## Benefits

1. **Intelligent Coordination**: Understands dependency relationships
2. **Automatic Resolution**: Fixes conflicts without human intervention
3. **Reliable Fallbacks**: Works even if Nemotron is unavailable
4. **Transparent Process**: Shows what was updated and why
5. **Production Ready**: Handles real-world dependency conflicts

## Demo Scenario

The `--demo-react` mode creates a scenario that triggers multi-package updates:

```bash
python main.py --demo-react
```

### Expected Flow
1. **Attempt 1**: Upgrade Flask → FAIL (Werkzeug conflict)
2. **ReAct Loop**: Nemotron analyzes conflict
3. **Attempt 2**: Upgrade Flask + Werkzeug + MarkupSafe → PASS ✅
4. **PR Created**: Documents all coordinated updates

## PR Description

Multi-package updates are documented in PR descriptions:

```markdown
### 🔄 ReAct Loop Refinement

This patch was refined through **2 attempts** using PatchForge's ReAct-style retry loop:

1. **Attempt 1**: Initial patch generated (single package update)
2. **Validation**: Failed with dependency conflicts
3. **Refinement**: Nemotron analyzed errors and coordinated multi-package updates
4. **Attempt 2**: Refined patch with coordinated updates passed all validation checks

### 📦 Multi-Package Updates

To resolve dependency conflicts, the following packages were automatically updated:

- `Werkzeug==2.3.0`
- `MarkupSafe==2.1.3`

*These packages were automatically upgraded to resolve dependency conflicts.*
```

## Supported Patterns

### Flask Ecosystem
- Flask upgrade → Werkzeug + MarkupSafe upgrades
- **Precise Rules**:
  - Flask 2.3.x → Werkzeug 2.3.3 (exact version)
  - Flask 2.2.x → Werkzeug 2.2.3 (exact version)
  - Werkzeug upgrade → MarkupSafe >= 2.1.1

### Future Patterns
- Django ecosystem coordination
- React/Node.js dependency chains
- Python scientific stack (NumPy, SciPy, Pandas)
- Extensible through Nemotron analysis

## Configuration

No configuration needed! Multi-package updates are:
- **Automatic**: Engages when conflicts are detected
- **Intelligent**: Uses Nemotron for analysis
- **Reliable**: Falls back to manual coordination
- **Transparent**: Documents all changes

## Limitations

1. **Max 3 Attempts**: After 3 failures, manual intervention required
2. **Nemotron Dependency**: Best results with Nemotron API access
3. **Python Focus**: Currently optimized for Python/PyPI ecosystem
4. **Complex Conflicts**: Very complex dependency trees may need manual review

## Future Enhancements

- Support for more ecosystems (npm, Maven, etc.)
- Machine learning for common patterns
- Integration with dependency resolvers
- Support for version ranges and constraints
- Multi-file updates (package.json + package-lock.json)

---

**This feature makes PatchForge truly intelligent** - it can coordinate complex dependency updates just like a human developer would! 🚀

