from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import (
    Project, Script, Scene, Character, CharacterRelationship,
    Event, LocationAppearance, KnowledgeItem, TrackedObject,
    DetectedIssue, RepairSuggestion, AnalysisHistory
)

def create_project(title: str = "Untitled Project", author: str = "Unknown", genre: str = "General", description: str = "") -> Project:
    session: Session = SessionLocal()
    try:
        project = Project(title=title, author=author, genre=genre, description=description)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project
    finally:
        session.close()

def get_project(project_id: int) -> Optional[Project]:
    session: Session = SessionLocal()
    try:
        return session.query(Project).filter(Project.id == project_id).first()
    finally:
        session.close()

def list_projects() -> List[Dict[str, Any]]:
    session: Session = SessionLocal()
    try:
        projects = session.query(Project).order_by(Project.updated_at.desc()).all()
        result = []
        for p in projects:
            scene_count = session.query(Scene).filter(Scene.project_id == p.id).count()
            issue_count = session.query(DetectedIssue).filter(DetectedIssue.project_id == p.id).count()
            char_count = session.query(Character).filter(Character.project_id == p.id).count()
            result.append({
                "id": p.id,
                "title": p.title,
                "author": p.author,
                "genre": p.genre,
                "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M") if p.updated_at else "",
                "scene_count": scene_count,
                "character_count": char_count,
                "issue_count": issue_count
            })
        return result
    finally:
        session.close()

def delete_project(project_id: int) -> bool:
    session: Session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            session.delete(project)
            session.commit()
            return True
        return False
    finally:
        session.close()

def save_script(
    project_id: int,
    filename: str,
    file_type: str,
    file_size_bytes: int,
    raw_text: str,
    word_count: int,
    char_count: int,
    scene_count: int,
    file_hash: Optional[str] = None
) -> Script:
    session: Session = SessionLocal()
    try:
        script = Script(
            project_id=project_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            raw_text=raw_text,
            word_count=word_count,
            char_count=char_count,
            scene_count=scene_count,
            file_hash=file_hash
        )
        session.add(script)
        session.commit()
        session.refresh(script)
        return script
    finally:
        session.close()

def save_scenes(project_id: int, scenes_data: List[Dict[str, Any]]) -> List[Scene]:
    session: Session = SessionLocal()
    try:
        # Clear existing scenes for this project
        session.query(Scene).filter(Scene.project_id == project_id).delete()
        
        scenes = []
        for s in scenes_data:
            scene = Scene(
                project_id=project_id,
                scene_number=s.get("scene_number", 1),
                heading=s.get("heading", "UNTITLED SCENE"),
                int_ext=s.get("int_ext", "INT"),
                location_name=s.get("location_name", "UNKNOWN"),
                time_of_day=s.get("time_of_day", "DAY"),
                raw_content=s.get("raw_content", ""),
                action_text=s.get("action_text", ""),
                dialogue_data=s.get("dialogue_data", []),
                characters_present=s.get("characters_present", []),
                time_reference=s.get("time_reference"),
                word_count=s.get("word_count", 0),
                is_customized=s.get("is_customized", False)
            )
            session.add(scene)
            scenes.append(scene)
        session.commit()
        return scenes
    finally:
        session.close()

def get_scenes(project_id: int) -> List[Scene]:
    session: Session = SessionLocal()
    try:
        return session.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number.asc()).all()
    finally:
        session.close()

def get_scene_by_number(project_id: int, scene_number: int) -> Optional[Scene]:
    session: Session = SessionLocal()
    try:
        return session.query(Scene).filter(Scene.project_id == project_id, Scene.scene_number == scene_number).first()
    finally:
        session.close()

def save_characters(project_id: int, characters_data: List[Dict[str, Any]]) -> List[Character]:
    session: Session = SessionLocal()
    try:
        session.query(Character).filter(Character.project_id == project_id).delete()
        chars = []
        for c in characters_data:
            char = Character(
                project_id=project_id,
                name=c.get("name", "Unknown"),
                first_appearance_scene=c.get("first_appearance_scene"),
                last_appearance_scene=c.get("last_appearance_scene"),
                total_scenes=c.get("total_scenes", 0),
                dialogue_count=c.get("dialogue_count", 0),
                personality_traits=c.get("personality_traits", []),
                explicit_traits=c.get("explicit_traits", []),
                inferred_traits=c.get("inferred_traits", []),
                motivations=c.get("motivations", []),
                goals=c.get("goals", []),
                important_actions=c.get("important_actions", []),
                dialogue_samples=c.get("dialogue_samples", []),
                known_information=c.get("known_information", []),
                notes=c.get("notes")
            )
            session.add(char)
            chars.append(char)
        session.commit()
        return chars
    finally:
        session.close()

def get_characters(project_id: int) -> List[Character]:
    session: Session = SessionLocal()
    try:
        return session.query(Character).filter(Character.project_id == project_id).order_by(Character.total_scenes.desc()).all()
    finally:
        session.close()

def save_relationships(project_id: int, relationships_data: List[Dict[str, Any]]) -> List[CharacterRelationship]:
    session: Session = SessionLocal()
    try:
        session.query(CharacterRelationship).filter(CharacterRelationship.project_id == project_id).delete()
        rels = []
        for r in relationships_data:
            rel = CharacterRelationship(
                project_id=project_id,
                source_character=r.get("source_character", ""),
                target_character=r.get("target_character", ""),
                relationship_type=r.get("relationship_type", "Acquaintance"),
                interaction_count=r.get("interaction_count", 1),
                sentiment=r.get("sentiment", "Neutral"),
                description=r.get("description", "")
            )
            session.add(rel)
            rels.append(rel)
        session.commit()
        return rels
    finally:
        session.close()

