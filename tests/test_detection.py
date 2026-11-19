import pytest
from pathlib import Path
from core.script_parser import ScriptParser
from core.character_extractor import CharacterExtractor
from core.event_extractor import EventExtractor
from core.timeline_engine import TimelineEngine
from core.location_tracker import LocationTracker
from core.knowledge_tracker import KnowledgeTracker
from core.object_tracker import ObjectTracker
from detection.detector_coordinator import DetectorCoordinator

@pytest.fixture
def sample_script_data():
    sample_path = Path(__file__).resolve().parent.parent / "sample_data" / "sample_screenplay.txt"
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    scenes = ScriptParser.parse_script(text)
    characters, relationships = CharacterExtractor.extract_characters(scenes)
    events = EventExtractor.extract_events(scenes)
    location_data = LocationTracker.track_locations(scenes)
    knowledge_data = KnowledgeTracker.track_knowledge(scenes)
    objects = ObjectTracker.track_objects(scenes)

    return {
        "scenes": scenes,
        "characters": characters,
        "relationships": relationships,
        "events": events,
        "location_data": location_data,
        "knowledge_data": knowledge_data,
        "objects": objects
    }

def test_sample_script_parsing(sample_script_data):
    scenes = sample_script_data["scenes"]
    assert len(scenes) == 6
    assert scenes[0]["scene_number"] == 1
    assert scenes[5]["scene_number"] == 6

def test_continuity_detection_engine(sample_script_data):
    issues = DetectorCoordinator.run_all_detectors(
        scenes=sample_script_data["scenes"],
        characters=sample_script_data["characters"],
        events=sample_script_data["events"],
        location_data=sample_script_data["location_data"],
        knowledge_data=sample_script_data["knowledge_data"],
        tracked_objects=sample_script_data["objects"]
    )

    assert len(issues) >= 5, f"Expected at least 5 plot holes, found {len(issues)}"

    issue_types = [i["issue_type"] for i in issues]

    # Verify key continuity categories are caught
    assert any("Timeline" in it for it in issue_types), "Timeline contradiction not detected"
    assert any("Knowledge" in it for it in issue_types), "Knowledge leak not detected"
    assert any("Object" in it for it in issue_types), "Object continuity error not detected"
    assert any("Motivation" in it for it in issue_types), "Motivation contradiction not detected"
    assert any("Logical" in it for it in issue_types), "Logical post-mortem contradiction not detected"

    # Verify issue structure matches requirement
    first_issue = issues[0]
    required_keys = ["issue_id", "issue_type", "title", "description", "severity", "confidence", "scene_references", "evidence", "reasoning", "suggested_fix"]
    for k in required_keys:
        assert k in first_issue, f"Missing required key '{k}' in detected issue"

    assert len(first_issue["evidence"]) >= 1
    assert "scene_number" in first_issue["evidence"][0]
    assert "text" in first_issue["evidence"][0]
