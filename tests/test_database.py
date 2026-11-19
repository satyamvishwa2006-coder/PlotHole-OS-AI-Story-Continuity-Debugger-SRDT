import pytest
from database.db import init_db, SessionLocal
from database.operations import (
    create_project, get_project, list_projects, delete_project,
    save_scenes, get_scenes, save_characters, get_characters,
    save_issues, get_issues, save_repair_suggestion, update_repair_status,
    get_project_summary
)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_project_crud():
    proj = create_project(title="Test Screenplay", author="Test Author", genre="Sci-Fi")
    assert proj.id is not None
    assert proj.title == "Test Screenplay"

    fetched = get_project(proj.id)
    assert fetched is not None
    assert fetched.author == "Test Author"

    proj_list = list_projects()
    assert any(p["id"] == proj.id for p in proj_list)

    # Test saving scenes
    scenes_data = [
        {
            "scene_number": 1,
            "heading": "INT. ROOM - DAY",
            "int_ext": "INT",
            "location_name": "ROOM",
            "time_of_day": "DAY",
            "raw_content": "Content of scene 1",
            "word_count": 4
        }
    ]
    saved_scenes = save_scenes(proj.id, scenes_data)
    assert len(saved_scenes) == 1

    scenes = get_scenes(proj.id)
    assert len(scenes) == 1
    assert scenes[0].heading == "INT. ROOM - DAY"

    # Test saving issues
    issues_data = [
        {
            "issue_id": "PH001",
            "issue_type": "Timeline Contradiction",
            "title": "Conflict",
            "description": "Details",
            "severity": "High",
            "confidence": 0.9,
            "scene_references": [1],
            "evidence": [{"scene_number": 1, "text": "evidence"}],
            "reasoning": "Reason",
            "suggested_fix": "Fix"
        }
    ]
    saved_issues = save_issues(proj.id, issues_data)
    assert len(saved_issues) == 1

    issues = get_issues(proj.id)
    assert len(issues) == 1
    assert issues[0].issue_id == "PH001"

    # Test repair suggestion
    rep = save_repair_suggestion(
        issue_id=saved_issues[0].id,
        explanation="Explain",
        continuity_impact="Impact",
        primary_fix="Primary",
        original_scene_text="Original",
        revised_scene_text="Revised"
    )
    assert rep.id is not None
    updated = update_repair_status(rep.id, "Accepted", "Looks good")
    assert updated is True

    # Test summary
    summary = get_project_summary(proj.id)
    assert summary["total_scenes"] == 1
    assert summary["total_issues"] == 1

    # Test deletion
    deleted = delete_project(proj.id)
    assert deleted is True
    assert get_project(proj.id) is None
