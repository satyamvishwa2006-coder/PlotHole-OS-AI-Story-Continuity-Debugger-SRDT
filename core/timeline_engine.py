import re
from typing import List, Dict, Any, Optional
from utils.helpers import get_val

class TimelineEngine:
    """Manages story chronology, temporal ordering, and relative time constraints."""

    TIME_OF_DAY_ORDER = {
        "DAWN": 1,
        "MORNING": 2,
        "DAY": 3,
        "AFTERNOON": 4,
        "DUSK": 5,
        "SUNSET": 5,
        "EVENING": 6,
        "NIGHT": 7,
        "LATE NIGHT": 8
    }

    DAYS_ORDER = {
        "MONDAY": 1,
        "TUESDAY": 2,
        "WEDNESDAY": 3,
        "THURSDAY": 4,
        "FRIDAY": 5,
        "SATURDAY": 6,
        "SUNDAY": 7
    }

    @classmethod
    def parse_time_minutes(cls, time_str: str) -> Optional[int]:
        """Parses a time string like '10:00 PM' or '9:30 AM' into minutes since midnight."""
        match = re.search(r'\b(\d{1,2}):(\d{2})\s*(AM|PM)\b', time_str, re.I)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            meridiem = match.group(3).upper()
            if meridiem == "PM" and hours != 12:
                hours += 12
            elif meridiem == "AM" and hours == 12:
                hours = 0
            return hours * 60 + minutes
        return None

    @classmethod
    def analyze_timeline(cls, scenes: List[Any], events: List[Any]) -> Dict[str, Any]:
        """Builds chronological analysis and detects timeline constraints."""
        scene_timeline = []
        for idx, s in enumerate(scenes or []):
            time_ref = get_val(s, "time_reference") or get_val(s, "time_of_day", "UNKNOWN")
            minutes = cls.parse_time_minutes(time_ref)
            scene_timeline.append({
                "scene_number": get_val(s, "scene_number", idx + 1),
                "heading": get_val(s, "heading", ""),
                "location": get_val(s, "location_name", "UNKNOWN"),
                "time_reference": time_ref,
                "parsed_minutes": minutes,
                "time_of_day": get_val(s, "time_of_day", "DAY"),
                "characters": get_val(s, "characters_present", []) or []
            })

        return {
            "scene_timeline": scene_timeline,
            "events_ordered": sorted(events or [], key=lambda e: (get_val(e, "scene_number", 1), get_val(e, "chronological_order", 0))),
            "total_scenes": len(scenes or [])
        }
