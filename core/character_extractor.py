import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from utils.helpers import get_val

class CharacterExtractor:
    """Extracts characters, analyzes dialogue frequency, appearance span,
    explicit traits from introduction parentheticals/action lines, and relationships."""

    # Stop words that should never be marked as characters
    STOP_CHARACTERS = {
        "FADE", "CUT", "THE", "SCENE", "CONTINUED", "TITLE", "SUPER", "BLACK",
        "VOICE", "AUDIO", "RADIO", "ANNOUNCER", "MAN", "WOMAN", "PEOPLE", "CROWD",
        "DOOR", "ROOM", "WINDOW", "ALARM", "COMPUTER", "PHONE", "CAR", "GUN",
        "TABLE", "DESK", "LIGHT", "LIGHTS", "WALL", "FLOOR", "CAMERA", "CLOSE",
        "ANGLE", "POV", "SHOT", "WIDE", "INSERT", "SFX", "VFX", "SOUND",
        "MORNING", "NIGHT", "DAY", "EVENING", "AFTERNOON", "DUSK", "DAWN", "LATER",
        "SAME", "TIME", "INT", "EXT", "END", "FLASHBACK", "MONTAGE", "OFFICE",
        "HALLWAY", "BUILDING", "STREET", "ALLEY", "POLICE", "GUARD", "GUARDS",
        "BEAT", "PAUSE", "SILENCE", "MOMENTS", "LATER", "HOURS", "MINUTES"
    }

    @classmethod
    def extract_characters(cls, scenes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts characters and character relationships across all scenes."""
        char_dialogue_counts = defaultdict(int)
        char_scenes = defaultdict(list)
        char_dialogue_samples = defaultdict(list)
        char_actions = defaultdict(list)
        explicit_traits_map = defaultdict(list)

        # 1. Gather scene-level appearances and dialogue
        for idx, scene in enumerate(scenes or []):
            s_num = get_val(scene, "scene_number", idx + 1)
            # Look at dialogue lines
            for d in get_val(scene, "dialogue_data", []) or []:
                char = str(get_val(d, "character", "")).strip().upper()
                if char in cls.STOP_CHARACTERS or len(char) < 2:
                    continue
                char_dialogue_counts[char] += 1
                if s_num not in char_scenes[char]:
                    char_scenes[char].append(s_num)
                d_text = get_val(d, "text", "")
                if len(char_dialogue_samples[char]) < 3 and d_text:
                    char_dialogue_samples[char].append(f"Scene {s_num}: \"{d_text[:120]}\"")

            # Look at explicit character introductions in action text
            action = get_val(scene, "action_text", "") or ""
            for line in action.splitlines():
                intro_match = re.search(r'\b([A-Z]{2,25}(?:\s+[A-Z]{2,25})?)\s*\(([^)]+)\)', line)
                if intro_match:
                    name = intro_match.group(1).strip().upper()
                    details = intro_match.group(2).strip()
                    if name not in cls.STOP_CHARACTERS:
                        explicit_traits_map[name].append(details)
                        if s_num not in char_scenes[name]:
                            char_scenes[name].append(s_num)

            # Record prominent actions
            for char_name in get_val(scene, "characters_present", []) or []:
                char_clean = str(char_name).strip().upper()
                if char_clean not in cls.STOP_CHARACTERS:
                    if s_num not in char_scenes[char_clean]:
                        char_scenes[char_clean].append(s_num)

        # 2. Build structured character profiles
        characters_list = []
        for char_name, scenes_list in char_scenes.items():
            scenes_list.sort()
            first_s = scenes_list[0] if scenes_list else 1
            last_s = scenes_list[-1] if scenes_list else 1
            diag_count = char_dialogue_counts.get(char_name, 0)
            samples = char_dialogue_samples.get(char_name, [])
            explicit = explicit_traits_map.get(char_name, [])

            # Deterministic traits based on actions and descriptions
            inferred = []
            if diag_count > 5:
                inferred.append("Prominent Speaker / Central Agent")
            elif diag_count == 0:
                inferred.append("Non-speaking / Background Presence")
            if len(scenes_list) > 3:
                inferred.append("Core Narrative Anchor")

            characters_list.append({
                "name": char_name,
                "first_appearance_scene": first_s,
                "last_appearance_scene": last_s,
                "total_scenes": len(scenes_list),
                "dialogue_count": diag_count,
                "personality_traits": explicit + inferred,
                "explicit_traits": explicit,
                "inferred_traits": inferred,
                "motivations": ["Pursuing narrative objective"] if diag_count > 2 else [],
                "goals": ["Resolve scene conflicts"],
                "important_actions": [f"Present in Scenes {', '.join(map(str, scenes_list[:6]))}"],
                "dialogue_samples": samples,
                "known_information": [f"Aware of events in Scene {s}" for s in scenes_list],
                "notes": f"Active across {len(scenes_list)} scene(s)."
            })

        # Sort characters by total scenes & dialogue count descending
        characters_list.sort(key=lambda x: (x["total_scenes"], x["dialogue_count"]), reverse=True)

        # 3. Build relationships based on co-occurrence in scenes
        relationships = cls._build_relationships(characters_list, scenes)

        return characters_list, relationships

    @classmethod
    def _build_relationships(
        cls,
        characters: List[Dict[str, Any]],
        scenes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculates co-occurrences and dialogue exchanges between characters."""
        co_occurrences = defaultdict(int)
        dialogue_exchanges = defaultdict(int)

        for scene in scenes or []:
            present = get_val(scene, "characters_present", []) or []
            # Co-occurrence
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    c1, c2 = sorted([str(present[i]).upper(), str(present[j]).upper()])
                    co_occurrences[(c1, c2)] += 1

            # Direct dialogue back-and-forth
            diags = get_val(scene, "dialogue_data", []) or []
            for k in range(len(diags) - 1):
                speaker1 = str(get_val(diags[k], "character", "")).upper()
                speaker2 = str(get_val(diags[k+1], "character", "")).upper()
                if speaker1 and speaker2 and speaker1 != speaker2:
                    pair = tuple(sorted([speaker1, speaker2]))
                    dialogue_exchanges[pair] += 1

        top_names = {get_val(c, "name", "") for c in (characters or [])[:12]}
        relationships = []

        for (c1, c2), count in co_occurrences.items():
            if c1 in top_names and c2 in top_names and count >= 1:
                exchanges = dialogue_exchanges.get((c1, c2), 0)
                rel_type = "Frequent Collaborators" if exchanges > 2 else "Scene Co-occupants"
                sentiment = "Positive" if exchanges > 3 else "Neutral"

                relationships.append({
                    "source_character": c1,
                    "target_character": c2,
                    "relationship_type": rel_type,
                    "interaction_count": count + exchanges,
                    "sentiment": sentiment,
                    "description": f"Shared {count} scene(s) with {exchanges} direct dialogue interaction(s)."
                })

        return relationships
