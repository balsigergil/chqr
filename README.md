<div align="center">

<h1>chqr</h1>

**Swiss QR-bill generation library for Python**

[![PyPI version](https://img.shields.io/pypi/v/chqr.svg?style=for-the-badge)](https://pypi.org/project/chqr/)
[![License](https://img.shields.io/pypi/l/chqr.svg?style=for-the-badge)](https://github.com/balsigergil/chqr/blob/main/LICENSE)

</div>

<div align="center">
<img src="assets/qr_bill_example.png" alt="Example Swiss QR-bill generated with chqr"/>
</div>

## Overview

The Swiss QR-bill is the standardized payment slip used throughout Switzerland and Liechtenstein. It combines a machine-readable Swiss QR Code with human-readable payment information, making it easy for individuals and businesses to process payments efficiently.

**chqr** is a Python library that generates compliant Swiss QR-bills in SVG format. It handles all the complexity of the Swiss QR-bill specification v2.3, including data validation, QR code generation, and proper formatting. The library ensures your generated bills meet the official standards valid from November 21, 2025.

### Key Features

- **Full compliance** with Swiss QR-bill specification v2.3
- **Complete validation** of all input data (IBANs, references, amounts, addresses)
- **SVG generation** with multilingual support (English, German, French, Italian)
- **Support for all reference types**: QRR (QR Reference), SCOR (Creditor Reference), and NON (no reference)
- **Type-safe API** with comprehensive error messages
- **Zero configuration** - works out of the box with sensible defaults

## Installation

Install chqr from PyPI using pip:

```bash
pip install chqr
```

Or using uv for faster installation:

```bash
uv pip install chqr
```

## Quick Start

Here's a minimal example to generate your first Swiss QR-bill:

```python
from decimal import Decimal
from chqr import QRBill, Creditor

# Define the creditor (who receives the payment)
creditor = Creditor(
    name="Max Muster & Söhne",
    street="Musterstrasse",
    building_number="123",
    postal_code="8000",
    city="Seldwyla",
    country="CH",
)

# Create the QR-bill
bill = QRBill(
    account="CH4431999123000889012",  # QR-IBAN
    creditor=creditor,
    amount=Decimal("1949.75"),
    currency="CHF",
    reference_type="QRR",
    reference="210000000003139471430009017",
)

# Generate SVG
svg_content = bill.generate_svg(language="en")

# Save to file
with open("qr_bill.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

This generates a complete Swiss QR-bill as an SVG file, ready to be printed or included in invoices.

## Usage Examples

### Basic QR-bill with Debtor Information

Including debtor (payer) information pre-fills the payment slip for your customers:

```python
from decimal import Decimal
from chqr import QRBill, Creditor, UltimateDebtor

creditor = Creditor(
    name="Furniture AG",
    street="Industriestrasse",
    building_number="45",
    postal_code="3007",
    city="Bern",
    country="CH",
)

debtor = UltimateDebtor(
    name="Anna Müller",
    street="Hauptstrasse",
    building_number="12",
    postal_code="8001",
    city="Zürich",
    country="CH",
)

bill = QRBill(
    account="CH5800791123000889012",
    creditor=creditor,
    debtor=debtor,
    amount=Decimal("550.00"),
    currency="CHF",
    reference_type="SCOR",
    reference="RF18539007547034",
    additional_information="Invoice #2024-0156",
)

svg = bill.generate_svg(language="de")
```

### Different Reference Types

The library supports all three reference types defined in the Swiss QR-bill standard.

#### QRR: QR Reference

QR References are 27-digit numeric references that can only be used with QR-IBANs (IBANs with IID in range 30000-31999):

```python
bill = QRBill(
    account="CH4431999123000889012",  # QR-IBAN (IID: 31999)
    creditor=creditor,
    amount=Decimal("250.00"),
    currency="CHF",
    reference_type="QRR",
    reference="210000000003139471430009017",  # 27 digits with check digit
)
```

#### SCOR: Creditor Reference (ISO 11649)

Creditor References are alphanumeric references that must be used with regular IBANs:

```python
bill = QRBill(
    account="CH5800791123000889012",  # Regular IBAN
    creditor=creditor,
    amount=Decimal("180.50"),
    currency="CHF",
    reference_type="SCOR",
    reference="RF720191230100405JSH0438",  # ISO 11649 format
)
```

#### NON: No Reference

When no structured reference is needed, use the NON type with regular IBANs:

```python
bill = QRBill(
    account="CH5800791123000889012",  # Regular IBAN
    creditor=creditor,
    amount=Decimal("75.00"),
    currency="EUR",
    reference_type="NON",
    additional_information="Donation - Thank you!",
)
```

### Optional Features

#### Additional Information and Billing Data

You can include unstructured messages and structured billing information:

```python
bill = QRBill(
    account="CH5800791123000889012",
    creditor=creditor,
    amount=Decimal("1200.00"),
    currency="CHF",
    reference_type="SCOR",
    reference="RF18539007547034",
    additional_information="Order #2024-0891 from 15.10.2024",
    billing_information="//S1/10/10201409/11/201021/30/102673386",
)
```

#### Alternative Payment Procedures

Support for alternative payment methods like eBill:

```python
bill = QRBill(
    account="CH5800791123000889012",
    creditor=creditor,
    amount=Decimal("450.00"),
    currency="CHF",
    reference_type="SCOR",
    reference="RF18539007547034",
    alternative_procedures=["eBill/B/customer@example.com"],
)
```

#### Multilingual Support

Generate QR-bills in any of the four official Swiss languages:

```python
# German
svg_de = bill.generate_svg(language="de")

# French
svg_fr = bill.generate_svg(language="fr")

# Italian
svg_it = bill.generate_svg(language="it")

# English (default)
svg_en = bill.generate_svg(language="en")
```

## API Reference

### QRBill

The main class for creating Swiss QR-bills.

```python
QRBill(
    account: str,
    creditor: Creditor,
    currency: str,
    amount: Decimal | None = None,
    reference_type: str = "NON",
    reference: str | None = None,
    additional_information: str | None = None,
    debtor: UltimateDebtor | None = None,
    billing_information: str | None = None,
    alternative_procedures: list[str] | None = None,
)
```

**Parameters:**

- **account** (str): IBAN or QR-IBAN, exactly 21 characters. Must be from Switzerland (CH) or Liechtenstein (LI).
- **creditor** (Creditor): Creditor information (who receives the payment).
- **currency** (str): Payment currency, either `"CHF"` or `"EUR"`.
- **amount** (Decimal | None): Payment amount with exactly 2 decimal places. Range: 0.01 to 999,999,999.99. Can be `None` for open amounts.
- **reference_type** (str): Reference type - `"QRR"`, `"SCOR"`, or `"NON"`. Default: `"NON"`.
- **reference** (str | None): Payment reference. Required for QRR and SCOR types.
- **additional_information** (str | None): Unstructured message, max 140 characters.
- **debtor** (UltimateDebtor | None): Ultimate debtor (payer) information.
- **billing_information** (str | None): Structured billing information, max 140 characters.
- **alternative_procedures** (list[str] | None): Alternative payment methods, max 2 items of 100 characters each.

**Methods:**

- **generate_svg(language: str = "en") → str**: Generate SVG representation. Language can be `"en"`, `"de"`, `"fr"`, or `"it"`.
- **generate_qr_code() → segno.QRCode**: Generate the QR code object.
- **build_data_string() → str**: Build the raw QR code data string.

### Creditor

Represents the creditor (invoice issuer) information.

```python
Creditor(
    name: str,
    postal_code: str,
    city: str,
    country: str,
    street: str | None = None,
    building_number: str | None = None,
)
```

**Parameters:**

- **name** (str): Creditor name or company, max 70 characters.
- **postal_code** (str): Postal code, max 16 characters, without country prefix.
- **city** (str): City/town name, max 35 characters.
- **country** (str): Two-character ISO 3166-1 country code (e.g., `"CH"`).
- **street** (str | None): Street name or P.O. Box, max 70 characters.
- **building_number** (str | None): Building number, max 16 characters.

### UltimateDebtor

Represents the ultimate debtor (payer) information. Has identical parameters to `Creditor`.

```python
UltimateDebtor(
    name: str,
    postal_code: str,
    city: str,
    country: str,
    street: str | None = None,
    building_number: str | None = None,
)
```

### ValidationError

Exception raised when input data fails validation. All validation happens during `QRBill` initialization, providing immediate feedback with clear error messages.

```python
from chqr import ValidationError

try:
    bill = QRBill(...)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Reference Types Explained

Understanding when to use each reference type is crucial for generating valid QR-bills.

### QRR (QR Reference)

The QR Reference is a 27-digit numeric reference with a built-in check digit. It can **only** be used with QR-IBANs, which are special IBANs with an Institution Identifier (IID) in the range 30000-31999.

**When to use:** You have a QR-IBAN from your bank and need systematic payment reconciliation with a unique numeric reference.

**Format:** Exactly 27 numeric digits, where the last digit is a Modulo 10 recursive check digit.

**Example:** `210000000003139471430009017`

### SCOR (Creditor Reference)

The Creditor Reference follows the ISO 11649 standard and is an alphanumeric reference. It **must** be used with regular IBANs (not QR-IBANs).

**When to use:** You have a regular IBAN and want to use a structured reference for payment reconciliation.

**Format:** Starts with "RF" followed by 2 check digits and 1-21 alphanumeric characters.

**Example:** `RF720191230100405JSH0438`

### NON (No Reference)

No structured reference is used. This **must** be used with regular IBANs (not QR-IBANs).

**When to use:** No specific payment reference is needed, such as for donations or simple payments where additional information is sufficient.

**Format:** The reference field remains empty, but you can use `additional_information` for unstructured messages.

## Work in Progress

The following features are currently under development and will be available in future releases:

### Additional Output Formats

While SVG generation is fully supported, we're working on adding more output formats to make the library even more versatile:

- **PDF Generation**: Direct PDF output for seamless integration into invoicing systems and document workflows
- **PNG Export**: Raster image export for use in contexts where vector graphics aren't supported

These formats will follow the same API pattern as `generate_svg()`, making it easy to switch between output types based on your needs.

### Optional Bill Variants

- Bill without a specified amount, allowing payers to enter their own amount
- Bill without a specified debtor, suitable for donation scenarios

## Development

### Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone https://github.com/balsigergil/chqr.git
cd chqr

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

The project follows Test-Driven Development (TDD) practices with comprehensive test coverage:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=chqr

# Run specific test file
uv run pytest tests/test_qr_bill.py

# Verbose output
uv run pytest -v
```

### Code Quality

Code formatting and linting is handled by Ruff:

```bash
# Format code
uv run ruff format

# Check code
uv run ruff check

# Auto-fix issues
uv run ruff check --fix
```

Pre-commit hooks automatically run these checks before each commit.

## License

This project is licensed under the ISC License. See the [LICENSE](LICENSE) file for details.

## Links & Resources

- **PyPI Package:** [https://pypi.org/project/chqr/](https://pypi.org/project/chqr/)
- **Swiss QR-bill Specification:** [SIX Payment Standards](https://www.six-group.com/en/products-services/banking-services/payment-standardization.html)
- **Official Implementation Guidelines:** See `assets/ig-qr-bill-v2.3-en.pdf`

---

<div align="center">
Made with ❤️ by Gil Balsiger in Switzerland
</div>
