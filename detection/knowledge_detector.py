import re
from typing import List, Dict, Any
from utils.helpers import get_val

class KnowledgeDetector:
    """Detects character knowledge inconsistencies where characters possess information they were never told."""

    @classmethod
    def detect(cls, scenes: List[Any], knowledge_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        issue_count = 1

        disclosed_facts = knowledge_data.get("disclosed_facts", {}) if knowledge_data else {}
        char_knowledge = knowledge_data.get("character_knowledge", {}) if knowledge_data else {}

        # Check every scene dialogue to see if a character speaks about a fact before they could know it
        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            raw_chars = get_val(scene, "characters_present", []) or []
            chars_present = [str(c).upper() for c in raw_chars]

            for d in get_val(scene, "dialogue_data", []) or []:
                speaker = str(get_val(d, "character", "")).upper()
                text = get_val(d, "text", "") or ""

                for fact_key, fact_info in disclosed_facts.items():
                    first_scene = fact_info["first_scene"]
                    fact_val = fact_info["fact_value"]

                    # Check if speaker mentions fact_val
                    if re.search(r'\b' + re.escape(fact_val) + r'\b', text, re.I):
                        # Case 1: Mentioned in a scene BEFORE the fact was established/revealed
                        if s_num < first_scene:
                            issues.append({
                                "issue_id": f"KN{issue_count:03d}",
                                "issue_type": "Knowledge Inconsistency",
                                "title": f"Premature Omniscient Knowledge: {speaker} cites '{fact_val}'",
                                "description": (
                                    f"{speaker} speaks about '{fact_val}' in Scene {s_num}, before it is first discovered "
                                    f"or established in Scene {first_scene}."
                                ),
                                "severity": "Critical",
                                "confidence": 0.96,
                                "scene_references": [s_num, first_scene],
                                "evidence": [
                                    {"scene_number": s_num, "text": f"{speaker}: \"{text}\""},
                                    {"scene_number": first_scene, "text": fact_info["evidence"]}
                                ],
                                "reasoning": (
                                    f"The classified code or event '{fact_val}' is formally uncovered in Scene {first_scene}. "
                                    f"{speaker} mentions it in Scene {s_num} without prior narrative exposure."
                                ),
                                "suggested_fix": (
                                    f"Remove the reference from Scene {s_num}, or introduce the revelation prior to Scene {s_num}."
                                )
                            })
                            issue_count += 1

                        # Case 2: Mentioned in a scene when speaker was NOT present in Scene 1 and was explicitly hidden from them
                        elif s_num >= first_scene and speaker not in fact_info["witnesses"]:
                            # Check if any scene between first_scene and s_num informed them
                            was_informed = False
                            for mid_s in (scenes or []):
                                mid_s_num = get_val(mid_s, "scene_number", 0)
                                if first_scene <= mid_s_num < s_num:
                                    mid_chars = [str(c).upper() for c in (get_val(mid_s, "characters_present", []) or [])]
                                    if speaker in mid_chars:
                                        # Someone could have told them in this scene
                                        for mid_d in (get_val(mid_s, "dialogue_data", []) or []):
                                            if re.search(r'\b' + re.escape(fact_val) + r'\b', get_val(mid_d, "text", ""), re.I):
                                                was_informed = True
                                                break
                                if was_informed:
                                    break

                            if not was_informed:
                                issues.append({
                                    "issue_id": f"KN{issue_count:03d}",
                                    "issue_type": "Knowledge Inconsistency",
                                    "title": f"Unexplained Classified Knowledge: {speaker} knows '{fact_val}'",
                                    "description": (
                                        f"{speaker} mentions or utilizes '{fact_val}' in Scene {s_num}, but was absent when "
                                        f"it was established in Scene {first_scene} and was never informed on-screen."
                                    ),
                                    "severity": "High",
                                    "confidence": 0.91,
                                    "scene_references": [first_scene, s_num],
                                    "evidence": [
                                        {"scene_number": first_scene, "text": fact_info["evidence"]},
                                        {"scene_number": s_num, "text": f"{speaker}: \"{text}\""}
                                    ],
                                    "reasoning": (
                                        f"{speaker} was not present in Scene {first_scene} when '{fact_val}' was originated, "
                                        f"and no intervening scene or dialogue line depicts another character sharing this secret with {speaker}."
                                    ),
                                    "suggested_fix": (
                                        f"Insert a line in Scene {first_scene} or an intermediate scene showing {speaker} learning or being told '{fact_val}'."
                                    )
                                })
                                issue_count += 1

            # Check action text for characters inputting/typing secret without being a witness
            action = get_val(scene, "action_text", "") or ""
            for fact_key, fact_info in disclosed_facts.items():
                first_scene = fact_info["first_scene"]
                fact_val = fact_info["fact_value"]
                if re.search(r'\b' + re.escape(fact_val) + r'\b', action, re.I):
                    for char in chars_present:
                        if char not in fact_info["witnesses"]:
                            char_action_pat = rf'\b{re.escape(char)}\b[^\.\n]*(?:types|enters|inputs|submits|writes|prompt)[^\.\n]*{re.escape(fact_val)}|types into the prompt:[^\.\n]*{re.escape(fact_val)}'
                            match = re.search(char_action_pat, action, re.I)
                            if match:
                                issues.append({
                                    "issue_id": f"KN{issue_count:03d}",
                                    "issue_type": "Knowledge Inconsistency",
                                    "title": f"Unexplained Classified Knowledge: {char} inputs '{fact_val}'",
                                    "description": (
                                        f"{char} utilizes password/code '{fact_val}' in Scene {s_num}, but was not a witness "
                                        f"when established in Scene {first_scene} and was never informed on-screen."
                                    ),
                                    "severity": "High",
                                    "confidence": 0.93,
                                    "scene_references": [first_scene, s_num],
                                    "evidence": [
                                        {"scene_number": first_scene, "text": fact_info["evidence"]},
                                        {"scene_number": s_num, "text": match.group(0).strip()}
                                    ],
                                    "reasoning": (
                                        f"{char} was concealed from '{fact_val}' in Scene {first_scene}. "
                                        f"In Scene {s_num}, {char} inputs the exact password with zero prior on-screen revelation."
                                    ),
                                    "suggested_fix": (
                                        f"Show {char} discovering or being informed of '{fact_val}' before Scene {s_num}."
                                    )
                                })
                                issue_count += 1

        return issues
