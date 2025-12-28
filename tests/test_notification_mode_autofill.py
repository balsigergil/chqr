from decimal import Decimal
from chqr import QRBill, Creditor

# Valid IBAN for testing (Regular IBAN, not QR-IBAN)
VALID_IBAN = "CH5800791123000889012"


def test_notification_mode_auto_fill():
    """Test auto-filling of notification text when amount is 0.00."""
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    # Case 1: No text provided
    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information=None,
    )
    assert bill.amount == Decimal("0.00")
    assert bill.additional_information == "DO NOT USE FOR PAYMENT"

    # Case 2: Random text provided (should be overridden)
    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="Some random info",
    )
    assert bill.amount == Decimal("0.00")
    assert bill.additional_information == "DO NOT USE FOR PAYMENT"


def test_notification_mode_preserves_valid_text():
    """Test that valid notification text in other languages is preserved."""
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    # German text provided explicitly
    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="NICHT ZUR ZAHLUNG VERWENDEN",
    )
    assert bill.amount == Decimal("0.00")
    assert bill.additional_information == "NICHT ZUR ZAHLUNG VERWENDEN"
