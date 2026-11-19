import re
from typing import List, Dict, Any
from utils.helpers import get_val

class ObjectDetector:
    """Detects object continuity errors, such as destroyed props reappearing or impossible transfers."""

    DESTROY_KEYWORDS = ["destroys", "destroyed", "incinerates", "burns", "smashes", "crushed", "melts", "vaporized", "into the fire", "into the incinerator"]

    @classmethod
    def detect(cls, scenes: List[Any], tracked_objects: List[Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        for obj in tracked_objects or []:
            obj_name = get_val(obj, "name", "Object")
            scenes_present = get_val(obj, "scenes_present", []) or []

            # Check if this object was destroyed in one scene and reappears in a later scene
            destruction_scene = None
            destruction_excerpt = ""

            for s_num in scenes_present:
                scene = next((s for s in (scenes or []) if get_val(s, "scene_number") == s_num), None)
                if not scene:
                    continue
                content = get_val(scene, "raw_content", "") or ""

                # Check if destruction happened in this scene
                for dk in cls.DESTROY_KEYWORDS:
                    pat = rf'\b(?:{re.escape(obj_name)}|[a-z]+\s+{re.escape(obj_name.lower())})[^\.\n]*\b{dk}\b|\b{dk}\b[^\.\n]*\b{re.escape(obj_name.lower())}\b'
                    match = re.search(pat, content, re.I)
                    if match:
                        destruction_scene = s_num
                        destruction_excerpt = match.group(0).strip()
                        break
                if destruction_scene:
                    break

            # If destroyed, check if it appears in any scene numbered > destruction_scene
            if destruction_scene:
                for later_s_num in scenes_present:
                    if later_s_num > destruction_scene:
                        later_scene = next((s for s in (scenes or []) if get_val(s, "scene_number") == later_s_num), None)
                        later_content = get_val(later_scene, "raw_content", "") if later_scene else ""

                        # Find mention in later scene
                        later_match = re.search(rf'\b[^\.\n]*\b{re.escape(obj_name.lower())}\b[^\.\n]*\.', later_content, re.I)
                        later_text = later_match.group(0).strip() if later_match else f"Scene {later_s_num} references {obj_name}"

                        # Check if it was explained as a backup or replica
                        is_replica = bool(re.search(r'\b(?:backup|duplicate|replica|copy|second)\b', later_text, re.I))

                        if not is_replica:
                            issues.append({
                                "issue_id": f"OBJ{issue_count:03d}",
                                "issue_type": "Object Continuity Error",
                                "title": f"Destroyed Prop Resurfaces: {obj_name} (Scene {destruction_scene} vs Scene {later_s_num})",
                                "description": (
                                    f"The {obj_name} was explicitly destroyed in Scene {destruction_scene}, "
                                    f"but reappears intact in Scene {later_s_num} without explanation."
                                ),
                                "severity": "Critical",
                                "confidence": 0.95,
                                "scene_references": [destruction_scene, later_s_num],
                                "evidence": [
                                    {"scene_number": destruction_scene, "text": destruction_excerpt or f"Destroyed in Scene {destruction_scene}"},
                                    {"scene_number": later_s_num, "text": later_text}
                                ],
                                "reasoning": (
                                    f"Physical object conservation is violated. The {obj_name} was terminated in Scene {destruction_scene}. "
                                    f"Its subsequent possession in Scene {later_s_num} creates a fatal physical continuity break."
                                ),
                                "suggested_fix": (
                                    f"Clarify that the object in Scene {later_s_num} is a secondary backup drive/copy, "
                                    f"or alter Scene {destruction_scene} so the item was merely lost or hidden rather than obliterated."
                                )
                            })
                            issue_count += 1

        return issues
