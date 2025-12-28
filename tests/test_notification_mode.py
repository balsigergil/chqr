import pytest
from decimal import Decimal
from chqr import QRBill, Creditor, ValidationError

# Valid IBAN for testing (Regular IBAN, not QR-IBAN)
VALID_IBAN = "CH5800791123000889012"


def test_notification_mode_valid():
    """Test valid 'DO NOT USE FOR PAYMENT' QR-bills."""
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    # German
    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="NICHT ZUR ZAHLUNG VERWENDEN",
    )
    assert bill.amount == Decimal("0.00")
    assert bill.additional_information == "NICHT ZUR ZAHLUNG VERWENDEN"

    # English
    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="DO NOT USE FOR PAYMENT",
    )
    assert bill.amount == Decimal("0.00")


def test_notification_mode_invalid_amount_non_zero():
    """Test notification text with non-zero amount.

    If one of the specific notification texts is used, amount MUST be 0.00.
    """
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    with pytest.raises(ValidationError, match="notification text"):
        QRBill(
            account=VALID_IBAN,
            creditor=creditor,
            currency="CHF",
            amount=Decimal("10.00"),
            additional_information="DO NOT USE FOR PAYMENT",
        )


def test_notification_mode_autocorrects_invalid_text():
    """Test zero amount with invalid notification text.

    If amount is 0.00 and text is not one of the allowed strings,
    it should be auto-corrected to DO NOT USE FOR PAYMENT.
    """
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="Some other text",
    )
    assert bill.additional_information == "DO NOT USE FOR PAYMENT"


def test_notification_mode_auto_corrects_casing():
    """Test notification text with wrong casing."""
    creditor = Creditor(
        name="Org",
        street="Street",
        building_number="1",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    bill = QRBill(
        account=VALID_IBAN,
        creditor=creditor,
        currency="CHF",
        amount=Decimal("0.00"),
        additional_information="Do Not Use For Payment",  # Mixed case
    )
    assert bill.additional_information == "DO NOT USE FOR PAYMENT"
