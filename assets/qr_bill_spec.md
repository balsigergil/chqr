# Swiss QR-bill Technical Specification

**Version:** 2.3
**Valid from:** November 21, 2025
**Document Type:** Developer Technical Reference

## 1. Overview

The Swiss QR-bill is the standard for written invoicing in Switzerland and Liechtenstein. It contains payment data both in digital form (Swiss QR Code) and human-readable text.

### Key Components

- **Payment Part**: 148 x 105 mm (DIN-A6 landscape)
- **Receipt**: 62 x 105 mm
- **Total Size**: 210 x 105 mm (DIN long)
- **Swiss QR Code**: 46 x 46 mm with Swiss cross recognition symbol

## 2. QR Code Technical Specifications

### 2.1 Generation Parameters

| Parameter              | Value          | Description                         |
| ---------------------- | -------------- | ----------------------------------- |
| Standard               | ISO 18004      | QR Code specification               |
| Error Correction Level | M              | ~15% redundancy                     |
| Character Encoding     | UTF-8          | Restricted to Latin character set   |
| Maximum Version        | 25             | 117 x 117 modules                   |
| Fixed Print Size       | 46 x 46 mm     | Regardless of version               |
| Module Size (min)      | 0.4 mm         | Minimum for reliable scanning       |
| Quiet Space            | ≥ 1.6 mm       | 4 modules width (5 mm recommended)  |
| Recognition Symbol     | 7 x 7 mm       | Swiss cross overlay (black & white) |
| Maximum Data           | 997 characters | Including separators                |

### 2.2 Character Set

Permitted UTF-8 characters:

- **Basic Latin**: U+0020–U+007E
- **Latin-1 Supplement**: U+00A0–U+00FF
- **Latin Extended A**: U+0100–U+017F
- **Additional Characters**:
  - Ș (U+0218), ș (U+0219)
  - Ț (U+021A), ț (U+021B)
  - € (U+20AC)

### 2.3 Data Separators

- **Element Separator**: Carriage return (CR+LF or LF alone)
- All data elements must be present
- Empty elements require separator (except trailing optional elements)
- No carriage return after final element

## 3. Complete Data Structure

### 3.1 Status Codes

| Code | Name        | Description                                   |
| ---- | ----------- | --------------------------------------------- |
| M    | Mandatory   | Must be filled                                |
| D    | Dependent   | Required if parent group is used              |
| O    | Optional    | Can be empty but must be present              |
| X    | Do not fill | Must not be filled (reserved for future use)  |
| A    | Additional  | Omitted if not used and no subsequent element |

### 3.2 Data Elements Table

```
QRCH
  +Header (Mandatory group)
    ++QRType (M): "SPC" (fixed) - 3 alphanumeric
    ++Version (M): "0200" (fixed for v2.0) - 4 numeric
    ++Coding (M): "1" (UTF-8) - 1 numeric

  +CdtrInf (Creditor Information - Mandatory group)
    ++IBAN (M): 21 alphanumeric, CH/LI only
    ++Cdtr (Creditor - Mandatory group)
      +++AdrTp (M): "S" (structured) - 1 alphanumeric
      +++Name (M): Max 70 characters
      +++StrtNmOrAdrLine1 (O): Street - Max 70 characters
      +++BldgNbOrAdrLine2 (O): Building number - Max 16 characters
      +++PstCd (D): Postal code - Max 16 characters (no country prefix)
      +++TwnNm (D): Town - Max 35 characters
      +++Ctry (M): 2-character ISO 3166-1 country code

  +UltmtCdtr (Ultimate Creditor - Do not use)
    ++AdrTp (X): Reserved for future use
    ++Name (X): Reserved for future use
    ++StrtNmOrAdrLine1 (X): Reserved for future use
    ++BldgNbOrAdrLine2 (X): Reserved for future use
    ++PstCd (X): Reserved for future use
    ++TwnNm (X): Reserved for future use
    ++Ctry (X): Reserved for future use

  +CcyAmt (Payment Amount - Mandatory group)
    ++Amt (O): Decimal, max 12 digits, "." separator, 2 decimals
               Range: 0.01 to 999,999,999.99
    ++Ccy (M): "CHF" or "EUR" - 3 alphanumeric

  +UltmtDbtr (Ultimate Debtor - Optional group)
    ++AdrTp (D): "S" (structured) - 1 alphanumeric
    ++Name (D): Max 70 characters
    ++StrtNmOrAdrLine1 (O): Street - Max 70 characters
    ++BldgNbOrAdrLine2 (O): Building number - Max 16 characters
    ++PstCd (D): Postal code - Max 16 characters (no country prefix)
    ++TwnNm (D): Town - Max 35 characters
    ++Ctry (D): 2-character ISO 3166-1 country code

  +RmtInf (Payment Reference - Mandatory group)
    ++Tp (M): "QRR", "SCOR", or "NON" - Max 4 alphanumeric
    ++Ref (D): Reference number (see section 4)
    ++AddInf (Additional Information)
      +++Ustrd (O): Unstructured message - Max 140 characters
      +++Trailer (M): "EPD" (fixed) - 3 alphanumeric
      +++StrdBkgInf (A): Billing information - Max 140 characters

  +AltPmtInf (Alternative Procedures - Optional group)
    ++AltPmt (A): Max 100 characters per procedure
                  Maximum 2 occurrences allowed
```

