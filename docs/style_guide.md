# QR-Bill Style Guide - SVG Generation Requirements

## Overview

The QR-bill consists of two main parts:

- **Receipt** (left side): 62 × 105 mm
- **Payment part** (right side): 148 × 105 mm
- **Total dimensions**: 210 × 105 mm (DIN A6/5 landscape format)

## Paper Specifications

- **Format**: DIN A6/5 landscape (210 × 105 mm)
- **Paper color**: Natural white or white
- **Paper weight**: 80-100 g/m²
- **Type**: Non-coated, non-reflecting
- **Certified papers**: Recycled, FSC, TCF permitted

## Typography

### Permitted Fonts

- Arial
- Frutiger
- Helvetica
- Liberation Sans

**All fonts must be sans-serif**

### Font Rules

- **Color**: Always black
- **Style**: No italic, no underline
- **Type**: Sans-serif only

### Font Sizes - Payment Part

| Element                | Heading Size            | Value Size          | Notes                                    |
| ---------------------- | ----------------------- | ------------------- | ---------------------------------------- |
| Title "Payment part"   | 11 pt bold              | -                   | -                                        |
| Account/Payable to     | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Reference              | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Additional information | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Amount                 | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Currency               | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Payable by             | 8 pt bold (recommended) | 10 pt (recommended) | Range: 6-10 pt                           |
| Alternative procedures | 7 pt                    | 7 pt                | -                                        |
| Further information    | 7 pt bold               | 7 pt                | For "Ultimate creditor" / "In favour of" |

**General rule**: Value font size should be 2 pt larger than heading font size

### Font Sizes - Receipt

| Element          | Heading Size | Value Size | Notes         |
| ---------------- | ------------ | ---------- | ------------- |
| Title "Receipt"  | 11 pt bold   | -          | -             |
| All headings     | 6 pt bold    | -          | -             |
| All values       | -            | 8 pt       | -             |
| Acceptance point | 6 pt bold    | -          | Right-aligned |

### Line Spacing

- **Receipt**: 9 pt line spacing
- **Payment part**: 11 pt line spacing
- **Between text blocks**: One blank line

## Overall Dimensions (in mm)

### Complete Layout

```
Total width: 210 mm
Total height: 105 mm

Receipt width: 62 mm
Payment part width: 148 mm
Both heights: 105 mm
```

### Key Measurements (from top-left corner)

#### Receipt Section (62 × 105 mm)

- Top margin: 5 mm
- Left margin: 5 mm
- Title section height: ~18 mm
- Information section: Variable based on content
- Amount section: ~22 mm from bottom
- Acceptance point section: 5 mm from bottom, right-aligned

#### Payment Part Section (148 × 105 mm)

- Positioned at x: 62 mm (after receipt)
- Top margin: 5 mm
- Left margin: 5 mm
- Title section height: ~14 mm
- Swiss QR Code section: 56 × 56 mm (46 mm code + 5 mm margins)
- Information section: Variable based on content
- Amount section: ~22 mm from bottom
- Further information section: Below information section

### Precise Dimensional Layout

#### Horizontal Divisions

- Receipt: 0-62 mm
- Separator/perforation: 62 mm
- Payment part: 62-210 mm

Within Payment part:

- QR Code section left edge: ~67 mm (5 mm margin)
- QR Code section: 67-123 mm (56 mm total)
- Information section starts: ~125 mm

#### Vertical Divisions

- Title sections: 5-19 mm from top (Receipt), 5-19 mm from top (Payment part)
- Main content area: 19-83 mm
- Amount section: 83-105 mm

## Swiss QR Code Specifications

### Dimensions

- **Printed size**: 46 × 46 mm (exact, mandatory)
- **Quiet space (border)**: Minimum 1.6 mm, **recommended 5 mm** around all sides
- **Total QR section**: 56 × 56 mm (46 mm + 2×5 mm margins)
- **Swiss cross logo**: 7 × 7 mm (centered overlay)

