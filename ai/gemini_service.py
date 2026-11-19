import os
import time
import json
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from config.settings import settings

class GeminiService:
    """Centralized service for calling the Google Gemini API with validation, retries,
    token-efficient chunking, and structured JSON parsing."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def is_available(self) -> bool:
        """Returns True if an API key is configured and valid client instance exists."""
        return bool(self.client and self.api_key and self.api_key.strip())

    def test_connection(self) -> Dict[str, Any]:
        """Tests the Gemini API connection with a minimal prompt."""
        if not self.is_available():
            return {"success": False, "error": "Gemini API key is not configured. Please enter your key in Settings or .env"}
        
        try:
            response = self.client.models.generate_content(
                model=settings.DEFAULT_GEMINI_MODEL,
                contents="Ping. Respond with 'PONG' and confirmation.",
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=30)
            )
            return {"success": True, "message": response.text.strip()}
        except Exception as e:
            # Fallback to secondary model if primary fails
            try:
                response = self.client.models.generate_content(
                    model=settings.FALLBACK_GEMINI_MODEL,
                    contents="Ping. Respond with 'PONG'.",
                    config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=30)
                )
                return {"success": True, "message": response.text.strip(), "used_fallback": True}
            except Exception as e2:
                return {"success": False, "error": f"Gemini API connection failed: {str(e2)}"}

    def generate_structured_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Calls Gemini with JSON mime-type and enforces structured output parsing."""
        if not self.is_available():
            return {"success": False, "error": "Gemini API key not configured."}

        target_model = model or settings.DEFAULT_GEMINI_MODEL
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            system_instruction=system_instruction or "You are an expert Hollywood screenplay continuity supervisor and narrative logic analyst."
        )

        last_error = ""
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config
                )
                text = response.text
                if not text:
                    raise ValueError("Empty response received from Gemini.")
                
                # Parse JSON
                parsed_data = json.loads(text)
                return {"success": True, "data": parsed_data}

            except json.JSONDecodeError as jde:
                last_error = f"JSON parsing error: {str(jde)}"
                # Attempt markdown code block stripping if enclosed in ```json ... ```
                try:
                    raw_text = response.text.strip()
                    if raw_text.startswith("```"):
                        lines = raw_text.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        parsed_data = json.loads("\n".join(lines))
                        return {"success": True, "data": parsed_data}
                except Exception:
                    pass

            except Exception as e:
                last_error = f"API Error (attempt {attempt+1}/{max_retries}): {str(e)}"
                time.sleep(2 ** attempt)  # Exponential backoff

        return {"success": False, "error": last_error}
