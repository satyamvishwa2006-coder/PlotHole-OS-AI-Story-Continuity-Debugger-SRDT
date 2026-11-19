import json
from datetime import datetime, timezone
from typing import Dict, Any

def export_project_json(project_summary: Dict[str, Any]) -> str:
    """Exports the entire project analysis structure into a clean JSON string."""
    def serialize_item(obj):
        if isinstance(obj, dict):
            return {k: serialize_item(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_item(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            data = dict(obj.__dict__)
            data.pop("_sa_instance_state", None)
            return {k: serialize_item(v) for k, v in data.items()}
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    export_payload = {
        "export_metadata": {
            "system": "PlotHole OS",
            "version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "tagline": "Every Story Has a Logic. We Find Where It Breaks."
        },
        "project": {
            "id": project_summary.get("project_id"),
            "title": project_summary.get("title"),
            "author": project_summary.get("author"),
            "genre": project_summary.get("genre"),
            "total_scenes": project_summary.get("total_scenes"),
            "total_characters": project_summary.get("total_characters"),
            "total_issues": project_summary.get("total_issues"),
            "severity_counts": project_summary.get("severity_counts")
        },
        "scenes": [serialize_item(s) for s in project_summary.get("scenes", [])],
        "characters": [serialize_item(c) for c in project_summary.get("characters", [])],
        "events": [serialize_item(e) for e in project_summary.get("events", [])],
        "objects": [serialize_item(o) for o in project_summary.get("objects", [])],
        "detected_issues": [serialize_item(i) for i in project_summary.get("issues", [])]
    }

    return json.dumps(export_payload, default=serialize_item, indent=2)
