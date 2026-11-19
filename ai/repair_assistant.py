from typing import Dict, Any, Optional
from ai.gemini_service import GeminiService
from ai.prompts import SCENE_REPAIR_PROMPT
from utils.helpers import generate_text_diff, get_val

class RepairAssistant:
    """Generates continuity repair suggestions, alternative fixes, and rewritten scenes."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.ai = gemini_service or GeminiService()

    def generate_repair(
        self,
        issue: Any,
        original_scene_content: str,
        target_scene_number: int
    ) -> Dict[str, Any]:
        """Generates a complete story repair proposal for an identified issue."""
        raw_evidence = get_val(issue, "evidence", []) or []
        evidence_str = "\n".join([f"Scene {get_val(e, 'scene_number')}: {get_val(e, 'text')}" for e in raw_evidence])
        
        # Check if AI is available
        if self.ai.is_available():
            prompt = SCENE_REPAIR_PROMPT.format(
                issue_type=get_val(issue, "issue_type", "Continuity Error"),
                title=get_val(issue, "title", ""),
                description=get_val(issue, "description", ""),
                scene_references=str(get_val(issue, "scene_references", []) or []),
                evidence=evidence_str,
                reasoning=get_val(issue, "reasoning", ""),
                target_scene_number=target_scene_number,
                original_scene_content=original_scene_content[:2500]
            )

            result = self.ai.generate_structured_json(prompt=prompt)
            if result.get("success"):
                data = result.get("data", {})
                revised_text = data.get("revised_scene_text", original_scene_content)
                diff = generate_text_diff(original_scene_content, revised_text)

                return {
                    "success": True,
                    "explanation": data.get("explanation", get_val(issue, "description", "")),
                    "continuity_impact": data.get("continuity_impact", "Breaks logical immersion."),
                    "primary_fix": data.get("primary_fix", get_val(issue, "suggested_fix", "")),
                    "alternative_fix": data.get("alternative_fix", "Restructure earlier establishing cues."),
                    "original_scene_text": original_scene_content,
                    "revised_scene_text": revised_text,
                    "diff": diff,
                    "target_scene_number": target_scene_number,
                    "source": "Gemini AI"
                }

        # Offline / Rule-based Fallback Repair Generation
        return self._generate_rule_based_repair(issue, original_scene_content, target_scene_number)

    def _generate_rule_based_repair(
        self,
        issue: Any,
        original_scene_content: str,
        target_scene_number: int
    ) -> Dict[str, Any]:
        """Generates deterministic story repair when AI is offline or key is missing."""
        issue_type = get_val(issue, "issue_type", "")
        fix = get_val(issue, "suggested_fix", "Clarify sequence.")
        
        # Smart line-replacement based on issue type
        revised_lines = []
        for line in original_scene_content.splitlines():
            # If timeline issue and line is heading
            if "Timeline" in issue_type and (line.startswith("INT.") or line.startswith("EXT.")):
                revised_lines.append(f"{line} (FLASHBACK)")
            elif "Location" in issue_type and (line.startswith("INT.") or line.startswith("EXT.")):
                revised_lines.append(f"{line} - FOUR HOURS LATER")
            else:
                revised_lines.append(line)

        revised_text = "\n".join(revised_lines)
        diff = generate_text_diff(original_scene_content, revised_text)

        return {
            "success": True,
            "explanation": f"Continuity conflict identified: {get_val(issue, 'title')}. {get_val(issue, 'description')}",
            "continuity_impact": "Directly contradicts established narrative chronology, physics, or character knowledge.",
            "primary_fix": fix,
            "alternative_fix": "Add an establishing transition scene to bridge the spatial or temporal gap.",
            "original_scene_text": original_scene_content,
            "revised_scene_text": revised_text,
            "diff": diff,
            "target_scene_number": target_scene_number,
            "source": "Deterministic Heuristic Engine"
        }
