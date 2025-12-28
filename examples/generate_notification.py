from decimal import Decimal
from chqr import QRBill, Creditor, UltimateDebtor


def main():
    creditor = Creditor(
        name="Service Provider AG",
        street="Business Street",
        building_number="55",
        postal_code="8000",
        city="Zurich",
        country="CH",
    )

    debtor = UltimateDebtor(
        name="Hans Muster",
        street="Village Street",
        building_number="3",
        postal_code="8055",
        city="Zurich",
        country="CH",
    )

    # Creating a notification-only QR-bill (e.g. for eBill enrollment)
    # Setting amount to 0.00 triggers the "DO NOT USE FOR PAYMENT" mode.
    # The required notification text is automatically filled if omitted.
    print("Generating notification QR-bill...")
    bill = QRBill(
        account="CH5800791123000889012",
        creditor=creditor,
        amount=Decimal("0.00"),  # Triggers notification mode
        currency="CHF",
        debtor=debtor,
        # To specify a language for the notification text, provide it explicitly:
        # additional_information="NICHT ZUR ZAHLUNG VERWENDEN"
    )

    output_filename = "notification_example.svg"
    svg = bill.generate_svg("en")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Successfully generated {output_filename}")
    print(f"- Amount: {bill.amount}")
    print(f"- Additional Info: {bill.additional_information}")


if __name__ == "__main__":
    main()
