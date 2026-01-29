"""
Unit tests for the call list generator with mocked API responses.

Run with: pytest tests/ -v
"""

import pytest
import os
import csv
from unittest.mock import Mock, patch, MagicMock
from connectwise_aircall.call_list_generator import CallListGenerator


# Sample mock data that mimics ConnectWise API responses
MOCK_COMPANIES = [
    {
        "id": 1,
        "name": "Acme Corp",
        "market": {"id": 10, "name": "Healthcare"},
        "types": [{"id": 5, "name": "Prospect"}],
    },
    {
        "id": 2,
        "name": "TechStart Inc",
        "market": {"id": 20, "name": "Technology"},
        "types": [{"id": 5, "name": "Prospect"}],
    },
    {
        "id": 3,
        "name": "Law Offices LLC",
        "market": {"id": 30, "name": "Legal"},
        "types": [{"id": 6, "name": "Customer"}],
    },
]

MOCK_CONTACTS = [
    {
        "id": 101,
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@acme.com",
        "title": "CEO",
        "company": {"id": 1, "name": "Acme Corp"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "(555) 111-1111"},
            {"type": {"name": "Mobile Phone"}, "value": "(555) 111-2222"},
        ],
    },
    {
        "id": 102,
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane@techstart.com",
        "title": "CTO",
        "company": {"id": 2, "name": "TechStart Inc"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "(555) 222-3333"},
        ],
    },
    {
        "id": 103,
        "firstName": "Bob",
        "lastName": "Wilson",
        "email": "bob@lawoffices.com",
        "title": "Partner",
        "company": {"id": 3, "name": "Law Offices LLC"},
        "communicationItems": [
            {"type": {"name": "Phone"}, "value": "(555) 333-4444"},
        ],
    },
    {
        "id": 104,
        "firstName": "No",
        "lastName": "Phone",
        "email": "nophone@example.com",
        "title": "Manager",
        "company": {"id": 1, "name": "Acme Corp"},
        "communicationItems": [],  # No phone number
    },
]

MOCK_MARKETS = [
    {"id": 10, "name": "Healthcare"},
    {"id": 20, "name": "Technology"},
    {"id": 30, "name": "Legal"},
    {"id": 40, "name": "Finance"},
]

MOCK_COMPANY_TYPES = [
    {"id": 5, "name": "Prospect"},
    {"id": 6, "name": "Customer"},
    {"id": 7, "name": "Vendor"},
]


@pytest.fixture
def mock_client():
    """Create a mock ConnectWise client."""
    client = Mock()

    # Mock the API methods
    client.get_all_companies.return_value = MOCK_COMPANIES
    client.get_all_contacts.return_value = MOCK_CONTACTS
    client.get_companies.return_value = MOCK_COMPANIES
    client.get_markets.return_value = MOCK_MARKETS
    client.get_company_types.return_value = MOCK_COMPANY_TYPES
    client.get_activities.return_value = []

    return client


@pytest.fixture
def generator(mock_client):
    """Create a CallListGenerator with mocked client."""
    return CallListGenerator(client=mock_client)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
        mock_config.OUTPUT_DIR = str(tmp_path)
        mock_config.CSV_FILENAME_PREFIX = "test_list"
        yield tmp_path


