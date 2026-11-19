import difflib
from typing import List, Dict, Any

def get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Safe universal attribute/dictionary accessor that works on dicts,
    Pydantic models, SQLAlchemy models, and regular objects."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, key):
        val = getattr(obj, key)
        return val if val is not None else default
    if hasattr(obj, "__getitem__"):
        try:
            val = obj[key]
            return val if val is not None else default
        except (KeyError, TypeError, IndexError):
            pass
    return default

def to_dict_safe(obj: Any) -> Dict[str, Any]:
    """Converts any object (SQLAlchemy model, Pydantic model, dataclass, dict)
    into a clean dictionary without internal private state."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "model_dump"):  # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):  # Pydantic v1
        return obj.dict()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__table__"):
        res = {}
        for col in obj.__table__.columns:
            res[col.name] = getattr(obj, col.name)
        return res
    if hasattr(obj, "__dict__"):
        d = dict(obj.__dict__)
        d.pop("_sa_instance_state", None)
        return d
    return {}

def to_dict_list(items: Any) -> List[Dict[str, Any]]:
    """Converts an iterable of items to a list of clean dictionaries."""
    if not items:
        return []
    return [to_dict_safe(item) for item in items]

def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens based on characters (~4 chars per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)

def generate_text_diff(original: str, revised: str) -> List[Dict[str, Any]]:
    """Generates line-by-line diff comparison between original and revised scene text."""
    orig_lines = original.splitlines()
    rev_lines = revised.splitlines()
    
    diff = difflib.ndiff(orig_lines, rev_lines)
    result = []
    
    for line in diff:
        code = line[:2]
        content = line[2:]
        if code == "  ":
            result.append({"type": "equal", "text": content})
        elif code == "- ":
            result.append({"type": "deleted", "text": content})
        elif code == "+ ":
            result.append({"type": "added", "text": content})
        elif code == "? ":
            continue
            
    return result

def format_confidence_badge(confidence: float) -> str:
    """Formats confidence float into a percentage and label."""
    pct = int(confidence * 100)
    if pct >= 85:
        return f"{pct}% (High Confidence)"
    elif pct >= 65:
        return f"{pct}% (Moderate Confidence)"
    else:
        return f"{pct}% (Low Confidence / Speculative)"

def format_severity_color(severity: str) -> str:
    """Returns CSS color or badge color for severity."""
    mapping = {
        "Critical": "#FF4B4B",
        "High": "#FFA500",
        "Medium": "#FFD700",
        "Low": "#1E90FF",
        "Informational": "#9E9E9E"
    }
    return mapping.get(severity, "#1E90FF")
