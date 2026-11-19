import re
from typing import List, Dict, Any
from collections import defaultdict
from utils.helpers import get_val

class ObjectTracker:
    """Tracks physical props and objects across scenes, their handlers, ownership, and state changes."""

    # Common tracked screenplay props
    OBJECT_KEYWORDS = [
        "flash drive", "usb drive", "drive", "laptop", "phone", "gun", "revolver", "pistol",
        "rifle", "knife", "blade", "dagger", "key", "keycard", "journal", "diary", "briefcase",
        "suitcase", "necklace", "ring", "amulet", "vial", "poison", "letter", "envelope",
        "document", "dossier", "file", "tape", "cassette", "disk", "hard drive"
    ]

    DESTROY_KEYWORDS = ["destroys", "destroyed", "incinerates", "burns", "smashes", "crushes", "melts", "vaporizes"]
    GIVE_KEYWORDS = ["hands", "gives", "passes", "delivers", "tosses", "slides"]

    @classmethod
    def track_objects(cls, scenes: List[Any]) -> List[Dict[str, Any]]:
        """Identifies key objects and tracks their state and appearances across scenes."""
        tracked_objects = {}

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            content = get_val(scene, "raw_content", "") or ""
            chars_present = get_val(scene, "characters_present", []) or []

            for kw in cls.OBJECT_KEYWORDS:
                # Search for specific compound matches like "cracked titanium flash drive" or just "flash drive"
                matches = re.finditer(r'\b(?:(?:[a-z]+\s+){0,3}' + re.escape(kw) + r')\b', content, re.I)
                for m in matches:
                    matched_phrase = m.group(0).strip().lower()
                    # Normalize phrase key to key object term
                    obj_key = kw.capitalize()
                    
                    if obj_key not in tracked_objects:
                        tracked_objects[obj_key] = {
                            "name": matched_phrase.capitalize() if len(matched_phrase) > len(kw) else obj_key,
                            "first_appearance_scene": s_num,
                            "scenes_present": [],
                            "handlers": [],
                            "owner": None,
                            "status": "Intact",
                            "important_events": [],
                            "notes": ""
                        }

                    obj_data = tracked_objects[obj_key]
                    if s_num not in obj_data["scenes_present"]:
                        obj_data["scenes_present"].append(s_num)

                    # Check surrounding context for destruction
                    sentence_context = cls._get_surrounding_sentence(content, m.start())
                    if any(dk in sentence_context.lower() for dk in cls.DESTROY_KEYWORDS):
                        obj_data["status"] = "Destroyed"
                        obj_data["important_events"].append(f"Scene {s_num}: Destroyed ({sentence_context[:100]})")

                    # Check for handlers
                    for char in chars_present:
                        if char.upper() in sentence_context.upper() and char not in obj_data["handlers"]:
                            obj_data["handlers"].append(char)

        # Filter out objects that only appear once in passing unless significant
        result = []
        for obj in tracked_objects.values():
            if len(obj["scenes_present"]) >= 1:
                result.append(obj)

        result.sort(key=lambda o: len(o["scenes_present"]), reverse=True)
        return result

    @staticmethod
    def _get_surrounding_sentence(text: str, pos: int) -> str:
        """Finds sentence surrounding a character offset."""
        start = text.rfind(".", 0, pos)
        start = 0 if start == -1 else start + 1
        end = text.find(".", pos)
        end = len(text) if end == -1 else end + 1
        return text[start:end].strip()
