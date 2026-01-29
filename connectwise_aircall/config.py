"""
Configuration module for ConnectWise PSA API credentials.

ConnectWise PSA API authentication requires:
- Company ID
- Public API Key
- Private API Key
- Client ID (for API versioning)

Set these via environment variables or a .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class ConnectWiseConfig:
    """Configuration for ConnectWise PSA API connection."""

    # API Base URL
    BASE_URL = os.getenv(
        "CW_BASE_URL",
        "https://connect.atlantic-it.net/v4_6_release/apis/3.0"
    )

    # Authentication credentials
    COMPANY_ID = os.getenv("CW_COMPANY_ID", "")
    PUBLIC_KEY = os.getenv("CW_PUBLIC_KEY", "")
    PRIVATE_KEY = os.getenv("CW_PRIVATE_KEY", "")
    CLIENT_ID = os.getenv("CW_CLIENT_ID", "")

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required = [
            ("CW_COMPANY_ID", cls.COMPANY_ID),
            ("CW_PUBLIC_KEY", cls.PUBLIC_KEY),
            ("CW_PRIVATE_KEY", cls.PRIVATE_KEY),
            ("CW_CLIENT_ID", cls.CLIENT_ID),
        ]

        missing = [name for name, value in required if not value]

        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            print("Set these as environment variables or in a .env file.")
            return False

        return True

    @classmethod
    def get_auth_string(cls) -> str:
        """
        Generate the authorization string for ConnectWise API.
        Format: companyId+publicKey:privateKey (base64 encoded)
        """
        import base64
        auth_string = f"{cls.COMPANY_ID}+{cls.PUBLIC_KEY}:{cls.PRIVATE_KEY}"
        return base64.b64encode(auth_string.encode()).decode()


class OutputConfig:
    """Configuration for output files."""

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    CSV_FILENAME_PREFIX = os.getenv("CSV_PREFIX", "aircall_list")
