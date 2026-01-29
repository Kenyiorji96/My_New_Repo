"""
Phone number formatter for Aircall Power Dialer.

Converts ConnectWise phone formats to Aircall E.164 format.
ConnectWise format: (555) 123-4567
Aircall format: +15551234567
"""

import re
from typing import Optional


def format_phone_for_aircall(
    phone: Optional[str],
    default_country_code: str = "1",
) -> Optional[str]:
    """
    Convert a phone number to Aircall Power Dialer format (+1XXXXXXXXXX).

    Handles common ConnectWise phone formats:
    - (555) 123-4567
    - 555-123-4567
    - 555.123.4567
    - 5551234567
    - +1 (555) 123-4567
    - 1-555-123-4567

    Args:
        phone: Phone number in any common format
        default_country_code: Country code to use if not present (default: "1" for US)

    Returns:
        Phone number in +1XXXXXXXXXX format, or None if invalid
    """
    if not phone:
        return None

    # Remove all non-digit characters except leading +
    cleaned = phone.strip()

    # Check if it already has a country code with +
    has_plus = cleaned.startswith("+")

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", cleaned)

    if not digits_only:
        return None

    # Handle different lengths
    if len(digits_only) == 10:
        # Standard US number without country code
        return f"+{default_country_code}{digits_only}"

    elif len(digits_only) == 11 and digits_only.startswith("1"):
        # US number with country code
        return f"+{digits_only}"

    elif len(digits_only) > 10 and has_plus:
        # International number with country code
        return f"+{digits_only}"

    elif len(digits_only) == 7:
        # Local number without area code - cannot use for Aircall
        return None

    else:
        # Try to make sense of it - if 11+ digits, assume country code included
        if len(digits_only) >= 11:
            return f"+{digits_only}"
        else:
            # Too short or invalid
            return None


def is_valid_phone(phone: Optional[str]) -> bool:
    """
    Check if a phone number can be formatted for Aircall.

    Args:
        phone: Phone number to validate

    Returns:
        True if the number can be formatted, False otherwise
    """
    return format_phone_for_aircall(phone) is not None


def extract_all_phones(contact: dict) -> list[tuple[str, str]]:
    """
    Extract all phone numbers from a ConnectWise contact.

    Args:
        contact: ConnectWise contact dictionary

    Returns:
        List of (phone_type, formatted_phone) tuples
    """
    phones = []

    # Common phone fields in ConnectWise contacts
    phone_fields = [
        ("communicationItems", None),  # Special handling for communication items
        ("defaultPhoneNbr", "Default"),
    ]

    # Handle direct phone fields
    for field, label in phone_fields:
        if field == "communicationItems":
            continue
        if field in contact and contact[field]:
            formatted = format_phone_for_aircall(contact[field])
            if formatted:
                phones.append((label, formatted))

    # Handle communication items (where phones are typically stored)
    if "communicationItems" in contact:
        for item in contact.get("communicationItems", []):
            comm_type = item.get("type", {})
            type_name = comm_type.get("name", "") if isinstance(comm_type, dict) else str(comm_type)

            # Look for phone-related communication types
            if any(keyword in type_name.lower() for keyword in ["phone", "mobile", "cell", "direct", "fax"]):
                # Skip fax numbers
                if "fax" in type_name.lower():
                    continue

                value = item.get("value", "")
                formatted = format_phone_for_aircall(value)
                if formatted:
                    phones.append((type_name, formatted))

    return phones


def get_primary_phone(contact: dict) -> Optional[str]:
    """
    Get the primary/best phone number from a ConnectWise contact.

    Priority:
    1. Default phone if marked as default
    2. Direct phone
    3. Mobile/Cell phone
    4. Any other phone

    Args:
        contact: ConnectWise contact dictionary

    Returns:
        Best formatted phone number, or None if no valid phone found
    """
    all_phones = extract_all_phones(contact)

    if not all_phones:
        return None

    # Priority order for phone types
    priority_keywords = ["default", "direct", "mobile", "cell", "phone"]

    for keyword in priority_keywords:
        for phone_type, phone_number in all_phones:
            if keyword in phone_type.lower():
                return phone_number

    # Return first available if no priority match
    return all_phones[0][1] if all_phones else None
