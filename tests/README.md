# Real Estate Analyzer Tests

This directory contains the test suite for the Real Estate Analyzer application.

## Test Structure

```
tests/
├── __init__.py                    # Makes tests a Python package
├── conftest.py                   # Pytest configuration and fixtures
├── test_real_estate_analyzer.py  # Main application tests
├── test_real_estate_scraper.py   # Scraper component tests
├── test_integration.py           # Integration tests
├── requirements-test.txt         # Test dependencies
└── README.md                     # This file
```

## Running Tests

### Quick Start

```bash
# Install test dependencies and run all tests
python run_tests.py

# Run tests with verbose output
python run_tests.py -v

# Run only fast tests (skip slow integration tests)
python run_tests.py -m "not slow"
```

### Using pytest directly

```bash
# Install test dependencies first
pip install -r tests/requirements-test.txt

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_real_estate_analyzer.py

# Run tests with coverage
pytest tests/ --cov=real_estate_analyzer

# Run only unit tests (exclude integration tests)
pytest tests/ -m "not integration"

# Run only integration tests
pytest tests/ -m integration
```

## Test Categories

### Unit Tests

- **Fast**: Test individual functions and components
- **Isolated**: Mock external dependencies
- **Reliable**: Should pass consistently

### Integration Tests

- **Slower**: Test full application workflows
- **Real dependencies**: May use actual network/file system
- **Marked with**: `@pytest.mark.integration`

### Slow Tests

- **Long running**: May take 10+ seconds
- **Resource intensive**: Start actual server processes
- **Marked with**: `@pytest.mark.slow`

## Test Fixtures

### Available Fixtures (defined in `conftest.py`):

- `sample_property_data`: Sample DataFrame with property listings
- `empty_dataframe`: Empty DataFrame for edge case testing
- `mock_dash_app`: Mock Dash application for testing

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only unit tests
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m "integration"

# Combine markers
pytest -m "integration and not slow"
```

## Continuous Integration

Tests are automatically run on:

- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

See `.github/workflows/test.yml` for CI configuration.

## Adding New Tests

### Guidelines:

1. **File naming**: Test files must start with `test_`
2. **Class naming**: Test classes must start with `Test`
3. **Function naming**: Test functions must start with `test_`
4. **Markers**: Add appropriate markers for slow/integration tests
5. **Documentation**: Include docstrings explaining what each test validates

### Example:

```python
@pytest.mark.integration
def test_server_startup(self):
    """Test that the application server starts successfully."""
    # Test implementation here
    pass
```

## Coverage

Run tests with coverage reporting:

```bash
pytest tests/ --cov=real_estate_analyzer --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

## Troubleshooting

### Common Issues:

1. **Import errors**: Ensure you're running from project root
2. **Port conflicts**: Integration tests use port 8055
3. **Missing dependencies**: Run `pip install -r tests/requirements-test.txt`
4. **Slow tests timing out**: Increase timeout values or skip with `-m "not slow"`