### Position

- In payment part section only
- Left side of payment part
- 5 mm from left edge of payment part (67 mm from left edge of full bill)
- Vertically centered or positioned according to layout

### Technical Requirements

- Must be vector-based for quality
- Error correction level: M (per ISO 18004)
- Version: Typically V23-V25 (roughly)
- Swiss cross logo overlay required (available at www.paymentstandards.ch)

## Receipt Section Layout

### Structure (top to bottom)

1. **Title section** (11 pt bold)
   - Text: "Receipt" (or translated equivalent)
2. **Information section**
   - Account / Payable to
   - Reference (if present)
   - Payable by / Payable by (name/address)
3. **Amount section**
   - Currency (CHF or EUR)
   - Amount (or blank field)
4. **Acceptance point section**
   - Text: "Acceptance point" (right-aligned, 6 pt bold)

### Field Specifications - Receipt

#### Account / Payable to

- IBAN/QR-IBAN formatted in groups of 4 characters
- Example: `CH44 3199 9123 0008 8901 2`
- Followed by creditor name and address (name, street, postal code + city)
- Street and number may be omitted if space is limited

#### Reference

- **QR reference**: Groups of 5 characters (starts with 2, then 5×5)
  - Example: `21 00000 00003 13947 14300 09017`
  - Right-justified
  - Leading zeros may be omitted
- **SCOR reference** (ISO 11649): Groups of 4 characters
  - Example: `RF18 5390 0754 7034`
  - Left-justified
  - Last group may have fewer than 4 characters

#### Payable by

- If debtor included in QR code: Show name and address
- If debtor NOT included: Use heading "Payable by (name/address)" with blank field
- Blank field: 52 × 20 mm with black corner marks (0.75 pt line thickness)

#### Amount

- If amount included: Show with format `CHF 1 590.00` or `EUR 1 590.00`
  - Space as thousands separator
  - Period (.) as decimal separator
  - Always 2 decimal places
- If amount NOT included: Blank field 30 × 10 mm with black corner marks (0.75 pt)

## Payment Part Section Layout

### Structure (left to right, top to bottom)

#### Left column (QR Code section)

1. **Title section** (11 pt bold)
   - Text: "Payment part"
2. **Swiss QR Code section**
   - QR code with specs above

#### Right column (Information section)

1. **Information section**

   - Account / Payable to
   - Reference (if present)
   - Additional information (if present)
   - Payable by / Payable by (name/address)

2. **Amount section**

   - Currency
   - Amount (or blank field)

3. **Further information section** (below everything)
   - Ultimate creditor ("In favour of" - bold) if present
   - Alternative procedures (up to 2 lines, may be truncated with "...")

### Field Specifications - Payment Part

#### Account / Payable to

- Same formatting as Receipt (groups of 4)
- Creditor name and full address

#### Reference

- Same formatting rules as Receipt
- QR reference: Groups of 5, right-justified
- SCOR reference: Groups of 4, left-justified

#### Additional information

- Content from "Ustrd" (Unstructured message) and/or "StrdBkginf" (Billing information)
- Maximum 140 characters total
- Line break after "Ustrd" if both fields present
- Truncate with "..." if too long (but preserve personal data)

#### Payable by

- If debtor included: Show full name and address
- If debtor NOT included: Use "Payable by (name/address)" with blank field
- Blank field: 65 × 25 mm with black corner marks (0.75 pt)

#### Amount

- If included: Same format as Receipt (`CHF 1 590.00`)
- If NOT included: Blank field 40 × 15 mm with black corner marks (0.75 pt)

#### Further information

- "Ultimate creditor" shown with prefix "In favour of" (bold)
- Alternative procedures: Max 90 characters per line (approx.)
- If truncated, mark with "..."
- Format: `Name AV1: UV;UltraPay005;12345`

## Blank Field Corner Marks

