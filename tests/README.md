# AI Assistant Test Suite

This directory contains unit tests for the AI Assistant functionality.

## Running Tests

### Using pytest directly:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_cli/test_args.py -v
```

### Using the test runner script:
```bash
python run_tests.py
```
## Dependencies

Tests require:
- `pytest>=7.0.0` (already in requirements.txt)
- `pytest-asyncio` for async test support
- Standard library `unittest.mock` for mocking

## Configuration

The test suite includes:
- `pytest.ini` - Pytest configuration with default options
- `conftest.py` - Test fixtures and Python path configuration
- Automatic project root detection for proper module imports