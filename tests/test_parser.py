import pytest
from core.script_parser import ScriptParser
from core.scene_extractor import SceneExtractor
from utils.text_cleaner import clean_script_text
from utils.validators import validate_file_extension, validate_file_size

SAMPLE_SCREENPLAY_SNIPPET = """
SCENE 1
INT. LAB - DAY
Dr. Aris types on the keyboard.

SARAH
The test is complete.

EXT. STREET - NIGHT
Rain falls heavily on the asphalt. Marcus waits in the shadows.
"""

PROSE_SNIPPET = """
Chapter One

Sarah walked into the archive room. The books were dusty and old. She opened the dossier and searched for Marcus's name.

Two hours later, Marcus arrived at the front entrance. He carried the heavy metal briefcase.
"""

def test_file_extension_validation():
    valid, _ = validate_file_extension("script.pdf")
    assert valid is True
    valid, _ = validate_file_extension("script.txt")
    assert valid is True
    valid, _ = validate_file_extension("script.docx")
    assert valid is True
    invalid, err = validate_file_extension("script.exe")
    assert invalid is False
    assert "Unsupported file type" in err

def test_file_size_validation():
    valid, _ = validate_file_size(1024)
    assert valid is True
    invalid_empty, err = validate_file_size(0)
    assert invalid_empty is False
    assert "empty" in err

def test_text_cleaner():
    raw = "INT. ROOM\r\n\r\n\r\n\r\n\r\nPage 1\nMarcus speaks: “Hello”—it's time."
    cleaned = clean_script_text(raw)
    assert "“" not in cleaned
    assert '"Hello"' in cleaned
    assert " - " in cleaned

def test_screenplay_parser():
    scenes = ScriptParser.parse_script(SAMPLE_SCREENPLAY_SNIPPET)
    assert len(scenes) >= 2
    assert scenes[0]["scene_number"] == 1
    assert "LAB" in scenes[0]["location_name"] or "INT" in scenes[0]["int_ext"]
    assert len(scenes[0]["dialogue_data"]) >= 1
    assert scenes[0]["dialogue_data"][0]["character"] == "SARAH"

def test_prose_parser():
    scenes = ScriptParser.parse_script(PROSE_SNIPPET)
    assert len(scenes) >= 1
    assert "PROSE" in scenes[0]["location_name"] or "SCENE" in scenes[0]["heading"]
