import io
from pathlib import Path
from typing import Dict, Any, Tuple
import pypdf
import docx
from utils.validators import validate_file_extension, validate_file_size, validate_extracted_text, compute_file_hash
from utils.text_cleaner import clean_script_text

class DocumentProcessor:
    """Processes PDF, DOCX, and TXT files, extracting raw text and metadata."""
    
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extracts text from PDF bytes using pypdf."""
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n\n".join(pages_text)

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extracts text from DOCX bytes using python-docx."""
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs_text = [p.text for p in doc.paragraphs if p.text]
        return "\n\n".join(paragraphs_text)

    @staticmethod
    def extract_text_from_txt(file_bytes: bytes) -> str:
        """Extracts text from TXT bytes, testing multiple encodings."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
        for enc in encodings:
            try:
                return file_bytes.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        # Fallback with replacement
        return file_bytes.decode("utf-8", errors="replace")

    @classmethod
    def process_file(cls, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """Main entry point: validates file, extracts text, cleans, and computes statistics."""
        # 1. Validate extension
        valid_ext, ext_err = validate_file_extension(filename)
        if not valid_ext:
            return {"success": False, "error": ext_err}

        # 2. Validate size
        valid_size, size_err = validate_file_size(len(file_bytes))
        if not valid_size:
            return {"success": False, "error": size_err}

        # 3. Extract text according to extension
        ext = Path(filename).suffix.lower()
        try:
            if ext == ".pdf":
                raw_extracted = cls.extract_text_from_pdf(file_bytes)
            elif ext == ".docx":
                raw_extracted = cls.extract_text_from_docx(file_bytes)
            elif ext == ".txt":
                raw_extracted = cls.extract_text_from_txt(file_bytes)
            else:
                return {"success": False, "error": f"Unsupported format: {ext}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract text from {filename}: {str(e)}"}

        # 4. Clean text
        cleaned_text = clean_script_text(raw_extracted)

        # 5. Validate text content
        valid_text, text_err = validate_extracted_text(cleaned_text)
        if not valid_text:
            return {"success": False, "error": text_err}

        # 6. Compute statistics
        words = cleaned_text.split()
        word_count = len(words)
        char_count = len(cleaned_text)
        file_hash = compute_file_hash(file_bytes)

        # Rough scene estimation based on headers or double line-breaks
        import re
        scene_heading_pattern = r'^(?:INT\.|EXT\.|INT\/EXT\.|I\/E\.|SCENE\s+\d+|CHAPTER\s+\d+)'
        headings = re.findall(scene_heading_pattern, cleaned_text, flags=re.MULTILINE | re.IGNORECASE)
        estimated_scenes = max(1, len(headings))

        return {
            "success": True,
            "filename": filename,
            "file_type": ext.lstrip(".").upper(),
            "file_size_bytes": len(file_bytes),
            "raw_text": cleaned_text,
            "word_count": word_count,
            "char_count": char_count,
            "estimated_scenes": estimated_scenes,
            "file_hash": file_hash
        }
