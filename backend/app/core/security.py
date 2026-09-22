import re


def sanitize_text(text: str) -> str:
    """Strip dangerous characters and normalize whitespace."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
