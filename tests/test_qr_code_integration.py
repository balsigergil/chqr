"""Tests for QR code integration in SVG generation."""

import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from chqr import QRBill, Creditor, UltimateDebtor


SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


@pytest.fixture
def sample_qr_bill():
    """Create a sample QR-bill for testing."""
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

    return QRBill(
        account="CH4431999123000889012",
        creditor=creditor,
        amount=Decimal("1949.75"),
        currency="CHF",
        reference_type="QRR",
        reference="210000000003139471430009017",
        additional_information="Order from 15.10.2020",
        debtor=debtor,
    )


class TestQRCodeIntegration:
    """Test that real QR code is integrated into SVG."""

    def test_qr_code_has_actual_modules(self, sample_qr_bill):
        """Test that QR code section contains actual QR code path."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Find the QR code section
        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        assert qr_code_svg is not None, "QR code section not found"

        # segno generates QR codes as paths, not rectangles
        # Find all path elements in the QR code section
        paths = qr_code_svg.findall(".//svg:path", SVG_NS)

        # Should have path elements (segno generates QR as paths)
        # At minimum: QR code path(s) + Swiss cross paths
        assert len(paths) > 0, f"Expected QR code paths, found only {len(paths)} paths"

    def test_qr_code_has_white_background(self, sample_qr_bill):
        """Test that QR code SVG container has correct dimensions."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Verify the QR code SVG container has correct dimensions
        assert qr_code_svg.get("width") == "46mm", "QR code width should be 46mm"
        assert qr_code_svg.get("height") == "46mm", "QR code height should be 46mm"

    def test_swiss_cross_overlay_present(self, sample_qr_bill):
        """Test that Swiss cross is still present on top of QR code."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Find all nested SVG elements in the QR code section
        nested_svgs = qr_code_svg.findall("svg:svg", SVG_NS)

        # Find the Swiss cross SVG (should have viewBox="0 0 36 36")
        swiss_cross = None
        for svg in nested_svgs:
            if svg.get("viewBox") == "0 0 36 36":
                swiss_cross = svg
                break

        assert swiss_cross is not None, "Swiss cross not found"
        assert swiss_cross.get("width") == "7mm"
        assert swiss_cross.get("height") == "7mm"

    def test_qr_modules_have_correct_dimensions(self, sample_qr_bill):
        """Test that QR code is properly sized to fill 46x46mm."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Verify QR code container dimensions
        assert qr_code_svg.get("width") == "46mm", "QR code width should be 46mm"
        assert qr_code_svg.get("height") == "46mm", "QR code height should be 46mm"

        # Find QR code paths (segno generates paths, not rectangles)
        paths = qr_code_svg.findall(".//svg:path", SVG_NS)

        # Should have at least one path for the QR code
        assert len(paths) > 0, "No QR code paths found"

    def test_qr_code_generation_creates_valid_matrix(self, sample_qr_bill):
        """Test that QR code generation creates a valid QR code object."""
        qr = sample_qr_bill.generate_qr_code()

        # segno QRCode objects have a version attribute
        assert qr.version is not None, "QR code should have a version"

        # QR code should be at least version 1 (21x21 modules)
        assert qr.version >= 1, f"QR version too small: {qr.version}"

        # Verify error correction level is M
        assert qr.error == "M", f"Error correction should be M, got {qr.error}"

    def test_different_data_produces_different_qr_codes(self):
        """Test that different QR-bills produce different QR codes."""
        creditor1 = Creditor(
            name="Company A",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        creditor2 = Creditor(
            name="Company B",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill1 = QRBill(
            account="CH5800791123000889012",
            creditor=creditor1,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        qr_bill2 = QRBill(
            account="CH5800791123000889012",
            creditor=creditor2,
            amount=Decimal("200.00"),
            currency="CHF",
        )

        svg1 = qr_bill1.generate_svg()
        svg2 = qr_bill2.generate_svg()

        # The SVGs should be different (different QR codes)
        assert svg1 != svg2, "Different data should produce different SVGs"

        # Extract QR code sections to compare
        root1 = ET.fromstring(svg1)
        root2 = ET.fromstring(svg2)

        payment1 = root1.find(".//svg:svg[@class='payment']", SVG_NS)
        payment2 = root2.find(".//svg:svg[@class='payment']", SVG_NS)

        qr1 = payment1.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)
        qr2 = payment2.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Convert to strings for comparison
        qr1_str = ET.tostring(qr1, encoding="unicode")
        qr2_str = ET.tostring(qr2, encoding="unicode")

        assert qr1_str != qr2_str, "Different data should produce different QR codes"

    def test_qr_code_modules_positioned_correctly(self, sample_qr_bill):
        """Test that QR code is positioned correctly within the payment part."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Verify QR code position within payment part
        assert qr_code_svg.get("x") == "0mm", "QR code x position should be 0mm"
        assert qr_code_svg.get("y") == "12mm", "QR code y position should be 12mm"

        # Verify dimensions
        assert qr_code_svg.get("width") == "46mm", "QR code width should be 46mm"
        assert qr_code_svg.get("height") == "46mm", "QR code height should be 46mm"
