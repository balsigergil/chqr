"""Tests for donation feature (QR-bills without amount)."""

import pytest
from decimal import Decimal
from chqr import QRBill, Creditor, UltimateDebtor


@pytest.fixture
def sample_creditor():
    """Create a sample creditor for testing."""
    return Creditor(
        name="Max Muster & Söhne",
        street="Musterstrasse",
        building_number="123",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )


@pytest.fixture
def sample_debtor():
    """Create a sample debtor for testing."""
    return UltimateDebtor(
        name="Simon Muster",
        street="Musterweg",
        building_number="1",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )


def test_donation_qr_data_structure(sample_creditor):
    """Test that QR code data has empty amount field for donation."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,  # No amount for donation
    )

    qr_data = qr_bill.build_data_string()
    lines = qr_data.split("\n")

    # Amount field should be empty (line 18)
    # Header (3) + Creditor IBAN (1) + Creditor address (7) + Ultimate creditor (7) = 18
    assert lines[18] == "", "Amount field should be empty for donation"
    assert lines[19] == "CHF", "Currency should still be present"


def test_donation_svg_has_amount_placeholder_receipt(sample_creditor):
    """Test that donation SVG has placeholder box for amount in receipt section."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have placeholder box with correct dimensions for receipt
    assert 'width="30.6mm"' in svg
    assert 'height="10.6mm"' in svg
    assert 'x="21.7mm"' in svg
    assert 'y="66.7mm"' in svg

    # Should have corner markers (viewBox for corners)
    assert 'viewBox="0 0 12 12"' in svg

    # Should NOT have an amount value displayed
    assert "1 949.75" not in svg


def test_donation_svg_has_amount_placeholder_payment(sample_creditor):
    """Test that donation SVG has placeholder box for amount in payment section."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have placeholder box with correct dimensions for payment part
    assert 'width="40.6mm"' in svg
    assert 'height="15.6mm"' in svg
    assert 'x="9.7mm"' in svg
    assert 'y="66.7mm"' in svg


def test_donation_with_debtor_provided(sample_creditor, sample_debtor):
    """Test donation form with debtor information provided.

    This tests that amount and debtor are independent features.
    """
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,  # No amount
        debtor=sample_debtor,  # But debtor is provided
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have amount placeholder boxes
    assert 'width="30.6mm" height="10.6mm"' in svg  # Receipt amount placeholder
    assert 'width="40.6mm" height="15.6mm"' in svg  # Payment amount placeholder

    # Should have debtor information (NOT placeholder)
    assert "Simon Muster" in svg
    assert "Musterweg 1" in svg

    # Should NOT have debtor placeholder boxes
    # The debtor placeholder boxes have different dimensions
    assert (
        svg.count('width="52.6mm" height="20.6mm"') == 0
    )  # Receipt debtor placeholder
    assert (
        svg.count('width="65.6mm" height="25.6mm"') == 0
    )  # Payment debtor placeholder


def test_amount_provided_without_debtor(sample_creditor):
    """Test QR-bill with amount but no debtor.

    This is the inverse case - already tested in test_no_debtor_svg.py but
    included here for completeness of the independence test.
    """
    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=sample_creditor,
        currency="CHF",
        amount=Decimal("1949.75"),  # Amount provided
        debtor=None,  # No debtor
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have amount displayed
    assert "1 949.75" in svg

    # Should have debtor placeholder boxes
    assert 'width="52.6mm" height="20.6mm"' in svg  # Receipt debtor placeholder
    assert 'width="65.6mm" height="25.6mm"' in svg  # Payment debtor placeholder

    # Should NOT have amount placeholder
    # We check by looking for the text value instead of placeholder
    assert 'width="30.6mm" height="10.6mm"' not in svg  # No receipt amount placeholder


def test_donation_all_placeholders(sample_creditor):
    """Test donation form with both amount and debtor missing.

    This is the classic donation scenario.
    """
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,  # No amount
        debtor=None,  # No debtor
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have ALL placeholder boxes
    # Amount placeholders
    assert 'width="30.6mm" height="10.6mm"' in svg  # Receipt amount
    assert 'width="40.6mm" height="15.6mm"' in svg  # Payment amount

    # Debtor placeholders
    assert 'width="52.6mm" height="20.6mm"' in svg  # Receipt debtor
    assert 'width="65.6mm" height="25.6mm"' in svg  # Payment debtor

    # Currency should still be shown
    assert "CHF" in svg
    assert "Currency" in svg


def test_donation_all_languages(sample_creditor):
    """Test that donation placeholder works in all supported languages."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,
    )

    for language in ["en", "de", "fr", "it"]:
        svg = qr_bill.generate_svg(language=language)

        # All should have amount placeholder boxes
        assert 'width="30.6mm" height="10.6mm"' in svg, f"Failed for {language}"
        assert 'width="40.6mm" height="15.6mm"' in svg, f"Failed for {language}"

        # Check that language-specific labels are present
        if language == "en":
            assert "Amount" in svg
            assert "Currency" in svg
        elif language == "de":
            assert "Betrag" in svg
            assert "Währung" in svg
        elif language == "fr":
            assert "Montant" in svg
            assert "Monnaie" in svg
        elif language == "it":
            assert "Importo" in svg
            assert "Valuta" in svg


def test_donation_with_additional_info(sample_creditor):
    """Test donation form with additional information."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="CHF",
        amount=None,
        additional_information="Spende für Projekt XYZ",
    )

    svg = qr_bill.generate_svg(language="de")

    # Should have amount placeholder
    assert 'width="30.6mm" height="10.6mm"' in svg

    # Should have additional information
    assert "Spende für Projekt XYZ" in svg
    assert "Zusätzliche Informationen" in svg


def test_both_amount_and_debtor_provided(sample_creditor, sample_debtor):
    """Test normal QR-bill with both amount and debtor (no placeholders).

    This is the baseline case - everything is provided.
    """
    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=sample_creditor,
        currency="CHF",
        amount=Decimal("1949.75"),
        debtor=sample_debtor,
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have NO placeholder boxes at all
    placeholder_dimensions = [
        'width="30.6mm" height="10.6mm"',  # Receipt amount
        'width="40.6mm" height="15.6mm"',  # Payment amount
        'width="52.6mm" height="20.6mm"',  # Receipt debtor
        'width="65.6mm" height="25.6mm"',  # Payment debtor
    ]

    for placeholder_dim in placeholder_dimensions:
        assert placeholder_dim not in svg, (
            f"Should not have placeholder: {placeholder_dim}"
        )

    # Should have actual values
    assert "1 949.75" in svg
    assert "Simon Muster" in svg


def test_donation_eur_currency(sample_creditor):
    """Test donation form with EUR currency."""
    qr_bill = QRBill(
        account="CH5204835012345671000",
        creditor=sample_creditor,
        currency="EUR",
        amount=None,
    )

    svg = qr_bill.generate_svg(language="en")

    # Should have amount placeholder
    assert 'width="30.6mm" height="10.6mm"' in svg
    assert 'width="40.6mm" height="15.6mm"' in svg

    # Should show EUR currency
    assert "EUR" in svg

    # QR data should have empty amount but EUR currency
    qr_data = qr_bill.build_data_string()
    lines = qr_data.split("\n")
    assert lines[18] == ""  # Empty amount
    assert lines[19] == "EUR"  # EUR currency