When amount or debtor details are not provided, blank fields must have corner marks:

- **Line thickness**: 0.75 pt
- **Corner mark size**: 3 × 3 mm
- **Color**: Black
- **Position**: At all 4 corners of the blank field

### Blank Field Dimensions

| Location     | Field Type | Dimensions |
| ------------ | ---------- | ---------- |
| Receipt      | Amount     | 30 × 10 mm |
| Receipt      | Payable by | 52 × 20 mm |
| Payment part | Amount     | 40 × 15 mm |
| Payment part | Payable by | 65 × 25 mm |

## Number and Reference Formatting

### IBAN/QR-IBAN

- Groups of 4 characters
- 6 groups of 4, last character separate (total 21 characters for Swiss IBAN)
- Example: `CH44 3199 9123 0008 8901 2`
- Left-justified

### QR Reference (QRR)

- First group: 2 characters
- Following groups: 5 characters each (5 groups)
- Total: 27 characters
- Example: `21 00000 00003 13947 14300 09017`
- Right-justified
- Leading zeros may be omitted in display

### Creditor Reference (SCOR/ISO 11649)

- Groups of 4 characters
- Last group may be shorter
- Example: `RF18 5390 0754 7034`
- Left-justified

### Amount

- Thousands separator: Space
- Decimal separator: Period (.)
- Always 2 decimal places
- Examples: `1 949.75`, `50.00`, `2 500.25`

## Language Support

The QR-bill can be produced in four languages with specific heading translations:

| English                   | German                         | French                        | Italian                          |
| ------------------------- | ------------------------------ | ----------------------------- | -------------------------------- |
| Payment part              | Zahlteil                       | Section paiement              | Sezione pagamento                |
| Receipt                   | Empfangsschein                 | Récépissé                     | Ricevuta                         |
| Account / Payable to      | Konto / Zahlbar an             | Compte / Payable à            | Conto / Pagabile a               |
| Reference                 | Referenz                       | Référence                     | Riferimento                      |
| Additional information    | Zusätzliche Informationen      | Informations supplémentaires  | Informazioni supplementari       |
| Further information       | Weitere Informationen          | Informations additionelles    | Informazioni aggiuntive          |
| Currency                  | Währung                        | Monnaie                       | Valuta                           |
| Amount                    | Betrag                         | Montant                       | Importo                          |
| Acceptance point          | Annahmestelle                  | Point de dépôt                | Punto di accettazione            |
| Payable by                | Zahlbar durch                  | Payable par                   | Pagabile da                      |
| Payable by (name/address) | Zahlbar durch (Name/Adresse)   | Payable par (nom/adresse)     | Pagabile da (nome/indirizzo)     |
| Separate before paying in | Vor der Einzahlung abzutrennen | A détacher avant le versement | Da staccare prima del versamento |
| In favour of              | Zugunsten                      | En faveur de                  | A favore di                      |

## Separation Lines

### Version 1: Hard copy integrated

- Perforation between billing info and payment part
- Perforation between receipt and payment part

### Version 2: Hard copy separate

- Perforation between receipt and payment part

### Version 3: PDF/Electronic

- Scissors symbol on separation lines OR
- Text "Separate before paying in" above line (outside payment part)
- Lines between billing info and payment part
- Lines between receipt and payment part

## Layout Sections Reference

### Receipt Sections (vertical)

1. **Title section**: Contains "Receipt"
2. **Information section**: Account/Payable to, Reference, Payable by
3. **Amount section**: Currency and Amount
4. **Acceptance point section**: "Acceptance point" text, right-aligned

### Payment Part Sections (mixed layout)

1. **Title section**: Contains "Payment part" (top)
2. **Swiss QR Code section**: 56×56mm area with QR code (left side)
3. **Information section**: Account, Reference, Additional info, Payable by (right side)
4. **Amount section**: Currency and Amount (right side, lower area)
5. **Further information section**: Ultimate creditor, Alternative procedures (bottom)

