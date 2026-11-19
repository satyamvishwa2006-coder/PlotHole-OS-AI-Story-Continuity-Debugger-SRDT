import json
import pytest
from reports.pdf_generator import generate_pdf_report
from reports.json_exporter import export_project_json

def test_pdf_generation():
    summary = {
        "project_id": 1,
        "title": "THE TEST PROTOCOL",
        "author": "Jane Doe",
        "genre": "Thriller",
        "total_scenes": 2,
        "total_characters": 2,
        "total_issues": 1,
        "severity_counts": {"Critical": 0, "High": 1, "Medium": 0, "Low": 0, "Informational": 0},
        "characters": [
            {"name": "MARCUS", "total_scenes": 2, "dialogue_count": 5, "personality_traits": ["Stealthy"]}
        ],
        "issues": [
            {
                "issue_id": "PH001",
                "issue_type": "Timeline Contradiction",
                "title": "Time Sequence Jump",
                "description": "Scene 2 precedes Scene 1 timestamp.",
                "severity": "High",
                "confidence": 0.94,
                "scene_references": [1, 2],
                "evidence": [{"scene_number": 1, "text": "10:00 PM"}, {"scene_number": 2, "text": "9:00 PM"}],
                "reasoning": "Linear continuity violation.",
                "suggested_fix": "Add flashback indicator."
            }
        ]
    }

    pdf_bytes = generate_pdf_report(summary)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_json_export():
    summary = {
        "project_id": 1,
        "title": "THE TEST PROTOCOL",
        "author": "Jane Doe",
        "genre": "Thriller",
        "total_scenes": 2,
        "total_characters": 2,
        "total_issues": 1,
        "severity_counts": {"Critical": 0, "High": 1, "Medium": 0, "Low": 0, "Informational": 0},
        "scenes": [{"scene_number": 1, "heading": "INT. LAB - DAY"}],
        "characters": [{"name": "MARCUS"}],
        "issues": [{"issue_id": "PH001", "title": "Test Issue"}]
    }

    json_str = export_project_json(summary)
    data = json.loads(json_str)
    assert data["project"]["title"] == "THE TEST PROTOCOL"
    assert len(data["detected_issues"]) == 1
    assert data["detected_issues"][0]["issue_id"] == "PH001"
