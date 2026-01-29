#!/usr/bin/env python3
"""
ConnectWise PSA to Aircall Call List Generator - Phase 1A

This script generates call lists from ConnectWise PSA contacts,
formatted for import into Aircall Power Dialer.

Usage:
    python -m connectwise_aircall.main [options]

Options:
    --list-markets          List all available markets/industries
    --list-types            List all available company types
    --market-ids            Comma-separated market IDs to filter by
    --type-ids              Comma-separated company type IDs to filter by
    --days-since-call       Minimum days since last call
    --output                Output filename (optional)
    --include-no-phone      Include contacts without valid phone numbers

Examples:
    # List available markets and types
    python -m connectwise_aircall.main --list-markets
    python -m connectwise_aircall.main --list-types

    # Generate list for specific markets
    python -m connectwise_aircall.main --market-ids 1,2,3

    # Generate list for contacts not called in 30+ days
    python -m connectwise_aircall.main --days-since-call 30

    # Combined filters
    python -m connectwise_aircall.main --market-ids 1,2 --type-ids 5 --days-since-call 14
"""

import argparse
import sys
from .call_list_generator import CallListGenerator
from .config import ConnectWiseConfig


def parse_int_list(value: str) -> list[int]:
    """Parse a comma-separated string into a list of integers."""
    if not value:
        return []
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def main():
    """Main entry point for the call list generator."""
    parser = argparse.ArgumentParser(
        description="Generate Aircall call lists from ConnectWise PSA contacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # List options
    parser.add_argument(
        "--list-markets",
        action="store_true",
        help="List all available markets/industries and exit",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all available company types and exit",
    )

    # Filter options
    parser.add_argument(
        "--market-ids",
        type=str,
        default="",
        help="Comma-separated list of market IDs to filter by",
    )
    parser.add_argument(
        "--type-ids",
        type=str,
        default="",
        help="Comma-separated list of company type IDs to filter by",
    )
    parser.add_argument(
        "--days-since-call",
        type=int,
        default=None,
        help="Minimum number of days since last call",
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename (auto-generated if not specified)",
    )
    parser.add_argument(
        "--include-no-phone",
        action="store_true",
        help="Include contacts without valid phone numbers",
    )
    parser.add_argument(
        "--no-company-info",
        action="store_true",
        help="Exclude company information from output",
    )

    args = parser.parse_args()

    # Validate configuration
    if not ConnectWiseConfig.validate():
        print("\nPlease set the required environment variables:")
        print("  CW_COMPANY_ID    - Your ConnectWise company ID")
        print("  CW_PUBLIC_KEY    - Your API public key")
        print("  CW_PRIVATE_KEY   - Your API private key")
        print("  CW_CLIENT_ID     - Your API client ID")
        print("\nOr create a .env file with these values.")
        sys.exit(1)

    try:
        generator = CallListGenerator()
    except Exception as e:
        print(f"Failed to initialize ConnectWise client: {e}")
        sys.exit(1)

    # Handle list commands
    if args.list_markets:
        print("\nAvailable Markets/Industries:")
        print("-" * 40)
        markets = generator.list_markets()
        for market in markets:
            print(f"  ID: {market['id']:4d}  |  {market.get('name', 'N/A')}")
        print(f"\nTotal: {len(markets)} markets")
        return

    if args.list_types:
        print("\nAvailable Company Types:")
        print("-" * 40)
        types = generator.list_company_types()
        for ctype in types:
            print(f"  ID: {ctype['id']:4d}  |  {ctype.get('name', 'N/A')}")
        print(f"\nTotal: {len(types)} company types")
        return

    # Parse filter IDs
    market_ids = parse_int_list(args.market_ids)
    type_ids = parse_int_list(args.type_ids)

    # Show filter summary
    print("\n" + "=" * 50)
    print("ConnectWise to Aircall Call List Generator")
    print("=" * 50)
    print("\nFilter Settings:")
    print(f"  Markets:         {market_ids if market_ids else 'All'}")
    print(f"  Company Types:   {type_ids if type_ids else 'All'}")
    print(f"  Days Since Call: {args.days_since_call if args.days_since_call else 'Any'}")
    print(f"  Include No Phone: {args.include_no_phone}")
    print()

    # Get filtered contacts
    print("Fetching contacts from ConnectWise...")
    contacts = generator.get_filtered_contacts(
        market_ids=market_ids if market_ids else None,
        company_type_ids=type_ids if type_ids else None,
        days_since_last_call=args.days_since_call,
        exclude_no_phone=not args.include_no_phone,
    )

    if not contacts:
        print("No contacts match the specified criteria.")
        sys.exit(0)

    print(f"Found {len(contacts)} contacts matching criteria.\n")

    # Generate CSV
    output_path = generator.generate_csv(
        contacts=contacts,
        filename=args.output,
        include_company_info=not args.no_company_info,
    )

    print(f"\nCall list generated successfully!")
    print(f"Output file: {output_path}")
    print("\nNext steps:")
    print("  1. Open Aircall Power Dialer")
    print("  2. Import the CSV file")
    print("  3. Start dialing!")


if __name__ == "__main__":
    main()
