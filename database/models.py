from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class ModelAccessMixin:
    """Enables dictionary-style subscripting (obj['field']), .get('field'), and .to_dict()
    on SQLAlchemy ORM models, providing complete cross-compatibility."""

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"'{self.__class__.__name__}' has no attribute '{item}'")

    def __setitem__(self, item: str, value: Any):
        setattr(self, item, value)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        return default

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if hasattr(self, "__table__"):
            for col in self.__table__.columns:
                result[col.name] = getattr(self, col.name)
        else:
            for k, v in self.__dict__.items():
                if not k.startswith("_"):
                    result[k] = v
        return result

class Project(ModelAccessMixin, Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, default="Untitled Project")
    author = Column(String(255), nullable=True, default="Unknown")
    genre = Column(String(100), nullable=True, default="General")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    scripts = relationship("Script", back_populates="project", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("DetectedIssue", back_populates="project", cascade="all, delete-orphan")
    tracked_objects = relationship("TrackedObject", back_populates="project", cascade="all, delete-orphan")
    analysis_history = relationship("AnalysisHistory", back_populates="project", cascade="all, delete-orphan")


class Script(ModelAccessMixin, Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    scene_count = Column(Integer, default=0)
    file_hash = Column(String(64), nullable=True)
    uploaded_at = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="scripts")


class Scene(ModelAccessMixin, Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    heading = Column(String(255), nullable=False)
    int_ext = Column(String(50), default="INT")  # INT, EXT, INT/EXT
    location_name = Column(String(255), nullable=False, default="UNKNOWN")
    time_of_day = Column(String(100), default="DAY")  # DAY, NIGHT, DUSK, DAWN, CONTINUOUS
    raw_content = Column(Text, nullable=False)
    action_text = Column(Text, default="")
    dialogue_data = Column(JSON, default=list)  # list of {"character": str, "text": str, "parenthetical": str}
    characters_present = Column(JSON, default=list)  # list of str
    time_reference = Column(String(255), nullable=True)  # e.g., "10:00 PM", "LATER", "TWO DAYS LATER"
    word_count = Column(Integer, default=0)
    is_customized = Column(Boolean, default=False)

    project = relationship("Project", back_populates="scenes")


class Character(ModelAccessMixin, Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    first_appearance_scene = Column(Integer, nullable=True)
    last_appearance_scene = Column(Integer, nullable=True)
    total_scenes = Column(Integer, default=0)
    dialogue_count = Column(Integer, default=0)
    personality_traits = Column(JSON, default=list)  # list of str
    explicit_traits = Column(JSON, default=list)  # explicitly stated in script
    inferred_traits = Column(JSON, default=list)  # AI inferred
    motivations = Column(JSON, default=list)
    goals = Column(JSON, default=list)
    important_actions = Column(JSON, default=list)
    dialogue_samples = Column(JSON, default=list)
    known_information = Column(JSON, default=list)  # list of facts they know
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="characters")


class CharacterRelationship(ModelAccessMixin, Base):
    __tablename__ = "character_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    source_character = Column(String(255), nullable=False)
    target_character = Column(String(255), nullable=False)
    relationship_type = Column(String(100), default="Acquaintance")  # Ally, Enemy, Family, Romantic, Colleague
    interaction_count = Column(Integer, default=1)
    sentiment = Column(String(50), default="Neutral")  # Positive, Negative, Neutral, Conflicted
    description = Column(Text, nullable=True)


class Event(ModelAccessMixin, Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    event_id = Column(String(50), nullable=False)
    scene_number = Column(Integer, nullable=False)
    characters_involved = Column(JSON, default=list)
    description = Column(Text, nullable=False)
    time_reference = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    related_events = Column(JSON, default=list)
    source_evidence = Column(Text, nullable=True)
    chronological_order = Column(Integer, default=0)

    project = relationship("Project", back_populates="events")


class LocationAppearance(ModelAccessMixin, Base):
    __tablename__ = "location_appearances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    location_name = Column(String(255), nullable=False)
    characters_present = Column(JSON, default=list)
    previous_location = Column(String(255), nullable=True)
    next_location = Column(String(255), nullable=True)
    transition_evidence = Column(Text, nullable=True)


class KnowledgeItem(ModelAccessMixin, Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    character_name = Column(String(255), nullable=False)
    knowledge_fact = Column(Text, nullable=False)
    learned_scene = Column(Integer, nullable=False)
    source_character = Column(String(255), nullable=True)  # Who told them or "Observed", "Self"
    has_identifiable_source = Column(Boolean, default=True)
    evidence_text = Column(Text, nullable=True)


class TrackedObject(ModelAccessMixin, Base):
    __tablename__ = "tracked_objects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    first_appearance_scene = Column(Integer, nullable=True)
    scenes_present = Column(JSON, default=list)  # list of int
    handlers = Column(JSON, default=list)  # list of character names
    owner = Column(String(255), nullable=True)
    status = Column(String(100), default="Intact")  # Intact, Destroyed, Lost, Stolen, Hidden
    important_events = Column(JSON, default=list)
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="tracked_objects")


class DetectedIssue(ModelAccessMixin, Base):
    __tablename__ = "detected_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    issue_id = Column(String(50), nullable=False)
    issue_type = Column(String(100), nullable=False)  # e.g. Timeline Contradiction, Character Inconsistency
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False, default="Medium")  # Critical, High, Medium, Low, Informational
    confidence = Column(Float, default=0.85)
    scene_references = Column(JSON, default=list)  # list of int
    evidence = Column(JSON, default=list)  # list of {"scene_number": int, "text": str}
    reasoning = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    status = Column(String(50), default="Open")  # Open, Accepted, Rejected, Resolved

    project = relationship("Project", back_populates="issues")
    repairs = relationship("RepairSuggestion", back_populates="issue", cascade="all, delete-orphan")


class RepairSuggestion(ModelAccessMixin, Base):
    __tablename__ = "repair_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("detected_issues.id"), nullable=False)
    explanation = Column(Text, nullable=False)
    continuity_impact = Column(Text, nullable=False)
    primary_fix = Column(Text, nullable=False)
    alternative_fix = Column(Text, nullable=True)
    original_scene_text = Column(Text, nullable=True)
    revised_scene_text = Column(Text, nullable=True)
    scene_number = Column(Integer, nullable=True)
    user_status = Column(String(50), default="Pending")  # Pending, Accepted, Rejected, Saved
    user_feedback = Column(Text, nullable=True)

    issue = relationship("DetectedIssue", back_populates="repairs")


class AnalysisHistory(ModelAccessMixin, Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    analysis_type = Column(String(100), default="Full Comprehensive")
    scenes_analyzed = Column(Integer, default=0)
    issues_found = Column(Integer, default=0)
    ai_model_used = Column(String(100), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    completed_at = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="analysis_history")
