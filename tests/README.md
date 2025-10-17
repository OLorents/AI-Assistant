# AI Assistant Test Suite

This directory contains comprehensive unit tests for the AI Assistant functionality.

## Test Structure

### CLI Tests (`test_cli/`)
- **test_args.py** (21 tests) - Argument parsing and validation
- **test_application.py** (11 tests) - CLI application logic and workflow
- **test_integration.py** (11 tests) - End-to-end CLI integration tests
- **test_main.py** (4 tests) - Main entry point functionality

### Intent System Tests (`test_intents/`)
- **test_time_intent.py** (5 tests) - Time intent handler
- **test_date_intent.py** (5 tests) - Date intent handler
- **test_public_ip_intent.py** (5 tests) - Public IP intent handler
- **test_list_files_intent.py** (6 tests) - List files intent handler
- **test_weather_intent.py** (7 tests) - Weather intent handler
- **test_intent_chain.py** (6 tests) - Intent chain processing
- **test_intent_integration.py** (7 tests) - Intent system integration

### Command Service Tests (`test_commands/`)
- **test_confirmation.py** (9 tests) - User confirmation system
- **test_runner.py** (5 tests) - Command execution runner
- **test_service.py** (5 tests) - Command service integration

### Utility Tests (`test_utils/`)
- **test_os_utils.py** (10 tests) - Operating system utilities

**Total: 119 tests** covering all major functionality.

## Running Tests

### Using pytest directly:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/test_intents/ -v
python -m pytest tests/test_commands/ -v
python -m pytest tests/test_cli/ -v

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
