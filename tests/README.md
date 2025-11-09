# Testing Guide for chqr

This directory contains the test suite for the chqr library following Test-Driven Development (TDD) principles.

## Test Structure

```
tests/
├── README.md                   # This file
├── test_data_structure.py      # Data structure building tests
├── test_validation.py          # Input validation tests
├── test_qr_generation.py       # QR code generation & SVG tests
└── test_qr_bill.py            # Legacy file (to be updated)
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_structure.py

# Run specific test class
pytest tests/test_validation.py::TestIBANValidation

# Run specific test
pytest tests/test_data_structure.py::TestQRDataStructure::test_minimal_qr_data_structure

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=chqr --cov-report=html

# Skip skipped tests (show only failures/passes)
pytest --tb=short
```

## Test Categories

### 1. Data Structure Tests (`test_data_structure.py`)

Tests the core QR code data string building:

- Minimal valid structure
- Optional fields handling
- Element separators
- Reserved fields (Ultimate Creditor)
- Data length limits

**Start here** when implementing - these are the foundation.

### 2. Validation Tests (`test_validation.py`)

Tests input validation and business rules:

- IBAN format and validation
- QR-IBAN identification
- Reference type validation (QRR, SCOR, NON)
- IBAN/Reference compatibility
- Amount format and ranges
- Currency validation
- Address field validation
- Character set restrictions

### 3. QR Generation Tests (`test_qr_generation.py`)

Tests QR code encoding and SVG output:

- QR code parameters (error correction, version)
- QR code decodability
- SVG format and dimensions
- Swiss cross overlay
- Modulo 10 check digit calculation
- Examples from specification

## TDD Workflow

1. **Pick a test** from one of the test files (start with `test_data_structure.py`)
2. **Remove `pytest.skip()`** from the test
3. **Uncomment the test code**
4. **Run the test** - it should fail (Red)
5. **Implement minimal code** to make it pass (Green)
6. **Refactor** if needed while keeping tests green
7. **Repeat** with the next test

Example:

```python
# Step 1-2: Enable the test
def test_minimal_qr_data_structure(self):
    """Test minimal valid QR-bill data structure."""
    from chqr import QRBill, Creditor

    creditor = Creditor(
        name="Test Company AG",
        postal_code="8000",
        city="Zurich",
        country="CH"
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF"
    )

    data = qr_bill.build_data_string()
    lines = data.split('\n')

    # Header
    assert lines[0] == "SPC"
    assert lines[1] == "0200"
    assert lines[2] == "1"

# Step 3: Run pytest - it will fail with ImportError
# Step 4: Create the classes to make it pass
# Step 5: Refactor once it's green
```

## Test Implementation Order

Recommended order for TDD:

### Phase 1: Core Data Structures

1. `test_data_structure.py::test_minimal_qr_data_structure`
2. `test_validation.py::test_valid_swiss_iban`
3. `test_validation.py::test_required_address_fields`

### Phase 2: Basic Validation

4. `test_validation.py::test_invalid_iban_format`
5. `test_validation.py::test_currency_validation`
6. `test_validation.py::test_qr_iban_identification`

### Phase 3: References

7. `test_validation.py::test_qr_iban_requires_qrr_reference`
8. `test_qr_generation.py::test_calculate_check_digit_example_1`
9. `test_validation.py::test_qr_reference_check_digit`

### Phase 4: QR Code Generation

10. `test_qr_generation.py::test_qr_code_error_correction_level`
11. `test_qr_generation.py::test_svg_is_valid_xml`
12. `test_qr_generation.py::test_svg_dimensions`

### Phase 5: Complete Examples

13. `test_qr_generation.py::test_example_1_from_spec`
14. `test_qr_generation.py::test_example_3_from_spec`

## Dependencies for Testing

Some tests require additional libraries:

```bash
# For QR code decoding tests (optional)
pip install pyzbar pillow

# For SVG to PNG conversion (optional)
pip install cairosvg

# For coverage reports
pip install pytest-cov
```

## Writing New Tests

Follow these guidelines:

1. **One concept per test** - Test one thing at a time
2. **Clear names** - Test name should describe what it tests
3. **AAA pattern** - Arrange, Act, Assert
4. **Good docstrings** - Explain what is being tested
5. **Use fixtures** - For repeated setup (add to `conftest.py`)

Example:

```python
def test_specific_feature(self):
    """Test that feature X works correctly with input Y."""
    # Arrange
    creditor = Creditor(name="Test", ...)
    qr_bill = QRBill(account="...", creditor=creditor)

    # Act
    result = qr_bill.some_method()

    # Assert
    assert result == expected_value
```

## Reference

- **Specification**: `docs/qr_bill_spec.md`
- **Guidelines**: `.clinerules/guidelines.md`
- **Original PDF**: `docs/ig-qr-bill-v2.3-en.pdf`

## Tips

- All tests are currently skipped - **this is intentional for TDD**
- Enable tests one at a time as you implement features
- Use `pytest -k "test_name"` to run tests matching a pattern
- Use `pytest --lf` to run only last failed tests
- Use `pytest -x` to stop on first failure

Happy testing! 🧪
