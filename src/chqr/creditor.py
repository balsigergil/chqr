"""Creditor address information for QR-bills."""


class Creditor:
    """Creditor information for a QR-bill.

    Represents the creditor (invoice issuer) with their address details.
    """

    def __init__(
        self,
        name: str,
        postal_code: str,
        city: str,
        country: str,
        street: str | None = None,
        building_number: str | None = None,
    ):
        """Initialize a Creditor.

        Args:
            name: Creditor name or company (max 70 characters)
            postal_code: Postal code (max 16 characters, no country prefix)
            city: City/town name (max 35 characters)
            country: Two-character ISO 3166-1 country code
            street: Street name or P.O. Box (max 70 characters, optional)
            building_number: Building number (max 16 characters, optional)
        """
        self.name = name
        self.postal_code = postal_code
        self.city = city
        self.country = country
        self.street = street or ""
        self.building_number = building_number or ""
