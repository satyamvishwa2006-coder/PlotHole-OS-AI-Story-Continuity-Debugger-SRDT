import re
from typing import List, Dict, Any
from utils.helpers import get_val

class EventExtractor:
    """Extracts narrative events from scenes, linking them to actors, times, and scene numbers."""

    KEY_ACTION_VERBS = [
        "discovers", "finds", "kills", "murders", "destroys", "burns", "steals", "takes",
        "gives", "hands", "shoots", "enters", "escapes", "confronts", "reveals", "opens",
        "locks", "hides", "arrests", "swears", "promises", "demands", "agrees", "refuses"
    ]

    @classmethod
    def extract_events(cls, scenes: List[Any]) -> List[Dict[str, Any]]:
        events = []
        event_counter = 1

        for idx, scene in enumerate(scenes):
            s_num = get_val(scene, "scene_number", idx + 1)
            loc = get_val(scene, "location_name", "UNKNOWN")
            time_ref = get_val(scene, "time_reference") or get_val(scene, "time_of_day", "DAY")
            action = get_val(scene, "action_text", "")
            chars_present = get_val(scene, "characters_present", []) or []

            # Extract major action sentences
            sentences = re.split(r'(?<=[.!?])\s+', action)
            for s in sentences:
                s_clean = s.strip()
                if not s_clean:
                    continue

                # Check if sentence contains any key action verb or character name
                has_key_verb = any(re.search(r'\b' + verb, s_clean, re.I) for verb in cls.KEY_ACTION_VERBS)
                actors_in_sentence = [c for c in chars_present if re.search(r'\b' + re.escape(c) + r'\b', s_clean, re.I)]

                if has_key_verb or actors_in_sentence or len(s_clean) > 40:
                    events.append({
                        "event_id": f"EV{event_counter:03d}",
                        "scene_number": s_num,
                        "characters_involved": actors_in_sentence or chars_present[:2],
                        "description": s_clean[:180],
                        "time_reference": time_ref,
                        "location": loc,
                        "related_events": [],
                        "source_evidence": f"Scene {s_num}: \"{s_clean}\"",
                        "chronological_order": event_counter
                    })
                    event_counter += 1

            # If no sentences found in action, create a summary event from dialogue or heading
            if not any(e["scene_number"] == s_num for e in events):
                events.append({
                    "event_id": f"EV{event_counter:03d}",
                    "scene_number": s_num,
                    "characters_involved": chars_present[:2],
                    "description": f"Occurrences at {loc} ({time_ref})",
                    "time_reference": time_ref,
                    "location": loc,
                    "related_events": [],
                    "source_evidence": f"Scene {s_num} Heading: {scene.get('heading', '')}",
                    "chronological_order": event_counter
                })
                event_counter += 1

        return events
