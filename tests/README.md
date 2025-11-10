# Testing Strategy for chqr

## QR Code Generation Testing

### Approach

The QR code generation is tested by comparing the **data string** that will be sent to the `qrcode` library with pre-generated fixtures. This approach has several advantages:

1. **Deterministic**: Same inputs always produce the same output
2. **Fast**: No need to render actual QR codes or decode images
3. **Focused**: Tests the business logic separately from the rendering library
4. **Library-agnostic**: Can swap QR libraries without changing tests

### Test Structure

```
tests/
├── test_qr_generation.py      # QR generation tests
└── fixtures/
    └── qr_data/                # Expected data string fixtures
        ├── example_1_qrr_with_amount.txt
        ├── example_3_scor_reference.txt
        └── example_4_donation.txt
```

### What Gets Tested

#### 1. Data String Generation (`TestQRDataString`)

Tests that `QRBill.build_data_string()` produces the exact data structure expected by the Swiss QR-bill specification:

- **Example 1**: QR Reference with amount and debtor
- **Example 3**: SCOR Reference (ISO 11649)
- **Example 4**: Donation (no amount, no debtor)

Each test:

1. Creates a `QRBill` object with specific parameters
2. Calls `build_data_string()` to generate the data
3. Compares with the expected fixture file

#### 2. QR Code Parameters (`TestQRCodeParameters`)

Tests for when actual QR code generation is implemented:

- Error correction level M (required by spec)
- Version auto-selection (max 25)
- UTF-8 encoding compatibility

#### 3. Edge Cases (`TestEdgeCases`)

Tests boundary conditions and special scenarios:

- Minimum amount (0.01 CHF)
- Maximum amount (999,999,999.99)
- Special characters (umlauts, ampersands)
- Empty fields (building numbers)
- P.O. Box addresses

### Running Tests

```bash
# Run all QR generation tests
uv run pytest tests/test_qr_generation.py -v

# Run specific test class
uv run pytest tests/test_qr_generation.py::TestQRDataString -v

# Run with verbose output
uv run pytest tests/test_qr_generation.py -vv
```

### Fixture Files

Fixture files contain the exact string that `build_data_string()` should produce. They are:

- Plain text files with newline-separated elements
- Generated directly from `QRBill.build_data_string()` output
- Match the Swiss QR-bill specification examples

To regenerate fixtures after code changes:

```python
from decimal import Decimal
from chqr import QRBill
from chqr.creditor import Creditor
from chqr.debtor import UltimateDebtor

# Create QRBill instance
qr_bill = QRBill(...)

# Generate and save fixture
result = qr_bill.build_data_string()
with open('tests/fixtures/qr_data/fixture_name.txt', 'w') as f:
    f.write(result)
```

### Future Testing

When QR code generation is implemented, additional tests will verify:

1. **QR Code Properties**:

   - Error correction level M
   - UTF-8 encoding
   - Version ≤ 25
   - 46×46 mm fixed size

2. **SVG Output**:

   - Valid XML structure
   - Correct dimensions
   - Swiss cross overlay (7×7 mm)
   - Proper viewBox attribute

3. **Decoding** (optional):
   - Generated QR codes can be decoded back to original data
   - Requires additional dependencies (pyzbar or similar)

## Test-Driven Development Workflow

1. Write test with expected behavior
2. Run test (it should fail)
3. Implement feature
4. Run test (it should pass)
5. Refactor if needed
6. Repeat

This ensures:

- All features have tests
- Tests guide implementation
- High code coverage
- Confidence in changes
