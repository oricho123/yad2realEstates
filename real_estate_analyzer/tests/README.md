# Real Estate Analyzer - Test Suite

This directory contains all tests for the Real Estate Analyzer project, organized by test type and scope.

## 📁 Test Directory Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_structured_hover_data.py       # Hover data structure tests
│   ├── test_price_formatting.py            # Price formatting utilities
│   ├── test_number_formatting.py           # Number formatting utilities
│   ├── test_api_parameter_fix.py           # API parameter handling
│   └── test_property_models.py             # Property data models
├── integration/                    # Integration tests for component interaction
│   ├── test_all_structured_hover_data.py   # Comprehensive hover data integration
│   ├── test_refactored_modules.py          # Cross-module integration
│   ├── test_visualization_components.py    # Visualization component integration
│   └── test_click_functionality.py         # Click interaction testing
├── refactoring/                    # Tests for refactoring validation
│   ├── test_phase_3_complete.py            # Phase 3 completion validation
│   ├── test_phase_4_complete.py            # Phase 4 completion validation
│   ├── test_fixes.py                       # General bug fixes validation
│   └── test_ui_fixes.py                    # UI improvement validation
└── fixtures/                       # Test data and fixtures
    └── (empty - add sample data here)
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

- **Individual component testing**
- **Pure function testing**
- **Data model validation**
- **Utility function testing**

### Integration Tests (`tests/integration/`)

- **Multi-component interaction**
- **End-to-end workflow testing**
- **Dashboard functionality**
- **Data pipeline testing**

### Refactoring Tests (`tests/refactoring/`)

- **Legacy vs new implementation validation**
- **Refactoring phase completion**
- **Backward compatibility**
- **Performance regression testing**

## 🚀 Running Tests

### Run All Tests

```bash
# From project root
python -m pytest tests/ -v
```

### Run by Category

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# Refactoring validation tests
python -m pytest tests/refactoring/ -v
```

### Run Specific Test Files

```bash
# Test hover data structures
python -m pytest tests/unit/test_structured_hover_data.py -v

# Test complete integration
python -m pytest tests/integration/test_all_structured_hover_data.py -v
```

### Run Individual Tests

```bash
# From the tests directory, individual Python files can be run directly
cd tests/unit
python test_structured_hover_data.py

cd ../integration
python test_refactored_modules.py
```

## 📊 Test Coverage

### Current Test Coverage:

- ✅ **Hover Data Structures**: Complete unit and integration tests
- ✅ **Visualization Components**: Full integration testing
- ✅ **Data Models**: Property models and validation
- ✅ **Formatting Utilities**: Price and number formatting
- ✅ **API Integration**: Parameter handling and validation
- ✅ **Refactoring Validation**: Phase completion and compatibility

### Areas for Expansion:

- [ ] **Scraping Module Tests**: API client and parser tests
- [ ] **Analysis Module Tests**: Market and value analysis tests
- [ ] **Dashboard Callback Tests**: Comprehensive callback testing
- [ ] **Error Handling Tests**: Exception and edge case testing
- [ ] **Performance Tests**: Load and stress testing

## 🔧 Test Configuration

### Required Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

### Environment Setup

```bash
# Ensure the src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Running with Coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

## 📝 Writing New Tests

### Test File Naming Convention

- **Unit tests**: `test_[module_name].py`
- **Integration tests**: `test_[feature_name]_integration.py`
- **Refactoring tests**: `test_[phase_name]_complete.py`

### Test Function Naming

- **Unit tests**: `test_[function_name]_[scenario]()`
- **Integration tests**: `test_[workflow_name]_integration()`
- **Validation tests**: `test_[feature_name]_validation()`

### Example Test Structure

```python
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from your_module import YourClass

def test_your_function():
    """Test description."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = your_function(input_data)

    # Assert
    assert result is not None
    assert len(result) > 0
```

## 🎯 Quality Standards

### Test Requirements

- **All tests must pass** before merging code
- **New features require corresponding tests**
- **Integration tests for component interactions**
- **Edge cases and error conditions must be tested**

### Continuous Integration

- Tests run automatically on code changes
- Coverage reports generated for each commit
- Performance regression detection
- Cross-platform compatibility validation

---

**Last Updated**: 2024
**Test Count**: 12 test files organized
**Coverage Target**: >90%