**Note**: Ustrd + StrdBkgInf combined cannot exceed 140 characters total.

## 4. Reference Types

### 4.1 QR Reference (QRR)

- **Usage**: Only with QR-IBAN
- **Length**: 27 numeric characters
- **Structure**: 26 digits + 1 check digit (position 27)
- **Check Digit**: Modulo 10 recursive algorithm
- **Constraint**: Must not be all zeros

### 4.2 Creditor Reference (SCOR)

- **Usage**: Only with regular IBAN (not QR-IBAN)
- **Standard**: ISO 11649
- **Length**: 5-25 alphanumeric characters
- **Structure**: "RF" + 2 check digits + reference (min 1 char)
- **Check Digit**: Modulo 97-10 algorithm

### 4.3 No Reference (NON)

- **Usage**: IBAN only (not QR-IBAN)
- **Reference field**: Must be empty
- **Use case**: No structured reference needed

**QR-IBAN Identification**: IID range 30000-31999 (positions 5-9 of IBAN)

## 5. Account Numbers

### 5.1 IBAN Format

- **Length**: 21 characters (fixed)
- **Format**: No spaces in QR code
- **Display**: Blocks of 4 characters (5 groups + 1 char)
- **Countries**: CH or LI only
- **Example**: `CH5800791123000889012`

### 5.2 QR-IBAN Specifics

- **Structure**: Same as IBAN
- **QR-IID Range**: 30000-31999 (in positions 5-9)
- **Usage**: Exclusively for QR Reference payments
- **Direction**: Incoming payments only (no debits)
- **Example**: `CH4431999123000889012` (QR-IID: 31999)

## 6. Amount Specifications

### 6.1 Format Requirements

```
Format:    [digits].[2 decimals]
Separator: "." (period/full stop only)
Minimum:   0.01
Maximum:   999999999.99
Examples:  1.50, 1590.00, 999999999.99
Display:   Space as thousands separator (1 590.00)
```

### 6.2 Special Cases

- **No Amount**: Leave Amt field empty (not zero)
- **Below 1.00**: Use format 0.XX (e.g., 0.10)
- **Notification Only**: Use `0.00` with text "DO NOT USE FOR PAYMENT" in Additional Information

## 7. Address Specifications

### 7.1 Structured Address Fields

| Field            | Status      | Max Length | Rules                             |
| ---------------- | ----------- | ---------- | --------------------------------- |
| AdrTp            | Required    | 1          | Must be "S"                       |
| Name             | Required    | 70         | First name + Last name or Company |
| StrtNmOrAdrLine1 | Optional    | 70         | Street or P.O. Box                |
| BldgNbOrAdrLine2 | Optional    | 16         | Building number                   |
| PstCd            | Dependent\* | 16         | No country prefix                 |
| TwnNm            | Dependent\* | 35         | Town/City name                    |
| Ctry             | Required    | 2          | ISO 3166-1 code                   |

\*Dependent: Required if address group is used

### 7.2 Address Rules

1. **Creditor Address**: Must match account holder details
2. **Country Code**: Always required for all addresses
3. **c/o Addresses**: Not included in QR code (use in invoice header)
4. **P.O. Box**: Place in StrtNmOrAdrLine1 field
5. **Building Number**: Can be in StrtNmOrAdrLine1 (tolerance), but separate field preferred

## 8. Additional Information Fields

### 8.1 Unstructured Message (Ustrd)

- **Max Length**: 140 characters
- **Purpose**: Payment purpose or additional text
- **Usage**: With any reference type
- **Display**: Printed on payment part
- **Combined Limit**: Ustrd + StrdBkgInf ≤ 140 characters total

### 8.2 Billing Information (StrdBkgInf)

- **Max Length**: 140 characters
- **Purpose**: Structured data for automated processing
- **Format**: Starts with "//" + 2-char code
- **Usage**: Not forwarded with payment
- **Print Requirement**: Mandatory if contains personal data
- **Example**: `//S1/10/10201409/11/190512/30/106017086`

#### Current Standard: Swico S1 Format

