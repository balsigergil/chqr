"""Validation functions for QR-bill data."""

import re
from .exceptions import ValidationError


def is_qr_iban(iban: str) -> bool:
    """Check if an IBAN is a QR-IBAN.

    QR-IBANs have an IID (Institution Identifier) in the range 30000-31999.
    The IID is located at positions 4-8 (0-indexed) of the IBAN.

    Args:
        iban: The IBAN to check

    Returns:
        True if QR-IBAN, False otherwise
    """
    if len(iban) != 21:
        return False

    # Extract IID (positions 4-8, which is characters at index 4-9)
    try:
        iid = int(iban[4:9])
        return 30000 <= iid <= 31999
    except (ValueError, IndexError):
        return False


def validate_iban(iban: str) -> None:
    """Validate Swiss/Liechtenstein IBAN format.

    Args:
        iban: The IBAN to validate

    Raises:
        ValidationError: If IBAN is invalid
    """
    if not iban:
        raise ValidationError("IBAN is required")

    # Remove spaces for validation
    iban_clean = iban.replace(" ", "")

    # Check country code first (must be CH or LI)
    # This gives a clearer error for foreign IBANs
    if len(iban_clean) >= 2:
        country_code = iban_clean[:2]
        if country_code not in ("CH", "LI"):
            raise ValidationError(f"IBAN must be from CH or LI, got {country_code}")

    # Check length (specific to Swiss/Liechtenstein IBANs)
    if len(iban_clean) != 21:
        raise ValidationError(
            f"IBAN must be exactly 21 characters, got {len(iban_clean)}"
        )

    # Check format (2 letters + 19 digits)
    if not re.match(r"^[A-Z]{2}\d{19}$", iban_clean):
        raise ValidationError(
            "IBAN format invalid. Must be 2 letters followed by 19 digits"
        )
