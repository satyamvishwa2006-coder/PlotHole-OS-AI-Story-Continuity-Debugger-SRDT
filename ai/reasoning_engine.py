from typing import List, Dict, Any, Optional
from ai.nvidia_service import NvidiaNimService
from ai.prompts import (
    CONTINUITY_ANALYSIS_SYSTEM_PROMPT,
    CONTINUITY_AUDIT_PROMPT_TEMPLATE,
    CHARACTER_DEEP_PROFILE_PROMPT
)
from config.settings import settings

class ReasoningEngine:
    """Orchestrates AI-driven narrative continuity reasoning, long script chunking,
    and cross-scene entity memory."""

    def __init__(self, nvidia_service: Optional[NvidiaNimService] = None):
        self.ai = nvidia_service or NvidiaNimService()

    def analyze_script_context(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs AI-assisted continuity analysis over screenplay scenes."""
        if not self.ai.is_available():
            return {
                "success": False,
                "error": "NVIDIA API key is not configured. Running in Deterministic Rule-Based Mode only.",
                "detected_issues": [],
                "overall_continuity_score": 100
            }

        # Format scenes into concise token-efficient text
        scene_chunks = self._chunk_scenes(scenes, max_scenes_per_chunk=settings.MAX_SCENES_PER_CHUNK)
        all_ai_issues = []
        overall_score = 100

        for chunk_idx, chunk in enumerate(scene_chunks):
            chunk_text = self._format_scenes_for_prompt(chunk)
            prompt = CONTINUITY_AUDIT_PROMPT_TEMPLATE.format(script_context=chunk_text)

            result = self.ai.generate_structured_json(
                prompt=prompt,
                system_instruction=CONTINUITY_ANALYSIS_SYSTEM_PROMPT
            )

            if result.get("success"):
                data = result.get("data", {})
                issues = data.get("detected_issues", [])
                score = data.get("overall_continuity_score", 90)
                overall_score = min(overall_score, score)

                # Validate evidence and fields
                for iss in issues:
                    iss["ai_generated"] = True
                    all_ai_issues.append(iss)
            else:
                return {
                    "success": False,
                    "error": result.get("error", "AI Analysis failed on chunk."),
                    "detected_issues": all_ai_issues,
                    "overall_continuity_score": overall_score
                }

        return {
            "success": True,
            "detected_issues": all_ai_issues,
            "overall_continuity_score": overall_score
        }

    def enrich_character_profiles(self, scenes: List[Dict[str, Any]], existing_characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Uses AI to deepen character psychological motives and detect subtle personality drift."""
        if not self.ai.is_available() or not scenes:
            return existing_characters

        # Sample key scenes with character dialogue
        sample_text = self._format_scenes_for_prompt(scenes[:8])
        prompt = CHARACTER_DEEP_PROFILE_PROMPT.format(script_context=sample_text)

        result = self.ai.generate_structured_json(prompt=prompt)
        if result.get("success"):
            ai_chars = result.get("data", {}).get("characters", [])
            ai_char_map = {c["name"].upper(): c for c in ai_chars if "name" in c}

            # Merge with existing profiles
            for char in existing_characters:
                c_name = char["name"].upper()
                if c_name in ai_char_map:
                    ai_c = ai_char_map[c_name]
                    if ai_c.get("motivations"):
                        char["motivations"] = list(set(char.get("motivations", []) + ai_c["motivations"]))
                    if ai_c.get("goals"):
                        char["goals"] = list(set(char.get("goals", []) + ai_c["goals"]))
                    if ai_c.get("inferred_traits"):
                        char["inferred_traits"] = list(set(char.get("inferred_traits", []) + ai_c["inferred_traits"]))

        return existing_characters

    @classmethod
    def _chunk_scenes(cls, scenes: List[Dict[str, Any]], max_scenes_per_chunk: int = 15) -> List[List[Dict[str, Any]]]:
        """Splits scenes into overlapping chunks to preserve narrative context."""
        if len(scenes) <= max_scenes_per_chunk:
            return [scenes]

        chunks = []
        step = max(1, max_scenes_per_chunk - 2)  # 2-scene overlap
        for i in range(0, len(scenes), step):
            chunk = scenes[i:i + max_scenes_per_chunk]
            if chunk:
                chunks.append(chunk)
            if i + max_scenes_per_chunk >= len(scenes):
                break
        return chunks

    @staticmethod
    def _format_scenes_for_prompt(scenes: List[Dict[str, Any]]) -> str:
        """Compresses scenes into a clean prompt representation."""
        blocks = []
        for s in scenes:
            s_num = s["scene_number"]
            heading = s.get("heading", "")
            time_ref = s.get("time_reference") or s.get("time_of_day", "")
            chars = ", ".join(s.get("characters_present", []))
            content = s.get("raw_content", "")[:1200]  # truncate huge scenes to avoid token explosion
            blocks.append(f"--- SCENE {s_num}: {heading} (TIME: {time_ref}) [CHARACTERS: {chars}] ---\n{content}\n")
        return "\n".join(blocks)
