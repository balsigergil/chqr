"""Tests for QR-bill input validation."""

import pytest
from decimal import Decimal

from chqr import QRBill, Creditor, ValidationError
from chqr.validators import (
    is_qr_iban,
    validate_iban,
    validate_creditor_reference,
    validate_qr_reference,
    validate_currency,
    validate_country_code,
    validate_character_set,
    validate_reference_type,
    validate_additional_information,
)


class TestIBANValidation:
    """Test IBAN validation rules."""

    def test_valid_swiss_iban(self):
        """Test that valid Swiss IBAN is accepted."""
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
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        with pytest.raises(ValidationError, match="IBAN"):
            QRBill(account="INVALID", creditor=creditor, currency="CHF")

    def test_iban_wrong_length(self):
        """Test that IBAN with wrong length is rejected."""
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
        # QR-IID range: 30000-31999
        assert is_qr_iban("CH4431999123000889012") is True  # QR-IID: 31999
        assert is_qr_iban("CH5800791123000889012") is False  # Regular IID

    def test_is_qr_iban_invalid_length(self):
        """Test is_qr_iban with invalid length."""
        assert is_qr_iban("CH123") is False

    def test_is_qr_iban_index_error(self):
        """Test is_qr_iban with non-integer IID."""
        assert is_qr_iban("CH12ABC45678901234567") is False

    def test_validate_iban_empty(self):
        """Test validate_iban with empty value."""
        with pytest.raises(ValidationError, match="IBAN is required"):
            validate_iban("")

    def test_validate_iban_invalid_format(self):
        """Test validate_iban with invalid format."""
        with pytest.raises(ValidationError, match="IBAN format invalid"):
            validate_iban("CH12!@#$%^&*()_+12345")

    def test_iban_checksum_validation(self):
        """Test that IBAN checksum is validated using MOD97."""
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

    def test_iban_with_letters(self):
        """Test that IBAN with letters is accepted."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid IBAN with a letter 'A'
        iban = "CH90007911230008890A1"
        qr_bill = QRBill(account=iban, creditor=creditor, currency="CHF")
        assert qr_bill.account == iban


class TestReferenceValidation:
    """Test reference type and number validation."""

    def test_qr_iban_requires_qrr_reference(self):
        """Test that QR-IBAN must use QRR reference type."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # QR-IBAN with wrong reference type
        with pytest.raises(ValidationError, match="QR-IBAN.*QRR"):
            QRBill(
                account="CH4431999123000889012",  # QR-IBAN
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",  # Wrong!
            )

    def test_iban_cannot_use_qrr_reference(self):
        """Test that regular IBAN cannot use QRR reference type."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Regular IBAN with QRR reference
        with pytest.raises(ValidationError, match="IBAN.*SCOR.*NON"):
            QRBill(
                account="CH5800791123000889012",  # Regular IBAN
                creditor=creditor,
                currency="CHF",
                reference_type="QRR",  # Wrong!
            )

    def test_validate_reference_type_invalid_for_regular_iban(self):
        """Test validate_reference_type with invalid type for regular IBAN."""
        regular_iban = "CH1200000000000000001"
        with pytest.raises(ValidationError, match="Reference type must be SCOR or NON"):
            validate_reference_type(regular_iban, "INVALID")

    def test_qr_reference_format(self):
        """Test QR reference must be 27 digits."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid: 27 digits
        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="QRR",
            reference="210000000003139471430009017",  # Valid 27 digits
        )
        assert qr_bill.reference == "210000000003139471430009017"

        # Too short
        with pytest.raises(ValidationError, match="27.*digits"):
            QRBill(
                account="CH4431999123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="QRR",
                reference="12345678901234567890123456",  # 26 digits
            )

        # Contains letters
        with pytest.raises(ValidationError, match="numeric"):
            QRBill(
                account="CH4431999123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="QRR",
                reference="1234567890123456789012345A",  # Has letter
            )

    def test_qr_reference_check_digit(self):
        """Test QR reference check digit validation."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid check digit (from spec example)
        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="QRR",
            reference="210000000003139471430009017",  # Valid (check digit = 7)
        )
        assert qr_bill.reference == "210000000003139471430009017"

        # Invalid check digit (last digit should be 7, not 8)
        with pytest.raises(ValidationError, match="check digit"):
            QRBill(
                account="CH4431999123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="QRR",
                reference="210000000003139471430009018",  # Wrong check digit
            )

    def test_validate_qr_reference_empty(self):
        """Test validate_qr_reference with empty value."""
        with pytest.raises(ValidationError, match="QR reference is required"):
            validate_qr_reference("")

    def test_creditor_reference_format(self):
        """Test Creditor Reference (ISO 11649) format validation."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid SCOR reference
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="SCOR",
            reference="RF18539007547034",
        )
        assert qr_bill.reference == "RF18539007547034"

        # Invalid: doesn't start with RF
        with pytest.raises(ValidationError, match="RF"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",
                reference="XX18539007547034",
            )

        # Invalid: too short (min 5 chars)
        with pytest.raises(ValidationError, match="5.*25"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",
                reference="RF12",
            )

        # Invalid: too long (max 25 chars)
        with pytest.raises(ValidationError, match="5.*25"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",
                reference="RF12345678901234567890123456",  # 26 chars
            )

    def test_creditor_reference_check_digit(self):
        """Test Creditor Reference check digit validation using modulo 97-10."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid SCOR reference (corrected from spec example - should be RF24, not RF72)
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="SCOR",
            reference="RF240191230100405JSH0438",  # Valid check digits: 24
        )
        assert qr_bill.reference == "RF240191230100405JSH0438"

        # Invalid: wrong check digits (should be 24, not 72)
        with pytest.raises(ValidationError, match="check digit"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",
                reference="RF720191230100405JSH0438",  # Wrong check digits
            )

        # Another valid reference
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="SCOR",
            reference="RF18539007547034",  # Valid check digits: 18
        )
        assert qr_bill.reference == "RF18539007547034"

        # Invalid: wrong check digits (should be 18, not 19)
        with pytest.raises(ValidationError, match="check digit"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                reference_type="SCOR",
                reference="RF19539007547034",  # Wrong check digits
            )

        # Test with minimal valid reference (RF + 2 digits + 1 char minimum)
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="SCOR",
            reference="RF25A",  # Valid minimal reference
        )
        assert qr_bill.reference == "RF25A"

    def test_validate_creditor_reference_empty(self):
        """Test validate_creditor_reference with empty value."""
        with pytest.raises(ValidationError, match="Creditor Reference is required"):
            validate_creditor_reference("")

    def test_validate_creditor_reference_non_alnum(self):
        """Test validate_creditor_reference with non-alphanumeric value."""
        with pytest.raises(
            ValidationError, match="Creditor Reference must be alphanumeric"
        ):
            validate_creditor_reference("RF18 5390")  # space makes it non-alnum


class TestAmountValidation:
    """Test amount format and range validation."""

    def test_amount_format_two_decimals(self):
        """Test amount must have exactly 2 decimal places."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid amounts
        QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("0.10"),
            currency="CHF",
        )

        # Invalid: 3 decimal places
        with pytest.raises(ValidationError, match="2 decimal"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                amount=Decimal("100.001"),
                currency="CHF",
            )

    def test_amount_minimum(self):
        """Test amount validation for minimum values."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid: minimum payment amount
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("0.01"),
            currency="CHF",
        )
        assert qr_bill.amount == Decimal("0.01")

        # Valid: zero for notification-only QR-bills (must have notification text)
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("0.00"),
            currency="CHF",
            additional_information="DO NOT USE FOR PAYMENT",
        )
        assert qr_bill.amount == Decimal("0.00")

        # Valid: zero amount without notification text (will auto-fill)
        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("0.00"),
            currency="CHF",
        )
        assert qr_bill.additional_information == "DO NOT USE FOR PAYMENT"

        # Invalid: negative amounts
        with pytest.raises(ValidationError, match="negative"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                amount=Decimal("-0.01"),
                currency="CHF",
            )

    def test_amount_maximum(self):
        """Test amount must not exceed 999,999,999.99."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid maximum
        QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("999999999.99"),
            currency="CHF",
        )

        # Invalid: too large
        with pytest.raises(ValidationError, match="999,999,999.99"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                amount=Decimal("1000000000.00"),
                currency="CHF",
            )

    def test_currency_validation(self):
        """Test only CHF and EUR are allowed."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        # Valid currencies
        QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="EUR",
        )

        # Invalid currency
        with pytest.raises(ValidationError, match="CHF.*EUR"):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                amount=Decimal("100.00"),
                currency="USD",
            )

    def test_validate_currency_empty(self):
        """Test validate_currency with empty value."""
        with pytest.raises(ValidationError, match="Currency is required"):
            validate_currency("")


class TestAddressValidation:
    """Test address field validation."""

    def test_name_max_length(self):
        """Test name cannot exceed 70 characters."""
        # Valid: 70 characters
        Creditor(name="A" * 70, postal_code="8000", city="Zurich", country="CH")

        # Invalid: 71 characters
        with pytest.raises(ValidationError, match="70"):
            Creditor(name="A" * 71, postal_code="8000", city="Zurich", country="CH")

    def test_required_address_fields(self):
        """Test that name, postal code, city, and country are required."""
        # Empty name
        with pytest.raises(ValidationError, match="Name"):
            Creditor(name="", postal_code="8000", city="Zurich", country="CH")

        # Empty postal code
        with pytest.raises(ValidationError, match="Postal code"):
            Creditor(name="Test", postal_code="", city="Zurich", country="CH")

        # Empty city
        with pytest.raises(ValidationError, match="City"):
            Creditor(name="Test", postal_code="8000", city="", country="CH")

        # Empty country
        with pytest.raises(ValidationError, match="Country"):
            Creditor(name="Test", postal_code="8000", city="Zurich", country="")

    def test_country_code_format(self):
        """Test country must be 2-character ISO 3166-1 code."""
        # Valid
        Creditor(name="Test", postal_code="8000", city="Zurich", country="CH")

        # Invalid: too long
        with pytest.raises(ValidationError, match="2.*character"):
            Creditor(name="Test", postal_code="8000", city="Zurich", country="CHE")

    def test_validate_country_code_non_alpha(self):
        """Test validate_country_code with non-alphabetic value."""
        with pytest.raises(
            ValidationError, match="Country code must contain only letters"
        ):
            validate_country_code("12")

    def test_validate_country_code_lowercase(self):
        """Test validate_country_code with lowercase value."""
        with pytest.raises(ValidationError, match="Country code must be uppercase"):
            validate_country_code("ch")


class TestCharacterSetValidation:
    """Test UTF-8 Latin character set restrictions."""

    def test_valid_characters_accepted(self):
        """Test that allowed Unicode characters are accepted."""
        # Basic Latin, Latin-1 Supplement, Latin Extended A
        Creditor(name="Müller & Söhne", postal_code="8000", city="Zürich", country="CH")

        # Euro sign
        Creditor(name="Test € Company", postal_code="8000", city="Zurich", country="CH")

        # Romanian characters (Ș, ș, Ț, ț)
        Creditor(name="Ștefan Țepeș", postal_code="8000", city="Zurich", country="CH")

    def test_invalid_characters_rejected(self):
        """Test that non-Latin characters are rejected."""
        # Cyrillic
        with pytest.raises(ValidationError, match="character"):
            Creditor(name="Тест", postal_code="8000", city="Zurich", country="CH")

        # Chinese
        with pytest.raises(ValidationError, match="character"):
            Creditor(name="测试", postal_code="8000", city="Zurich", country="CH")

        # Arabic
        with pytest.raises(ValidationError, match="character"):
            Creditor(name="اختبار", postal_code="8000", city="Zurich", country="CH")

    def test_validate_character_set_empty(self):
        """Test validate_character_set with empty/None value."""
        # Should not raise anything
        validate_character_set("", "test_field")
        validate_character_set(None, "test_field")


class TestAdditionalInformationValidation:
    """Test additional information field validation."""

    def test_unstructured_msg_and_billing_info_not_exceed_140_characters_validation(
        self,
    ):
        """Test that unstructured message and billing information do not exceed 140 characters with the raw validation function."""
        with pytest.raises(ValidationError):
            validate_additional_information(
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxy",
            )

        validate_additional_information(
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )

    def test_unstructured_msg_and_billing_info_not_exceed_140_characters_constructor(
        self,
    ):
        """Test that unstructured message and billing information do not exceed 140 characters with the QRBill constructor."""
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        with pytest.raises(ValidationError):
            QRBill(
                account="CH5800791123000889012",
                creditor=creditor,
                currency="CHF",
                additional_information="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                billing_information="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxy",
            )
