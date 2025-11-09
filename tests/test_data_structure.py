"""Tests for QR-bill data structure generation."""

from chqr import QRBill, Creditor
from decimal import Decimal

from chqr.debtor import UltimateDebtor


class TestQRDataStructure:
    """Test building the QR code data string according to Swiss specification."""

    def test_minimal_qr_data_structure(self):
        """Test minimal valid QR-bill data structure."""
        # Expected structure (see qr_bill_spec.md section 3.2):

        creditor = Creditor(
            name="Test Company AG",
            street="Teststrasse",
            building_number="1",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012", creditor=creditor, currency="CHF"
        )

        data = qr_bill.build_data_string()
        lines = data.split("\n")

        # Header
        assert lines[0] == "SPC"
        assert lines[1] == "0200"
        assert lines[2] == "1"

        # Creditor IBAN
        assert lines[3] == "CH5800791123000889012"

        # Creditor info
        assert lines[4] == "S"  # Address type
        assert lines[5] == "Test Company AG"
        assert lines[6] == "Teststrasse"
        assert lines[7] == "1"
        assert lines[8] == "8000"
        assert lines[9] == "Zurich"
        assert lines[10] == "CH"

    def test_qr_data_with_debtor(self):
        """Test QR data structure including ultimate debtor."""

        creditor = Creditor(
            name="Test Company AG",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        debtor = UltimateDebtor(
            name="Max Muster",
            street="Musterstrasse",
            building_number="10",
            postal_code="3000",
            city="Bern",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            currency="CHF",
            debtor=debtor,
        )

        data = qr_bill.build_data_string()
        lines = data.split("\n")

        # Ultimate Debtor info should start at line 20
        assert lines[20] == "S"  # Address type
        assert lines[21] == "Max Muster"
        assert lines[22] == "Musterstrasse"
        assert lines[23] == "10"
        assert lines[24] == "3000"
        assert lines[25] == "Bern"
        assert lines[26] == "CH"

    def test_qr_data_with_amount(self):
        """Test QR data structure including amount."""

        creditor = Creditor(
            name="Test Company AG",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("199.95"),
            currency="CHF",
        )

        data = qr_bill.build_data_string()
        lines = data.split("\n")

        # Amount should be formatted with 2 decimals
        assert "199.95" in data
        assert "CHF" in data
        assert lines[18] == "199.95"  # Amount line
        assert lines[19] == "CHF"  # Currency line

    def test_qr_data_with_reference(self):
        """Test QR data structure with QR reference."""

        creditor = Creditor(
            name="Test Company AG",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        # QR-IBAN requires QR reference
        qr_bill = QRBill(
            account="CH4431999123000889012",  # QR-IBAN
            creditor=creditor,
            currency="CHF",
            reference_type="QRR",
            reference="210000000003139471430009017",
        )

        data = qr_bill.build_data_string()

        assert "QRR" in data
        assert "210000000003139471430009017" in data

    def test_qr_data_separator(self):
        """Test that elements are separated by newline."""

        creditor = Creditor(
            name="Test",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012", creditor=creditor, currency="CHF"
        )

        data = qr_bill.build_data_string()

        # Should use LF or CR+LF as separator
        assert "\n" in data or "\r\n" in data

    def test_empty_fields_have_separator(self):
        """Test that empty optional fields still have separators."""

        # Creditor without street/building number
        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        qr_bill = QRBill(
            account="CH5800791123000889012", creditor=creditor, currency="CHF"
        )

        data = qr_bill.build_data_string()
        lines = data.split("\n")

        # Lines 6 and 7 should be empty but present (street and building number)
        assert lines[6] == ""
        assert lines[7] == ""

    def test_ultimate_creditor_fields_empty(self):
        """Test that Ultimate Creditor fields are not filled (reserved for future)."""

        creditor = Creditor(
            name="Test", postal_code="8000", city="Zurich", country="CH"
        )

        qr_bill = QRBill(
            account="CH5800791123000889012", creditor=creditor, currency="CHF"
        )

        data = qr_bill.build_data_string()
        lines = data.split("\n")

        # Ultimate Creditor fields (lines 11-17) must be empty
        # See qr_bill_spec.md section 3.2
        for i in range(11, 18):
            assert lines[i] == ""

    def test_data_length_under_limit(self):
        """Test that data string doesn't exceed 997 character limit."""

        # Create QR-bill with maximum length data
        creditor = Creditor(
            name="A" * 70,  # Max length
            street="B" * 70,
            building_number="C" * 16,
            postal_code="D" * 16,
            city="E" * 35,
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("999999999.99"),
            currency="CHF",
            reference_type="SCOR",
            reference="RF18" + "X" * 21,  # Max length
            additional_information="Y" * 140,  # Max length
        )

        data = qr_bill.build_data_string()

        assert len(data) <= 997
