"""Tests for recreating official Swiss QR-bill test data schemas.

This module tests that the chqr library can accurately recreate all official
test data provided by the Swiss payment standards documentation.
"""

from decimal import Decimal
from pathlib import Path
from typing import NamedTuple

import pytest

from chqr import QRBill
from chqr.creditor import Creditor
from chqr.debtor import UltimateDebtor


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "datenschema"


class ParsedQRData(NamedTuple):
    """Parsed QR-bill data structure."""

    # Header
    qr_type: str
    version: str
    coding: str

    # Creditor account
    account: str

    # Creditor address
    creditor_address_type: str
    creditor_name: str
    creditor_street: str
    creditor_building_number: str
    creditor_postal_code: str
    creditor_city: str
    creditor_country: str

    # Amount
    amount: str
    currency: str

    # Debtor address
    debtor_address_type: str
    debtor_name: str
    debtor_street: str
    debtor_building_number: str
    debtor_postal_code: str
    debtor_city: str
    debtor_country: str

    # Reference
    reference_type: str
    reference: str

    # Additional information
    additional_information: str
    trailer: str

    # Optional fields
    billing_information: str
    alternative_procedures: list[str]


def parse_qr_data_file(file_path: Path) -> ParsedQRData:
    """Parse a QR-bill data file into structured components.

    Args:
        file_path: Path to the QR data file

    Returns:
        ParsedQRData object with all extracted fields
    """
    content = file_path.read_text().rstrip("\n")
    lines = content.split("\n")

    # Parse fixed-position fields (first 31 lines)
    data = ParsedQRData(
        # Header (3 lines)
        qr_type=lines[0],
        version=lines[1],
        coding=lines[2],
        # Creditor account (1 line)
        account=lines[3],
        # Creditor address (7 lines)
        creditor_address_type=lines[4],
        creditor_name=lines[5],
        creditor_street=lines[6],
        creditor_building_number=lines[7],
        creditor_postal_code=lines[8],
        creditor_city=lines[9],
        creditor_country=lines[10],
        # Ultimate creditor - reserved (7 lines, should be empty)
        # lines[11:18] - skipped
        # Amount information (2 lines)
        amount=lines[18],
        currency=lines[19],
        # Ultimate debtor address (7 lines)
        debtor_address_type=lines[20],
        debtor_name=lines[21],
        debtor_street=lines[22],
        debtor_building_number=lines[23],
        debtor_postal_code=lines[24],
        debtor_city=lines[25],
        debtor_country=lines[26],
        # Reference (2 lines)
        reference_type=lines[27],
        reference=lines[28],
        # Additional information (2 lines)
        additional_information=lines[29],
        trailer=lines[30],
        # Optional fields (remaining lines after trailer)
        billing_information=lines[31] if len(lines) > 31 else "",
        alternative_procedures=[lines[i] for i in range(32, len(lines))]
        if len(lines) > 32
        else [],
    )

    return data


def create_qr_bill_from_parsed_data(data: ParsedQRData) -> QRBill:
    """Create a QRBill instance from parsed QR data.

    Args:
        data: Parsed QR data structure

    Returns:
        QRBill instance configured with the parsed data
    """
    # Create creditor
    creditor = Creditor(
        name=data.creditor_name,
        street=data.creditor_street if data.creditor_street else None,
        building_number=data.creditor_building_number
        if data.creditor_building_number
        else None,
        postal_code=data.creditor_postal_code,
        city=data.creditor_city,
        country=data.creditor_country,
    )

    # Create debtor if debtor info is present
    debtor = None
    if data.debtor_name:  # If debtor has a name, create debtor object
        debtor = UltimateDebtor(
            name=data.debtor_name,
            street=data.debtor_street if data.debtor_street else None,
            building_number=data.debtor_building_number
            if data.debtor_building_number
            else None,
            postal_code=data.debtor_postal_code,
            city=data.debtor_city,
            country=data.debtor_country,
        )

    # Parse amount (empty string means no amount)
    amount = None
    if data.amount:
        amount = Decimal(data.amount)

    # Create QR bill
    qr_bill = QRBill(
        account=data.account,
        creditor=creditor,
        currency=data.currency,
        amount=amount,
        reference_type=data.reference_type,
        reference=data.reference if data.reference else None,
        additional_information=data.additional_information
        if data.additional_information
        else None,
        debtor=debtor,
        billing_information=data.billing_information
        if data.billing_information
        else None,
        alternative_procedures=data.alternative_procedures
        if data.alternative_procedures
        else None,
    )

    return qr_bill


