import re
from typing import List, Dict, Any
from core.timeline_engine import TimelineEngine
from utils.helpers import get_val

class TimelineDetector:
    """Detects chronological inconsistencies, conflicting timestamps, and impossible event sequences."""

    @classmethod
    def detect(cls, scenes: List[Any], events: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        if not scenes or len(scenes) < 2:
            return issues

        # Check pairwise consecutive or nearby scenes for explicit clock or day contradictions
        for i in range(len(scenes) - 1):
            s1 = scenes[i]
            s2 = scenes[i + 1]
            s1_num = get_val(s1, "scene_number", i + 1)
            s2_num = get_val(s2, "scene_number", i + 2)

            time1_str = get_val(s1, "time_reference") or get_val(s1, "time_of_day", "")
            time2_str = get_val(s2, "time_reference") or get_val(s2, "time_of_day", "")

            # 1. Check for explicit earlier time indicator without flashback tag
            raw2 = get_val(s2, "raw_content", "") or ""
            raw1 = get_val(s1, "raw_content", "") or ""
            earlier_match = re.search(r'\b(?:earlier|before|prior)\b', raw2, re.I)
            is_flashback = bool(re.search(r'\b(?:FLASHBACK|MEMORY|DREAM)\b', raw2, re.I))

            mins1 = TimelineEngine.parse_time_minutes(time1_str)
            mins2 = TimelineEngine.parse_time_minutes(time2_str)

            # Check if mins2 < mins1 within the same implied cycle
            if mins1 is not None and mins2 is not None:
                if mins2 < mins1 and not is_flashback:
                    # An explicit time backwards jump without marked flashback
                    excerpt1 = cls._find_excerpt(raw1, time1_str)
                    excerpt2 = cls._find_excerpt(raw2, time2_str)

                    issues.append({
                        "issue_id": f"TL{issue_count:03d}",
                        "issue_type": "Timeline Contradiction",
                        "title": f"Chronological Sequence Regression (Scene {s1_num} vs Scene {s2_num})",
                        "description": (
                            f"Scene {s2_num} is timestamped at '{time2_str}', which chronologically precedes "
                            f"Scene {s1_num}'s timestamp of '{time1_str}' without being designated as a Flashback."
                        ),
                        "severity": "High",
                        "confidence": 0.94,
                        "scene_references": [s1_num, s2_num],
                        "evidence": [
                            {"scene_number": s1_num, "text": excerpt1 or f"Scene {s1_num} timestamp: {time1_str}"},
                            {"scene_number": s2_num, "text": excerpt2 or f"Scene {s2_num} timestamp: {time2_str}"}
                        ],
                        "reasoning": (
                            f"Standard linear narrative requires sequential time progression. Scene {s1_num} takes place at {time1_str}, "
                            f"but the narrative immediately continues in Scene {s2_num} at {time2_str} without an explicit FLASHBACK slugline."
                        ),
                        "suggested_fix": (
                            f"Add a 'FLASHBACK' indicator to Scene {s2_num}'s heading, or adjust Scene {s2_num}'s timestamp to occur after {time1_str}."
                        )
                    })
                    issue_count += 1

            # 2. Check for continuous indicator contradiction
            tod2_raw = get_val(s2, "time_of_day", "") or ""
            tod1_raw = get_val(s1, "time_of_day", "DAY") or "DAY"
            if "CONTINUOUS" in tod2_raw.upper() and tod1_raw != tod2_raw:
                tod1 = tod1_raw.upper()
                tod2 = tod2_raw.upper()
                if "DAY" in tod1 and "NIGHT" in tod2:
                    issues.append({
                        "issue_id": f"TL{issue_count:03d}",
                        "issue_type": "Timeline Contradiction",
                        "title": f"Continuous Time of Day Mismatch (Scene {s1_num} to {s2_num})",
                        "description": f"Scene {s2_num} specifies CONTINUOUS transition from Scene {s1_num}, but switches between {tod1} and {tod2}.",
                        "severity": "Medium",
                        "confidence": 0.88,
                        "scene_references": [s1_num, s2_num],
                        "evidence": [
                            {"scene_number": s1_num, "text": get_val(s1, "heading", "")},
                            {"scene_number": s2_num, "text": get_val(s2, "heading", "")}
                        ],
                        "reasoning": "A scene marked CONTINUOUS occurs in immediate unbroken real-time; ambient daylight cannot instantly switch without passage of time.",
                        "suggested_fix": f"Change Scene {s2_num}'s time of day to match Scene {s1_num} ({tod1}) or replace CONTINUOUS with LATER."
                    })
                    issue_count += 1

        return issues

    @staticmethod
    def _find_excerpt(content: str, term: str) -> str:
        if not term or not content:
            return ""
        lines = content.splitlines()
        for line in lines:
            if term.lower() in line.lower():
                return line.strip()
        return lines[0].strip() if lines else ""
