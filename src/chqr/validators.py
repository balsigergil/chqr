"""Validation functions for QR-bill data."""

import re
from decimal import Decimal
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


def validate_currency(currency: str) -> None:
    """Validate currency code.

    Only CHF and EUR are allowed for Swiss QR-bills.

    Args:
        currency: The currency code to validate

    Raises:
        ValidationError: If currency is not CHF or EUR
    """
    if not currency:
        raise ValidationError("Currency is required")

    if currency not in ("CHF", "EUR"):
        raise ValidationError(f"Currency must be CHF or EUR, got {currency}")


def validate_amount(amount: Decimal | None, currency: str) -> None:
    """Validate payment amount.

    Amount must be:
    - Between 0.01 and 999,999,999.99 for regular payments
    - 0.00 for notification-only QR-bills
    - Have exactly 2 decimal places
    - Not negative

    Args:
        amount: The amount to validate (can be None)
        currency: The currency (for context in error messages)

    Raises:
        ValidationError: If amount is invalid
    """
    # Amount is optional (can be None)
    if amount is None:
        return

    # Check for negative amounts
    if amount < 0:
        raise ValidationError(f"Amount cannot be negative, got {amount}")

    # Check decimal places (must be exactly 2)
    # We do this by checking if the amount equals itself when quantized to 2 decimals
    quantized = amount.quantize(Decimal("0.01"))
    if amount != quantized:
        raise ValidationError(
            f"Amount must have exactly 2 decimal places, got {amount}"
        )

    # Check maximum amount
    max_amount = Decimal("999999999.99")
    if amount > max_amount:
        raise ValidationError(
            f"Amount cannot exceed 999,999,999.99 {currency}, got {amount}"
        )

    # Note: 0.00 is valid for notification-only QR-bills
    # Minimum payment amount is 0.01, but we allow 0.00


def validate_address_field(
    field_name: str, value: str | None, max_length: int, required: bool = True
) -> None:
    """Validate an address field.

    Args:
        field_name: Name of the field (for error messages)
        value: The field value to validate
        max_length: Maximum allowed length
        required: Whether the field is required

    Raises:
        ValidationError: If the field is invalid
    """
    if required and not value:
        raise ValidationError(f"{field_name} is required")

    if value:
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} cannot exceed {max_length} characters, got {len(value)}"
            )
        # Validate character set
        validate_character_set(value, field_name)


def validate_country_code(country: str) -> None:
    """Validate country code.

    Must be a 2-character ISO 3166-1 code.

    Args:
        country: The country code to validate

    Raises:
        ValidationError: If country code is invalid
    """
    if not country:
        raise ValidationError("Country is required")

    if len(country) != 2:
        raise ValidationError(
            f"Country must be a 2-character ISO 3166-1 code, got {len(country)} characters"
        )

    if not country.isalpha():
        raise ValidationError("Country code must contain only letters")

    if not country.isupper():
        raise ValidationError("Country code must be uppercase")


def validate_character_set(value: str, field_name: str) -> None:
    """Validate that string contains only allowed characters for QR-bill.

    Allowed characters according to Swiss QR-bill spec (section 4.1.1):
    - Basic Latin (U+0020–U+007E)
    - Latin-1 Supplement (U+00A0–U+00FF)
    - Latin Extended-A (U+0100–U+017F)
    - Plus specific characters: Ș (U+0218), ș (U+0219), Ț (U+021A), ț (U+021B), € (U+20AC)

    Args:
        value: The string to validate
        field_name: Name of the field (for error messages)

    Raises:
        ValidationError: If string contains invalid characters
    """
    if not value:
        return

    # Define allowed Unicode ranges
    allowed_ranges = [
        (0x0020, 0x007E),  # Basic Latin
        (0x00A0, 0x00FF),  # Latin-1 Supplement
        (0x0100, 0x017F),  # Latin Extended-A
    ]

    # Additional allowed characters
    allowed_chars = {
        0x0218,  # Ș
        0x0219,  # ș
        0x021A,  # Ț
        0x021B,  # ț
        0x20AC,  # €
    }

    for char in value:
        code_point = ord(char)
        is_valid = False

        # Check if in allowed ranges
        for start, end in allowed_ranges:
            if start <= code_point <= end:
                is_valid = True
                break

        # Check if in additional allowed characters
        if code_point in allowed_chars:
            is_valid = True

        if not is_valid:
            raise ValidationError(
                f"{field_name} contains invalid character '{char}' (U+{code_point:04X}). "
                f"Only Latin characters are allowed."
            )
