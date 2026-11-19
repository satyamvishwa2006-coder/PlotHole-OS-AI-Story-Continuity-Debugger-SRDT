import re
from typing import List, Dict, Any
from utils.helpers import get_val

class LocationDetector:
    """Detects location continuity errors, impossible spatial teleportation, and transit discrepancies."""

    # Major distinct cities/countries
    DISTANT_LOCATIONS = ["BERLIN", "PARIS", "LONDON", "NEW YORK", "TOKYO", "MOSCOW", "CAIRO", "ROME", "LOS ANGELES"]

    @classmethod
    def detect(cls, scenes: List[Any], location_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        journeys = location_data.get("character_journeys", {}) if location_data else {}

        for char_name, history in journeys.items():
            for i in range(len(history) - 1):
                h1 = history[i]
                h2 = history[i + 1]

                s1_num = get_val(h1, "scene_number")
                s2_num = get_val(h2, "scene_number")

                loc1 = str(get_val(h1, "location", "")).upper()
                loc2 = str(get_val(h2, "location", "")).upper()

                # Check if consecutive scenes feature different distant cities
                city1 = next((city for city in cls.DISTANT_LOCATIONS if city in loc1), None)
                city2 = next((city for city in cls.DISTANT_LOCATIONS if city in loc2), None)

                if city1 and city2 and city1 != city2:
                    # Check if scenes are consecutive or have negligible time difference
                    s1 = next((s for s in (scenes or []) if get_val(s, "scene_number") == s1_num), None)
                    s2 = next((s for s in (scenes or []) if get_val(s, "scene_number") == s2_num), None)

                    # Check time difference
                    t1_str = get_val(s1, "time_reference", "") if s1 else ""
                    t2_str = get_val(s2, "time_reference", "") if s2 else ""

                    # If scene numbers are consecutive (e.g. Scene 2 and Scene 3)
                    if s2_num == s1_num + 1:
                        # Check if transit was explicitly stated (flight, hours of travel)
                        s2_raw = get_val(s2, "raw_content", "") if s2 else ""
                        has_transit = bool(re.search(r'\b(?:flight|plane|train|traveled|hours later|days later|next morning)\b', s2_raw, re.I))

                        if not has_transit:
                            issues.append({
                                "issue_id": f"LOC{issue_count:03d}",
                                "issue_type": "Location Continuity Error",
                                "title": f"Instantaneous Inter-City Teleportation: {char_name} ({city1} to {city2})",
                                "description": (
                                    f"{char_name} appears in {city1} in Scene {s1_num} ({get_val(s1, 'heading', '')}), "
                                    f"and immediately appears in {city2} in Scene {s2_num} ({get_val(s2, 'heading', '')}) "
                                    f"without any transit scene or passage of travel time."
                                ),
                                "severity": "High",
                                "confidence": 0.92,
                                "scene_references": [s1_num, s2_num],
                                "evidence": [
                                    {"scene_number": s1_num, "text": get_val(s1, "heading", "") if s1 else ""},
                                    {"scene_number": s2_num, "text": get_val(s2, "heading", "") if s2 else ""}
                                ],
                                "reasoning": (
                                    f"Travel between {city1} and {city2} requires hours of commercial or tactical transit. "
                                    f"Scene {s2_num} immediately follows Scene {s1_num} without an establishing shot, travel scene, or time-lapse transition."
                                ),
                                "suggested_fix": (
                                    f"Insert an establishing travel slugline (e.g., 'EXT. FLIGHT - NIGHT') or specify 'FOUR HOURS LATER' "
                                    f"in Scene {s2_num}'s heading."
                                )
                            })
                            issue_count += 1

                # Check for locked/trapped in location
                s1 = next((s for s in (scenes or []) if get_val(s, "scene_number") == s1_num), None)
                if s1:
                    s1_action = get_val(s1, "action_text", "") or ""
                    is_locked = bool(re.search(rf'\b{re.escape(char_name)}\b[^\.\n]*(?:locked in|trapped in|bunker doors seal|cell door slams)', s1_action, re.I))
                    if is_locked and s2_num == s1_num + 1 and loc1 != loc2:
                        issues.append({
                            "issue_id": f"LOC{issue_count:03d}",
                            "issue_type": "Location Continuity Error",
                            "title": f"Unexplained Confinement Escape: {char_name}",
                            "description": f"{char_name} is explicitly trapped/locked inside {loc1} in Scene {s1_num}, but appears freely in {loc2} in Scene {s2_num}.",
                            "severity": "Critical",
                            "confidence": 0.95,
                            "scene_references": [s1_num, s2_num],
                            "evidence": [
                                {"scene_number": s1_num, "text": f"Trapped in {loc1}"},
                                {"scene_number": s2_num, "text": f"Appears freely in {loc2}"}
                            ],
                            "reasoning": "A character explicitly locked in a secure subterranean facility cannot appear elsewhere without an escape sequence.",
                            "suggested_fix": f"Show the escape sequence, intervention, or rescue between Scene {s1_num} and Scene {s2_num}."
                        })
                        issue_count += 1

        return issues
