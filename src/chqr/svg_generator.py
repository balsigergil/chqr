"""SVG generation for Swiss QR-bills."""

from decimal import Decimal
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .qr_bill import QRBill


# Language translations for QR-bill headings
TRANSLATIONS = {
    "en": {
        "payment_part": "Payment part",
        "receipt": "Receipt",
        "account_payable_to": "Account / Payable to",
        "reference": "Reference",
        "additional_information": "Additional information",
        "currency": "Currency",
        "amount": "Amount",
        "acceptance_point": "Acceptance point",
        "payable_by": "Payable by",
        "payable_by_name_address": "Payable by (name/address)",
    },
    "de": {
        "payment_part": "Zahlteil",
        "receipt": "Empfangsschein",
        "account_payable_to": "Konto / Zahlbar an",
        "reference": "Referenz",
        "additional_information": "Zusätzliche Informationen",
        "currency": "Währung",
        "amount": "Betrag",
        "acceptance_point": "Annahmestelle",
        "payable_by": "Zahlbar durch",
        "payable_by_name_address": "Zahlbar durch (Name/Adresse)",
    },
    "fr": {
        "payment_part": "Section paiement",
        "receipt": "Récépissé",
        "account_payable_to": "Compte / Payable à",
        "reference": "Référence",
        "additional_information": "Informations supplémentaires",
        "currency": "Monnaie",
        "amount": "Montant",
        "acceptance_point": "Point de dépôt",
        "payable_by": "Payable par",
        "payable_by_name_address": "Payable par (nom/adresse)",
    },
    "it": {
        "payment_part": "Sezione pagamento",
        "receipt": "Ricevuta",
        "account_payable_to": "Conto / Pagabile a",
        "reference": "Riferimento",
        "additional_information": "Informazioni supplementari",
        "currency": "Valuta",
        "amount": "Importo",
        "acceptance_point": "Punto di accettazione",
        "payable_by": "Pagabile da",
        "payable_by_name_address": "Pagabile da (nome/indirizzo)",
    },
}


def format_iban(iban: str) -> str:
    """Format IBAN in groups of 4 characters.

    Args:
        iban: The IBAN string (21 characters for Swiss IBAN)

    Returns:
        Formatted IBAN with spaces

    Example:
        CH4431999123000889012 -> CH44 3199 9123 0008 8901 2
    """
    # Remove any existing spaces
    iban = iban.replace(" ", "")

    # Group in 4s
    groups = []
    for i in range(0, len(iban), 4):
        groups.append(iban[i : i + 4])

    return " ".join(groups)


def format_qr_reference(reference: str) -> str:
    """Format QR reference in groups of 5 characters.

    Args:
        reference: The QR reference string (27 characters)

    Returns:
        Formatted reference with spaces

    Example:
        210000000003139471430009017 -> 21 00000 00003 13947 14300 09017
    """
    # Remove any existing spaces
    reference = reference.replace(" ", "")

    # First 2 chars, then groups of 5
    if len(reference) < 2:
        return reference

    result = reference[:2]
    remainder = reference[2:]

    groups = []
    for i in range(0, len(remainder), 5):
        groups.append(remainder[i : i + 5])

    return result + " " + " ".join(groups)


def format_creditor_reference(reference: str) -> str:
    """Format SCOR/Creditor reference in groups of 4 characters.

    Args:
        reference: The creditor reference string

    Returns:
        Formatted reference with spaces

    Example:
        RF18539007547034 -> RF18 5390 0754 7034
    """
    # Remove any existing spaces
    reference = reference.replace(" ", "")

    # Group in 4s
    groups = []
    for i in range(0, len(reference), 4):
        groups.append(reference[i : i + 4])

    return " ".join(groups)


def format_amount(amount: Decimal) -> str:
    """Format amount with space as thousands separator.

    Args:
        amount: The amount as Decimal

    Returns:
        Formatted amount string

    Example:
        1949.75 -> 1 949.75
        50 -> 50.00
    """
    # Format with 2 decimal places
    formatted = f"{amount:.2f}"

    # Split into integer and decimal parts
    parts = formatted.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    # Add space as thousands separator
    # Reverse, group by 3, reverse back
    integer_reversed = integer_part[::-1]
    groups = []
    for i in range(0, len(integer_reversed), 3):
        groups.append(integer_reversed[i : i + 3])

    integer_formatted = " ".join(groups)[::-1]

    return f"{integer_formatted}.{decimal_part}"


