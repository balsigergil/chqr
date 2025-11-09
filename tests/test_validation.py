"""Tests for QR-bill input validation."""

import pytest
from decimal import Decimal


class TestIBANValidation:
    """Test IBAN validation rules."""

    def test_valid_swiss_iban(self):
        """Test that valid Swiss IBAN is accepted."""
        from chqr import QRBill, Creditor

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Should not raise
        qr_bill = QRBill(
            account="CH5800791123000889012", creditor=creditor, currency="CHF"
        )
        assert qr_bill.account == "CH5800791123000889012"

    def test_invalid_iban_format(self):
        """Test that invalid IBAN format is rejected."""
        from chqr import QRBill, Creditor, ValidationError

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        with pytest.raises(ValidationError, match="IBAN"):
            QRBill(account="INVALID", creditor=creditor, currency="CHF")

    def test_iban_wrong_length(self):
        """Test that IBAN with wrong length is rejected."""
        from chqr import QRBill, Creditor, ValidationError

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        with pytest.raises(ValidationError, match="21 characters"):
            QRBill(
                account="CH58007911230008890",  # Too short
                creditor=creditor,
                currency="CHF",
            )

    def test_non_swiss_iban_rejected(self):
        """Test that non-CH/LI IBAN is rejected."""
        from chqr import QRBill, Creditor, ValidationError

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        with pytest.raises(ValidationError, match="CH or LI"):
            QRBill(
                account="DE89370400440532013000",  # German IBAN
                creditor=creditor,
                currency="CHF",
            )

    def test_qr_iban_identification(self):
        """Test that QR-IBAN is correctly identified."""
        from chqr.validators import is_qr_iban

        # QR-IID range: 30000-31999
        assert is_qr_iban("CH4431999123000889012") is True  # QR-IID: 31999
        assert is_qr_iban("CH5800791123000889012") is False  # Regular IID

    def test_iban_checksum_validation(self):
        """Test that IBAN checksum is validated using MOD97."""
        from chqr import QRBill, Creditor, ValidationError

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid IBAN with correct checksum
        qr_bill = QRBill(
            account="CH9300762011623852957",  # Valid checksum
            creditor=creditor,
            currency="CHF",
        )
        assert qr_bill.account == "CH9300762011623852957"

        # Invalid IBAN with wrong checksum (changed last digit from 93 to 00)
        with pytest.raises(ValidationError, match="checksum"):
            QRBill(
                account="CH0000762011623852957",  # Invalid checksum
                creditor=creditor,
                currency="CHF",
            )


class TestReferenceValidation:
    """Test reference type and number validation."""

    def test_qr_iban_requires_qrr_reference(self):
        """Test that QR-IBAN must use QRR reference type."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # QR-IBAN with wrong reference type
        # with pytest.raises(ValidationError, match="QR-IBAN.*QRR"):
        #     QRBill(
        #         account="CH4431999123000889012",  # QR-IBAN
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="SCOR"  # Wrong!
        #     )

    def test_iban_cannot_use_qrr_reference(self):
        """Test that regular IBAN cannot use QRR reference type."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Regular IBAN with QRR reference
        # with pytest.raises(ValidationError, match="IBAN.*SCOR.*NON"):
        #     QRBill(
        #         account="CH5800791123000889012",  # Regular IBAN
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="QRR"  # Wrong!
        #     )

    def test_qr_reference_format(self):
        """Test QR reference must be 27 digits."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Too short
        # with pytest.raises(ValidationError, match="27.*digits"):
        #     QRBill(
        #         account="CH4431999123000889012",
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="QRR",
        #         reference="12345678901234567890123456"  # 26 digits
        #     )
        #
        # # Contains letters
        # with pytest.raises(ValidationError, match="numeric"):
        #     QRBill(
        #         account="CH4431999123000889012",
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="QRR",
        #         reference="1234567890123456789012345A"  # Has letter
        #     )

    def test_qr_reference_check_digit(self):
        """Test QR reference check digit validation."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Invalid check digit (last digit should be 7)
        # with pytest.raises(ValidationError, match="check digit"):
        #     QRBill(
        #         account="CH4431999123000889012",
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="QRR",
        #         reference="210000000003139471430009018"  # Wrong check digit
        #     )

    def test_creditor_reference_format(self):
        """Test Creditor Reference (ISO 11649) format validation."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Valid SCOR reference
        # qr_bill = QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     currency="CHF",
        #     reference_type="SCOR",
        #     reference="RF18539007547034"
        # )
        #
        # # Invalid: doesn't start with RF
        # with pytest.raises(ValidationError, match="RF"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="SCOR",
        #         reference="XX18539007547034"
        #     )
        #
        # # Invalid: too short (min 5 chars)
        # with pytest.raises(ValidationError, match="5.*25"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         currency="CHF",
        #         reference_type="SCOR",
        #         reference="RF12"
        #     )


class TestAmountValidation:
    """Test amount format and range validation."""

    def test_amount_format_two_decimals(self):
        """Test amount must have exactly 2 decimal places."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Valid amounts
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("100.00"),
        #     currency="CHF"
        # )
        #
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("0.10"),
        #     currency="CHF"
        # )
        #
        # # Invalid: 3 decimal places
        # with pytest.raises(ValidationError, match="2 decimal"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         amount=Decimal("100.001"),
        #         currency="CHF"
        #     )

    def test_amount_minimum(self):
        """Test amount must be at least 0.01."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Valid minimum
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("0.01"),
        #     currency="CHF"
        # )
        #
        # # Invalid: zero (unless notification-only)
        # with pytest.raises(ValidationError, match="0.01"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         amount=Decimal("0.00"),
        #         currency="CHF"
        #     )

    def test_amount_maximum(self):
        """Test amount must not exceed 999,999,999.99."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Valid maximum
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("999999999.99"),
        #     currency="CHF"
        # )
        #
        # # Invalid: too large
        # with pytest.raises(ValidationError, match="999,999,999.99"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         amount=Decimal("1000000000.00"),
        #         currency="CHF"
        #     )

    def test_currency_validation(self):
        """Test only CHF and EUR are allowed."""
        pytest.skip("Not implemented yet")

        # from chqr import QRBill, Creditor
        # from chqr.exceptions import ValidationError
        #
        # creditor = Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Valid currencies
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("100.00"),
        #     currency="CHF"
        # )
        #
        # QRBill(
        #     account="CH5800791123000889012",
        #     creditor=creditor,
        #     amount=Decimal("100.00"),
        #     currency="EUR"
        # )
        #
        # # Invalid currency
        # with pytest.raises(ValidationError, match="CHF.*EUR"):
        #     QRBill(
        #         account="CH5800791123000889012",
        #         creditor=creditor,
        #         amount=Decimal("100.00"),
        #         currency="USD"
        #     )


