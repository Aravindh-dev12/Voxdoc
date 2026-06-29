from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch

from evidra.api import create_app
from evidra.pipeline import rightnow_inference, settings


def test_providers_endpoint(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'providers.db'}")
    with TestClient(app) as client:
        res = client.get("/api/providers")
        assert res.status_code == 200
        data = res.json()
        assert "supported" in data
        names = [p["name"] for p in data["supported"]]
        assert "rightnow" in names
        assert "openai" in names
        assert "transformers" in names
        assert "extractive" in names


def test_rightnow_inference_with_mock(monkeypatch):
    monkeypatch.setenv("RIGHTNOW_API_KEY", "test-mock-key")
    evidence = [{"id": "1", "locator": "Section 1", "text": "Employees get 24 days leave."}]

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"answer": "Employees receive 24 days leave each year.", "citations": [1]}'
                }
            }
        ]
    }

    with patch("httpx.post", return_value=mock_response) as mock_post:
        result = rightnow_inference(
            "How many days leave?",
            evidence=evidence,
            guarded=True,
            api_key="test-mock-key",
        )
        assert "24 days" in result["answer"]
        assert 1 in result["citations"]
        assert mock_post.called
        headers = mock_post.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-mock-key"
