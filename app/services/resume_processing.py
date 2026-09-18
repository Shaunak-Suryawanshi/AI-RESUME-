"""Deterministic, local first-pass processing for resume PDFs.

This does not claim to understand a resume like an LLM.  It extracts text and
applies transparent rules, which makes the output predictable and explainable.
"""
import re
from pathlib import Path

from pypdf import PdfReader


SECTION_HEADERS = {
    "summary": "summary",
    "professional summary": "summary",
    "profile": "summary",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "education": "education",
    "skills": "skills",
    "technical skills": "skills",
    "projects": "projects",
    "certifications": "certifications",
}

KNOWN_SKILLS = (
    "Python", "Flask", "Django", "FastAPI", "SQL", "PostgreSQL", "MySQL",
    "SQLite", "REST API", "Git", "Docker", "Linux", "AWS", "Azure",
    "Kubernetes", "Redis", "Celery", "JavaScript", "React", "HTML", "CSS",
    "Pandas", "NumPy", "scikit-learn", "Machine Learning", "TensorFlow",
    "PyTorch", "Java", "C++", "C", "Data Structures", "Algorithms",
)


class ResumeProcessingError(Exception):
    """Raised when a submitted PDF cannot yield usable text."""


def extract_pdf_text(file_path: str | Path) -> str:
    try:
        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as error:
        raise ResumeProcessingError("Unable to read this PDF") from error
    if not text.strip():
        raise ResumeProcessingError(
            "No selectable text was found. This may be a scanned image PDF."
        )
    return text


def clean_resume_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_section = "other"
    sections[current_section] = []
    for line in text.splitlines():
        normalized = re.sub(r"[:\s]+$", "", line.strip().lower())
        if normalized in SECTION_HEADERS and len(line.strip()) <= 50:
            current_section = SECTION_HEADERS[normalized]
            sections.setdefault(current_section, [])
        else:
            sections[current_section].append(line)
    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
        if "\n".join(lines).strip()
    }


def extract_skills(text: str) -> list[str]:
    found = []
    for skill in KNOWN_SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)
    return found


def process_resume_file(file_path: str | Path) -> dict:
    raw_text = extract_pdf_text(file_path)
    cleaned_text = clean_resume_text(raw_text)
    return {
        "extracted_text": cleaned_text,
        "sections": extract_sections(cleaned_text),
        "skills": extract_skills(cleaned_text),
    }
