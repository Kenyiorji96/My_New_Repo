#!/usr/bin/env python3
"""
Demo mode for ConnectWise-Aircall integration.

Run this to test the call list generator without API credentials.
Uses sample data to demonstrate the workflow.

Usage:
    python -m connectwise_aircall.demo
"""

import os
from datetime import datetime, timedelta
from .call_list_generator import CallListGenerator
from .config import OutputConfig


# Sample data mimicking ConnectWise API responses
SAMPLE_CONTACTS = [
    {
        "id": 1001,
        "firstName": "Sarah",
        "lastName": "Johnson",
        "email": "sarah.johnson@acmehealthcare.com",
        "title": "Practice Manager",
        "company": {"id": 1, "name": "Acme Healthcare"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "(555) 123-4567"},
            {"type": {"name": "Mobile Phone"}, "value": "(555) 123-9999"},
        ],
    },
    {
        "id": 1002,
        "firstName": "Michael",
        "lastName": "Chen",
        "email": "mchen@techstartup.io",
        "title": "CTO",
        "company": {"id": 2, "name": "TechStartup Inc"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "(555) 234-5678"},
        ],
    },
    {
        "id": 1003,
        "firstName": "Emily",
        "lastName": "Rodriguez",
        "email": "emily@legalpartners.com",
        "title": "Managing Partner",
        "company": {"id": 3, "name": "Legal Partners LLP"},
        "communicationItems": [
            {"type": {"name": "Phone"}, "value": "(555) 345-6789"},
            {"type": {"name": "Fax"}, "value": "(555) 345-0000"},  # Should be excluded
        ],
    },
    {
        "id": 1004,
        "firstName": "David",
        "lastName": "Thompson",
        "email": "dthompson@financecorp.com",
        "title": "CFO",
        "company": {"id": 4, "name": "Finance Corp"},
        "communicationItems": [
            {"type": {"name": "Mobile Phone"}, "value": "555.456.7890"},
        ],
    },
    {
        "id": 1005,
        "firstName": "Lisa",
        "lastName": "Wang",
        "email": "lwang@manufacturingco.com",
        "title": "Operations Director",
        "company": {"id": 5, "name": "Manufacturing Co"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "1-555-567-8901"},
        ],
    },
    {
        "id": 1006,
        "firstName": "James",
        "lastName": "Miller",
        "email": "jmiller@retailgroup.com",
        "title": "Regional Manager",
        "company": {"id": 6, "name": "Retail Group"},
        "communicationItems": [
            {"type": {"name": "Cell Phone"}, "value": "+1 (555) 678-9012"},
        ],
    },
    {
        "id": 1007,
        "firstName": "Amanda",
        "lastName": "Davis",
        "email": "adavis@consultingfirm.com",
        "title": "Senior Consultant",
        "company": {"id": 7, "name": "Consulting Firm LLC"},
        "communicationItems": [
            {"type": {"name": "Direct Phone"}, "value": "(555) 789-0123"},
        ],
    },
    {
        "id": 1008,
        "firstName": "Robert",
        "lastName": "Brown",
        "email": "rbrown@educationinst.edu",
        "title": "IT Director",
        "company": {"id": 8, "name": "Education Institute"},
        "communicationItems": [
            {"type": {"name": "Phone"}, "value": "(555) 890-1234"},
        ],
    },
    {
        "id": 1009,
        "firstName": "No",
        "lastName": "Phone",
        "email": "nophone@example.com",
        "title": "Contact Without Phone",
        "company": {"id": 9, "name": "Example Corp"},
        "communicationItems": [],  # No phone - should be excluded
    },
    {
        "id": 1010,
        "firstName": "Invalid",
        "lastName": "Number",
        "email": "invalid@example.com",
        "title": "Bad Phone Format",
        "company": {"id": 10, "name": "Another Corp"},
        "communicationItems": [
            {"type": {"name": "Phone"}, "value": "123"},  # Invalid - too short
        ],
    },
]

SAMPLE_COMPANIES = {
    1: {"id": 1, "name": "Acme Healthcare", "market": {"id": 10, "name": "Healthcare"}, "types": [{"id": 1, "name": "Prospect"}]},
    2: {"id": 2, "name": "TechStartup Inc", "market": {"id": 20, "name": "Technology"}, "types": [{"id": 1, "name": "Prospect"}]},
    3: {"id": 3, "name": "Legal Partners LLP", "market": {"id": 30, "name": "Legal"}, "types": [{"id": 2, "name": "Customer"}]},
    4: {"id": 4, "name": "Finance Corp", "market": {"id": 40, "name": "Finance"}, "types": [{"id": 1, "name": "Prospect"}]},
    5: {"id": 5, "name": "Manufacturing Co", "market": {"id": 50, "name": "Manufacturing"}, "types": [{"id": 2, "name": "Customer"}]},
    6: {"id": 6, "name": "Retail Group", "market": {"id": 60, "name": "Retail"}, "types": [{"id": 1, "name": "Prospect"}]},
    7: {"id": 7, "name": "Consulting Firm LLC", "market": {"id": 70, "name": "Consulting"}, "types": [{"id": 3, "name": "Vendor"}]},
    8: {"id": 8, "name": "Education Institute", "market": {"id": 80, "name": "Education"}, "types": [{"id": 1, "name": "Prospect"}]},
    9: {"id": 9, "name": "Example Corp", "market": {"id": 20, "name": "Technology"}, "types": [{"id": 1, "name": "Prospect"}]},
    10: {"id": 10, "name": "Another Corp", "market": {"id": 20, "name": "Technology"}, "types": [{"id": 1, "name": "Prospect"}]},
}

