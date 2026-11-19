from typing import List, Dict, Any, Optional
from detection.timeline_detector import TimelineDetector
from detection.character_detector import CharacterDetector
from detection.location_detector import LocationDetector
from detection.knowledge_detector import KnowledgeDetector
from detection.object_detector import ObjectDetector
from detection.motivation_detector import MotivationDetector
from detection.missing_transition_detector import MissingTransitionDetector
from detection.logical_detector import LogicalDetector
from utils.helpers import get_val

class DetectorCoordinator:
    """Coordinates deterministic rule-based checks and AI contextual findings into a verified, unified issue registry."""

    @classmethod
    def run_all_detectors(
        cls,
        scenes: List[Any],
        characters: List[Any],
        events: List[Any],
        location_data: Dict[str, Any],
        knowledge_data: Dict[str, Any],
        tracked_objects: List[Any],
        ai_issues: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        all_issues = []

        # 1. Timeline Consistency
        all_issues.extend(TimelineDetector.detect(scenes, events))

        # 2. Character Consistency
        all_issues.extend(CharacterDetector.detect(scenes, characters))

        # 3. Location Continuity
        all_issues.extend(LocationDetector.detect(scenes, location_data))

        # 4. Knowledge Consistency
        all_issues.extend(KnowledgeDetector.detect(scenes, knowledge_data))

        # 5. Object Continuity
        all_issues.extend(ObjectDetector.detect(scenes, tracked_objects))

        # 6. Motivation Consistency
        all_issues.extend(MotivationDetector.detect(scenes, characters))

        # 7. Missing Transitions
        all_issues.extend(MissingTransitionDetector.detect(scenes))

        # 8. Logical Contradictions
        all_issues.extend(LogicalDetector.detect(scenes, characters))

        # 9. Merge and normalize AI contextual issues if provided
        if ai_issues:
            for ai_iss in ai_issues:
                # Deduplicate: check if an issue with the same scene references and title already exists
                is_dup = any(
                    cls._is_duplicate(ai_iss, existing)
                    for existing in all_issues
                )
                if not is_dup:
                    all_issues.append(cls._normalize_issue_schema(ai_iss, len(all_issues) + 1))

        # Sort issues by severity priority: Critical > High > Medium > Low > Informational
        severity_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4, "Informational": 5}
        all_issues.sort(key=lambda x: (severity_order.get(x.get("severity", "Medium"), 3), -x.get("confidence", 0.8)))

        # Assign unified issue IDs (e.g., PH001, PH002, ...)
        for idx, issue in enumerate(all_issues):
            issue["issue_id"] = f"PH{idx+1:03d}"

        return all_issues

    @staticmethod
    def _is_duplicate(issue_a: Any, issue_b: Any) -> bool:
        """Determines if two issues describe the same core contradiction."""
        scenes_a = set(get_val(issue_a, "scene_references", []) or [])
        scenes_b = set(get_val(issue_b, "scene_references", []) or [])
        if scenes_a and scenes_b and scenes_a == scenes_b:
            type_a = str(get_val(issue_a, "issue_type", "")).lower()
            type_b = str(get_val(issue_b, "issue_type", "")).lower()
            if type_a == type_b or ("contradiction" in type_a and "contradiction" in type_b):
                return True
        return False

    @staticmethod
    def _normalize_issue_schema(issue: Any, index: int) -> Dict[str, Any]:
        """Ensures every issue has the exact required keys and formatting."""
        return {
            "issue_id": get_val(issue, "issue_id", f"PH{index:03d}"),
            "issue_type": get_val(issue, "issue_type", "Contextual Contradiction"),
            "title": get_val(issue, "title", "Narrative Inconsistency"),
            "description": get_val(issue, "description", "Potential narrative contradiction detected by AI."),
            "severity": get_val(issue, "severity", "Medium"),
            "confidence": float(get_val(issue, "confidence", 0.85) or 0.85),
            "scene_references": get_val(issue, "scene_references", []) or [],
            "evidence": get_val(issue, "evidence", []) or [],
            "reasoning": get_val(issue, "reasoning", "Discrepancy identified in contextual story logic."),
            "suggested_fix": get_val(issue, "suggested_fix", "Clarify narrative progression.")
        }
