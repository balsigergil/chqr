from decimal import Decimal
from chqr.qr_bill import QRBill, Creditor, UltimateDebtor


def main():
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

    bill = QRBill(
        account="CH4431999123000889012",
        creditor=creditor,
        amount=Decimal("1949.75"),
        currency="CHF",
        reference_type="QRR",
        reference="210000000003139471430009017",
        additional_information="Auftrag vom 15.06.2020",
        debtor=debtor,
    )

    svg = bill.generate_svg("fr")
    with open("qr_bill.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
