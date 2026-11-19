from typing import List, Dict, Any
from collections import defaultdict
from utils.helpers import get_val

class LocationTracker:
    """Tracks locations, scene occupancy, character journeys, and transitions across scenes."""

    @classmethod
    def track_locations(cls, scenes: List[Any]) -> Dict[str, Any]:
        """Builds structured location history and character journey paths."""
        location_scenes = defaultdict(list)
        character_journeys = defaultdict(list)
        transitions = []

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            loc = (get_val(scene, "location_name", "UNKNOWN") or "UNKNOWN").strip()
            int_ext = get_val(scene, "int_ext", "INT") or "INT"
            chars = get_val(scene, "characters_present", []) or []
            time_ref = get_val(scene, "time_reference") or get_val(scene, "time_of_day", "DAY")

            location_scenes[loc].append({
                "scene_number": s_num,
                "int_ext": int_ext,
                "characters": chars,
                "time_reference": time_ref
            })

            # Record each character's location in this scene
            for c in chars:
                c_clean = str(c).strip().upper()
                character_journeys[c_clean].append({
                    "scene_number": s_num,
                    "location": loc,
                    "int_ext": int_ext,
                    "time_reference": time_ref
                })

            # Record scene transition
            prev_loc = get_val(scenes[idx - 1], "location_name", "UNKNOWN") if idx > 0 else "START"
            transitions.append({
                "scene_number": s_num,
                "from_location": prev_loc,
                "to_location": loc,
                "characters": chars,
                "transition_evidence": get_val(scene, "heading", "")
            })

        # Summarize unique locations
        unique_locations = []
        for loc_name, appearances in location_scenes.items():
            all_chars = set()
            for app in appearances:
                all_chars.update(app["characters"])
            unique_locations.append({
                "location_name": loc_name,
                "scene_count": len(appearances),
                "scenes": [a["scene_number"] for a in appearances],
                "visitors": list(all_chars)
            })

        unique_locations.sort(key=lambda x: x["scene_count"], reverse=True)

        return {
            "unique_locations": unique_locations,
            "character_journeys": dict(character_journeys),
            "transitions": transitions
        }
