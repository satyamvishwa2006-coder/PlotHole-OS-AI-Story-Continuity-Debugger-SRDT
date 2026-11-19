import re
from typing import List, Dict, Any
from utils.helpers import get_val

class MissingTransitionDetector:
    """Detects jarring scene transitions, unresolved abrupt plot jumps, and missing narrative connective tissue."""

    @classmethod
    def detect(cls, scenes: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        if not scenes or len(scenes) < 2:
            return issues

        for i in range(len(scenes) - 1):
            s1 = scenes[i]
            s2 = scenes[i + 1]
            s1_num = get_val(s1, "scene_number", i + 1)
            s2_num = get_val(s2, "scene_number", i + 2)

            content1 = get_val(s1, "raw_content", "") or ""
            content2 = get_val(s2, "raw_content", "") or ""

            # Check if Scene 1 ends on an acute immediate crisis
            crisis_match = re.search(r'\b(?:gun pointed at|timer hits 00:|building explodes|surrounded by armed guards|thrown off the cliff)\b', content1, re.I)
            if crisis_match:
                # Check if Scene 2 begins calmly in an unrelated location without resolution
                s2_heading = get_val(s2, "heading", "") or ""
                is_casual = bool(re.search(r'\b(?:café|living room|office|park|breakfast|peaceful|sipping coffee)\b', s2_heading + " " + content2, re.I))

                if is_casual:
                    issues.append({
                        "issue_id": f"TR{issue_count:03d}",
                        "issue_type": "Missing Narrative Transition",
                        "title": f"Unresolved Immediate Crisis Transition (Scene {s1_num} to Scene {s2_num})",
                        "description": (
                            f"Scene {s1_num} culminates in an immediate life-or-death crisis ('{crisis_match.group(0)}'), "
                            f"but Scene {s2_num} abruptly transitions to a calm setting without depicting or explaining the resolution."
                        ),
                        "severity": "Medium",
                        "confidence": 0.86,
                        "scene_references": [s1_num, s2_num],
                        "evidence": [
                            {"scene_number": s1_num, "text": f"Scene ends on: {crisis_match.group(0)}"},
                            {"scene_number": s2_num, "text": s2_heading}
                        ],
                        "reasoning": (
                            f"Audiences require payoff for acute physical peril. Scene {s1_num} leaves characters in mortal danger, "
                            f"while Scene {s2_num} proceeds as if the crisis never took place."
                        ),
                        "suggested_fix": (
                            f"Show the escape or resolution sequence, or provide dialogue in Scene {s2_num} recounting how they survived the crisis."
                        )
                    })
                    issue_count += 1

        return issues