SAMPLE_MARKETS = [
    {"id": 10, "name": "Healthcare"},
    {"id": 20, "name": "Technology"},
    {"id": 30, "name": "Legal"},
    {"id": 40, "name": "Finance"},
    {"id": 50, "name": "Manufacturing"},
    {"id": 60, "name": "Retail"},
    {"id": 70, "name": "Consulting"},
    {"id": 80, "name": "Education"},
]

SAMPLE_COMPANY_TYPES = [
    {"id": 1, "name": "Prospect"},
    {"id": 2, "name": "Customer"},
    {"id": 3, "name": "Vendor"},
]


class DemoClient:
    """Mock ConnectWise client for demo mode."""

    def get_all_contacts(self, conditions=None, **kwargs):
        return SAMPLE_CONTACTS

    def get_all_companies(self, conditions=None):
        return list(SAMPLE_COMPANIES.values())

    def get_companies(self, conditions=None, **kwargs):
        return list(SAMPLE_COMPANIES.values())

    def get_activities(self, **kwargs):
        return []

    def get_markets(self):
        return SAMPLE_MARKETS

    def get_company_types(self):
        return SAMPLE_COMPANY_TYPES


def run_demo():
    """Run the demo with sample data."""
    print("=" * 60)
    print("ConnectWise-Aircall Integration - DEMO MODE")
    print("=" * 60)
    print("\nThis demo uses sample data to show how the tool works.")
    print("No API credentials required.\n")

    # Create generator with demo client
    demo_client = DemoClient()
    generator = CallListGenerator(client=demo_client)

    # Manually populate the companies cache for demo
    generator._companies_cache = SAMPLE_COMPANIES

    # Show available markets
    print("Available Markets (Industries):")
    print("-" * 40)
    for market in SAMPLE_MARKETS:
        print(f"  ID: {market['id']:3d}  |  {market['name']}")

    print("\nAvailable Company Types:")
    print("-" * 40)
    for ctype in SAMPLE_COMPANY_TYPES:
        print(f"  ID: {ctype['id']:3d}  |  {ctype['name']}")

    # Generate sample call list
    print("\n" + "=" * 60)
    print("Generating Sample Call List")
    print("=" * 60)

    from .phone_formatter import get_primary_phone

    # Process contacts like the real generator would
    filtered_contacts = []
    for contact in SAMPLE_CONTACTS:
        phone = get_primary_phone(contact)
        if not phone:
            print(f"  Skipping {contact['firstName']} {contact['lastName']} - no valid phone")
            continue

        contact["_formatted_phone"] = phone
        company_id = contact.get("company", {}).get("id")
        contact["_company_data"] = SAMPLE_COMPANIES.get(company_id, {})
        filtered_contacts.append(contact)

    print(f"\nFiltered {len(filtered_contacts)} contacts with valid phone numbers")
    print(f"(Excluded {len(SAMPLE_CONTACTS) - len(filtered_contacts)} contacts without valid phones)\n")

    # Show sample of formatted data
    print("Sample Output Preview:")
    print("-" * 80)
    print(f"{'Phone':<15} {'Name':<25} {'Company':<25} {'Title'}")
    print("-" * 80)

    for contact in filtered_contacts[:5]:
        phone = contact["_formatted_phone"]
        name = f"{contact['firstName']} {contact['lastName']}"
        company = contact.get("_company_data", {}).get("name", "")
        title = contact.get("title", "")
        print(f"{phone:<15} {name:<25} {company:<25} {title}")

    if len(filtered_contacts) > 5:
        print(f"  ... and {len(filtered_contacts) - 5} more contacts")

    # Generate actual CSV
    print("\n" + "=" * 60)
    print("Generating CSV File")
    print("=" * 60)

    os.makedirs(OutputConfig.OUTPUT_DIR, exist_ok=True)
    filepath = generator.generate_csv(
        filtered_contacts,
        filename="demo_call_list.csv"
    )

    print(f"\nDemo CSV created: {filepath}")
    print("\nPhone Number Conversion Examples:")
    print("-" * 50)
    print("  (555) 123-4567  -->  +15551234567")
    print("  555.456.7890    -->  +15554567890")
    print("  1-555-567-8901  -->  +15555678901")
    print("  +1 (555) 678-9012 -> +15556789012")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Review the generated CSV file")
    print("  2. Set up your .env file with real ConnectWise credentials")
    print("  3. Run: python -m connectwise_aircall.main --list-markets")
    print("  4. Generate real call lists with your data")


if __name__ == "__main__":
    run_demo()
