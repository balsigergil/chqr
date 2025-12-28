# Developer Guidelines

## Project Overview

**chqr** is a Python library for generating Swiss QR-bills in SVG format.

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
docs/              # Technical documentation
assets/            # QR-bill specifications and resources
```

### Key References

- **Technical Spec**: `assets/qr_bill_spec.md` - Complete Swiss QR-bill specification
- **PDF Source**: `assets/ig-qr-bill-v2.3-en.pdf` - Official implementation guidelines

## Output Formats

The library should support: SVG

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

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_qr_bill.py

# With coverage
uv run pytest --cov=chqr
```

## Code Quality

- Format with Ruff
- Use type hints for all public APIs
- Document all public classes and methods using Google-style docstrings
- Keep functions focused and testable