```
Syntax: //S1/TAG/value/TAG/value...

Tags:
/10/ - Invoice number
/11/ - Invoice date (YYMMDD)
/20/ - Customer reference
/30/ - VAT number (UID without CHE prefix)
/31/ - VAT date (YYMMDD or YYMMDD-YYMMDD)
/32/ - VAT details (rate or rate:amount;rate:amount)
/33/ - VAT import tax
/40/ - Payment conditions (discount:days or list)

Example: //S1/10/10201409/11/190512/20/1400.000-53/30/106017086/32/7.7/40/2:10;0:30
```

### 8.3 Alternative Procedures (AltPmt)

- **Max Occurrences**: 2
- **Max Length**: 100 characters each
- **Format**: `ProcedureName/separator/data/separator/data...`
- **Example**: `eBill/B/simon.muster@example.com`
- **Purpose**: Enable conversion to other payment methods

## 9. Layout Requirements

### 9.1 Paper Specifications

- **Weight**: 80-100 g/m²
- **Color**: White (no coating/reflection)
- **Certified Types**: Recycled, FSC, TCF permitted
- **Perforation**: Mandatory between sections

### 9.2 Font Specifications

| Element                | Font            | Size                           | Style               |
| ---------------------- | --------------- | ------------------------------ | ------------------- |
| Headings               | Sans-serif\*    | 6-10 pt                        | Bold                |
| Values                 | Sans-serif\*    | 6-10 pt                        | Regular             |
| Title "Payment part"   | Sans-serif\*    | 11 pt                          | Bold                |
| Recommended            | Arial/Helvetica | 8 pt (heading) / 10 pt (value) | -                   |
| Alternative Procedures | Sans-serif\*    | 7 pt                           | Procedure name bold |

\*Allowed: Arial, Frutiger, Helvetica, Liberation Sans (black, not italic, not underlined)

### 9.3 Section Layout

**Payment Part Sections:**

1. Title Section: "Payment part" (11 pt bold)
2. Swiss QR Code Section: 46×46 mm with 5 mm border
3. Amount Section: Currency + Amount or blank field (40×15 mm)
4. Information Section: Account, Reference, Additional info, Payable by
5. Further Information Section: Alternative procedures

**Receipt Sections:**

1. Title Section: "Receipt" (11 pt bold)
2. Information Section: Same as payment part (excluding additional info)
3. Amount Section: Currency + Amount or blank field (30×10 mm)
4. Acceptance Point Section: "Acceptance point" (right-aligned, min 20 mm height)

## 10. Validation Rules

### 10.1 Mandatory Checks

```
1. QRType = "SPC"
2. Version = "0200"
3. Coding = "1"
4. Currency ∈ {"CHF", "EUR"}
5. IBAN country code ∈ {"CH", "LI"}
6. IBAN length = 21
7. Reference type ∈ {"QRR", "SCOR", "NON"}
8. IBAN/Reference compatibility (see section 4.4)
9. Amount format: \d{1,9}\.\d{2} (if present)
10. Amount range: 0.01 ≤ Amt ≤ 999999999.99
```

### 10.2 Field Dependencies

```
IF QR-IBAN THEN
  - Reference type MUST be "QRR"
  - Reference MUST be 27 numeric characters
  - Check digit MUST be valid (Modulo 10 recursive)

IF IBAN THEN
  - Reference type MUST be "SCOR" or "NON"
  - IF "SCOR" THEN Reference MUST be ISO 11649 format
  - IF "NON" THEN Reference MUST be empty

IF UltmtDbtr used THEN
  - All dependent fields (AdrTp, Name, PstCd, TwnNm, Ctry) MUST be filled

IF Alternative Procedure used THEN
  - Max 2 procedures
  - Each max 100 characters
```

## 11. Example Data Structures

### 11.1 Example 1: QR Reference with Amount and Debtor

```
SPC
0200
1
CH6431961000004421557
S
Max Muster & Söhne
Musterstrasse
123
8000
Seldwyla
CH




50.00
CHF
S
Simon Muster
Musterstrasse
1
8000
Seldwyla
CH
QRR
000008207791225857421286694
Payment of travel
EPD


```

### 11.2 Example 2: With Billing Information and Alternative Procedure

```
SPC
0200
1
CH4431999123000889012
S
Max Muster & Söhne
Musterstrasse
123
8000
Seldwyla
CH




1949.75
CHF
S
Simon Muster
Musterstrasse
1
8000
Seldwyla
CH
QRR
210000000003139471430009017
Order from 15.10.2020
EPD
//S1/10/1234/11/201021/30/102673386/32/7.7/40/0:30
eBill/B/simon.muster@example.com

```

### 11.3 Example 3: Creditor Reference (ISO 11649)

