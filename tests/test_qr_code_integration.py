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
        """Test that QR code section contains actual QR modules (rectangles)."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Find the QR code section
        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        assert qr_code_svg is not None, "QR code section not found"

        # Find all rect elements in the QR code section (excluding the white background)
        rects = qr_code_svg.findall("svg:rect", SVG_NS)

        # Should have multiple rectangles (QR modules)
        # At minimum: 1 white background + many black modules
        assert len(rects) > 10, (
            f"Expected many QR code modules, found only {len(rects)} rectangles"
        )

        # Check that we have black modules
        black_modules = [r for r in rects if r.get("fill") == "black"]
        assert len(black_modules) > 0, "No black QR code modules found"

    def test_qr_code_has_white_background(self, sample_qr_bill):
        """Test that QR code has a white background rectangle."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Find white background rectangle
        rects = qr_code_svg.findall("svg:rect", SVG_NS)
        white_bg = [
            r
            for r in rects
            if r.get("fill") == "white"
            and r.get("width") == "46mm"
            and r.get("height") == "46mm"
        ]

        assert len(white_bg) == 1, "QR code should have exactly one white background"

    def test_swiss_cross_overlay_present(self, sample_qr_bill):
        """Test that Swiss cross is still present on top of QR code."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Find the Swiss cross SVG
        swiss_cross = qr_code_svg.find("svg:svg", SVG_NS)

        assert swiss_cross is not None, "Swiss cross not found"
        assert swiss_cross.get("width") == "7mm"
        assert swiss_cross.get("height") == "7mm"

    def test_qr_modules_have_correct_dimensions(self, sample_qr_bill):
        """Test that QR modules are properly sized to fill 46x46mm."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Find black modules
        rects = qr_code_svg.findall("svg:rect", SVG_NS)
        black_modules = [r for r in rects if r.get("fill") == "black"]

        assert len(black_modules) > 0, "No black modules found"

        # All black modules should have the same size
        module_widths = set(r.get("width") for r in black_modules)
        module_heights = set(r.get("height") for r in black_modules)

        assert len(module_widths) == 1, "All modules should have same width"
        assert len(module_heights) == 1, "All modules should have same height"

        # Width and height should be equal (square modules)
        assert module_widths == module_heights, "Modules should be square"

    def test_qr_code_generation_creates_valid_matrix(self, sample_qr_bill):
        """Test that QR code generation creates a valid matrix."""
        qr = sample_qr_bill.generate_qr_code()
        matrix = qr.get_matrix()

        # QR code should have a square matrix
        assert len(matrix) > 0, "QR matrix should not be empty"
        assert len(matrix) == len(matrix[0]), "QR matrix should be square"

        # QR code should be at least version 1 (21x21)
        assert len(matrix) >= 21, f"QR matrix too small: {len(matrix)}x{len(matrix)}"

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
        """Test that QR modules are positioned within the 46x46mm bounds."""
        svg_string = sample_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        # Find black modules
        rects = qr_code_svg.findall("svg:rect", SVG_NS)
        black_modules = [r for r in rects if r.get("fill") == "black"]

        for module in black_modules:
            x = module.get("x")
            y = module.get("y")

            # Extract numeric value (remove 'mm' suffix)
            x_val = float(x.replace("mm", ""))
            y_val = float(y.replace("mm", ""))

            # Modules should be positioned within 0-46mm range
            assert 0 <= x_val < 46, f"Module x position {x_val} out of bounds"
            assert 0 <= y_val < 46, f"Module y position {y_val} out of bounds"
