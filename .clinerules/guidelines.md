# Developer Guidelines

## Project Overview

**chqr** is a Python library for generating Swiss QR-bills in multiple formats (SVG, PDF, HTML).

## Development Practices

### Test Driven Development (TDD)

- Write tests **before** implementing features
- Use `pytest` for all tests
- Run tests: `uv run pytest`
- Aim for high test coverage

### Code Structure

```
src/chqr/          # Main package code
tests/             # Test files (mirror src/ structure)
docs/              # Documentation and specifications
```

### Key References

- **Technical Spec**: `docs/qr_bill_spec.md` - Complete Swiss QR-bill specification
- **PDF Source**: `docs/ig-qr-bill-v2.3-en.pdf` - Official implementation guidelines

## Output Formats

The library must support: SVG, PDF and HTML

## Validation Requirements

All generated QR-bills must comply with:

- Swiss QR Code standard (46×46 mm, error correction M)
- Data structure validation (see `qr_bill_spec.md` section 10)
- Reference type validation (QRR/SCOR/NON with appropriate IBAN type)
- Amount format (2 decimals, CHF/EUR only)
- Character set restrictions (UTF-8 Latin subset)

## Testing Guidelines

### Test Structure

```python
# tests/test_feature.py
import pytest
from chqr import QRBill

def test_feature_description():
    """Test that feature works as expected."""
    # Arrange
    qr_bill = QRBill(...)

    # Act
    result = qr_bill.generate()

    # Assert
    assert result.is_valid()
```

### Test Categories

- **Unit tests**: Individual components and validators
- **Integration tests**: Complete QR-bill generation
- **Validation tests**: Compliance with Swiss specification
- **Format tests**: SVG, PDF, HTML output validation

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_qr_bill.py

# With coverage
pytest --cov=chqr

# Verbose output
pytest -v
```

## Code Quality

- Format with Ruff
- Use type hints for all public APIs
- Document all public classes and methods using Google-style docstrings
- Keep functions focused and testable
