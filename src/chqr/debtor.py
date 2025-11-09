"""Ultimate debtor address information for QR-bills."""

from .validators import validate_address_field, validate_country_code


class UltimateDebtor:
    """Ultimate debtor information for a QR-bill.

    Represents the ultimate debtor (payer) with their address details.
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
        """Initialize an UltimateDebtor.

        Args:
            name: Debtor name or company (max 70 characters)
            postal_code: Postal code (max 16 characters, no country prefix)
            city: City/town name (max 35 characters)
            country: Two-character ISO 3166-1 country code
            street: Street name or P.O. Box (max 70 characters, optional)
            building_number: Building number (max 16 characters, optional)

        Raises:
            ValidationError: If any field is invalid
        """
        # Validate required fields
        validate_address_field("Name", name, 70, required=True)
        validate_address_field("Postal code", postal_code, 16, required=True)
        validate_address_field("City", city, 35, required=True)
        validate_country_code(country)

        # Validate optional fields
        validate_address_field("Street", street, 70, required=False)
        validate_address_field("Building number", building_number, 16, required=False)

        self.name = name
        self.postal_code = postal_code
        self.city = city
        self.country = country
        self.street = street or ""
        self.building_number = building_number or ""
