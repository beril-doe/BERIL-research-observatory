"""Tests for beril_cli.ov_client — the Bearer-authed OV credential exchange."""

from __future__ import annotations

import json
from unittest.mock import patch

import httpx
import pytest

from beril_cli import ov_client
from beril_cli.ov_client import OvLinkError, fetch_ov_credential


def _client_from_handler(handler):
    """Return an httpx.Client whose requests are served by ``handler``.

    ``handler`` maps (method, path) -> httpx.Response. We patch
    ``ov_client.httpx.Client`` so the module builds this mocked client but keeps
    the real headers/base-url/timeout wiring it passes in.
    """
    def _route(request: httpx.Request) -> httpx.Response:
        return handler(request.method, request.url.path, request)

    transport = httpx.MockTransport(_route)

    real_client = httpx.Client

    def _factory(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    return _factory


def _json(body: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, content=json.dumps(body).encode())


class TestFetchOvCredential:
    def test_happy_path_returns_proxy_url_and_key(self):
        calls = []

        def handler(method, path, request):
            calls.append((method, path))
            if path == "/api/ov/user":
                return _json({"created": True}, status=201)
            if path == "/api/ov/credentials":
                # Response ov_url is BERIL's INTERNAL address — must be ignored.
                return _json(
                    {"ov_url": "http://openviking:1933", "user_key": "ovk_secret"}
                )
            return _json({"detail": "unexpected"}, status=500)

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            url, key = fetch_ov_credential("https://srv", "tok")

        # URL is derived from base_url (the proxy path), NOT the response.
        assert url == "https://srv/ov"
        assert key == "ovk_secret"
        # POST /api/ov/user then GET /api/ov/credentials.
        assert ("POST", "/api/ov/user") in calls
        assert ("GET", "/api/ov/credentials") in calls

    def test_response_ov_url_is_ignored_even_if_absent(self):
        # Credentials response with no ov_url at all still works — we don't need it.
        def handler(method, path, request):
            if path == "/api/ov/user":
                return _json({"created": True}, status=201)
            return _json({"user_key": "k"})

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            url, key = fetch_ov_credential("https://beril.kbase.us", "tok")

        assert url == "https://beril.kbase.us/ov"
        assert key == "k"

    def test_sends_bearer_header(self):
        seen = {}

        def handler(method, path, request):
            seen["auth"] = request.headers.get("Authorization")
            if path == "/api/ov/user":
                return _json({}, status=201)
            return _json({"ov_url": "https://srv/ov", "user_key": "k"})

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            fetch_ov_credential("https://srv", "tok123")

        assert seen["auth"] == "Bearer tok123"

    def test_regenerate_hits_regenerate_endpoint(self):
        calls = []

        def handler(method, path, request):
            calls.append((method, path))
            if path == "/api/ov/user/regenerate":
                return _json({}, status=200)
            if path == "/api/ov/credentials":
                return _json({"ov_url": "https://srv/ov", "user_key": "fresh"})
            return _json({"detail": "unexpected"}, status=500)

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            url, key = fetch_ov_credential("https://srv", "tok", regenerate=True)

        assert key == "fresh"
        assert ("POST", "/api/ov/user/regenerate") in calls
        assert ("POST", "/api/ov/user") not in calls

    def test_409_raises_needs_regenerate(self):
        def handler(method, path, request):
            if path == "/api/ov/user":
                return _json({"detail": "already exists"}, status=409)
            return _json({}, status=500)

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            with pytest.raises(OvLinkError) as exc:
                fetch_ov_credential("https://srv", "tok")

        assert exc.value.needs_regenerate is True

    def test_401_raises_link_error(self):
        def handler(method, path, request):
            return _json({"detail": "Unauthorized"}, status=401)

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            with pytest.raises(OvLinkError) as exc:
                fetch_ov_credential("https://srv", "tok")

        assert "rejected" in str(exc.value).lower()
        assert exc.value.needs_regenerate is False

    def test_missing_key_in_credentials_raises(self):
        def handler(method, path, request):
            if path == "/api/ov/user":
                return _json({}, status=201)
            return _json({"ov_url": "https://srv/ov"})  # no user_key

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            with pytest.raises(OvLinkError) as exc:
                fetch_ov_credential("https://srv", "tok")

        assert "user_key" in str(exc.value)

    def test_transport_error_raises_link_error(self):
        def handler(method, path, request):
            raise httpx.ConnectError("connection refused", request=request)

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            with pytest.raises(OvLinkError) as exc:
                fetch_ov_credential("https://srv", "tok")

        assert "could not reach" in str(exc.value)

    def test_base_url_trailing_slash_is_stripped(self):
        seen = []

        def handler(method, path, request):
            seen.append(str(request.url))
            if path == "/api/ov/user":
                return _json({}, status=201)
            return _json({"user_key": "k"})

        with patch.object(ov_client.httpx, "Client", _client_from_handler(handler)):
            url, _ = fetch_ov_credential("https://srv/", "tok")

        # No double slash in the constructed request URLs...
        assert all("//api" not in u.replace("https://", "") for u in seen)
        # ...nor in the derived proxy URL.
        assert url == "https://srv/ov"
