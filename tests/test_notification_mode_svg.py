from decimal import Decimal
from chqr import QRBill, Creditor

# Valid IBAN for testing
VALID_IBAN = "CH5800791123000889012"


def test_notification_mode_svg_rendering():
    """Test that notification mode (0.00 amount) renders 0.00 and no placeholders."""
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    qr_bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
    )

    # Generate SVG
    svg = qr_bill.generate_svg()

    # Assertions
    # 1. Should contain "0.00" text
    assert ">0.00<" in svg

    # 2. Should NOT contain empty amount placeholder box
    # Placeholder box uses specific dimensions.
    # From svg_generator.py:
    # generate_placeholder_box("30.6mm", "10.6mm", "21.7mm", "66.7mm") -> Receipt
    # generate_placeholder_box("40.6mm", "15.6mm", "9.7mm", "66.7mm") -> Payment part

    # Checking for specific width/height strings might be brittle but effective
    assert 'width="30.6mm"' not in svg
    assert 'width="40.6mm"' not in svg

    # 3. Should contain notification text
    assert ">DO NOT USE FOR PAYMENT<" in svg
