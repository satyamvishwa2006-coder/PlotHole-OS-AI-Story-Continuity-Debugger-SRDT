import re
from typing import List, Dict, Any
from utils.helpers import get_val

class LogicalDetector:
    """Detects causality contradictions, impossible physical states, and factual self-contradictions."""

    DEATH_PATTERNS = [
        r'\b(?:shoots\s+([A-Za-z]{2,20})\s+dead|kills\s+([A-Za-z]{2,20})|([A-Za-z]{2,20})\s+dies in his arms|([A-Za-z]{2,20})\s+is pronounced dead|([A-Za-z]{2,20})[\'’]s lifeless body|([A-Za-z]{2,20})[^\.\n]*dead on impact)\b'
    ]

    @classmethod
    def detect(cls, scenes: List[Any], characters: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        dead_characters = {}  # char -> {"scene": int, "evidence": str}

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            content = get_val(scene, "raw_content", "") or ""
            action = get_val(scene, "action_text", "") or ""

            # 1. Check for character death
            for pat in cls.DEATH_PATTERNS:
                for match in re.finditer(pat, content, re.I):
                    killed_names = [g for g in match.groups() if g]
                    if killed_names:
                        killed_name = killed_names[0].upper()
                        if killed_name not in dead_characters:
                            dead_characters[killed_name] = {
                                "scene": s_num,
                                "evidence": match.group(0).strip()
                            }

            # 2. Check if a declared dead character acts or appears in a subsequent scene
            for char_name, death_info in dead_characters.items():
                if s_num > death_info["scene"]:
                    # Check if speaking in dialogue or present in scene/action
                    speaking = any(str(get_val(d, "character", "")).upper() == char_name for d in (get_val(scene, "dialogue_data", []) or []))
                    raw_chars = [str(c).upper() for c in (get_val(scene, "characters_present", []) or [])]
                    present = char_name in raw_chars
                    in_action = bool(re.search(rf'\b{re.escape(char_name)}\b[^\.\n]*(?:stands|enters|walks|alive|healthy|speaks|looks)', content, re.I))

                    # Ensure scene is not a flashback or hallucination
                    is_vision = bool(re.search(r'\b(?:FLASHBACK|HALLUCINATION|GHOST|MEMORY|DREAM)\b', get_val(scene, "heading", "") + " " + content, re.I))

                    if (speaking or present or in_action) and not is_vision:
                        issues.append({
                            "issue_id": f"LOG{issue_count:03d}",
                            "issue_type": "Logical Contradiction",
                            "title": f"Post-Mortem Character Appearance: {char_name} (Scene {death_info['scene']} vs Scene {s_num})",
                            "description": (
                                f"{char_name} was killed or pronounced dead in Scene {death_info['scene']}, "
                                f"but reappears active and speaking in Scene {s_num} without explanation or supernatural framework."
                            ),
                            "severity": "Critical",
                            "confidence": 0.98,
                            "scene_references": [death_info["scene"], s_num],
                            "evidence": [
                                {"scene_number": death_info["scene"], "text": death_info["evidence"]},
                                {"scene_number": s_num, "text": f"{char_name} present and active in Scene {s_num}"}
                            ],
                            "reasoning": (
                                f"Biological finality is breached. Unless the story features cloning, necromancy, or an explicit faked death, "
                                f"a deceased character cannot walk onto the set in Scene {s_num}."
                            ),
                            "suggested_fix": (
                                f"Clarify in Scene {death_info['scene']} that the character was only incapacitated or unconscious, "
                                f"or label Scene {s_num} as a flashback or visionary memory."
                            )
                        })
                        issue_count += 1
                        # Remove from dead_characters to prevent redundant alerts
                        del dead_characters[char_name]
                        break

        return issues
