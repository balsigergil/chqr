"""Example: Generate QR-bill SVG without debtor information.

This example demonstrates how to generate a Swiss QR-bill when the debtor
(payer) information is not known in advance. The generated SVG will include
placeholder boxes with corner markers where the debtor information can be
written in by hand.
"""

from decimal import Decimal
from chqr import QRBill, Creditor


def main():
    """Generate a QR-bill without debtor information."""
    # Create creditor (the person/organization receiving payment)
    creditor = Creditor(
        name="Max Muster & Söhne",
        street="Musterstrasse",
        building_number="123",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )

    # Create QR-bill WITHOUT debtor information (debtor=None is the default)
    qr_bill = QRBill(
        account="CH5800791123000889012",  # Regular IBAN (not QR-IBAN)
        creditor=creditor,
        currency="CHF",
        amount=Decimal("1949.75"),
        additional_information="Auftrag vom 21.12.2025",
        # Note: debtor is None by default, so no debtor info is included
    )

    # Generate SVG in English
    svg_en = qr_bill.generate_svg(language="en")

    # Save to file
    with open("qr_bill_no_debtor_en.svg", "w", encoding="utf-8") as f:
        f.write(svg_en)

    print("Generated: qr_bill_no_debtor_en.svg")
    print()

    # You can also generate in other languages
    svg_de = qr_bill.generate_svg(language="de")
    with open("qr_bill_no_debtor_de.svg", "w", encoding="utf-8") as f:
        f.write(svg_de)

    print("Generated: qr_bill_no_debtor_de.svg (German version)")
    print()

    # Example 2: Donation form (no amount, no debtor)
    donation_qr = QRBill(
        account="CH5204835012345671000",
        creditor=Creditor(
            name="Muster Stiftung",
            street="P.O. Box",
            building_number="",  # Empty is OK
            postal_code="3001",
            city="Bern",
            country="CH",
        ),
        currency="CHF",
        # No amount - will be filled in by donor
        # No debtor - will be filled in by donor
    )

    svg_donation = donation_qr.generate_svg(language="en")
    with open("qr_bill_donation.svg", "w", encoding="utf-8") as f:
        f.write(svg_donation)


if __name__ == "__main__":
    main()