class TestAddressValidation:
    """Test address field validation."""

    def test_name_max_length(self):
        """Test name cannot exceed 70 characters."""
        pytest.skip("Not implemented yet")

        # from chqr import Creditor
        # from chqr.exceptions import ValidationError
        #
        # # Valid: 70 characters
        # Creditor(
        #     name="A" * 70,
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Invalid: 71 characters
        # with pytest.raises(ValidationError, match="70"):
        #     Creditor(
        #         name="A" * 71,
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CH"
        #     )

    def test_required_address_fields(self):
        """Test that name, postal code, city, and country are required."""
        pytest.skip("Not implemented yet")

        # from chqr import Creditor
        # from chqr.exceptions import ValidationError
        #
        # # Missing name
        # with pytest.raises(ValidationError, match="name"):
        #     Creditor(
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CH"
        #     )
        #
        # # Missing postal code
        # with pytest.raises(ValidationError, match="postal"):
        #     Creditor(
        #         name="Test",
        #         city="Zurich",
        #         country="CH"
        #     )
        #
        # # Missing city
        # with pytest.raises(ValidationError, match="city"):
        #     Creditor(
        #         name="Test",
        #         postal_code="8000",
        #         country="CH"
        #     )
        #
        # # Missing country
        # with pytest.raises(ValidationError, match="country"):
        #     Creditor(
        #         name="Test",
        #         postal_code="8000",
        #         city="Zurich"
        #     )

    def test_country_code_format(self):
        """Test country must be 2-character ISO 3166-1 code."""
        pytest.skip("Not implemented yet")

        # from chqr import Creditor
        # from chqr.exceptions import ValidationError
        #
        # # Valid
        # Creditor(
        #     name="Test",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Invalid: too long
        # with pytest.raises(ValidationError, match="2.*character"):
        #     Creditor(
        #         name="Test",
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CHE"
        #     )


class TestCharacterSetValidation:
    """Test UTF-8 Latin character set restrictions."""

    def test_valid_characters_accepted(self):
        """Test that allowed Unicode characters are accepted."""
        pytest.skip("Not implemented yet")

        # from chqr import Creditor
        #
        # # Basic Latin, Latin-1 Supplement, Latin Extended A
        # Creditor(
        #     name="Müller & Söhne",
        #     postal_code="8000",
        #     city="Zürich",
        #     country="CH"
        # )
        #
        # # Euro sign
        # Creditor(
        #     name="Test € Company",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )
        #
        # # Romanian characters (Ș, ș, Ț, ț)
        # Creditor(
        #     name="Ștefan Țepeș",
        #     postal_code="8000",
        #     city="Zurich",
        #     country="CH"
        # )

    def test_invalid_characters_rejected(self):
        """Test that non-Latin characters are rejected."""
        pytest.skip("Not implemented yet")

        # from chqr import Creditor
        # from chqr.exceptions import ValidationError
        #
        # # Cyrillic
        # with pytest.raises(ValidationError, match="character"):
        #     Creditor(
        #         name="Тест",
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CH"
        #     )
        #
        # # Chinese
        # with pytest.raises(ValidationError, match="character"):
        #     Creditor(
        #         name="测试",
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CH"
        #     )
        #
        # # Arabic
        # with pytest.raises(ValidationError, match="character"):
        #     Creditor(
        #         name="اختبار",
        #         postal_code="8000",
        #         city="Zurich",
        #         country="CH"
        #     )
