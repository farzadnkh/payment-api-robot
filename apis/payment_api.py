"""Payment API – HTTP and JSON handling.

Provides Robot keywords for calling the payment endpoint and parsing responses.
Follows a clear separation: this module handles transport/parsing; validation lives in steps/.
"""

import json
from typing import Any

import requests
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


class PaymentAPI:
    """Robot library for payment API: HTTP calls and JSON parsing."""

    def __init__(self, base_url: str = "http://localhost:8080") -> None:
        """Initialize with configurable base URL.

        Args:
            base_url: API base URL (default: http://localhost:8080).
        """
        self.base_url = base_url.rstrip("/")

    def ensure_server_available(self) -> None:
        """Verify mock server is reachable. Raises AssertionError with clear message if not."""
        try:
            requests.get(
                f"{self.base_url}/payment/",
                params={"CellNumber": "09123456789", "scenario": "s1"},
                timeout=3,
            )
        except requests.exceptions.ConnectionError:
            raise AssertionError(
                "Mock server is not running. Start it first: python mock_server.py"
            ) from None
        except requests.exceptions.Timeout:
            raise AssertionError(
                f"Mock server at {self.base_url} did not respond within 3 seconds."
            ) from None

    def get_payment_methods(self, cell_number: str = "09123456789") -> dict:
        """GET /payment/ with CellNumber. Returns parsed JSON or raises.

        Args:
            cell_number: User cell number for the request.

        Returns:
            Parsed JSON response as dict.
        """
        url = f"{self.base_url}/payment/"
        params = {"CellNumber": cell_number}
        logger.info(f"GET {url} params={params}")
        resp = requests.get(url, params=params, timeout=10)
        logger.info(f"Status: {resp.status_code}, Body: {resp.text[:500]}")
        resp.raise_for_status()
        return resp.json()

    def response_to_json(self, response: Any) -> dict:
        """Parse HTTP response body to JSON dict.

        Args:
            response: requests.Response (or compatible) object.

        Returns:
            Parsed JSON as dict.
        """
        return response.json()

    def get_payment_response_from_file(self, json_path: str) -> dict:
        """Load and return JSON from a file (for testdata).

        Args:
            json_path: Relative or absolute path to JSON file.

        Returns:
            Parsed JSON as dict.
        """
        path = BuiltIn().get_variable_value("${EXECDIR}") or "."
        full_path = path if json_path.startswith("/") else f"{path}/{json_path}"
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
