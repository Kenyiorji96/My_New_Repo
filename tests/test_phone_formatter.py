"""
Unit tests for the phone number formatter.

Run with: pytest tests/ -v
"""

import pytest
from connectwise_aircall.phone_formatter import (
    format_phone_for_aircall,
    is_valid_phone,
    extract_all_phones,
    get_primary_phone,
)


class TestFormatPhoneForAircall:
    """Tests for the format_phone_for_aircall function."""

    def test_standard_parentheses_format(self):
        """Test ConnectWise standard format: (555) 123-4567"""
        assert format_phone_for_aircall("(555) 123-4567") == "+15551234567"

    def test_dashes_only_format(self):
        """Test dash-separated format: 555-123-4567"""
        assert format_phone_for_aircall("555-123-4567") == "+15551234567"

    def test_dots_format(self):
        """Test dot-separated format: 555.123.4567"""
        assert format_phone_for_aircall("555.123.4567") == "+15551234567"

    def test_digits_only(self):
        """Test plain digits: 5551234567"""
        assert format_phone_for_aircall("5551234567") == "+15551234567"

    def test_with_country_code_plus(self):
        """Test with +1 country code: +1 (555) 123-4567"""
        assert format_phone_for_aircall("+1 (555) 123-4567") == "+15551234567"

    def test_with_country_code_no_plus(self):
        """Test with 1 prefix: 1-555-123-4567"""
        assert format_phone_for_aircall("1-555-123-4567") == "+15551234567"

    def test_eleven_digits_starting_with_one(self):
        """Test 11-digit number starting with 1"""
        assert format_phone_for_aircall("15551234567") == "+15551234567"

    def test_spaces_format(self):
        """Test space-separated: 555 123 4567"""
        assert format_phone_for_aircall("555 123 4567") == "+15551234567"

    def test_mixed_format(self):
        """Test mixed separators: (555) 123.4567"""
        assert format_phone_for_aircall("(555) 123.4567") == "+15551234567"

    def test_empty_string(self):
        """Test empty string returns None"""
        assert format_phone_for_aircall("") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert format_phone_for_aircall(None) is None

    def test_whitespace_only(self):
        """Test whitespace-only returns None"""
        assert format_phone_for_aircall("   ") is None

    def test_seven_digit_local_number(self):
        """Test 7-digit local number returns None (incomplete)"""
        assert format_phone_for_aircall("123-4567") is None

    def test_letters_in_phone_returns_none(self):
        """Test vanity numbers with letters return None (incomplete after stripping)"""
        # "555-ABC-4567" becomes "5554567" (7 digits) which is too short
        assert format_phone_for_aircall("555-ABC-4567") is None

    def test_extension_included_in_digits(self):
        """Test phone with extension - extension digits get included (known limitation)"""
        # Note: extensions get included, resulting in >10 digits treated as international
        # In practice, ConnectWise rarely stores extensions this way
        result = format_phone_for_aircall("(555) 123-4567 x123")
        assert result == "+5551234567123"  # 13 digits, no +1 added

    def test_international_number(self):
        """Test international number with +"""
        assert format_phone_for_aircall("+44 20 7123 4567") == "+442071234567"

    def test_leading_trailing_whitespace(self):
        """Test whitespace is trimmed"""
        assert format_phone_for_aircall("  (555) 123-4567  ") == "+15551234567"


class TestIsValidPhone:
    """Tests for the is_valid_phone function."""

    def test_valid_phone(self):
        """Test valid phone returns True"""
        assert is_valid_phone("(555) 123-4567") is True

    def test_invalid_phone(self):
        """Test invalid phone returns False"""
        assert is_valid_phone("123") is False

    def test_empty_phone(self):
        """Test empty phone returns False"""
        assert is_valid_phone("") is False

    def test_none_phone(self):
        """Test None returns False"""
        assert is_valid_phone(None) is False


class TestExtractAllPhones:
    """Tests for the extract_all_phones function."""

    def test_contact_with_communication_items(self):
        """Test extracting phones from communicationItems"""
        contact = {
            "id": 1,
            "firstName": "John",
            "communicationItems": [
                {
                    "type": {"name": "Direct Phone"},
                    "value": "(555) 123-4567",
                },
                {
                    "type": {"name": "Mobile Phone"},
                    "value": "(555) 987-6543",
                },
            ],
        }
        phones = extract_all_phones(contact)
        assert len(phones) == 2
        assert ("Direct Phone", "+15551234567") in phones
        assert ("Mobile Phone", "+15559876543") in phones

    def test_contact_with_fax_excluded(self):
        """Test that fax numbers are excluded"""
        contact = {
            "id": 1,
            "communicationItems": [
                {
                    "type": {"name": "Direct Phone"},
                    "value": "(555) 123-4567",
                },
                {
                    "type": {"name": "Fax"},
                    "value": "(555) 999-8888",
                },
            ],
        }
        phones = extract_all_phones(contact)
        assert len(phones) == 1
        assert phones[0][1] == "+15551234567"

    def test_contact_with_no_phones(self):
        """Test contact with no phone numbers"""
        contact = {
            "id": 1,
            "firstName": "John",
            "communicationItems": [],
        }
        phones = extract_all_phones(contact)
        assert phones == []

    def test_contact_with_invalid_phone(self):
        """Test that invalid phones are excluded"""
        contact = {
            "id": 1,
            "communicationItems": [
                {
                    "type": {"name": "Phone"},
                    "value": "invalid",
                },
            ],
        }
        phones = extract_all_phones(contact)
        assert phones == []


class TestGetPrimaryPhone:
    """Tests for the get_primary_phone function."""

    def test_prefers_direct_phone(self):
        """Test that direct phone is preferred"""
        contact = {
            "id": 1,
            "communicationItems": [
                {
                    "type": {"name": "Mobile Phone"},
                    "value": "(555) 111-1111",
                },
                {
                    "type": {"name": "Direct Phone"},
                    "value": "(555) 222-2222",
                },
            ],
        }
        assert get_primary_phone(contact) == "+15552222222"

    def test_falls_back_to_mobile(self):
        """Test fallback to mobile when no direct"""
        contact = {
            "id": 1,
            "communicationItems": [
                {
                    "type": {"name": "Mobile Phone"},
                    "value": "(555) 111-1111",
                },
                {
                    "type": {"name": "Other Phone"},
                    "value": "(555) 333-3333",
                },
            ],
        }
        assert get_primary_phone(contact) == "+15551111111"

    def test_returns_none_for_no_phones(self):
        """Test returns None when no phones available"""
        contact = {
            "id": 1,
            "communicationItems": [],
        }
        assert get_primary_phone(contact) is None
