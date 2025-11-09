# ReAct Loop Feature - PatchForge

## Overview

PatchForge now includes a **ReAct-style retry loop** that automatically refines patches when validation fails. This enables the system to learn from errors and generate improved patches on subsequent attempts.

## How It Works

### 1. Initial Patch Generation
- First attempt uses fast regex-based updates
- No AI overhead for simple dependency updates
- Most patches pass on the first try

### 2. Validation & Feedback
- Validator tests the patch in an isolated environment
- If validation fails, error details are captured
- Feedback includes:
  - Error messages
  - Dependency conflicts
  - Build failures
  - Compatibility issues

### 3. Retry with Refinement
- If validation fails, PatchGenerator uses Nemotron to refine the patch
- Nemotron analyzes the feedback and:
  - Updates the target package
  - Resolves dependency conflicts
  - Updates related dependencies for compatibility
  - Preserves file formatting

### 4. Iterative Improvement
- Up to 3 attempts total
- Each attempt learns from previous failures
- Only proceeds to PR creation if validation passes

## Configuration

### Max Retries
Set in `main.py`:
```python
MAX_RETRIES = 3  # Maximum number of retry attempts
```

### Retry Conditions
Retries are triggered when:
- Dependency installation fails
- Dependency conflicts are detected
- Build errors occur (except Python 3.13 compatibility issues)
- Import tests fail

## Example Flow

```
Attempt 1:
  → Generate patch (regex-based)
  → Validate
  → ❌ FAIL: Dependency conflict detected
  → Extract feedback: "Jinja2==2.11.3 conflicts with PyYAML 5.4.1"

Attempt 2:
  → Refine patch (Nemotron)
  → Analyzes: "Need to upgrade Jinja2 for compatibility"
  → Generate refined patch: Upgrades both PyYAML and Jinja2
  → Validate
  → ✅ PASS: All dependencies compatible

Result: PR created with refined patch
```

## Benefits

1. **Automatic Conflict Resolution**: Resolves dependency conflicts without human intervention
2. **Intelligent Refinement**: Uses AI to understand and fix complex issues
3. **Higher Success Rate**: More patches pass validation after refinement
4. **Transparent Process**: Clear logging of attempts and feedback

## Logging

The system logs:
- Attempt number
- Validation results
- Feedback extracted
- Refinement decisions
- Final success/failure status

## Demo Repository

The `patchforge-demo` repository includes:
- `test_app.py` - Test file for validation
- `pytest.ini` - Pytest configuration
- Dependency conflicts that trigger refinement

## Usage

The ReAct loop is **always enabled** and runs automatically when validation fails. No configuration needed!

```bash
python main.py
# The retry loop will automatically engage if validation fails
```

## Limitations

1. **Max 3 Attempts**: After 3 failures, manual intervention is required
2. **Nemotron Dependency**: Refinement requires Nemotron API access
3. **Python 3.13**: Build errors on Python 3.13 are handled specially (not retried)

## Future Enhancements

- Configurable max retries
- More sophisticated conflict resolution
- Support for multi-file patches
- Integration with test suites

---

**This feature makes PatchForge truly autonomous** - it can fix its own mistakes and learn from failures! 🚀

