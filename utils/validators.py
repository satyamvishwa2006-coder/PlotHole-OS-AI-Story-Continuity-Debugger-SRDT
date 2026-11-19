import hashlib
from pathlib import Path
from typing import Tuple, Optional
from config.settings import settings

def validate_file_extension(filename: str) -> Tuple[bool, str]:
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
    return True, ""

def validate_file_size(size_bytes: int) -> Tuple[bool, str]:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File size ({size_bytes / (1024*1024):.1f} MB) exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE_MB} MB)."
    if size_bytes == 0:
        return False, "Uploaded file is empty (0 bytes)."
    return True, ""

def validate_extracted_text(text: str) -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, "Extracted text is empty. Document may be corrupt, password-protected, or image-only."
    word_count = len(text.split())
    if word_count < 20:
        return False, f"Document is too short ({word_count} words). Please provide a fuller script or narrative."
    return True, ""

def compute_file_hash(content_bytes: bytes) -> str:
    return hashlib.sha256(content_bytes).hexdigest()
