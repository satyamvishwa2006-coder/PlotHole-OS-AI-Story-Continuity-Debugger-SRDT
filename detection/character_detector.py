import re
from typing import List, Dict, Any
from utils.helpers import get_val

class CharacterDetector:
    """Detects character state contradictions, such as incapacitated or injured characters performing impossible physical tasks."""

    INJURY_KEYWORDS = ["shot in the", "bullet wound", "broken arm", "broken leg", "severely wounded", "unconscious", "paralyzed", "tied up", "handcuffed", "blindfolded"]
    ATHLETIC_KEYWORDS = ["hangs from", "climbs with", "sprints", "leaps across", "punches with both", "effortlessly", "scaling the wall"]

    @classmethod
    def detect(cls, scenes: List[Any], characters: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        # Track character physical state across scenes
        # char -> {"state": str, "scene": int, "excerpt": str}
        char_states = {}

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            action = get_val(scene, "action_text", "") or ""

            # Check for injuries or restraints
            for char in get_val(scene, "characters_present", []) or []:
                char_upper = str(char).upper()
                
                # Check if this character is incapacitated/injured in this scene
                for ik in cls.INJURY_KEYWORDS:
                    pat = rf'\b{re.escape(char_upper)}\b[^\.\n]*\b{ik}\b'
                    match = re.search(pat, action, re.I)
                    if match:
                        char_states[char_upper] = {
                            "injury": ik,
                            "scene": s_num,
                            "excerpt": match.group(0).strip()
                        }

                # Check if character performs athletic actions while previously injured
                if char_upper in char_states:
                    prior = char_states[char_upper]
                    if s_num > prior["scene"]:
                        # Look for contradictory athletic feats with injured limb/state
                        for ak in cls.ATHLETIC_KEYWORDS:
                            pat_act = rf'\b{re.escape(char_upper)}\b[^\.\n]*\b{ak}\b'
                            match_act = re.search(pat_act, action, re.I)
                            if match_act:
                                issues.append({
                                    "issue_id": f"CH{issue_count:03d}",
                                    "issue_type": "Character Consistency",
                                    "title": f"Physical State Inconsistency: {char_upper} (Scene {prior['scene']} vs {s_num})",
                                    "description": (
                                        f"{char_upper} suffered an incapacitating condition ('{prior['injury']}') in Scene {prior['scene']}, "
                                        f"but in Scene {s_num} performs strenuous physical action ('{ak}') without healing or medical intervention."
                                    ),
                                    "severity": "High",
                                    "confidence": 0.90,
                                    "scene_references": [prior["scene"], s_num],
                                    "evidence": [
                                        {"scene_number": prior["scene"], "text": prior["excerpt"]},
                                        {"scene_number": s_num, "text": match_act.group(0).strip()}
                                    ],
                                    "reasoning": (
                                        f"In Scene {prior['scene']}, {char_upper} is explicitly established as having a '{prior['injury']}'. "
                                        f"In Scene {s_num}, the character executes '{ak}' without any narrative bridge showing recovery, adrenaline, or splinting."
                                    ),
                                    "suggested_fix": (
                                        f"Incorporate the physical impediment into Scene {s_num} (e.g. grimacing in agony, struggling with one arm) "
                                        f"or insert a prior treatment scene."
                                    )
                                })
                                issue_count += 1
                                # Clear state after reporting to prevent duplicate cascades
                                del char_states[char_upper]
                                break

        return issues