```
SPC
0200
1
CH5800791123000889012
S
Muster Krankenkasse
Musterstrasse
12
8000
Seldwyla
CH




211.00
CHF
S
Sarah Beispiel
Musterstrasse
1
8000
Seldwyla
CH
SCOR
RF720191230100405JSH0438

EPD


```

### 11.4 Example 4: No Amount, No Debtor (Donation)

```
SPC
0200
1
CH5204835012345671000
S
Muster Stiftung
P.O. Box

3001
Bern
CH





CHF






NON


EPD


```

### 11.5 Example 5: "DO NOT USE FOR PAYMENT" Notification

```
Field: Amount = 0.00
Field: Additional Information = "DO NOT USE FOR PAYMENT"
       (or "NICHT ZUR ZAHLUNG VERWENDEN" in German)
```

## 12. Implementation Notes

### 12.1 QR Code Generation

```python
# Pseudocode example
qr_data = build_data_structure()  # Build according to section 3.2
qr_code = generate_qr(
    data=qr_data,
    version=None,  # Auto-select (max v25)
    error_correction='M',
    encoding='UTF-8'
)
qr_code.scale_to(46, 46, 'mm')  # Fixed size
qr_code.add_swiss_cross(7, 7, 'mm')  # Center overlay
```

### 12.2 Data Building

```python
# Element separator
SEP = '\r\n'  # or '\n'

# Build data string
elements = [
    'SPC',
    '0200',
    '1',
    iban,
    'S',
    creditor_name,
    # ... all fields in order
]

# Join with separator, omit trailing empty elements
qr_data = SEP.join(elements).rstrip(SEP)
```

### 12.3 Validation Example

```python
def validate_qr_reference(ref: str) -> bool:
    if len(ref) != 27 or not ref.isdigit():
        return False

    # Modulo 10 recursive check
    carry = 0
    table = [
        [0,9,4,6,8,2,7,1,3,5],
        [9,4,6,8,2,7,1,3,5,0],
        [4,6,8,2,7,1,3,5,0,9],
        [6,8,2,7,1,3,5,0,9,4],
        [8,2,7,1,3,5,0,9,4,6],
        [2,7,1,3,5,0,9,4,6,8],
        [7,1,3,5,0,9,4,6,8,2],
        [1,3,5,0,9,4,6,8,2,7],
        [3,5,0,9,4,6,8,2,7,1],
        [5,0,9,4,6,8,2,7,1,3]
    ]

    for digit in ref[:-1]:  # All except check digit
        carry = table[carry][int(digit)]

    expected_check = (10 - carry) % 10
    return int(ref[-1]) == expected_check
```

## 13. Common Errors to Avoid

1. **Wrong separator**: Using comma instead of period for decimals
2. **IBAN/Reference mismatch**: QR-IBAN with SCOR or regular IBAN with QRR
3. **Missing separators**: Forgetting newlines between elements
4. **Wrong encoding**: Using non-UTF-8 or wrong character subset
5. **Invalid QR-IID**: Using QR-IID outside 30000-31999 range
6. **Amount precision**: More or less than 2 decimal places
7. **Reference format**: QRR not exactly 27 digits or invalid check digit
8. **Address validation**: Missing required dependent fields
9. **Character limit**: Exceeding max lengths or 140-char combined limit
10. **Future fields**: Filling UltmtCdtr fields (reserved, must be empty)

## 14. Multilingual Terms

### 14.1 Section Titles

| English                | German                    | French                       | Italian                    |
| ---------------------- | ------------------------- | ---------------------------- | -------------------------- |
| Payment part           | Zahlteil                  | Section paiement             | Sezione pagamento          |
| Receipt                | Empfangsschein            | Récépissé                    | Ricevuta                   |
| Account / Payable to   | Konto / Zahlbar an        | Compte / Payable à           | Conto / Pagabile a         |
| Reference              | Referenz                  | Référence                    | Riferimento                |
| Additional information | Zusätzliche Informationen | Informations supplémentaires | Informazioni supplementari |
| Payable by             | Zahlbar durch             | Payable par                  | Pagabile da                |
| Currency               | Währung                   | Monnaie                      | Valuta                     |
| Amount                 | Betrag                    | Montant                      | Importo                    |
| Acceptance point       | Annahmestelle             | Point de dépôt               | Punto di accettazione      |

## 15. Reference Links

- **Standards**: ISO 18004 (QR Code), ISO 11649 (Creditor Reference), ISO 3166-1 (Country Codes)
- **Resources**: www.six-group.com (Payment Standardization)
- **Bank Master**: List of IIDs and QR-IIDs
- **Swico Billing**: www.swico.ch (S1 format specification)

---

**Document Version**: Based on Implementation Guidelines v2.3 (November 21, 2025)
**Target Audience**: Software developers implementing QR-bill generation/processing
