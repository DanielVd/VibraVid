import pytest

from VibraVid.services.cinezo import client as cinezo_client


class _FakeClient:
    def __init__(self, response):
        self.response = response

    def get(self, *args, **kwargs):
        return self.response

    def close(self):
        return None


class _HtmlResponse:
    ok = True
    status_code = 200
    headers = {"content-type": "text/html; charset=utf-8"}
    text = "<!doctype html><title>Pterodactyl</title>"

    def json(self):
        raise AssertionError("json() must not be called for a non-JSON response")


class _InvalidJsonResponse:
    ok = True
    status_code = 200
    headers = {"content-type": "application/json"}
    text = "{"

    def json(self):
        raise ValueError("invalid json")


def test_get_stream_rejects_html_sources_response(monkeypatch):
    monkeypatch.setattr(
        cinezo_client,
        "create_client",
        lambda **kwargs: _FakeClient(_HtmlResponse()),
    )

    with pytest.raises(RuntimeError, match="Sources API returned non-JSON content"):
        cinezo_client.get_stream(1643768, "movie")


def test_get_stream_reports_invalid_json(monkeypatch):
    monkeypatch.setattr(
        cinezo_client,
        "create_client",
        lambda **kwargs: _FakeClient(_InvalidJsonResponse()),
    )

    with pytest.raises(RuntimeError, match="Sources API returned invalid JSON"):
        cinezo_client.get_stream(1643768, "movie")
