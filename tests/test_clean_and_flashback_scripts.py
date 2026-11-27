import pytest
from core.script_parser import ScriptParser
from core.character_extractor import CharacterExtractor
from core.event_extractor import EventExtractor
from core.timeline_engine import TimelineEngine
from core.location_tracker import LocationTracker
from core.knowledge_tracker import KnowledgeTracker
from core.object_tracker import ObjectTracker
from detection.detector_coordinator import DetectorCoordinator
from detection.timeline_detector import TimelineDetector
from detection.character_detector import CharacterDetector
from detection.location_detector import LocationDetector
from detection.knowledge_detector import KnowledgeDetector
from detection.object_detector import ObjectDetector
from detection.motivation_detector import MotivationDetector
from detection.missing_transition_detector import MissingTransitionDetector
from detection.logical_detector import LogicalDetector

CLEAN_SCREENPLAY = """
SCENE 1
INT. SAFE HOUSE - MORNING
DR. ARLO sits at the wooden desk, reviewing satellite coordinates.
SARAH enters carrying two mugs of tea.

SARAH
Here's your tea, Arlo.

DR. ARLO
Thank you. The shipment departs at noon.

SCENE 2
INT. SAFE HOUSE - AFTERNOON
DR. ARLO packs his laptop into a canvas backpack.
SARAH checks the street below through the blinds.

SARAH
Street is clear. Time to move.

SCENE 3
EXT. WAREHOUSE DISTRICT - NIGHT
DR. ARLO and SARAH arrive outside the rusted loading dock.
DR. ARLO unlocks the side door with the silver key.
They slip inside quietly.
"""

FLASHBACK_SCREENPLAY = """
SCENE 1
INT. PRISON CELL - NIGHT
DR. ARLO stares at the concrete wall. The clock reads 10:00 PM.
He remembers the day everything fell apart.

SCENE 2
INT. LABORATORY - DAY (FLASHBACK)
FIVE YEARS EARLIER.
DR. ARLO, younger and energetic, seals the antidote formula.
DR. ARLO
The formula is complete.

SCENE 3
INT. PRISON CELL - NIGHT
DR. ARLO blinks as the cell buzzer rings at 10:05 PM.
GUARD
Time for your hearing, Doctor.
"""

def test_clean_screenplay_has_zero_false_positives():
    """Verify that a completely consistent screenplay produces zero continuity issues."""
    scenes = ScriptParser.parse_script(CLEAN_SCREENPLAY)
    assert len(scenes) == 3

    chars, rels = CharacterExtractor.extract_characters(scenes)
    events = EventExtractor.extract_events(scenes)
    loc_data = LocationTracker.track_locations(scenes)
    know_data = KnowledgeTracker.track_knowledge(scenes)
    objs = ObjectTracker.track_objects(scenes)

    issues = DetectorCoordinator.run_all_detectors(
        scenes=scenes,
        characters=chars,
        events=events,
        location_data=loc_data,
        knowledge_data=know_data,
        tracked_objects=objs
    )

    # Clean screenplay should have no continuity errors
    assert len(issues) == 0, f"Expected 0 issues for clean script, found {len(issues)}: {[i['title'] for i in issues]}"

def test_flashback_screenplay_does_not_trigger_timeline_error():
    """Verify that intentional flashbacks marked in sluglines do not trigger timeline regressions."""
    scenes = ScriptParser.parse_script(FLASHBACK_SCREENPLAY)
    assert len(scenes) == 3

    events = EventExtractor.extract_events(scenes)
    timeline_analysis = TimelineEngine.analyze_timeline(scenes, events)
    
    # Check that Scene 2 is detected as flashback
    assert timeline_analysis["scene_timeline"][1]["is_flashback"] is True
    assert timeline_analysis["scene_timeline"][0]["is_flashback"] is False

    # Run Timeline Detector specifically
    tl_issues = TimelineDetector.detect(scenes, events)
    assert len(tl_issues) == 0, f"Flashback triggered false timeline error: {[i['title'] for i in tl_issues]}"

def test_object_tracker_destruction_and_preservation():
    """Test object tracker correctly detects when a prop is destroyed."""
    script = """
    SCENE 1
    INT. LAB - DAY
    DR. ARLO holds the flash drive.
    
    SCENE 2
    INT. FURNACE - NIGHT
    DR. ARLO throws the flash drive into the fire. The incinerator burns and destroys the flash drive completely.
    """
    scenes = ScriptParser.parse_script(script)
    objs = ObjectTracker.track_objects(scenes)
    drive_obj = next((o for o in objs if "Drive" in o["name"]), None)
    assert drive_obj is not None
    assert drive_obj["status"] == "Destroyed"

def test_logical_detector_prevents_false_positive_on_vision():
    """Test logical detector ignores appearances of deceased characters in marked dream or memory scenes."""
    script = """
    SCENE 1
    INT. ALLEY - NIGHT
    A gunman shoots MARCUS dead on impact.
    
    SCENE 2
    INT. BEDROOM - NIGHT (DREAM SEQUENCE)
    MARCUS appears in Sarah's dream, smiling quietly.
    """
    scenes = ScriptParser.parse_script(script)
    chars, _ = CharacterExtractor.extract_characters(scenes)
    issues = LogicalDetector.detect(scenes, chars)
    # The dream sequence should not be flagged as a post-mortem plot hole
    assert len(issues) == 0
