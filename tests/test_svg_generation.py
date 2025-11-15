"""Tests for QR-bill SVG generation."""

from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from chqr import QRBill, Creditor, UltimateDebtor


# SVG namespace
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


@pytest.fixture
def basic_qr_bill():
    """Create a basic QR-bill for testing."""
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
        additional_information="Auftrag vom 15.06.2020",
        debtor=debtor,
    )


@pytest.fixture
def reference_svg():
    """Load the reference SVG layout."""
    reference_path = Path(__file__).parent / "fixtures" / "reference_layout.xml"
    return ET.parse(reference_path)


class TestSVGStructure:
    """Test SVG document structure."""

    def test_svg_root_attributes(self, basic_qr_bill):
        """Test that root SVG element has correct attributes."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.get("width") == "210mm"
        assert root.get("height") == "105mm"
        assert "Arial" in root.get("font-family", "")

    def test_svg_has_receipt_and_payment_sections(self, basic_qr_bill):
        """Test that SVG contains both receipt and payment part sections."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Find nested SVG elements with class attributes
        receipt_svg = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        payment_svg = root.find(".//svg:svg[@class='payment']", SVG_NS)

        assert receipt_svg is not None, "Receipt section not found"
        assert payment_svg is not None, "Payment part section not found"

    def test_receipt_dimensions(self, basic_qr_bill):
        """Test receipt section has correct dimensions."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        assert receipt.get("width") == "62mm"
        assert receipt.get("height") == "105mm"
        assert receipt.get("x") == "0mm"
        assert receipt.get("y") == "0mm"

    def test_payment_part_dimensions(self, basic_qr_bill):
        """Test payment part section has correct dimensions."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        assert payment.get("width") == "148mm"
        assert payment.get("height") == "105mm"
        assert payment.get("x") == "62mm"
        assert payment.get("y") == "0mm"

    def test_separator_line(self, basic_qr_bill):
        """Test that separator line between receipt and payment part exists."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Find line element (direct child of root)
        lines = root.findall("svg:line", SVG_NS)
        separator_found = False

        for line in lines:
            if line.get("x1") == "62mm" and line.get("x2") == "62mm":
                separator_found = True
                assert line.get("y1") == "0mm"
                assert line.get("y2") == "105mm"
                break

        assert separator_found, "Separator line not found"


class TestReceiptContent:
    """Test receipt section content."""

    def test_receipt_title(self, basic_qr_bill):
        """Test receipt contains title."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Find all text elements in receipt section
        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        texts = receipt.findall(".//svg:text", SVG_NS)

        # Look for title text
        title_found = any("Receipt" in (t.text or "") for t in texts)
        assert title_found, "Receipt title not found"

    def test_receipt_has_creditor_info(self, basic_qr_bill):
        """Test receipt contains creditor information."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)

        # Get all text content
        all_text = self._get_all_text_content(receipt)

        assert "Account / Payable to" in all_text
        assert "Max Muster & Söhne" in all_text
        assert "8000 Seldwyla" in all_text

    def test_receipt_has_amount(self, basic_qr_bill):
        """Test receipt contains amount information."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        all_text = self._get_all_text_content(receipt)

        assert "Currency" in all_text
        assert "CHF" in all_text
        assert "Amount" in all_text
        assert "1 949.75" in all_text

    def test_receipt_has_reference(self, basic_qr_bill):
        """Test receipt contains payment reference."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        all_text = self._get_all_text_content(receipt)

        assert "Reference" in all_text
        # Reference should be formatted in groups
        assert "21 00000 00003 13947 14300 09017" in all_text

    def test_receipt_has_debtor(self, basic_qr_bill):
        """Test receipt contains debtor information."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        all_text = self._get_all_text_content(receipt)

        assert "Payable by" in all_text
        assert "Simon Muster" in all_text

    def test_receipt_acceptance_point(self, basic_qr_bill):
        """Test receipt has acceptance point text."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)
        all_text = self._get_all_text_content(receipt)

        assert "Acceptance point" in all_text

    def test_receipt_font_sizes(self, basic_qr_bill):
        """Test receipt uses correct font sizes."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        receipt = root.find(".//svg:svg[@class='receipt']", SVG_NS)

        # Find title
        texts = receipt.findall(".//svg:text", SVG_NS)
        title_text = [t for t in texts if "Receipt" in (t.text or "")]

        if title_text:
            assert title_text[0].get("font-size") == "11pt"

        # Find headings (should be 6pt)
        tspans = receipt.findall(".//svg:tspan", SVG_NS)
        heading_tspans = [
            t
            for t in tspans
            if t.get("font-weight") == "bold" and "Account" in (t.text or "")
        ]

        if heading_tspans:
            assert heading_tspans[0].get("font-size") == "6pt"

    @staticmethod
    def _get_all_text_content(element):
        """Extract all text content from an element and its children."""
        texts = []
        for text_elem in element.iter():
            if text_elem.text:
                texts.append(text_elem.text.strip())
            if text_elem.tail:
                texts.append(text_elem.tail.strip())
        return " ".join(texts)


