"""Backward-compatibility module redirecting legacy GeminiService references to NvidiaNimService."""
from ai.nvidia_service import NvidiaNimService as GeminiService

__all__ = ["GeminiService"]
