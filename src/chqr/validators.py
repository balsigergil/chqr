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


def _validate_iban_checksum(iban: str) -> bool:
    """Validate IBAN checksum using MOD97 algorithm.

    Args:
        iban: The IBAN to validate (without spaces)

    Returns:
        True if checksum is valid, False otherwise
    """
    # Move first 4 characters to the end
    rearranged = iban[4:] + iban[:4]

    # Replace letters with numbers (A=10, B=11, ..., Z=35)
    numeric_string = ""
    for char in rearranged:
        if char.isdigit():
            numeric_string += char
        else:
            # Convert letter to number (A=10, B=11, etc.)
            numeric_string += str(ord(char) - ord("A") + 10)

    # Calculate MOD97
    return int(numeric_string) % 97 == 1


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

    # Validate checksum using MOD97
    if not _validate_iban_checksum(iban_clean):
        raise ValidationError("IBAN checksum is invalid")


def validate_reference_type(account: str, reference_type: str) -> None:
    """Validate that reference type matches account type.

    Args:
        account: The IBAN or QR-IBAN
        reference_type: The reference type (QRR, SCOR, or NON)

    Raises:
        ValidationError: If reference type doesn't match account type
    """
    # Check if QR-IBAN
    if is_qr_iban(account):
        # QR-IBAN must use QRR reference type
        if reference_type != "QRR":
            raise ValidationError(
                f"QR-IBAN must use QRR reference type, got {reference_type}"
            )
    else:
        # Regular IBAN cannot use QRR reference type
        if reference_type == "QRR":
            raise ValidationError(
                "Regular IBAN cannot use QRR reference type. Use SCOR or NON instead"
            )


def _calculate_mod10_recursive_check_digit(reference: str) -> int:
    """Calculate Modulo 10 recursive check digit.

    Args:
        reference: The 26-digit reference number (without check digit)

    Returns:
        The calculated check digit (0-9)
    """
    # Modulo 10 recursive lookup table
    table = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]

    carry = 0
    for digit in reference:
        carry = table[(carry + int(digit)) % 10]

    # The check digit is (10 - carry) % 10
    return (10 - carry) % 10


def validate_creditor_reference(reference: str) -> None:
    """Validate Creditor Reference (ISO 11649) format.

    Args:
        reference: The Creditor Reference to validate

    Raises:
        ValidationError: If Creditor Reference is invalid
    """
    if not reference:
        raise ValidationError("Creditor Reference is required for SCOR reference type")

    # Must start with RF
    if not reference.upper().startswith("RF"):
        raise ValidationError("Creditor Reference must start with 'RF'")

    # Must be 5-25 characters
    if len(reference) < 5 or len(reference) > 25:
        raise ValidationError(
            f"Creditor Reference must be between 5 and 25 characters, got {len(reference)}"
        )

    # Must be alphanumeric
    if not reference.isalnum():
        raise ValidationError("Creditor Reference must be alphanumeric")


def validate_qr_reference(reference: str) -> None:
    """Validate QR reference format.

    Args:
        reference: The QR reference to validate

    Raises:
        ValidationError: If QR reference is invalid
    """
    if not reference:
        raise ValidationError("QR reference is required for QRR reference type")

    # Must be numeric only
    if not reference.isdigit():
        raise ValidationError("QR reference must be numeric only")

    # Must be exactly 27 characters
    if len(reference) != 27:
        raise ValidationError(
            f"QR reference must be exactly 27 digits, got {len(reference)}"
        )

    # Validate check digit (last digit) using Modulo 10 recursive
    reference_without_check = reference[:26]
    check_digit = int(reference[26])
    expected_check_digit = _calculate_mod10_recursive_check_digit(
        reference_without_check
    )

    if check_digit != expected_check_digit:
        raise ValidationError(
            f"QR reference check digit is invalid. Expected {expected_check_digit}, got {check_digit}"
        )
