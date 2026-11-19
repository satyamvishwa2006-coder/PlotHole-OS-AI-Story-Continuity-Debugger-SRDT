import re
import unicodedata

def clean_script_text(raw_text: str) -> str:
    """Normalizes script text, fixing encoding issues, non-standard quotes,
    page numbering artifacts, and excessive whitespace while preserving screenplay structure."""
    if not raw_text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKD", raw_text)
    
    # Replace curly quotes and apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("—", " - ").replace("–", " - ")
    
    # Standardize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Remove common page number patterns like "Page 1", "1.", "12 / 80" at line beginnings/ends
    text = re.sub(r'^(?:Page|\d+)\s*(?:of|\/)?\s*\d*\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove excessive blank lines (> 3 consecutive newlines -> 2)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    return text.strip()

def strip_formatting_artifacts(text: str) -> str:
    """Removes non-ascii characters and weird formatting artifacts from OCR or PDF extracts."""
    # Retain standard ascii + common punctuation
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Collapse multiple inline spaces
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()
