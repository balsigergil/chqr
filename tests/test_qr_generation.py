"""Tests for QR code generation and data string output."""

from decimal import Decimal
from pathlib import Path


from chqr import QRBill
from chqr.creditor import Creditor
from chqr.debtor import UltimateDebtor


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "qr_data"


class TestQRDataString:
    """Test QR data string generation against spec examples."""

    def test_example_1_qrr_with_amount_and_debtor(self):
        """Test example 1: QR Reference with amount and debtor."""
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
            account="CH6431961000004421557",
            creditor=creditor,
            amount=Decimal("50.00"),
            currency="CHF",
            debtor=debtor,
            reference_type="QRR",
            reference="000008207791225857421286694",
            additional_information="Payment of travel",
        )

        result = qr_bill.build_data_string()

        # Load expected fixture
        fixture_path = FIXTURES_DIR / "example_1_qrr_with_amount.txt"
        expected = fixture_path.read_text().rstrip("\n")

        assert result == expected

    def test_example_2_with_billing_info_and_alt_procedure(self):
        """Test example 2: With billing information and alternative procedure."""
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
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("1949.75"),
            currency="CHF",
            debtor=debtor,
            reference_type="QRR",
            reference="210000000003139471430009017",
            additional_information="Order from 15.10.2020",
            billing_information="//S1/10/1234/11/201021/30/102673386/32/7.7/40/0:30",
            alternative_procedures=["eBill/B/simon.muster@example.com"],
        )

        result = qr_bill.build_data_string()

        fixture_path = FIXTURES_DIR / "example_2_with_billing_info.txt"
        expected = fixture_path.read_text().rstrip("\n")

        assert result == expected

    def test_example_3_scor_reference(self):
        """Test example 3: Creditor Reference (ISO 11649)."""
        creditor = Creditor(
            name="Muster Krankenkasse",
            street="Musterstrasse",
            building_number="12",
            postal_code="8000",
            city="Seldwyla",
            country="CH",
        )

        debtor = UltimateDebtor(
            name="Sarah Beispiel",
            street="Musterstrasse",
            building_number="1",
            postal_code="8000",
            city="Seldwyla",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("211.00"),
            currency="CHF",
            debtor=debtor,
            reference_type="SCOR",
            reference="RF720191230100405JSH0438",
        )

        result = qr_bill.build_data_string()

        fixture_path = FIXTURES_DIR / "example_3_scor_reference.txt"
        expected = fixture_path.read_text().rstrip("\n")

        assert result == expected

    def test_example_4_donation_no_amount_no_debtor(self):
        """Test example 4: No amount, no debtor (donation)."""
        creditor = Creditor(
            name="Muster Stiftung",
            street="P.O. Box",
            building_number="",
            postal_code="3001",
            city="Bern",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5204835012345671000",
            creditor=creditor,
            currency="CHF",
            reference_type="NON",
        )

        result = qr_bill.build_data_string()

        fixture_path = FIXTURES_DIR / "example_4_donation.txt"
        expected = fixture_path.read_text().rstrip("\n")

        assert result == expected


class TestQRCodeParameters:
    """Test QR code generation parameters."""

    def test_qr_code_error_correction_level(self):
        """Test QR code uses error correction level M."""
        creditor = Creditor(
            name="Test",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
        )

        # Generate QR code
        qr_code = qr_bill.generate_qr_code()

        # Error correction level M (~15% redundancy)
        # segno uses 'M' as a string for error correction level
        assert qr_code.error == "M", f"Expected error correction M, got {qr_code.error}"

    def test_qr_code_version_auto_select(self):
        """Test QR code version is auto-selected with max 25."""
        creditor = Creditor(
            name="Test",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
        )

        qr_code = qr_bill.generate_qr_code()

        # Version should be auto-selected and <= 25 (117x117 modules)
        assert qr_code.version is not None
        assert qr_code.version <= 25

    def test_qr_data_string_is_utf8_compatible(self):
        """Test that data string can be encoded as UTF-8."""
        creditor = Creditor(
            name="Test Müller & Söhne",  # Special characters
            postal_code="8000",
            city="Zürich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()

        # Should be able to encode as UTF-8 without errors
        encoded = data_string.encode("utf-8")
        assert isinstance(encoded, bytes)

        # And decode back
        decoded = encoded.decode("utf-8")
        assert decoded == data_string


class TestEdgeCases:
    """Test edge cases for QR data string generation."""

    def test_minimum_amount(self):
        """Test QR bill with minimum amount (0.01)."""
        creditor = Creditor(
            name="Test",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("0.01"),
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()
        lines = data_string.split("\n")

        # Amount should be formatted with 2 decimals
        assert "0.01" in lines

    def test_maximum_amount(self):
        """Test QR bill with maximum amount (999,999,999.99)."""
        creditor = Creditor(
            name="Test",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("999999999.99"),
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()
        lines = data_string.split("\n")

        # Amount should be formatted with 2 decimals, no spaces
        assert "999999999.99" in lines

    def test_special_characters_in_name(self):
        """Test that special characters in names are preserved."""
        creditor = Creditor(
            name="Max Muster & Söhne",  # Ampersand and umlaut
            postal_code="8000",
            city="Zürich",  # Umlaut
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()

        # Special characters should be preserved
        assert "Max Muster & Söhne" in data_string
        assert "Zürich" in data_string

    def test_empty_building_number(self):
        """Test that empty building number produces empty field."""
        creditor = Creditor(
            name="Test",
            street="Main Street",
            building_number="",  # Empty
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()
        lines = data_string.split("\n")

        # Find the building number line (after street)
        # Structure: ...street, building_number, postal_code...
        street_idx = lines.index("Main Street")
        building_number_line = lines[street_idx + 1]

        assert building_number_line == ""

    def test_po_box_in_street_field(self):
        """Test P.O. Box is correctly placed in street field."""
        creditor = Creditor(
            name="Test Foundation",
            street="P.O. Box",
            building_number="",
            postal_code="3001",
            city="Bern",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            reference_type="NON",
        )

        data_string = qr_bill.build_data_string()

        assert "P.O. Box" in data_string