def escape_xml(text: str) -> str:
    """Escape XML special characters.

    Args:
        text: The text to escape

    Returns:
        Escaped text
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_svg(qr_bill: "QRBill", language: str = "en") -> str:
    """Generate SVG for QR-bill.

    Args:
        qr_bill: The QRBill instance
        language: Language code (en, de, fr, it)

    Returns:
        SVG string
    """
    # Get translations
    t = TRANSLATIONS.get(language, TRANSLATIONS["en"])

    # Format data
    formatted_iban = format_iban(qr_bill.account)
    formatted_amount = format_amount(qr_bill.amount) if qr_bill.amount else None

    # Format reference based on type
    formatted_reference = None
    if qr_bill.reference:
        if qr_bill.reference_type == "QRR":
            formatted_reference = format_qr_reference(qr_bill.reference)
        elif qr_bill.reference_type == "SCOR":
            formatted_reference = format_creditor_reference(qr_bill.reference)

    # Build SVG
    svg_parts = []

    # SVG header
    svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_parts.append(
        '<svg width="210mm" height="108mm" xmlns="http://www.w3.org/2000/svg"'
    )
    svg_parts.append('  font-family="Arial, Helvetica, Liberation Sans, sans-serif">')

    # Background
    svg_parts.append(
        '  <rect x="0mm" y="0mm" width="210mm" height="108mm" fill="white" />'
    )

    # Separator lines (4 lines with gaps for scissors)
    # Horizontal top line (left part)
    svg_parts.append(
        '  <line x1="0mm" y1="3mm" x2="202.5mm" y2="3mm" stroke="black" stroke-width="0.1mm" />'
    )
    # Horizontal top line (right part, after scissors)
    svg_parts.append(
        '  <line x1="204.8mm" y1="3mm" x2="210mm" y2="3mm" stroke="black" stroke-width="0.1mm" />'
    )
    # Vertical line (top part)
    svg_parts.append(
        '  <line x1="62mm" y1="3mm" x2="62mm" y2="102.5mm" stroke="black" stroke-width="0.1mm" />'
    )
    # Vertical line (bottom part, after scissors)
    svg_parts.append(
        '  <line x1="62mm" y1="104.8mm" x2="62mm" y2="110mm" stroke="black" stroke-width="0.1mm" />'
    )

    # Scissors symbols
    # Top scissors (horizontal separator)
    svg_parts.append(
        '  <svg x="202mm" y="1.5mm" width="3mm" height="3mm" viewBox="0 0 12 12">'
    )
    svg_parts.append('    <path fill="#000" transform="rotate(-180 6 6)"')
    svg_parts.append(
        '      d="M3 1a2 2 0 0 1 1.72 3L6 5.3L9.65 1.65a0.35 0.35 45 0 1 0.7 0.7L6.7 6h-1.4L4 4.72A2 2 0 1 1 3 1v1a1 1 0 0 0 -1 1a1 1 0 1 0 1 -1z" />'
    )
    svg_parts.append('    <path fill="#000" transform="rotate(-180 6 6)"')
    svg_parts.append(
        '      d="M3 11a2 2 0 0 0 1.72 -3L6.7 6h-1.4L4 7.28A2 2 0 1 0 3 11v-1a1 1 0 0 1 -1 -1a1 1 0 1 1 1 1zM7.15 7.85L9.65 10.35a0.35 0.35 45 0 0 0.7 -0.7L7.85 7.15a0.35 0.35 45 0 0 -0.7 0.7z" />'
    )
    svg_parts.append("  </svg>")

    # Side scissors (vertical separator)
    svg_parts.append(
        '  <svg x="60.5mm" y="102mm" width="3mm" height="3mm" viewBox="0 0 12 12">'
    )
    svg_parts.append('    <path fill="#000" transform="rotate(-90 6 6)"')
    svg_parts.append(
        '      d="M3 1a2 2 0 0 1 1.72 3L6 5.3L9.65 1.65a0.35 0.35 45 0 1 0.7 0.7L6.7 6h-1.4L4 4.72A2 2 0 1 1 3 1v1a1 1 0 0 0 -1 1a1 1 0 1 0 1 -1z" />'
    )
    svg_parts.append('    <path fill="#000" transform="rotate(-90 6 6)"')
    svg_parts.append(
        '      d="M3 11a2 2 0 0 0 1.72 -3L6.7 6h-1.4L4 7.28A2 2 0 1 0 3 11v-1a1 1 0 0 1 -1 -1a1 1 0 1 1 1 1zM7.15 7.85L9.65 10.35a0.35 0.35 45 0 0 0.7 -0.7L7.85 7.15a0.35 0.35 45 0 0 -0.7 0.7z" />'
    )
    svg_parts.append("  </svg>")

    # Receipt section (starts at y=3mm after separator line)
    svg_parts.append(
        '  <svg class="receipt" x="0mm" y="3mm" width="62mm" height="105mm">'
    )
    svg_parts.append(
        '    <svg class="innerReceipt" x="5mm" y="5mm" width="52mm" height="95mm">'
    )
    svg_parts.append(
        f'      <text x="0mm" y="3mm" font-size="11pt" font-weight="bold">{escape_xml(t["receipt"])}</text>'
    )

    # Receipt information section
    svg_parts.append('      <text x="0mm" y="3.65mm">')
    svg_parts.append(
        f'        <tspan x="0mm" dy="18pt" font-size="6pt" font-weight="bold">{escape_xml(t["account_payable_to"])}</tspan>'
    )
    svg_parts.append(
        f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(formatted_iban)}</tspan>'
    )
    svg_parts.append(
        f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(qr_bill.creditor.name)}</tspan>'
    )

    # Creditor address
    creditor_address_line = (
        f"{qr_bill.creditor.street} {qr_bill.creditor.building_number}".strip()
    )
    if creditor_address_line:
        svg_parts.append(
            f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(creditor_address_line)}</tspan>'
        )

    creditor_city_line = (
        f"{qr_bill.creditor.postal_code} {qr_bill.creditor.city}".strip()
    )
    if creditor_city_line:
        svg_parts.append(
            f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(creditor_city_line)}</tspan>'
        )

    # Reference (if present)
    if formatted_reference:
        svg_parts.append(
            f'        <tspan x="0mm" dy="18pt" font-size="6pt" font-weight="bold">{escape_xml(t["reference"])}</tspan>'
        )
        svg_parts.append(
            f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(formatted_reference)}</tspan>'
        )

    # Payable by
    if qr_bill.debtor:
        svg_parts.append(
            f'        <tspan x="0mm" dy="18pt" font-size="6pt" font-weight="bold">{escape_xml(t["payable_by"])}</tspan>'
        )
        svg_parts.append(
            f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(qr_bill.debtor.name)}</tspan>'
        )

        debtor_address_line = (
            f"{qr_bill.debtor.street} {qr_bill.debtor.building_number}".strip()
        )
        if debtor_address_line:
            svg_parts.append(
                f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(debtor_address_line)}</tspan>'
            )

        debtor_city_line = f"{qr_bill.debtor.postal_code} {qr_bill.debtor.city}".strip()
        if debtor_city_line:
            svg_parts.append(
                f'        <tspan x="0mm" dy="9pt" font-size="8pt">{escape_xml(debtor_city_line)}</tspan>'
            )
    else:
        svg_parts.append(
            f'        <tspan x="0mm" dy="18pt" font-size="6pt" font-weight="bold">{escape_xml(t["payable_by_name_address"])}</tspan>'
        )

    svg_parts.append("      </text>")

    # Amount section
    svg_parts.append(
        f'      <text x="0mm" y="66mm" font-size="6pt" font-weight="bold">{escape_xml(t["currency"])}</text>'
    )
    svg_parts.append(
        f'      <text x="0mm" y="70mm" font-size="8pt">{escape_xml(qr_bill.currency)}</text>'
    )
    svg_parts.append(
        f'      <text x="22mm" y="66mm" font-size="6pt" font-weight="bold">{escape_xml(t["amount"])}</text>'
    )

    if formatted_amount:
        svg_parts.append(
            f'      <text x="22mm" y="70mm" font-size="8pt">{escape_xml(formatted_amount)}</text>'
        )

    # Acceptance point
    svg_parts.append(
        f'      <text x="52mm" y="80mm" text-anchor="end" font-size="6pt" font-weight="bold">{escape_xml(t["acceptance_point"])}</text>'
    )

    svg_parts.append("    </svg>")
    svg_parts.append("  </svg>")

    # Payment part section (starts at y=3mm after separator line)
    svg_parts.append(
        '  <svg class="payment" x="62mm" y="3mm" width="148mm" height="105mm">'
    )
    svg_parts.append(
        '    <svg class="innerPayment" x="5mm" y="5mm" width="138mm" height="95mm">'
    )
    svg_parts.append(
        f'      <text x="0mm" y="3mm" font-size="11pt" font-weight="bold">{escape_xml(t["payment_part"])}</text>'
    )

    # QR Code section with actual QR code
    svg_parts.append(
        '      <svg id="qr_code_svg" width="46mm" height="46mm" x="0mm" y="12mm">'
    )
    # Generate and insert the actual QR code
    qr_code = qr_bill.generate_qr_code()
    buffer = io.BytesIO()
    qr_code.save(
        buffer,
        kind="svg",
        xmldecl=False,
        svgns=False,
        svgclass=None,
        lineclass=None,
        omitsize=True,
        border=0,
    )
    qr_svg_content = buffer.getvalue().decode("utf-8")
    svg_parts.append(f"        {qr_svg_content.strip()}")

    # Swiss cross overlay (must be on top of QR code)
    svg_parts.append(
        '        <svg width="7mm" height="7mm" x="19.5mm" y="19.5mm" viewBox="0 0 36 36"><path d="m0 0h36v36h-36z" fill="#fff" /><path d="m2 2h32v32h-32z" fill="#000" /><path d="m15 8h6v7h7v6h-7v7h-6v-7h-7v-6h7z" fill="#fff" /></svg>'
    )
    svg_parts.append(
        "      </svg>",
    )

    # Currency and Amount (bottom left)
    svg_parts.append(
        f'      <text x="0mm" y="66mm" font-size="8pt" font-weight="bold">{escape_xml(t["currency"])}</text>'
    )
    svg_parts.append(
        f'      <text x="0mm" y="70mm" font-size="10pt">{escape_xml(qr_bill.currency)}</text>'
    )
    svg_parts.append(
        f'      <text x="22mm" y="66mm" font-size="8pt" font-weight="bold">{escape_xml(t["amount"])}</text>'
    )

    if formatted_amount:
        svg_parts.append(
            f'      <text x="22mm" y="70mm" font-size="10pt">{escape_xml(formatted_amount)}</text>'
        )

    # Information section (right side)
    svg_parts.append('      <text x="51mm" y="-4.76mm">')
    svg_parts.append(
        f'        <tspan x="51mm" dy="22pt" font-size="8pt" font-weight="bold">{escape_xml(t["account_payable_to"])}</tspan>'
    )
    svg_parts.append(
        f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(formatted_iban)}</tspan>'
    )
    svg_parts.append(
        f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(qr_bill.creditor.name)}</tspan>'
    )

    # Creditor full address in payment part
    creditor_street_full = (
        f"{qr_bill.creditor.street} {qr_bill.creditor.building_number}".strip()
    )
    if creditor_street_full:
        svg_parts.append(
            f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(creditor_street_full)}</tspan>'
        )

    creditor_city_full = (
        f"{qr_bill.creditor.postal_code} {qr_bill.creditor.city}".strip()
    )
    if creditor_city_full:
        svg_parts.append(
            f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(creditor_city_full)}</tspan>'
        )

    # Reference (if present)
    if formatted_reference:
        svg_parts.append(
            f'        <tspan x="51mm" dy="22pt" font-size="8pt" font-weight="bold">{escape_xml(t["reference"])}</tspan>'
        )
        svg_parts.append(
            f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(formatted_reference)}</tspan>'
        )

    # Additional information (if present)
    if qr_bill.additional_information:
        svg_parts.append(
            f'        <tspan x="51mm" dy="22pt" font-size="8pt" font-weight="bold">{escape_xml(t["additional_information"])}</tspan>'
        )
        svg_parts.append(
            f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(qr_bill.additional_information)}</tspan>'
        )

    # Payable by
    if qr_bill.debtor:
        svg_parts.append(
            f'        <tspan x="51mm" dy="22pt" font-size="8pt" font-weight="bold">{escape_xml(t["payable_by"])}</tspan>'
        )
        svg_parts.append(
            f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(qr_bill.debtor.name)}</tspan>'
        )

        debtor_street_full = (
            f"{qr_bill.debtor.street} {qr_bill.debtor.building_number}".strip()
        )
        if debtor_street_full:
            svg_parts.append(
                f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(debtor_street_full)}</tspan>'
            )

        debtor_city_full = f"{qr_bill.debtor.postal_code} {qr_bill.debtor.city}".strip()
        if debtor_city_full:
            svg_parts.append(
                f'        <tspan x="51mm" dy="11pt" font-size="10pt">{escape_xml(debtor_city_full)}</tspan>'
            )
    else:
        svg_parts.append(
            f'        <tspan x="51mm" dy="22pt" font-size="8pt" font-weight="bold">{escape_xml(t["payable_by_name_address"])}</tspan>'
        )

    svg_parts.append("      </text>")

    svg_parts.append("    </svg>")
    svg_parts.append("  </svg>")

    # Close SVG
    svg_parts.append("</svg>")

    return "\n".join(svg_parts)