class TestCallListGenerator:
    """Tests for the CallListGenerator class."""

    def test_list_markets(self, generator):
        """Test listing available markets."""
        markets = generator.list_markets()
        assert len(markets) == 4
        assert markets[0]["name"] == "Healthcare"

    def test_list_company_types(self, generator):
        """Test listing company types."""
        types = generator.list_company_types()
        assert len(types) == 3
        assert types[0]["name"] == "Prospect"

    def test_get_filtered_contacts_no_filters(self, generator):
        """Test getting contacts without filters."""
        contacts = generator.get_filtered_contacts()
        # Should exclude the contact without a phone
        assert len(contacts) == 3

    def test_get_filtered_contacts_include_no_phone(self, generator):
        """Test including contacts without phone numbers."""
        contacts = generator.get_filtered_contacts(exclude_no_phone=False)
        assert len(contacts) == 4

    def test_contacts_have_formatted_phone(self, generator):
        """Test that contacts have formatted phone numbers."""
        contacts = generator.get_filtered_contacts()
        for contact in contacts:
            assert "_formatted_phone" in contact
            assert contact["_formatted_phone"].startswith("+1")

    def test_generate_csv_creates_file(self, generator, temp_output_dir):
        """Test that CSV file is created."""
        with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
            mock_config.OUTPUT_DIR = str(temp_output_dir)
            mock_config.CSV_FILENAME_PREFIX = "test"

            contacts = generator.get_filtered_contacts()
            filepath = generator.generate_csv(contacts, filename="test_output.csv")

            assert os.path.exists(filepath)

    def test_generate_csv_content(self, generator, temp_output_dir):
        """Test CSV content is correct."""
        with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
            mock_config.OUTPUT_DIR = str(temp_output_dir)
            mock_config.CSV_FILENAME_PREFIX = "test"

            contacts = generator.get_filtered_contacts()
            filepath = generator.generate_csv(contacts, filename="test_content.csv")

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 3

            # Check first row
            first_row = rows[0]
            assert first_row["phone_number"] == "+15551111111"
            assert first_row["first_name"] == "John"
            assert first_row["last_name"] == "Doe"
            assert first_row["email"] == "john@acme.com"

    def test_csv_has_required_columns(self, generator, temp_output_dir):
        """Test CSV has all required Aircall columns."""
        with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
            mock_config.OUTPUT_DIR = str(temp_output_dir)
            mock_config.CSV_FILENAME_PREFIX = "test"

            contacts = generator.get_filtered_contacts()
            filepath = generator.generate_csv(contacts, filename="test_columns.csv")

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames

            required_fields = ["phone_number", "first_name", "last_name", "email"]
            for field in required_fields:
                assert field in fieldnames

    def test_filter_by_market(self, generator, mock_client):
        """Test filtering by market ID."""
        # Setup: Only return companies with matching market
        mock_client.get_all_companies.return_value = [
            c for c in MOCK_COMPANIES if c["market"]["id"] == 10
        ]
        mock_client.get_all_contacts.return_value = [
            c for c in MOCK_CONTACTS if c["company"]["id"] == 1
        ]

        contacts = generator.get_filtered_contacts(market_ids=[10])

        # Verify companies were queried with conditions
        mock_client.get_all_companies.assert_called()


class TestCSVFormat:
    """Tests specifically for Aircall CSV format compliance."""

    def test_phone_number_format(self, generator, temp_output_dir):
        """Test phone numbers are in +1XXXXXXXXXX format."""
        with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
            mock_config.OUTPUT_DIR = str(temp_output_dir)
            mock_config.CSV_FILENAME_PREFIX = "test"

            contacts = generator.get_filtered_contacts()
            filepath = generator.generate_csv(contacts, filename="test_phones.csv")

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    phone = row["phone_number"]
                    assert phone.startswith("+1"), f"Phone {phone} should start with +1"
                    assert len(phone) == 12, f"Phone {phone} should be 12 chars (+1 + 10 digits)"
                    assert phone[1:].isdigit(), f"Phone {phone} should be all digits after +"

    def test_no_empty_phone_numbers(self, generator, temp_output_dir):
        """Test no rows have empty phone numbers."""
        with patch('connectwise_aircall.call_list_generator.OutputConfig') as mock_config:
            mock_config.OUTPUT_DIR = str(temp_output_dir)
            mock_config.CSV_FILENAME_PREFIX = "test"

            contacts = generator.get_filtered_contacts()  # exclude_no_phone=True by default
            filepath = generator.generate_csv(contacts, filename="test_no_empty.csv")

            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    assert row["phone_number"], "Phone number should not be empty"