# List all fixture files with structured (S) address format
# Note: Files with combined (K) address format are not included as the library
# currently only supports structured addresses.
# K format files: Nr. 2, 6, 14, 18, 22, 30, 34, 38, 46
OFFICIAL_TEST_FILES = [
    "Nr. 1 Datenschema englisch.txt",  # S - QRR with amount and debtor
    "Nr. 5 Datenschema englisch.txt",  # S - QRR with billing info and alt procedure
    "Nr. 13 Datenschema englisch.txt",  # S - QRR with billing info
    "Nr. 17 Datenschema englisch.txt",  # S - SCOR with amount and debtor
    "Nr. 21 Datenschema englisch.txt",  # S - SCOR with billing info and alt procedure
    "Nr. 29 Datenschema englisch.txt",  # S - SCOR with billing info
    "Nr. 33 Datenschema englisch.txt",  # S - NON with amount and debtor
    "Nr. 37 Datenschema englisch.txt",  # S - NON with billing info and alt procedure
    "Nr. 45 Datenschema englisch.txt",  # S - NON with billing info
]


@pytest.mark.parametrize("fixture_file", OFFICIAL_TEST_FILES)
def test_recreate_official_data_schema(fixture_file):
    """Test that library can recreate official QR-bill test data.

    This test verifies that the chqr library can accurately recreate
    the official Swiss QR-bill test data schemas. Each test case
    represents a different scenario from the official specification.

    Args:
        fixture_file: Name of the fixture file to test
    """
    # Load the official test data
    fixture_path = FIXTURES_DIR / fixture_file
    expected_output = fixture_path.read_text().rstrip("\n")

    # Parse the QR data
    parsed_data = parse_qr_data_file(fixture_path)

    # Create QRBill from parsed data
    qr_bill = create_qr_bill_from_parsed_data(parsed_data)

    # Generate the data string
    generated_output = qr_bill.build_data_string()

    # Assert exact match
    assert generated_output == expected_output, (
        f"Generated output does not match official test data for {fixture_file}\n"
        f"Expected:\n{expected_output}\n\n"
        f"Generated:\n{generated_output}"
    )


class TestOfficialDataSchemaParser:
    """Test the parser utility functions."""

    def test_parse_qr_data_file_structure(self):
        """Test that parser correctly extracts all fields."""
        fixture_path = FIXTURES_DIR / "Nr. 1 Datenschema englisch.txt"
        parsed = parse_qr_data_file(fixture_path)

        # Verify header
        assert parsed.qr_type == "SPC"
        assert parsed.version == "0200"
        assert parsed.coding == "1"

        # Verify creditor
        assert parsed.account == "CH6431961000004421557"
        assert parsed.creditor_name == "Health insurance fit&kicking"
        assert parsed.creditor_street == "Am Wasser"
        assert parsed.creditor_building_number == "1"
        assert parsed.creditor_postal_code == "3000"
        assert parsed.creditor_city == "Bern"
        assert parsed.creditor_country == "CH"

        # Verify amount
        assert parsed.amount == "111.00"
        assert parsed.currency == "CHF"

        # Verify debtor
        assert parsed.debtor_name == "Sarah Beispiel"
        assert parsed.debtor_street == "Mustergasse"
        assert parsed.debtor_building_number == "1"
        assert parsed.debtor_postal_code == "3600"
        assert parsed.debtor_city == "Thun"
        assert parsed.debtor_country == "CH"

        # Verify reference
        assert parsed.reference_type == "QRR"
        assert parsed.reference == "000008207791225857421286694"

        # Verify additional info
        assert parsed.additional_information == "Premium calculation July 2020"
        assert parsed.trailer == "EPD"

    def test_parse_qr_data_with_billing_info(self):
        """Test parser handles billing information correctly."""
        fixture_path = FIXTURES_DIR / "Nr. 13 Datenschema englisch.txt"
        parsed = parse_qr_data_file(fixture_path)

        # Should have billing information
        assert parsed.billing_information.startswith("//S1/")
        assert len(parsed.billing_information) > 0

    def test_parse_qr_data_with_alternative_procedures(self):
        """Test parser handles alternative procedures correctly."""
        fixture_path = FIXTURES_DIR / "Nr. 5 Datenschema englisch.txt"
        parsed = parse_qr_data_file(fixture_path)

        # Should have billing info and alternative procedure
        assert parsed.billing_information.startswith("//S1/")
        assert len(parsed.alternative_procedures) == 1
        assert parsed.alternative_procedures[0].startswith("eBill/")

    def test_parse_qr_data_without_debtor(self):
        """Test parser handles missing debtor information."""
        fixture_path = FIXTURES_DIR / "Nr. 2 Datenschema englisch.txt"
        parsed = parse_qr_data_file(fixture_path)

        # Debtor fields should be empty
        assert parsed.debtor_name == ""
        assert parsed.debtor_street == ""
        assert parsed.debtor_city == ""

    def test_parse_qr_data_without_amount(self):
        """Test parser handles missing amount."""
        fixture_path = FIXTURES_DIR / "Nr. 2 Datenschema englisch.txt"
        parsed = parse_qr_data_file(fixture_path)

        # Amount should be empty string
        assert parsed.amount == ""
        assert parsed.currency == "CHF"
