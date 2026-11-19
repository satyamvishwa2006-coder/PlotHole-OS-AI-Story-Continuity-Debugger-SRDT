from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

class SubscriptableSchema(BaseModel):
    """Base Pydantic schema supporting both dictionary subscripting (obj['field']),
    .get('field'), and attribute access (obj.field) for universal compatibility."""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val
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
        return self.model_dump()


class SceneModel(SubscriptableSchema):
    scene_number: int = 1
    heading: str = "UNTITLED SCENE"
    int_ext: str = "INT"
    location_name: str = "UNKNOWN"
    time_of_day: str = "DAY"
    raw_content: str = ""
    action_text: str = ""
    dialogue_data: List[Dict[str, Any]] = Field(default_factory=list)
    characters_present: List[str] = Field(default_factory=list)
    time_reference: Optional[str] = None
    word_count: int = 0
    is_customized: bool = False


class CharacterModel(SubscriptableSchema):
    name: str
    first_appearance_scene: Optional[int] = None
    last_appearance_scene: Optional[int] = None
    total_scenes: int = 0
    dialogue_count: int = 0
    personality_traits: List[str] = Field(default_factory=list)
    explicit_traits: List[str] = Field(default_factory=list)
    inferred_traits: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    important_actions: List[str] = Field(default_factory=list)
    dialogue_samples: List[str] = Field(default_factory=list)
    known_information: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class CharacterRelationshipModel(SubscriptableSchema):
    source_character: str = ""
    target_character: str = ""
    relationship_type: str = "Acquaintance"
    interaction_count: int = 1
    sentiment: str = "Neutral"
    description: Optional[str] = ""

    @model_validator(mode="before")
    @classmethod
    def handle_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "character1" in data and "source_character" not in data:
                data["source_character"] = data["character1"]
            if "character2" in data and "target_character" not in data:
                data["target_character"] = data["character2"]
            if "co_occurrences" in data and "interaction_count" not in data:
                data["interaction_count"] = data["co_occurrences"]
        return data


class EventModel(SubscriptableSchema):
    event_id: str = "EV001"
    scene_number: int = 1
    characters_involved: List[str] = Field(default_factory=list)
    description: str = ""
    time_reference: Optional[str] = None
    location: Optional[str] = None
    related_events: List[str] = Field(default_factory=list)
    source_evidence: Optional[str] = None
    chronological_order: int = 0


class LocationModel(SubscriptableSchema):
    location_name: str
    scene_count: int = 1
    scenes: List[int] = Field(default_factory=list)
    visitors: List[str] = Field(default_factory=list)


class PlotHoleModel(SubscriptableSchema):
    issue_id: str = "PH001"
    issue_type: str = "Logical Contradiction"
    title: str = "Continuity Inconsistency"
    description: str = ""
    severity: str = "Medium"
    confidence: float = 0.85
    scene_references: List[int] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str = ""
    suggested_fix: Optional[str] = ""
    status: str = "Open"


class CharacterKnowledgeModel(SubscriptableSchema):
    character_name: str
    knowledge_fact: str
    learned_scene: int
    source_character: Optional[str] = None
    has_identifiable_source: bool = True
    evidence_text: Optional[str] = None


class StoryObjectModel(SubscriptableSchema):
    name: str
    first_appearance_scene: Optional[int] = None
    scenes_present: List[int] = Field(default_factory=list)
    handlers: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    status: str = "Intact"
    important_events: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class RepairSuggestionModel(SubscriptableSchema):
    issue_id: int
    explanation: str
    continuity_impact: str
    primary_fix: str
    alternative_fix: Optional[str] = None
    original_scene_text: Optional[str] = None
    revised_scene_text: Optional[str] = None
    scene_number: Optional[int] = None
    user_status: str = "Pending"
    user_feedback: Optional[str] = None


class AnalysisSummaryModel(SubscriptableSchema):
    project_id: Optional[int] = None
    title: str = "Untitled Project"
    author: Optional[str] = "Unknown"
    genre: Optional[str] = "General"
    total_scenes: int = 0
    total_characters: int = 0
    total_events: int = 0
    total_objects: int = 0
    total_issues: int = 0
    severity_counts: Dict[str, int] = Field(default_factory=lambda: {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0})
    scenes: List[SceneModel] = Field(default_factory=list)
    characters: List[CharacterModel] = Field(default_factory=list)
    issues: List[PlotHoleModel] = Field(default_factory=list)
    events: List[EventModel] = Field(default_factory=list)
    objects: List[StoryObjectModel] = Field(default_factory=list)
    relationships: List[CharacterRelationshipModel] = Field(default_factory=list)
