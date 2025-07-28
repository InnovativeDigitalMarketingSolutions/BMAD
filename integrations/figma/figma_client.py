import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

# Load .env if present (voor lokale ontwikkeling)
load_dotenv()

logger = logging.getLogger("figma_client")
logging.basicConfig(level=logging.INFO)

FIGMA_API_URL = "https://api.figma.com/v1"
FIGMA_API_TOKEN = os.getenv("FIGMA_API_TOKEN")
FIGMA_DEMO_MODE = os.getenv("FIGMA_DEMO_MODE", "false").lower() == "true"

if not FIGMA_API_TOKEN and not FIGMA_DEMO_MODE:
    logger.error("FIGMA_API_TOKEN is not set in environment variables.")


class RateLimitException(Exception):
    pass


class FigmaClient:
    def __init__(
        self, api_token: Optional[str] = None, max_retries: int = 3, backoff_factor: float = 0.5, demo_mode: bool = None
    ):
        self.demo_mode = demo_mode if demo_mode is not None else FIGMA_DEMO_MODE
        self.api_token = api_token or FIGMA_API_TOKEN

        if not self.api_token and not self.demo_mode:
            raise ValueError("Figma API token is required unless demo mode is enabled.")

        if not self.demo_mode:
            self.session = requests.Session()
            retries = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retries))
            self.session.headers.update(
                {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
            )

        self.cache: Dict[str, Any] = {}

    def _request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        if self.demo_mode:
            logger.info(f"DEMO MODE: Mocking request to {endpoint}")
            return self._get_mock_response(endpoint, params)

        url = f"{FIGMA_API_URL}{endpoint}"
        cache_key = f"{method}:{url}:{params!s}"
        # Simple in-memory cache
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self.cache[cache_key]
        for attempt in range(5):
            try:
                logger.info(f"Requesting {url} (attempt {attempt+1})")
                response = self.session.request(method, url, params=params)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    logger.warning(f"Rate limited by Figma API. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                data = response.json()
                self.cache[cache_key] = data
                return data
            except requests.RequestException as e:
                logger.error(f"HTTP error: {e}")
                if attempt == 4:
                    raise
                time.sleep(2**attempt)
        raise RateLimitException("Exceeded retry attempts for Figma API request.")

    def _get_mock_response(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Generate mock responses for demo mode."""
        if "/me" in endpoint:
            return {
                "id": "demo_user_123",
                "email": "demo@example.com",
                "name": "Demo User",
                "profile_img_url": "https://via.placeholder.com/150",
            }
        if "/files/" in endpoint:
            file_id = endpoint.split("/files/")[1]
            return {
                "document": {
                    "id": "0:0",
                    "name": f"Demo File {file_id}",
                    "type": "DOCUMENT",
                    "children": [
                        {
                            "id": "1:1",
                            "name": "Page 1",
                            "type": "CANVAS",
                            "children": [
                                {
                                    "id": "2:1",
                                    "name": "Button Component",
                                    "type": "COMPONENT",
                                    "fills": [{"type": "SOLID", "color": {"r": 0.2, "g": 0.4, "b": 0.8}}],
                                    "absoluteBoundingBox": {"x": 0, "y": 0, "width": 120, "height": 40},
                                },
                                {
                                    "id": "2:2",
                                    "name": "Text Element",
                                    "type": "TEXT",
                                    "characters": "Hello World",
                                    "style": {"fontSize": 16, "fontFamily": "Inter"},
                                },
                            ],
                        }
                    ],
                },
                "name": f"Demo Design File {file_id}",
                "version": "1.0.0",
                "lastModified": "2025-01-27T10:00:00.000Z",
                "thumbnailUrl": "https://via.placeholder.com/300x200",
            }
        if "/components" in endpoint:
            return {
                "meta": {
                    "components": {
                        "1:1": {
                            "key": "demo_component_1",
                            "name": "Button Component",
                            "description": "A demo button component",
                        },
                        "1:2": {
                            "key": "demo_component_2",
                            "name": "Card Component",
                            "description": "A demo card component",
                        },
                    }
                }
            }
        if "/comments" in endpoint:
            return {
                "comments": [
                    {
                        "id": "comment_1",
                        "message": "This is a demo comment",
                        "user": {"name": "Demo User", "id": "user_1"},
                        "created_at": "2025-01-27T10:00:00.000Z",
                    }
                ]
            }
        return {"error": "Unknown endpoint in demo mode"}

    def get_file(self, file_id: str) -> dict:
        """Haalt de volledige Figma file op (inclusief pages, document tree, styles, enz.)"""
        return self._request("GET", f"/files/{file_id}")

    def get_components(self, file_id: str) -> dict:
        """Haalt alle componenten op uit een Figma file."""
        return self._request("GET", f"/files/{file_id}/components")

    def get_comments(self, file_id: str) -> dict:
        """Haalt alle comments op uit een Figma file."""
        return self._request("GET", f"/files/{file_id}/comments")

    def get_images(self, file_id: str, ids: List[str], format: str = "svg") -> dict:
        """Haalt afbeeldingen op van nodes (bijv. componenten) in een Figma file."""
        params = {"ids": ",".join(ids), "format": format}
        return self._request("GET", f"/images/{file_id}", params=params)

    def clear_cache(self):
        self.cache.clear()


# Voorbeeld gebruik:
# client = FigmaClient()
# file_data = client.get_file("<file_id>")
# components = client.get_components("<file_id>")
# comments = client.get_comments("<file_id>")
# images = client.get_images("<file_id>", ["1:2", "3:4"])