def get_relationships(project_id: int) -> List[CharacterRelationship]:
    session: Session = SessionLocal()
    try:
        return session.query(CharacterRelationship).filter(CharacterRelationship.project_id == project_id).all()
    finally:
        session.close()

def save_events(project_id: int, events_data: List[Dict[str, Any]]) -> List[Event]:
    session: Session = SessionLocal()
    try:
        session.query(Event).filter(Event.project_id == project_id).delete()
        events = []
        for idx, e in enumerate(events_data):
            event = Event(
                project_id=project_id,
                event_id=e.get("event_id", f"EV{idx+1:03d}"),
                scene_number=e.get("scene_number", 1),
                characters_involved=e.get("characters_involved", []),
                description=e.get("description", ""),
                time_reference=e.get("time_reference"),
                location=e.get("location"),
                related_events=e.get("related_events", []),
                source_evidence=e.get("source_evidence"),
                chronological_order=e.get("chronological_order", idx + 1)
            )
            session.add(event)
            events.append(event)
        session.commit()
        return events
    finally:
        session.close()

def get_events(project_id: int) -> List[Event]:
    session: Session = SessionLocal()
    try:
        return session.query(Event).filter(Event.project_id == project_id).order_by(Event.chronological_order.asc()).all()
    finally:
        session.close()

def save_tracked_objects(project_id: int, objects_data: List[Dict[str, Any]]) -> List[TrackedObject]:
    session: Session = SessionLocal()
    try:
        session.query(TrackedObject).filter(TrackedObject.project_id == project_id).delete()
        objs = []
        for o in objects_data:
            obj = TrackedObject(
                project_id=project_id,
                name=o.get("name", "Object"),
                first_appearance_scene=o.get("first_appearance_scene"),
                scenes_present=o.get("scenes_present", []),
                handlers=o.get("handlers", []),
                owner=o.get("owner"),
                status=o.get("status", "Intact"),
                important_events=o.get("important_events", []),
                notes=o.get("notes")
            )
            session.add(obj)
            objs.append(obj)
        session.commit()
        return objs
    finally:
        session.close()

def get_tracked_objects(project_id: int) -> List[TrackedObject]:
    session: Session = SessionLocal()
    try:
        return session.query(TrackedObject).filter(TrackedObject.project_id == project_id).all()
    finally:
        session.close()

def save_issues(project_id: int, issues_data: List[Dict[str, Any]]) -> List[DetectedIssue]:
    session: Session = SessionLocal()
    try:
        session.query(DetectedIssue).filter(DetectedIssue.project_id == project_id).delete()
        issues = []
        for idx, i in enumerate(issues_data):
            issue = DetectedIssue(
                project_id=project_id,
                issue_id=i.get("issue_id", f"PH{idx+1:03d}"),
                issue_type=i.get("issue_type", "Logical Contradiction"),
                title=i.get("title", "Continuity Issue"),
                description=i.get("description", ""),
                severity=i.get("severity", "Medium"),
                confidence=float(i.get("confidence", 0.85)),
                scene_references=i.get("scene_references", []),
                evidence=i.get("evidence", []),
                reasoning=i.get("reasoning", ""),
                suggested_fix=i.get("suggested_fix", ""),
                status=i.get("status", "Open")
            )
            session.add(issue)
            issues.append(issue)
        session.commit()
        return issues
    finally:
        session.close()

def get_issues(project_id: int) -> List[DetectedIssue]:
    session: Session = SessionLocal()
    try:
        return session.query(DetectedIssue).filter(DetectedIssue.project_id == project_id).all()
    finally:
        session.close()

def save_repair_suggestion(issue_id: int, **kwargs) -> RepairSuggestion:
    session: Session = SessionLocal()
    try:
        repair = RepairSuggestion(issue_id=issue_id, **kwargs)
        session.add(repair)
        session.commit()
        session.refresh(repair)
        return repair
    finally:
        session.close()

def update_repair_status(suggestion_id: int, status: str, feedback: Optional[str] = None) -> bool:
    session: Session = SessionLocal()
    try:
        repair = session.query(RepairSuggestion).filter(RepairSuggestion.id == suggestion_id).first()
        if repair:
            repair.user_status = status
            if feedback:
                repair.user_feedback = feedback
            session.commit()
            return True
        return False
    finally:
        session.close()

def save_analysis_history(project_id: int, **kwargs) -> AnalysisHistory:
    session: Session = SessionLocal()
    try:
        history = AnalysisHistory(project_id=project_id, **kwargs)
        session.add(history)
        session.commit()
        session.refresh(history)
        return history
    finally:
        session.close()

def get_project_summary(project_id: int) -> Dict[str, Any]:
    session: Session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}
        scenes = session.query(Scene).filter(Scene.project_id == project_id).all()
        chars = session.query(Character).filter(Character.project_id == project_id).all()
        issues = session.query(DetectedIssue).filter(DetectedIssue.project_id == project_id).all()
        events = session.query(Event).filter(Event.project_id == project_id).all()
        objects = session.query(TrackedObject).filter(TrackedObject.project_id == project_id).all()
        relationships = session.query(CharacterRelationship).filter(CharacterRelationship.project_id == project_id).all()
        
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for iss in issues:
            sev = iss.severity if iss.severity in severity_counts else "Medium"
            severity_counts[sev] += 1
            
        return {
            "project_id": project.id,
            "title": project.title,
            "author": project.author,
            "genre": project.genre,
            "total_scenes": len(scenes),
            "total_characters": len(chars),
            "total_events": len(events),
            "total_objects": len(objects),
            "total_issues": len(issues),
            "severity_counts": severity_counts,
            "scenes": scenes,
            "characters": chars,
            "issues": issues,
            "events": events,
            "objects": objects,
            "relationships": relationships
        }
    finally:
        session.close()
