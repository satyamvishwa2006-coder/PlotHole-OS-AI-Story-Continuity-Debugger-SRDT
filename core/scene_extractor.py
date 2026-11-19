from typing import List, Dict, Any, Optional
from core.script_parser import ScriptParser
from utils.helpers import get_val, to_dict_safe

class SceneExtractor:
    """Manages scene segmentation, extraction, and user corrections."""

    @classmethod
    def extract_scenes(cls, script_text: str) -> List[Dict[str, Any]]:
        """Parses script and extracts structured scenes."""
        return ScriptParser.parse_script(script_text)

    @classmethod
    def apply_manual_override(
        cls,
        scenes: List[Any],
        scene_number: int,
        new_heading: Optional[str] = None,
        new_location: Optional[str] = None,
        new_time: Optional[str] = None,
        new_content: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Applies manual correction to a specific scene."""
        updated = []
        for s in scenes:
            s_dict = to_dict_safe(s)
            if s_dict.get("scene_number") == scene_number:
                if new_heading:
                    s_dict["heading"] = new_heading
                if new_location:
                    s_dict["location_name"] = new_location
                if new_time:
                    s_dict["time_of_day"] = new_time
                    s_dict["time_reference"] = new_time
                if new_content:
                    s_dict["raw_content"] = new_content
                    s_dict["word_count"] = len(new_content.split())
                s_dict["is_customized"] = True
                updated.append(s_dict)
            else:
                updated.append(s_dict)
        return updated
