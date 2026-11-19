import pytest
from unittest.mock import MagicMock, patch
from ai.nvidia_service import NvidiaNimService, GeminiService
from config.settings import settings

def test_nvidia_service_init():
    """Test NvidiaNimService initializes properly with custom and default parameters."""
    svc = NvidiaNimService(api_key="test-key-123", model="test-model", base_url="https://test.api.nvidia.com/v1")
    assert svc.api_key == "test-key-123"
    assert svc.model == "test-model"
    assert svc.base_url == "https://test.api.nvidia.com/v1"
    assert svc.is_available() is True

def test_nvidia_service_unavailable_when_no_key():
    """Test service reports unavailable when no API key is set."""
    svc = NvidiaNimService(api_key="")
    assert svc.is_available() is False
    res = svc.test_connection()
    assert res["success"] is False
    assert "not configured" in res["error"].lower()

def test_gemini_service_alias():
    """Test backward-compatible GeminiService alias maps to NvidiaNimService."""
    assert GeminiService is NvidiaNimService
    alias_svc = GeminiService(api_key="alias-key")
    assert isinstance(alias_svc, NvidiaNimService)

def test_extract_json_clean():
    """Test extracting clean JSON."""
    raw = '{"status": "ok", "count": 42}'
    res = NvidiaNimService._extract_json(raw)
    assert res == {"status": "ok", "count": 42}

def test_extract_json_markdown_fence():
    """Test extracting JSON wrapped in markdown code fence."""
    raw = "Here is the result:\n```json\n{\"issues\": [{\"id\": 1, \"title\": \"Test\"}]}\n```\nHope this helps!"
    res = NvidiaNimService._extract_json(raw)
    assert "issues" in res
    assert len(res["issues"]) == 1
    assert res["issues"][0]["title"] == "Test"

def test_extract_json_fallback_substring():
    """Test extracting JSON from text with brackets without markdown fence."""
    raw = "The analysis found: {\"success\": true, \"errors\": []} - end of analysis."
    res = NvidiaNimService._extract_json(raw)
    assert res.get("success") is True
    assert res.get("errors") == []

def test_extract_json_invalid():
    """Test extracting invalid non-JSON raises JSONDecodeError."""
    import json
    with pytest.raises(json.JSONDecodeError):
        NvidiaNimService._extract_json("Just plain non-json text with no braces.")

@patch("ai.nvidia_service.OpenAI")
def test_generate_structured_json_mock(mock_openai_class):
    """Test structured JSON generation using mocked OpenAI client."""
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # Mock chat completion response
    mock_choice = MagicMock()
    mock_choice.message.content = '{"detected_issues": [{"title": "Timeline Warping", "severity": "high"}]}'
    mock_choice.message.reasoning_content = None
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_resp

    svc = NvidiaNimService(api_key="mock-key")
    result = svc.generate_structured_json("Analyze script continuity")

    assert result["success"] is True
    data = result["data"]
    assert "detected_issues" in data
    assert data["detected_issues"][0]["title"] == "Timeline Warping"

@patch("ai.nvidia_service.OpenAI")
def test_generate_structured_json_api_error(mock_openai_class):
    """Test error handling when API call fails."""
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("Connection timeout from NIM")

    svc = NvidiaNimService(api_key="mock-key")
    result = svc.generate_structured_json("Analyze script")

    assert result["success"] is False
    assert "Connection timeout" in result["error"]
