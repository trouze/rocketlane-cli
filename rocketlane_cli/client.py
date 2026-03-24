"""HTTP client for the Rocketlane REST API."""

from __future__ import annotations

from typing import Any

import httpx

from .config import BASE_URL, get_api_key


class RocketlaneClient:
    """Thin wrapper around Rocketlane's REST API."""

    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        resolved = api_key or get_api_key()
        if not resolved:
            raise RuntimeError("No API key configured. Run: rocketlane add-instance")
        self._api_key = resolved
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "api-key": self._api_key,
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=30.0,
        )

    # --- low-level helpers ---------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        resp = self._http.request(method, path, params=params, json=json_body)
        if resp.status_code == 204:
            return {"status": "success"}
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise RocketlaneAPIError(resp.status_code, detail) from exc
        return resp.json()

    def get(self, path: str, **params: Any) -> Any:
        cleaned = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", path, params=cleaned or None)

    def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, json_body=body)

    def put(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return self._request("PUT", path, json_body=body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def close(self) -> None:
        self._http.close()


class RocketlaneAPIError(Exception):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")