class TestPaymentPartContent:
    """Test payment part section content."""

    def test_payment_part_title(self, basic_qr_bill):
        """Test payment part contains title."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        texts = payment.findall(".//svg:text", SVG_NS)

        title_found = any("Payment part" in (t.text or "") for t in texts)
        assert title_found, "Payment part title not found"

    def test_payment_part_has_qr_code(self, basic_qr_bill):
        """Test payment part contains QR code placeholder."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        qr_code_svg = payment.find(".//svg:svg[@id='qr_code_svg']", SVG_NS)

        assert qr_code_svg is not None, "QR code section not found"
        assert qr_code_svg.get("width") == "46mm"
        assert qr_code_svg.get("height") == "46mm"

    def test_payment_part_has_creditor_info(self, basic_qr_bill):
        """Test payment part contains creditor information."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        all_text = TestReceiptContent._get_all_text_content(payment)

        assert "Account / Payable to" in all_text
        assert "Max Muster & Söhne" in all_text
        assert "Musterstrasse 123" in all_text

    def test_payment_part_has_amount(self, basic_qr_bill):
        """Test payment part contains amount information."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)
        all_text = TestReceiptContent._get_all_text_content(payment)

        assert "CHF" in all_text
        assert "1 949.75" in all_text

    def test_payment_part_font_sizes(self, basic_qr_bill):
        """Test payment part uses correct font sizes."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        payment = root.find(".//svg:svg[@class='payment']", SVG_NS)

        # Find title
        texts = payment.findall(".//svg:text", SVG_NS)
        title_text = [t for t in texts if "Payment part" in (t.text or "")]

        if title_text:
            assert title_text[0].get("font-size") == "11pt"

        # Payment part headings should be 8pt, values 10pt
        tspans = payment.findall(".//svg:tspan", SVG_NS)
        heading_tspans = [
            t
            for t in tspans
            if t.get("font-weight") == "bold" and "Account" in (t.text or "")
        ]

        if heading_tspans:
            assert heading_tspans[0].get("font-size") == "8pt"


class TestIBANFormatting:
    """Test IBAN formatting in SVG output."""

    def test_iban_formatted_with_spaces(self, basic_qr_bill):
        """Test IBAN is formatted in groups of 4 characters."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # IBAN should be formatted as: CH44 3199 9123 0008 8901 2
        assert "CH44 3199 9123 0008 8901 2" in all_text


class TestReferenceFormatting:
    """Test reference formatting in SVG output."""

    def test_qr_reference_formatted_correctly(self, basic_qr_bill):
        """Test QR reference is formatted in groups of 5."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # QR reference: 21 00000 00003 13947 14300 09017
        assert "21 00000 00003 13947 14300 09017" in all_text

    def test_scor_reference_formatted_correctly(self):
        """Test SCOR reference is formatted in groups of 4."""
        creditor = Creditor(
            name="Test Company",
            street="Main Street",
            building_number="1",
            postal_code="8000",
            city="Zurich",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
            reference_type="SCOR",
            reference="RF18539007547034",
        )

        svg_string = qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # SCOR reference: RF18 5390 0754 7034
        assert "RF18 5390 0754 7034" in all_text


class TestAmountFormatting:
    """Test amount formatting in SVG output."""

    def test_amount_formatted_with_spaces(self, basic_qr_bill):
        """Test amount is formatted with space as thousands separator."""
        svg_string = basic_qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # Amount should be: 1 949.75
        assert "1 949.75" in all_text

    def test_amount_always_two_decimals(self):
        """Test amount always has exactly 2 decimal places."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("50"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        assert "50.00" in all_text


class TestConditionalElements:
    """Test conditional rendering of optional elements."""

    def test_without_amount(self):
        """Test SVG generation when amount is not provided."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        # Should have blank field for amount
        # This is implementation-specific, just verify it doesn't crash
        assert root is not None

    def test_without_debtor(self):
        """Test SVG generation when debtor is not provided."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # Should show "Payable by (name/address)" heading instead
        assert "Payable by" in all_text

    def test_without_reference(self):
        """Test SVG generation when reference is not provided."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH5800791123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
            reference_type="NON",
        )

        svg_string = qr_bill.generate_svg()
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        # Reference heading should not appear
        assert "Reference" not in all_text or all_text.count("Reference") == 0


class TestLanguageSupport:
    """Test multi-language support for headings."""

    def test_german_language(self):
        """Test SVG generation with German language."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg(language="de")
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        assert "Zahlteil" in all_text
        assert "Empfangsschein" in all_text
        assert "Konto / Zahlbar an" in all_text

    def test_french_language(self):
        """Test SVG generation with French language."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg(language="fr")
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        assert "Section paiement" in all_text
        assert "Récépissé" in all_text
        assert "Compte / Payable à" in all_text

    def test_italian_language(self):
        """Test SVG generation with Italian language."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg(language="it")
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        assert "Sezione pagamento" in all_text
        assert "Ricevuta" in all_text
        assert "Conto / Pagabile a" in all_text

    def test_english_language(self):
        """Test SVG generation with English language (default)."""
        creditor = Creditor(
            name="Test",
            street="Street",
            building_number="1",
            postal_code="8000",
            city="City",
            country="CH",
        )

        qr_bill = QRBill(
            account="CH4431999123000889012",
            creditor=creditor,
            amount=Decimal("100.00"),
            currency="CHF",
        )

        svg_string = qr_bill.generate_svg(language="en")
        root = ET.fromstring(svg_string)

        all_text = TestReceiptContent._get_all_text_content(root)

        assert "Payment part" in all_text
        assert "Receipt" in all_text
        assert "Account / Payable to" in all_text
