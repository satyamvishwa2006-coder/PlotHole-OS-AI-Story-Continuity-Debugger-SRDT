import os
import time
import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from config.settings import settings

class NvidiaNimService:
    """Centralized service for calling the NVIDIA NIM API using the OpenAI-compatible SDK.
    Provides structured JSON generation, automatic markdown fence stripping, retry handling,
    configurable model selection, and graceful offline fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        raw_key = api_key if api_key is not None else (settings.NVIDIA_API_KEY or os.environ.get("NVIDIA_API_KEY", ""))
        self.api_key = raw_key.strip()
        raw_base = base_url if base_url is not None else (settings.NVIDIA_BASE_URL or os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
        self.base_url = raw_base.strip()
        self.default_model = model or settings.DEFAULT_NVIDIA_MODEL or "minimaxai/minimax-m3.1-flash"
        self.fallback_model = settings.FALLBACK_NVIDIA_MODEL or "google/gemma-4-31b-it"
        self.client: Optional[OpenAI] = None

        if self.api_key:
            try:
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=60.0
                )
            except Exception:
                self.client = None

    @property
    def model(self) -> str:
        return self.default_model

    @model.setter
    def model(self, value: str):
        self.default_model = value

    def is_available(self) -> bool:
        """Returns True if an API key is configured and valid client instance exists."""
        return bool(self.client and self.api_key)

    def test_connection(self) -> Dict[str, Any]:
        """Tests the NVIDIA NIM API connection with a minimal prompt."""
        if not self.is_available():
            return {
                "success": False,
                "error": "NVIDIA API key is not configured. Please enter your key in Settings or .env"
            }

        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "Ping. Respond with 'PONG' only."}],
                temperature=0.1,
                max_tokens=30
            )
            msg = response.choices[0].message
            reply = (msg.content or getattr(msg, "reasoning_content", "") or "PONG").strip()
            return {
                "success": True,
                "message": reply,
                "model": self.default_model
            }
        except Exception as e:
            # Fallback to secondary model if primary experiences load or unavailability
            try:
                response = self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[{"role": "user", "content": "Ping. Respond with 'PONG' only."}],
                    temperature=0.1,
                    max_tokens=30
                )
                msg = response.choices[0].message
                reply = (msg.content or getattr(msg, "reasoning_content", "") or "PONG").strip()
                return {
                    "success": True,
                    "message": reply,
                    "model": self.fallback_model,
                    "used_fallback": True
                }
            except Exception as e2:
                # Mask key in errors
                err_msg = str(e2)
                if self.api_key:
                    err_msg = err_msg.replace(self.api_key, "***KEY***")
                return {
                    "success": False,
                    "error": f"NVIDIA NIM API connection failed: {err_msg}"
                }

    def generate_structured_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Calls NVIDIA NIM with system instructions and enforces structured JSON output parsing."""
        if not self.is_available():
            return {"success": False, "error": "NVIDIA API key not configured."}

        target_model = model or self.default_model
        sys_msg = system_prompt or system_instruction or "You are a professional screenplay script doctor and continuity analyst. You must return valid JSON only."

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]

        max_retries = 3
        backoff = 1.5

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                choice = response.choices[0]
                msg = choice.message
                raw_text = (msg.content or getattr(msg, "reasoning_content", "") or "").strip()

                if not raw_text:
                    raise ValueError("Empty response received from NVIDIA NIM.")

                # Extract JSON from potential markdown code fences or narrative wrapping
                parsed_json = self._extract_json(raw_text)
                return {
                    "success": True,
                    "data": parsed_json,
                    "raw_text": raw_text,
                    "model_used": target_model
                }

            except (RateLimitError, APITimeoutError) as e:
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"NVIDIA NIM Rate limit/timeout: {str(e)}"}
                time.sleep(backoff * (attempt + 1))
            except json.JSONDecodeError as jde:
                return {
                    "success": False,
                    "error": f"JSON Schema Validation Error: {str(jde)}",
                    "raw_text": raw_text if 'raw_text' in locals() else ""
                }
            except Exception as e:
                err_msg = str(e)
                if self.api_key:
                    err_msg = err_msg.replace(self.api_key, "***KEY***")
                return {"success": False, "error": f"NVIDIA NIM API Error: {err_msg}"}

        return {"success": False, "error": "Maximum retries exceeded."}

    @staticmethod
    def _extract_json(text: str) -> Any:
        """Robustly extracts and parses JSON from raw LLM output."""
        cleaned = text.strip()

        # Handle markdown fences: ```json ... ``` or ``` ... ```
        fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, re.IGNORECASE)
        if fence_match:
            cleaned = fence_match.group(1).strip()

        # Direct JSON load attempt
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Locate outermost JSON braces { ... } or brackets [ ... ]
        obj_match = re.search(r'(\{[\s\S]*\})', cleaned)
        if obj_match:
            try:
                return json.loads(obj_match.group(1))
            except json.JSONDecodeError:
                pass

        arr_match = re.search(r'(\[[\s\S]*\])', cleaned)
        if arr_match:
            try:
                return json.loads(arr_match.group(1))
            except json.JSONDecodeError:
                pass

        # Raise decode error if extraction fails
        raise json.JSONDecodeError("Could not extract valid JSON from LLM response", text, 0)

# Backward-compatible alias
GeminiService = NvidiaNimService
