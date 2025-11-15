"""QR-bill generation for Swiss payment standards."""

from decimal import Decimal
import segno
from .creditor import Creditor
from .debtor import UltimateDebtor
from .svg_generator import generate_svg

from .validators import (
    validate_iban,
    validate_reference_type,
    validate_qr_reference,
    validate_creditor_reference,
    validate_currency,
    validate_amount,
)


class QRBill:
    """Swiss QR-bill generator.

    Generates QR-bill data structures compliant with Swiss payment standards.
    """

    def __init__(
        self,
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
    ):
        """Initialize a QR-bill.

        Args:
            account: IBAN or QR-IBAN (21 characters)
            creditor: Creditor information
            currency: Currency code (CHF or EUR)
            amount: Payment amount (optional)
            reference_type: Reference type (QRR, SCOR, or NON)
            reference: Payment reference (optional)
            additional_information: Unstructured message (optional)
            debtor: Ultimate debtor information (optional)
            billing_information: Structured billing information (optional, max 140 chars)
            alternative_procedures: List of alternative procedures (optional, max 2, 100 chars each)

        Raises:
            ValidationError: If any input data is invalid
        """
        # Validate IBAN
        validate_iban(account)

        # Validate reference type matches account type
        validate_reference_type(account, reference_type)

        # Validate reference format if provided
        if reference_type == "QRR" and reference:
            validate_qr_reference(reference)
        elif reference_type == "SCOR" and reference:
            validate_creditor_reference(reference)

        # Validate currency and amount
        validate_currency(currency)
        validate_amount(amount, currency)

        self.account = account
        self.creditor = creditor
        self.currency = currency
        self.amount = amount
        self.reference_type = reference_type
        self.reference = reference or ""
        self.additional_information = additional_information or ""
        self.debtor = debtor
        self.billing_information = billing_information or ""
        self.alternative_procedures = alternative_procedures or []

    def build_data_string(self) -> str:
        """Build the QR code data string.

        Returns:
            QR code data string with elements separated by newlines.
        """
        elements = []

        # Header (mandatory)
        elements.append("SPC")  # QR type
        elements.append("0200")  # Version
        elements.append("1")  # Coding type (UTF-8)

        # Creditor information (mandatory)
        elements.append(self.account)  # IBAN

        # Creditor address
        elements.append("S")  # Address type (structured), required since November 2025
        elements.append(self.creditor.name)
        elements.append(self.creditor.street)
        elements.append(self.creditor.building_number)
        elements.append(self.creditor.postal_code)
        elements.append(self.creditor.city)
        elements.append(self.creditor.country)

        # Ultimate Creditor (reserved for future use - 7 empty fields)
        for _ in range(7):
            elements.append("")

        # Payment amount information
        if self.amount is not None:
            elements.append(f"{self.amount:.2f}")
        else:
            elements.append("")
        elements.append(self.currency)

        # Ultimate Debtor (optional - 7 fields)
        if self.debtor:
            elements.append("S")  # Address type
            elements.append(self.debtor.name)
            elements.append(self.debtor.street)
            elements.append(self.debtor.building_number)
            elements.append(self.debtor.postal_code)
            elements.append(self.debtor.city)
            elements.append(self.debtor.country)
        else:
            for _ in range(7):
                elements.append("")

        # Payment reference
        elements.append(self.reference_type)
        elements.append(self.reference)

        # Additional information
        elements.append(self.additional_information)  # Unstructured message
        elements.append("EPD")  # Trailer (End Payment Data)

        # Billing information (optional)
        if self.billing_information:
            elements.append(self.billing_information)

        # Alternative procedures (optional, max 2)
        if self.alternative_procedures:
            for procedure in self.alternative_procedures[:2]:  # Max 2 procedures
                elements.append(procedure)

        return "\n".join(elements)

    def generate_qr_code(self) -> segno.QRCode:
        """Generate a QR code for the Swiss QR-bill.

        Returns:
            QRCode object configured with Swiss QR-bill specifications.
            - Error correction level M (~15% redundancy)
            - Version auto-selected (max 25)
            - UTF-8 encoding
        """
        data = self.build_data_string()
        qr = segno.make(
            content=data,
            version=None,  # Auto-select version
            error="M",  # Error correction level M
        )

        return qr

    def generate_svg(self, language: str = "en") -> str:
        """Generate SVG for the QR-bill.

        Args:
            language: Language code (en, de, fr, it). Defaults to "en".

        Returns:
            SVG string representing the complete QR-bill.

        Example:
            >>> qr_bill = QRBill(...)
            >>> svg_string = qr_bill.generate_svg(language="de")
            >>> with open("qr_bill.svg", "w") as f:
            ...     f.write(svg_string)
        """
        return generate_svg(self, language)
