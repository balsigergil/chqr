"""Test SVG generation for QR-bills without debtor information."""

from decimal import Decimal
from chqr import QRBill, Creditor


def test_svg_generation_without_debtor():
    """Test that SVG is generated correctly when no debtor is provided."""
    # Create a QR bill without debtor (similar to reference_layout_no_debtor.xml)
    creditor = Creditor(
        name="Max Muster & Söhne",
        street="Musterstrasse",
        building_number="123",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF",
        amount=Decimal("1949.75"),
        additional_information="Auftrag vom 21.12.2025",
        debtor=None,  # No debtor provided
    )

    # Generate SVG
    svg = qr_bill.generate_svg(language="en")

    # Verify SVG is generated
    assert svg is not None
    assert len(svg) > 0

    # Verify it contains the XML declaration and SVG root
    assert '<?xml version="1.0" encoding="UTF-8"?>' in svg
    assert '<svg width="210mm" height="108mm"' in svg

    # Verify "Payable by (name/address)" label is present (not "Payable by")
    assert "Payable by (name/address)" in svg

    # Verify placeholder boxes are rendered in receipt section
    # Receipt box: 52.6mm × 20.6mm at (-0.3mm, 42.7mm)
    assert '<svg x="-0.3mm" y="42.7mm" width="52.6mm" height="20.6mm">' in svg

    # Verify placeholder boxes are rendered in payment part section
    # Payment box: 65.6mm × 25.6mm at (50.7mm, 59.7mm)
    assert '<svg x="50.7mm" y="59.7mm" width="65.6mm" height="25.6mm">' in svg

    # Verify corner markers are present (L-shaped paths)
    assert 'path d="m0 0h12v1H1v11H0z"' in svg  # Top-left corner
    assert 'path d="m0 0h12v12H11V1H0z"' in svg  # Top-right corner
    assert 'path d="m0 0h1v11h11v1H0z"' in svg  # Bottom-left corner
    assert 'path d="m11 0h1v12H0V11h11z"' in svg  # Bottom-right corner

    # Verify that debtor name/address is NOT present
    assert "Simon Muster" not in svg  # Example debtor name that shouldn't be there


def test_svg_generation_with_debtor_still_works():
    """Test that SVG with debtor still works as before (regression test)."""
    from chqr import UltimateDebtor

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
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF",
        amount=Decimal("1949.75"),
        debtor=debtor,
    )

    # Generate SVG
    svg = qr_bill.generate_svg(language="en")

    # Verify SVG is generated
    assert svg is not None
    assert len(svg) > 0

    # Verify debtor information is present
    assert "Simon Muster" in svg
    assert "Musterstrasse 1" in svg

    # Verify "Payable by" label is present (not "Payable by (name/address)")
    # and that placeholder boxes are NOT present
    assert '<svg x="-0.3mm" y="42.7mm" width="52.6mm" height="20.6mm">' not in svg
    assert '<svg x="50.7mm" y="59.7mm" width="65.6mm" height="25.6mm">' not in svg


def test_svg_no_debtor_different_languages():
    """Test that placeholder boxes work with different language translations."""
    creditor = Creditor(
        name="Max Muster & Söhne",
        street="Musterstrasse",
        building_number="123",
        postal_code="8000",
        city="Seldwyla",
        country="CH",
    )

    qr_bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        currency="CHF",
        amount=Decimal("100.00"),
        debtor=None,
    )

    # Test German
    svg_de = qr_bill.generate_svg(language="de")
    assert "Zahlbar durch (Name/Adresse)" in svg_de
    assert '<svg x="-0.3mm" y="42.7mm" width="52.6mm" height="20.6mm">' in svg_de

    # Test French
    svg_fr = qr_bill.generate_svg(language="fr")
    assert "Payable par (nom/adresse)" in svg_fr
    assert '<svg x="-0.3mm" y="42.7mm" width="52.6mm" height="20.6mm">' in svg_fr

    # Test Italian
    svg_it = qr_bill.generate_svg(language="it")
    assert "Pagabile da (nome/indirizzo)" in svg_it
    assert '<svg x="-0.3mm" y="42.7mm" width="52.6mm" height="20.6mm">' in svg_it