## Positioning Rules

### General

- Payment part always on the right
- Receipt always on the left
- Both positioned at lower edge of bill
- Same height (105 mm)

### Margins

- Top margin: 5 mm
- Left margin (receipt): 5 mm
- Left margin (payment part content): 5 mm from payment part edge (67 mm from full bill edge)
- Between sections: 5 mm spacing generally

### Text Block Positioning

- No fixed vertical positions for text blocks
- Blocks move up if optional fields are omitted
- Blank line (line spacing) between different information blocks
- Content flows top to bottom within each section

## Validation Rules for Display

### Mandatory Elements (always show if present in QR code)

- Account / Payable to (IBAN and creditor info)
- Amount and Currency (if specified, otherwise blank field)
- Payable by (debtor info if specified, otherwise blank field with different heading)

### Optional Elements (only show if present in QR code)

- Reference (QR reference or SCOR reference)
- Additional information (Ustrd, StrdBkginf)
- Ultimate creditor
- Alternative procedures

### Display Rules

- If value not in QR code → Don't display the heading
- If debtor not specified → Change heading to "Payable by (name/address)" and show blank field
- If amount not specified → Show blank field instead of amount value
- Personal data must always be fully displayed (no truncation)
- Non-personal data may be truncated with "..." if space limited

## Common Layout Variations

### Version 1a - QRR with amount

- QR-IBAN + QR reference
- Debtor details present
- Amount present
- No additional information

### Version 1b - QRR with additional info

- QR-IBAN + QR reference
- Debtor details present
- Amount present
- Additional information present

### Version 2a - SCOR with amount

- Regular IBAN + SCOR reference
- Debtor details present
- Amount present
- No additional information

### Version 2b - SCOR with additional info

- Regular IBAN + SCOR reference
- Debtor details present
- Amount present
- Additional information present

### Version 3a - No reference with info

- Regular IBAN, no reference
- Debtor details present
- Amount present
- Additional information present

### Version 3b - Minimal (e.g., donation)

- Regular IBAN, no reference
- No debtor details (blank field)
- No amount (blank field)
- No additional information

## Critical "Do Not" Rules

### Prohibited Practices

❌ Do not use colored backgrounds (impairs legibility)
❌ Do not swap receipt and payment part positions
❌ Do not use fonts smaller than 6 pt or larger than specified maximums
❌ Do not use serif fonts or fonts other than the 4 permitted
❌ Do not use italic or underlined text
❌ Do not make QR code anything other than exactly 46×46 mm
❌ Do not use colored text (must be black)
❌ Do not use coated or reflective paper
❌ Do not deviate from specified dimensions

## Resources

- Swiss cross logo file: Available at www.paymentstandards.ch
- Corner marks template: Available at www.paymentstandards.ch
- Implementation Guidelines: ig-qr-bill-v2.3-en.pdf
- QR Code standard: ISO 18004

## Summary for SVG Generation

### Key SVG Requirements

1. **Canvas size**: 210 × 105 mm (or scaled proportionally)
2. **Use SVG groups** for Receipt and Payment part sections
3. **Swiss cross overlay**: 7×7 mm, centered on QR code
4. **Fonts**: Arial, Helvetica, Liberation Sans, or Frutiger (embedded or system)
5. **All text**: Black color (`#000000`)
6. **Line thickness**: 0.75 pt for corner marks
7. **Positioning**: Absolute positioning in mm
8. **Text alignment**: Left-aligned (except Acceptance point = right-aligned)
9. **Number formatting**: Apply grouping per specifications
10. **Conditional rendering**: Show/hide elements based on data presence

### SVG Coordinate System

- Use millimeters as units
- Origin (0,0) at top-left corner
- Positive X rightward
- Positive Y downward
- Receipt: 0-62 mm horizontal
- Payment part: 62-210 mm horizontal
- Both: 0-105 mm vertical
