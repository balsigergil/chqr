"""Generate multiple QR-bill variations.

This example demonstrates various Swiss QR-bill configurations, showcasing
different combinations of features and use cases.
"""

from decimal import Decimal
from chqr import QRBill, Creditor, UltimateDebtor


def example_1_qrr_with_amount_and_debtor():
    """Example 1: Standard QR-bill with QRR reference, amount, and debtor."""
    print("1. QRR reference with amount and debtor...")

    creditor = Creditor(
        name="Max Muster & Söhne",
        street="Musterstrasse",
        building_number="123",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Simon Muster",
        street="Musterstrasse",
        building_number="1",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH4431999123000889012",  # QR-IBAN (required for QRR)
        creditor=creditor,
        amount=Decimal("1949.75"),
        currency="CHF",
        reference_type="QRR",
        reference="210000000003139471430009017",
        additional_information="Invoice #2020-001",
        debtor=debtor,
    )

    with open("variation_1_qrr_full.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_1_qrr_full.svg\n")


def example_2_scor_reference():
    """Example 2: QR-bill with SCOR reference (ISO 11649)."""
    print("2. SCOR reference with regular IBAN...")

    creditor = Creditor(
        name="Automation AG",
        street="Werkstrasse",
        building_number="45",
        postal_code="8005",
        city="Zürich",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Maria Schmidt",
        street="Bahnhofstrasse",
        building_number="88",
        postal_code="8001",
        city="Zürich",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",  # Regular IBAN
        creditor=creditor,
        amount=Decimal("750.00"),
        currency="CHF",
        reference_type="SCOR",
        reference="RF18539007547034",  # ISO 11649 creditor reference
        debtor=debtor,
    )

    with open("variation_2_scor.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_2_scor.svg\n")


def example_3_no_reference():
    """Example 3: QR-bill without reference."""
    print("3. No reference (NON)...")

    creditor = Creditor(
        name="Small Business GmbH",
        street="Dorfstrasse",
        building_number="7",
        postal_code="3000",
        city="Bern",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Peter Müller",
        street="Hauptstrasse",
        building_number="12",
        postal_code="3005",
        city="Bern",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("89.90"),
        currency="CHF",
        additional_information="Order #54321",
        debtor=debtor,
    )

    with open("variation_3_no_reference.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("de"))
    print("   ✓ Generated: variation_3_no_reference.svg\n")


def example_4_no_debtor():
    """Example 4: QR-bill without debtor information."""
    print("4. No debtor information...")

    creditor = Creditor(
        name="Invoice Service SA",
        street="Rue du Commerce",
        building_number="23",
        postal_code="1000",
        city="Lausanne",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("250.50"),
        currency="CHF",
        additional_information="Payment reference: 2025-XYZ",
        # debtor is None by default
    )

    with open("variation_4_no_debtor.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("fr"))
    print("   ✓ Generated: variation_4_no_debtor.svg\n")


def example_5_no_amount():
    """Example 5: QR-bill without fixed amount (open amount)."""
    print("5. No amount (open amount)...")

    creditor = Creditor(
        name="Subscription Service Ltd",
        street="Tech Park",
        building_number="100",
        postal_code="6900",
        city="Lugano",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Anna Rossi",
        street="Via Nassa",
        building_number="5",
        postal_code="6900",
        city="Lugano",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF",
        debtor=debtor,
        # amount is None - to be filled in by payer
    )

    with open("variation_5_no_amount.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("it"))
    print("   ✓ Generated: variation_5_no_amount.svg\n")


def example_6_donation_form():
    """Example 6: Donation form (no amount, no debtor)."""
    print("6. Donation form (no amount, no debtor)...")

    creditor = Creditor(
        name="Charity Foundation",
        street="Postfach",
        building_number="",
        postal_code="3001",
        city="Bern",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=creditor,
        currency="CHF",
        additional_information="Your donation helps!",
        # No amount and no debtor
    )

    with open("variation_6_donation.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_6_donation.svg\n")


def example_7_eur_currency():
    """Example 7: QR-bill in EUR currency."""
    print("7. EUR currency instead of CHF...")

    creditor = Creditor(
        name="International Trade SA",
        street="Avenue de la Gare",
        building_number="42",
        postal_code="1201",
        city="Genève",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="European Customer Ltd",
        street="Main Street",
        building_number="10",
        postal_code="75001",
        city="Paris",
        country="FR",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("1250.00"),
        currency="EUR",  # EUR instead of CHF
        debtor=debtor,
    )

    with open("variation_7_eur.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_7_eur.svg\n")


def example_8_notification_mode():
    """Example 8: Notification mode (0.00 amount)."""
    print("8. Notification mode (0.00 amount)...")

    creditor = Creditor(
        name="E-Bill Service AG",
        street="Digital Plaza",
        building_number="1",
        postal_code="8050",
        city="Zürich",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Customer Account",
        street="Wohnstrasse",
        building_number="99",
        postal_code="8055",
        city="Zürich",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("0.00"),  # Triggers "DO NOT USE FOR PAYMENT" mode
        currency="CHF",
        debtor=debtor,
    )

    with open("variation_8_notification.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_8_notification.svg\n")


def example_9_minimal():
    """Example 9: Minimal QR-bill (only required fields)."""
    print("9. Minimal QR-bill (only required fields)...")

    creditor = Creditor(
        name="Minimal Shop",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zürich",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF",
        # No amount, no debtor, no reference, no additional_information
    )

    with open("variation_9_minimal.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_9_minimal.svg\n")


def example_10_with_billing_info():
    """Example 10: QR-bill with both billing_information and additional_information."""
    print("10. With structured billing information and additional message...")

    creditor = Creditor(
        name="Professional Services Ltd",
        street="Office Park",
        building_number="25",
        postal_code="4000",
        city="Basel",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Corporate Client AG",
        street="Firmenweg",
        building_number="50",
        postal_code="4051",
        city="Basel",
        country="CH",
    )

    # Structured billing information (max 140 chars)
    # Can use structured format like //S1/... for standards-compliant data
    billing_info = "//S1/10/10201409/11/201021/20/1400.000-53/30/106017086/31/181023/32/7.7/40/2:10;0:30"

    # Additional unstructured message
    additional_message = "Payment for consulting services - December 2025"

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("5432.10"),
        currency="CHF",
        reference_type="SCOR",
        reference="RF48500040025684371",
        additional_information=additional_message,
        billing_information=billing_info,  # Using the billing_information field
        debtor=debtor,
    )

    with open("variation_10_billing_info.svg", "w", encoding="utf-8") as f:
        f.write(qr_bill.generate_svg("en"))
    print("   ✓ Generated: variation_10_billing_info.svg\n")


def main():
    """Generate all QR-bill variations."""
    print("=" * 60)
    print("Generating Swiss QR-Bill Variations")
    print("=" * 60 + "\n")

    example_1_qrr_with_amount_and_debtor()
    example_2_scor_reference()
    example_3_no_reference()
    example_4_no_debtor()
    example_5_no_amount()
    example_6_donation_form()
    example_7_eur_currency()
    example_8_notification_mode()
    example_9_minimal()
    example_10_with_billing_info()

    print("=" * 60)
    print("✓ All 10 variations generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
