"""
ConnectWise PSA API Client.

Handles authentication and API requests to ConnectWise PSA.
"""

import requests
from typing import Optional
from .config import ConnectWiseConfig


class ConnectWiseClient:
    """Client for interacting with ConnectWise PSA API."""

    def __init__(self):
        """Initialize the ConnectWise API client."""
        if not ConnectWiseConfig.validate():
            raise ValueError("Invalid ConnectWise configuration")

        self.base_url = ConnectWiseConfig.BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

    def _get_headers(self) -> dict:
        """Build the required headers for ConnectWise API requests."""
        return {
            "Authorization": f"Basic {ConnectWiseConfig.get_auth_string()}",
            "clientId": ConnectWiseConfig.CLIENT_ID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict | list:
        """
        Make an API request to ConnectWise.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/company/contacts')
            params: Query parameters
            data: Request body for POST/PUT

        Returns:
            JSON response from the API
        """
        url = f"{self.base_url}{endpoint}"

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
        )

        response.raise_for_status()
        return response.json()

    def get_contacts(
        self,
        conditions: Optional[str] = None,
        page: int = 1,
        page_size: int = 1000,
        order_by: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> list[dict]:
        """
        Get contacts from ConnectWise PSA.

        Args:
            conditions: CW query conditions string
            page: Page number for pagination
            page_size: Number of records per page (max 1000)
            order_by: Field to order results by
            fields: Comma-separated list of fields to return

        Returns:
            List of contact dictionaries
        """
        params = {
            "page": page,
            "pageSize": page_size,
        }

        if conditions:
            params["conditions"] = conditions
        if order_by:
            params["orderBy"] = order_by
        if fields:
            params["fields"] = fields

        return self._make_request("GET", "/company/contacts", params=params)

    def get_all_contacts(
        self,
        conditions: Optional[str] = None,
        order_by: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> list[dict]:
        """
        Get all contacts, handling pagination automatically.

        Args:
            conditions: CW query conditions string
            order_by: Field to order results by
            fields: Comma-separated list of fields to return

        Returns:
            List of all matching contact dictionaries
        """
        all_contacts = []
        page = 1
        page_size = 1000

        while True:
            contacts = self.get_contacts(
                conditions=conditions,
                page=page,
                page_size=page_size,
                order_by=order_by,
                fields=fields,
            )

            if not contacts:
                break

            all_contacts.extend(contacts)

            if len(contacts) < page_size:
                break

            page += 1

        return all_contacts

    def get_companies(
        self,
        conditions: Optional[str] = None,
        page: int = 1,
        page_size: int = 1000,
    ) -> list[dict]:
        """
        Get companies from ConnectWise PSA.

        Args:
            conditions: CW query conditions string
            page: Page number for pagination
            page_size: Number of records per page

        Returns:
            List of company dictionaries
        """
        params = {
            "page": page,
            "pageSize": page_size,
        }

        if conditions:
            params["conditions"] = conditions

        return self._make_request("GET", "/company/companies", params=params)

    def get_all_companies(
        self,
        conditions: Optional[str] = None,
    ) -> list[dict]:
        """
        Get all companies, handling pagination automatically.

        Args:
            conditions: CW query conditions string

        Returns:
            List of all matching company dictionaries
        """
        all_companies = []
        page = 1
        page_size = 1000

        while True:
            companies = self.get_companies(
                conditions=conditions,
                page=page,
                page_size=page_size,
            )

            if not companies:
                break

            all_companies.extend(companies)

            if len(companies) < page_size:
                break

            page += 1

        return all_companies

    def get_activities(
        self,
        conditions: Optional[str] = None,
        page: int = 1,
        page_size: int = 1000,
    ) -> list[dict]:
        """
        Get activities (including call logs) from ConnectWise PSA.

        Args:
            conditions: CW query conditions string
            page: Page number for pagination
            page_size: Number of records per page

        Returns:
            List of activity dictionaries
        """
        params = {
            "page": page,
            "pageSize": page_size,
        }

        if conditions:
            params["conditions"] = conditions

        return self._make_request("GET", "/sales/activities", params=params)

    def get_contact_communications(
        self,
        contact_id: int,
    ) -> list[dict]:
        """
        Get communication items for a specific contact.

        Args:
            contact_id: The contact ID

        Returns:
            List of communication dictionaries
        """
        return self._make_request(
            "GET",
            f"/company/contacts/{contact_id}/communications",
        )

    def get_markets(self) -> list[dict]:
        """
        Get all market/industry types from ConnectWise.

        Returns:
            List of market dictionaries
        """
        return self._make_request("GET", "/company/marketDescriptions")

    def get_company_types(self) -> list[dict]:
        """
        Get all company types from ConnectWise.

        Returns:
            List of company type dictionaries
        """
        return self._make_request("GET", "/company/companies/types")
