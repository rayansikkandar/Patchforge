# PatchForge Test Suite

Comprehensive test suite for PatchForge, including unit tests, integration tests, and end-to-end pipeline validation.

## Running Tests

### Quick Start

```bash
# Run all unit tests (excludes integration tests)
pytest tests/ -v

# Run all tests including integration
pytest tests/ -v -m "not slow"

# Run only integration tests
pytest tests/ -v -m integration

# Run specific test file
pytest tests/test_validator.py -v

# Run with coverage
pytest tests/ --cov=agents --cov=tools --cov=utils --cov-report=html
```

### Using the Test Runner

```bash
python tests/run_tests.py
```

## Test Structure

### Unit Tests

- **test_validator.py**: Tests for `ValidatorAgent` with focus on the new isolated venv validation flow
- **test_patch_generator.py**: Tests for `PatchGeneratorAgent` including version selection and line updating
- **test_parsers.py**: Tests for utility parsers (`parse_requirements`, `parse_package_json`)

### Integration Tests

- **test_integration.py**: End-to-end pipeline tests with mocked external services
- Validator integration tests that use real pip installations

## Test Fixtures

Located in `conftest.py`:

- `mock_nemotron_response`: Mock Nemotron API responses
- `sample_cve_data`: Sample CVE data for testing
- `sample_research_data`: Sample research data
- `sample_patch_data`: Sample patch data
- `temp_repo`: Temporary repository with requirements.txt
- `mock_nvd_client`: Mock NVD client
- `mock_github_client`: Mock GitHub client
- `mock_openai_client`: Mock OpenAI client for Nemotron

## Focus: Validator Flow Testing

The validator tests specifically exercise the new isolated venv validation flow:

1. **Isolated Environment**: Tests verify that validation creates and uses an isolated virtual environment
2. **Dependency Installation**: Tests verify pip install in the isolated venv
3. **Dependency Checking**: Tests verify `pip check` runs after installation
4. **Error Handling**: Tests verify graceful handling of timeouts, failures, and errors
5. **Integration**: Real integration tests that actually install dependencies

## Running Without API Keys

All tests use mocks by default, so you can run the test suite without configuring API keys:

```bash
pytest tests/ -v -m "not integration"
```

Integration tests may require network access for real pip installations, but don't require API keys.

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v --tb=short
```

## Coverage Goals

- Unit test coverage: >80%
- Integration test coverage: All critical paths
- Validator flow: 100% coverage of new isolated venv logic

