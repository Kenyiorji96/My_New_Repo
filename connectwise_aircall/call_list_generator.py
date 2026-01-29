"""
Call List Generator for Aircall Power Dialer.

Generates CSV files with contacts filtered by:
- Market (industry)
- Company Type
- Last call date

Output format is compatible with Aircall Power Dialer import.
"""

import csv
import os
from datetime import datetime, timedelta
from typing import Optional
from .connectwise_client import ConnectWiseClient
from .phone_formatter import get_primary_phone, format_phone_for_aircall
from .config import OutputConfig


class CallListGenerator:
    """Generates call lists from ConnectWise contacts for Aircall."""

    def __init__(self, client: Optional[ConnectWiseClient] = None):
        """
        Initialize the call list generator.

        Args:
            client: Optional ConnectWise client instance
        """
        self.client = client or ConnectWiseClient()
        self._companies_cache: dict[int, dict] = {}

    def _build_company_conditions(
        self,
        market_ids: Optional[list[int]] = None,
        company_type_ids: Optional[list[int]] = None,
    ) -> str:
        """
        Build ConnectWise conditions string for company filtering.

        Args:
            market_ids: List of market/industry IDs to filter by
            company_type_ids: List of company type IDs to filter by

        Returns:
            ConnectWise conditions query string
        """
        conditions = []

        if market_ids:
            market_conditions = " or ".join(
                f"market/id={mid}" for mid in market_ids
            )
            conditions.append(f"({market_conditions})")

        if company_type_ids:
            type_conditions = " or ".join(
                f"types/id={tid}" for tid in company_type_ids
            )
            conditions.append(f"({type_conditions})")

        return " and ".join(conditions) if conditions else ""

    def _cache_companies(
        self,
        market_ids: Optional[list[int]] = None,
        company_type_ids: Optional[list[int]] = None,
    ) -> None:
        """
        Cache companies matching the filter criteria.

        Args:
            market_ids: List of market/industry IDs
            company_type_ids: List of company type IDs
        """
        conditions = self._build_company_conditions(market_ids, company_type_ids)
        companies = self.client.get_all_companies(conditions=conditions if conditions else None)

        self._companies_cache = {
            company["id"]: company for company in companies
        }

    def _get_contact_last_call_date(self, contact_id: int) -> Optional[datetime]:
        """
        Get the last call date for a contact from activities.

        Args:
            contact_id: The contact ID

        Returns:
            Last call datetime or None if no calls found
        """
        # Query activities for this contact that are phone calls
        conditions = f"contact/id={contact_id} and type/name contains 'Call'"

        try:
            activities = self.client.get_activities(
                conditions=conditions,
                page_size=1,
            )

            if activities:
                # Get the most recent activity date
                date_str = activities[0].get("dateStart") or activities[0].get("dateEnd")
                if date_str:
                    # ConnectWise returns ISO format dates
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            # If we can't get activities, continue without last call date
            pass

        return None

    def get_filtered_contacts(
        self,
        market_ids: Optional[list[int]] = None,
        company_type_ids: Optional[list[int]] = None,
        days_since_last_call: Optional[int] = None,
        exclude_no_phone: bool = True,
    ) -> list[dict]:
        """
        Get contacts filtered by specified criteria.

        Args:
            market_ids: List of market/industry IDs to include
            company_type_ids: List of company type IDs to include
            days_since_last_call: Minimum days since last call (None = any)
            exclude_no_phone: Exclude contacts without valid phone numbers

        Returns:
            List of contact dictionaries with company info
        """
        # First, cache companies matching our criteria
        if market_ids or company_type_ids:
            self._cache_companies(market_ids, company_type_ids)
            if not self._companies_cache:
                print("No companies match the specified criteria.")
                return []

            # Build contact conditions based on company IDs
            company_ids = list(self._companies_cache.keys())
            # ConnectWise has limits on condition length, so batch if needed
            all_contacts = []

            batch_size = 100
            for i in range(0, len(company_ids), batch_size):
                batch = company_ids[i:i + batch_size]
                conditions = " or ".join(f"company/id={cid}" for cid in batch)
                contacts = self.client.get_all_contacts(conditions=f"({conditions})")
                all_contacts.extend(contacts)
        else:
            # No company filters - get all contacts
            all_contacts = self.client.get_all_contacts()

        # Filter contacts
        filtered_contacts = []
        cutoff_date = None
        if days_since_last_call is not None:
            cutoff_date = datetime.now() - timedelta(days=days_since_last_call)

        for contact in all_contacts:
            # Check phone number
            phone = get_primary_phone(contact)
            if exclude_no_phone and not phone:
                continue

            # Add formatted phone to contact
            contact["_formatted_phone"] = phone

            # Add company info from cache
            company_id = contact.get("company", {}).get("id")
            if company_id and company_id in self._companies_cache:
                contact["_company_data"] = self._companies_cache[company_id]
            elif company_id:
                # Fetch company if not in cache
                try:
                    companies = self.client.get_companies(
                        conditions=f"id={company_id}"
                    )
                    if companies:
                        contact["_company_data"] = companies[0]
                        self._companies_cache[company_id] = companies[0]
                except Exception:
                    contact["_company_data"] = {}
            else:
                contact["_company_data"] = {}

            # Check last call date filter
            if cutoff_date:
                last_call = self._get_contact_last_call_date(contact["id"])
                if last_call and last_call > cutoff_date:
                    # Called too recently, skip
                    continue
                contact["_last_call_date"] = last_call

            filtered_contacts.append(contact)

        return filtered_contacts

    def generate_csv(
        self,
        contacts: list[dict],
        filename: Optional[str] = None,
        include_company_info: bool = True,
    ) -> str:
        """
        Generate a CSV file formatted for Aircall Power Dialer.

        Aircall Power Dialer CSV format:
        - phone_number (required): E.164 format (+1XXXXXXXXXX)
        - first_name (optional)
        - last_name (optional)
        - company_name (optional)
        - email (optional)
        - Additional custom fields as needed

        Args:
            contacts: List of contact dictionaries
            filename: Output filename (auto-generated if not provided)
            include_company_info: Include company information columns

        Returns:
            Path to the generated CSV file
        """
        # Ensure output directory exists
        os.makedirs(OutputConfig.OUTPUT_DIR, exist_ok=True)

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OutputConfig.CSV_FILENAME_PREFIX}_{timestamp}.csv"

        filepath = os.path.join(OutputConfig.OUTPUT_DIR, filename)

        # Define CSV columns
        fieldnames = [
            "phone_number",
            "first_name",
            "last_name",
            "email",
        ]

        if include_company_info:
            fieldnames.extend([
                "company_name",
                "company_id",
                "market",
                "company_type",
            ])

        # Additional context fields
        fieldnames.extend([
            "contact_id",
            "title",
        ])

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for contact in contacts:
                row = {
                    "phone_number": contact.get("_formatted_phone", ""),
                    "first_name": contact.get("firstName", ""),
                    "last_name": contact.get("lastName", ""),
                    "email": contact.get("email", ""),
                    "contact_id": contact.get("id", ""),
                    "title": contact.get("title", ""),
                }

                if include_company_info:
                    company = contact.get("_company_data", {})
                    company_ref = contact.get("company", {})

                    row["company_name"] = (
                        company.get("name") or
                        company_ref.get("name", "")
                    )
                    row["company_id"] = (
                        company.get("id") or
                        company_ref.get("id", "")
                    )

                    # Market/industry
                    market = company.get("market", {})
                    row["market"] = market.get("name", "") if isinstance(market, dict) else ""

                    # Company type (first one if multiple)
                    types = company.get("types", [])
                    row["company_type"] = types[0].get("name", "") if types else ""

                writer.writerow(row)

        print(f"Generated call list: {filepath}")
        print(f"Total contacts: {len(contacts)}")

        return filepath

    def list_markets(self) -> list[dict]:
        """
        List all available markets/industries in ConnectWise.

        Returns:
            List of market dictionaries with id and name
        """
        return self.client.get_markets()

    def list_company_types(self) -> list[dict]:
        """
        List all available company types in ConnectWise.

        Returns:
            List of company type dictionaries with id and name
        """
        return self.client.get_company_types()
