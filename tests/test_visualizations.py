import pytest
from database.models import Scene, DetectedIssue, Character, CharacterRelationship
from core.schemas import SceneModel, CharacterModel, CharacterRelationshipModel, PlotHoleModel
from visualization import (
    create_timeline_chart,
    create_character_network_graph,
    create_severity_donut,
    create_issue_type_bar,
    create_continuity_gauge,
    create_character_appearance_chart,
    create_scene_distribution_chart,
    create_knowledge_map,
    create_location_journey_chart
)

def test_timeline_chart_empty():
    fig = create_timeline_chart([], [])
    assert fig is not None

def test_timeline_chart_with_dicts():
    scenes = [
        {"scene_number": 1, "heading": "INT. OFFICE - DAY", "location_name": "OFFICE", "time_of_day": "DAY"},
        {"scene_number": 2, "heading": "EXT. STREET - NIGHT", "location_name": "STREET", "time_of_day": "NIGHT"}
    ]
    issues = [
        {"issue_id": "ISS001", "title": "Time Jump", "severity": "Critical", "scene_references": [1, 2]}
    ]
    fig = create_timeline_chart(scenes, issues)
    assert fig is not None

def test_timeline_chart_with_orm_objects():
    scene1 = Scene(id=1, project_id=1, scene_number=1, heading="INT. OFFICE - DAY", location_name="OFFICE", time_of_day="DAY")
    scene2 = Scene(id=2, project_id=1, scene_number=2, heading="EXT. STREET - NIGHT", location_name="STREET", time_of_day="NIGHT")
    issue = DetectedIssue(id=1, project_id=1, issue_id="ISS001", title="Time Jump", severity="Critical", scene_references=[1, 2])
    
    # Must not raise TypeError: 'Scene' object is not subscriptable!
    fig = create_timeline_chart([scene1, scene2], [issue])
    assert fig is not None

def test_timeline_chart_with_pydantic_models():
    scene1 = SceneModel(scene_number=1, heading="INT. LAB - DAY", location_name="LAB", time_of_day="DAY")
    scene2 = SceneModel(scene_number=2, heading="EXT. ROOF - NIGHT", location_name="ROOF", time_of_day="NIGHT")
    issue = PlotHoleModel(issue_id="ISS002", title="Missing Key", issue_type="Object Continuity", severity="High", scene_references=[1, 2])
    
    fig = create_timeline_chart([scene1, scene2], [issue])
    assert fig is not None

def test_character_network_graph():
    # Empty
    assert create_character_network_graph([], []) is not None
    
    # Dicts
    chars_dict = [
        {"name": "ALEX", "total_scenes": 5, "dialogue_count": 12},
        {"name": "ELENA", "total_scenes": 4, "dialogue_count": 8}
    ]
    rels_dict = [
        {"character1": "ALEX", "character2": "ELENA", "scenes_together": [1, 2], "co_occurrences": 2}
    ]
    assert create_character_network_graph(chars_dict, rels_dict) is not None
    
    # ORM objects
    c1 = Character(id=1, project_id=1, name="ALEX", total_scenes=5, dialogue_count=12)
    c2 = Character(id=2, project_id=1, name="ELENA", total_scenes=4, dialogue_count=8)
    r1 = CharacterRelationship(id=1, project_id=1, source_character="ALEX", target_character="ELENA", interaction_count=2)
    assert create_character_network_graph([c1, c2], [r1]) is not None
    
    # Pydantic schemas
    pm1 = CharacterModel(name="ALEX", total_scenes=5, dialogue_count=12)
    pm2 = CharacterModel(name="ELENA", total_scenes=4, dialogue_count=8)
    prm = CharacterRelationshipModel(character1="ALEX", character2="ELENA", scenes_together=[1, 2], co_occurrences=2)
    assert create_character_network_graph([pm1, pm2], [prm]) is not None

def test_all_analytics_visualizations():
    # Severity donut
    assert create_severity_donut([]) is not None
    assert create_severity_donut([{"severity": "Critical"}, {"severity": "High"}]) is not None
    
    # Issue type bar
    assert create_issue_type_bar([]) is not None
    assert create_issue_type_bar([{"issue_type": "Timeline Contradiction"}, {"issue_type": "Knowledge Leak"}]) is not None
    
    # Continuity gauge
    assert create_continuity_gauge(85) is not None
    
    # Character appearance chart
    assert create_character_appearance_chart([]) is not None
    assert create_character_appearance_chart([{"name": "ALEX", "total_scenes": 5, "dialogue_count": 10}]) is not None
    
    # Scene distribution chart
    assert create_scene_distribution_chart([]) is not None
    assert create_scene_distribution_chart([{"scene_number": 1, "word_count": 250, "characters_present": ["ALEX"]}]) is not None
    
    # Knowledge map
    assert create_knowledge_map({}) is not None
    know_data = {
        "disclosed_facts": {
            "PROJECT_NEXUS": {
                "first_scene": 1,
                "discloser": "ELENA",
                "witnesses": ["ALEX"],
                "evidence": "Elena whispers Project Nexus"
            }
        }
    }
    assert create_knowledge_map(know_data) is not None
    
    # Location journey chart
    assert create_location_journey_chart([]) is not None
    scenes = [
        {"scene_number": 1, "location_name": "OFFICE"},
        {"scene_number": 2, "location_name": "STREET"},
        {"scene_number": 3, "location_name": "OFFICE"}
    ]
    assert create_location_journey_chart(scenes) is not None
