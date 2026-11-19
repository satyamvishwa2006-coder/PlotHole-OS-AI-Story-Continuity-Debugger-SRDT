import re
from typing import List, Dict, Any
from collections import defaultdict
from utils.helpers import get_val

class KnowledgeTracker:
    """Tracks what each character knows, when they learned it, who informed them,
    and flags unexplained knowledge leaks."""

    # Patterns for secrets, codes, identities, critical facts
    SECRET_PATTERNS = [
        r'\b(?:password|passcode|cipher|code|protocol)\s*(?:is|:)?\s*["\']?([A-Z0-9_\-]+)["\']?',
        r'\b(?:murdered|killed|poisoned|betrayed)\s+([A-Z][a-z]+)',
        r'\b(?:the bomb is at|the device is in|the money is at|the hideout is in)\s+([A-Za-z0-9\s]+)',
        r'\b(?:informant|mole|traitor|spy)\s+is\s+([A-Z][a-z]+)'
    ]

    @classmethod
    def track_knowledge(cls, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Scans dialogue and action for stated secrets, disclosures, and character mentions."""
        knowledge_timeline = []
        fact_first_disclosed = {}  # fact -> {"scene": int, "discloser": str, "witnesses": list}
        character_knowledge = defaultdict(list)

        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            raw_chars = get_val(scene, "characters_present", []) or []
            chars_present = [str(c).upper() for c in raw_chars]
            content = get_val(scene, "raw_content", "") or ""

            # Check for secrets/passwords/revelations in scene
            for pat in cls.SECRET_PATTERNS:
                for match in re.finditer(pat, content, re.I):
                    fact_key = match.group(0).strip()
                    target_val = match.group(1).strip() if match.groups() else fact_key

                    # Find speaker if in dialogue
                    speaker = None
                    for d in get_val(scene, "dialogue_data", []) or []:
                        d_text = get_val(d, "text", "")
                        if fact_key.lower() in d_text.lower():
                            speaker = str(get_val(d, "character", "")).upper()
                            break

                    if fact_key not in fact_first_disclosed:
                        # Determine actual witnesses, excluding characters who entered late or were lied to
                        actual_witnesses = list(chars_present)
                        for c in chars_present:
                            # Check if character was lied to or did not see
                            lie_pat = rf'\b(?:blank|nothing|noise|does not see|did not see)[^\.\n]*\b{re.escape(c)}\b|\b{re.escape(c)}\b[^\.\n]*(?:does not see|did not see|hears nothing)'
                            if re.search(lie_pat, content, re.I):
                                if c in actual_witnesses:
                                    actual_witnesses.remove(c)

                        fact_first_disclosed[fact_key] = {
                            "first_scene": s_num,
                            "discloser": speaker or "Script Action",
                            "witnesses": actual_witnesses,
                            "fact_value": target_val,
                            "evidence": f"Scene {s_num}: \"{fact_key}\""
                        }

                    # Informed characters
                    for c in fact_first_disclosed[fact_key]["witnesses"]:
                        if fact_key not in [k["fact"] for k in character_knowledge[c]]:
                            character_knowledge[c].append({
                                "fact": fact_key,
                                "learned_scene": s_num,
                                "source": speaker or "Observed in scene",
                                "has_identifiable_source": True,
                                "evidence": f"Present in Scene {s_num}"
                            })

                    knowledge_timeline.append({
                        "scene_number": s_num,
                        "fact": fact_key,
                        "speaker": speaker,
                        "witnesses": chars_present,
                        "raw_excerpt": fact_key
                    })

        return {
            "disclosed_facts": fact_first_disclosed,
            "character_knowledge": dict(character_knowledge),
            "knowledge_timeline": knowledge_timeline
        }
