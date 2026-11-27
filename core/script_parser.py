import re
from typing import List, Dict, Any, Optional, Tuple

class ScriptParser:
    """Parses screenplay text into structured scenes, headings, actions, dialogues, and characters.
    Supports both formal industry screenplay syntax and free-form prose story formats."""

    # Heading patterns
    SCENE_HEADING_REGEX = re.compile(
        r'^(?:(?P<number>\d+[\.:\s-]+)?\s*'
        r'(?P<type>INT\./EXT\.|EXT\./INT\.|INT\/EXT|INT|EXT|I\/E)\.?\s+'
        r'(?P<location>[^-–\n]+)'
        r'(?:[-–]\s*(?P<time>DAY|NIGHT|DUSK|DAWN|LATER|CONTINUOUS|SAME|MORNING|EVENING|AFTERNOON|[^\n]+))?'
        r'|^(?P<alt_num>SCENE\s+\d+|CHAPTER\s+\d+|ACT\s+[IVX]+)[\.:\s-]*(?P<alt_title>[^\n]*))',
        re.IGNORECASE | re.MULTILINE
    )

    # Character cue in screenplay (ALL CAPS on its own line, possibly with (V.O.) or (O.S.))
    CHARACTER_CUE_REGEX = re.compile(
        r'^[ \t]*([A-Z0-9_\-\.\'\s]{2,30}?)(?:\s*\((?:V\.O\.|O\.S\.|CONT\'D|CONTINUED|WHISPERING|BEAT|[^\)]+)\))?[ \t]*$',
        re.MULTILINE
    )

    # Common words that are NOT character names even if capitalized
    STOP_WORDS = {
        "FADE IN", "FADE OUT", "FADE TO BLACK", "CUT TO", "DISSOLVE TO", "MATCH CUT",
        "BACK TO", "THE END", "CONTINUED", "CONTINUOUS", "TITLE", "SUPER", "BLACK",
        "MOMENTS LATER", "INTERCUT", "SCENE", "ACT", "CHAPTER", "NOTE", "CLOSE ON",
        "WIDE SHOT", "ANGLE ON", "POV", "FLASHBACK", "END FLASHBACK", "MONTAGE", "VOICE", "AUDIO",
        "DOOR", "ROOM", "WINDOW", "ALARM", "COMPUTER", "PHONE", "CAR", "GUN",
        "TABLE", "DESK", "LIGHT", "LIGHTS", "WALL", "FLOOR", "CAMERA", "CLOSE",
        "ANGLE", "SHOT", "WIDE", "INSERT", "SFX", "VFX", "SOUND", "BEAT", "PAUSE",
        "MORNING", "NIGHT", "DAY", "EVENING", "AFTERNOON", "DUSK", "DAWN", "LATER",
        "SAME", "TIME", "INT", "EXT", "END", "OFFICE", "HALLWAY", "BUILDING", "STREET"
    }

    @classmethod
    def parse_script(cls, script_text: str) -> List[Dict[str, Any]]:
        """Splits the script into structured scene dictionaries."""
        lines = script_text.splitlines()
        scenes_data = []
        
        # 1. Detect heading indices
        heading_matches = []
        for idx, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            match = cls.SCENE_HEADING_REGEX.match(line_clean)
            if match:
                heading_matches.append((idx, line_clean, match))

        # Merge separate "SCENE X" labels directly preceding "INT./EXT." headings
        merged_matches = []
        skip_next = False
        for idx, (l_idx, line_clean, match) in enumerate(heading_matches):
            if skip_next:
                skip_next = False
                continue
            if match.group("alt_num") and idx + 1 < len(heading_matches):
                next_l_idx, next_line_clean, next_match = heading_matches[idx + 1]
                if next_l_idx - l_idx <= 3 and next_match.group("type"):
                    combined_heading = f"{line_clean} - {next_line_clean}"
                    merged_matches.append((l_idx, combined_heading, next_match))
                    skip_next = True
                    continue
            merged_matches.append((l_idx, line_clean, match))
        heading_matches = merged_matches

        # Fallback if no conventional scene headings found: Prose / Story mode
        if not heading_matches:
            return cls._parse_prose_story(script_text)

        # 2. Slice scenes between headings
        for i, (start_idx, heading_line, match) in enumerate(heading_matches):
            end_idx = heading_matches[i + 1][0] if i + 1 < len(heading_matches) else len(lines)
            scene_lines = lines[start_idx:end_idx]
            scene_content = "\n".join(scene_lines)

            # Extract components from heading
            int_ext = "INT"
            location = "UNKNOWN"
            time_of_day = "DAY"
            
            if match.group("type"):
                int_ext = match.group("type").upper().replace("/", "/").rstrip(".")
                location = (match.group("location") or "UNKNOWN").strip()
                time_of_day = (match.group("time") or "DAY").strip().upper()
            elif match.group("alt_num"):
                int_ext = "INT/EXT"
                location = (match.group("alt_title") or match.group("alt_num")).strip() or "UNKNOWN"
                time_of_day = "DAY"

            # Skip any leading heading lines to get scene body
            body_start = 0
            while body_start < len(scene_lines) and (not scene_lines[body_start].strip() or cls.SCENE_HEADING_REGEX.match(scene_lines[body_start].strip())):
                body_start += 1
            dialogues, action_text, characters_present = cls._parse_scene_body(scene_lines[body_start:])

            # Search for explicit time references in action (e.g., "10:00 PM", "TUESDAY", "TWO HOURS LATER")
            time_ref = cls._extract_time_reference(scene_content, time_of_day)

            scenes_data.append({
                "scene_number": i + 1,
                "heading": heading_line,
                "int_ext": int_ext,
                "location_name": location,
                "time_of_day": time_of_day,
                "raw_content": scene_content,
                "action_text": action_text,
                "dialogue_data": dialogues,
                "characters_present": list(set(characters_present)),
                "time_reference": time_ref,
                "word_count": len(scene_content.split()),
                "is_customized": False
            })

        return scenes_data

    @classmethod
    def _parse_scene_body(cls, body_lines: List[str]) -> Tuple[List[Dict[str, str]], str, List[str]]:
        """Parses the body of a scene into dialogue blocks, action text, and present characters."""
        dialogues = []
        action_lines = []
        characters = set()

        i = 0
        while i < len(body_lines):
            line = body_lines[i]
            line_str = line.strip()

            if not line_str:
                i += 1
                continue

            # Check if this line is a character cue
            is_char_cue = False
            char_match = cls.CHARACTER_CUE_REGEX.match(line_str)
            if char_match:
                name_candidate = char_match.group(1).strip().upper()
                # Ensure it's not a stop word and not an action sentence
                if (name_candidate not in cls.STOP_WORDS and 
                    len(name_candidate) >= 2 and 
                    not any(punct in name_candidate for punct in [".", ",", "!", "?", ":", ";"]) and
                    len(name_candidate.split()) <= 4):
                    is_char_cue = True

            if is_char_cue:
                char_name = char_match.group(1).strip().upper()
                characters.add(char_name)
                i += 1
                parenthetical = ""
                dialogue_text_parts = []

                # Collect optional parenthetical and subsequent dialogue lines
                while i < len(body_lines):
                    next_line = body_lines[i].strip()
                    if not next_line:
                        # Empty line usually concludes dialogue block
                        i += 1
                        break
                    if next_line.startswith("(") and next_line.endswith(")"):
                        parenthetical = next_line[1:-1].strip()
                    elif cls.CHARACTER_CUE_REGEX.match(next_line):
                        # Another character begins immediately
                        break
                    elif cls.SCENE_HEADING_REGEX.match(next_line):
                        break
                    else:
                        dialogue_text_parts.append(next_line)
                    i += 1

                dialogue_content = " ".join(dialogue_text_parts).strip()
                if dialogue_content or parenthetical:
                    dialogues.append({
                        "character": char_name,
                        "text": dialogue_content,
                        "parenthetical": parenthetical
                    })
            else:
                # It is an action line
                action_lines.append(line_str)
                # Also detect named entities in action (e.g. SARAH walks in)
                words = re.findall(r'\b[A-Z]{2,20}\b', line_str)
                for w in words:
                    if w not in cls.STOP_WORDS and len(w) > 2:
                        characters.add(w)
                i += 1

        return dialogues, "\n".join(action_lines), list(characters)

    @classmethod
    def _parse_prose_story(cls, text: str) -> List[Dict[str, Any]]:
        """Fallback parser for prose stories, novels, or scripts without conventional INT/EXT headers."""
        # Split by double newlines or chapter/section indicators
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        scenes_data = []

        # Group paragraphs into logical scenes (every ~3-5 paragraphs or whenever time/location changes)
        chunk_size = 4
        current_scene_paragraphs = []
        scene_idx = 1

        for p in paragraphs:
            current_scene_paragraphs.append(p)
            # Check for explicit scene transition markers
            has_transition = bool(re.search(r'^(?:Later|Meanwhile|The next day|Hours later|Chapter|Scene|Part)', p, re.I))
            if (len(current_scene_paragraphs) >= chunk_size) or (has_transition and len(current_scene_paragraphs) > 1):
                scene_content = "\n\n".join(current_scene_paragraphs)
                first_line = current_scene_paragraphs[0][:60]
                
                # Detect characters from capitalized names
                names = set(re.findall(r'\b[A-Z][a-z]{2,15}\b', scene_content))
                
                scenes_data.append({
                    "scene_number": scene_idx,
                    "heading": f"SCENE {scene_idx} - {first_line}...",
                    "int_ext": "INT/EXT",
                    "location_name": "PROSE NARRATIVE",
                    "time_of_day": "DAY",
                    "raw_content": scene_content,
                    "action_text": scene_content,
                    "dialogue_data": [],
                    "characters_present": list(names)[:8],
                    "time_reference": cls._extract_time_reference(scene_content, "DAY"),
                    "word_count": len(scene_content.split()),
                    "is_customized": False
                })
                scene_idx += 1
                current_scene_paragraphs = []

        if current_scene_paragraphs:
            scene_content = "\n\n".join(current_scene_paragraphs)
            names = set(re.findall(r'\b[A-Z][a-z]{2,15}\b', scene_content))
            scenes_data.append({
                "scene_number": scene_idx,
                "heading": f"SCENE {scene_idx} - Narrative Continuation",
                "int_ext": "INT/EXT",
                "location_name": "PROSE NARRATIVE",
                "time_of_day": "DAY",
                "raw_content": scene_content,
                "action_text": scene_content,
                "dialogue_data": [],
                "characters_present": list(names)[:8],
                "time_reference": cls._extract_time_reference(scene_content, "DAY"),
                "word_count": len(scene_content.split()),
                "is_customized": False
            })

        return scenes_data

    @staticmethod
    def _extract_time_reference(content: str, default_time: str) -> str:
        """Finds explicit time stamps like 10:00 PM, 9:30 AM, 'two hours earlier', 'next day'."""
        clock_match = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\b', content)
        if clock_match:
            return clock_match.group(1).upper()
        
        rel_match = re.search(
            r'\b((?:two|three|four|five|\d+)\s+(?:hours?|days?|minutes?|weeks?|months?|years?)\s+(?:earlier|later|prior|before|after))\b',
            content,
            re.I
        )
        if rel_match:
            return rel_match.group(1)

        day_match = re.search(r'\b(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)\b', content, re.I)
        if day_match:
            return f"{day_match.group(1).upper()} - {default_time}"

        return default_time
