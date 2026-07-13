import re

from ai.transaction_schema import NormalizedTranscript
from ai.nlp_service import clean_text


def is_urdu(text: str) ->bool:
    """
    Returns True if the text contains Urdu script.
    """
    return bool(re.search(r"[\u0600-\u06FF]", text))


def detect_language(text: str) -> str:
    """
    Detect the dominant language/script.
    """

    has_urdu = is_urdu(text)
    has_english = bool(re.search(r"[a-zA-Z]", text))

    if has_urdu and has_english:
        return "mixed"

    if has_urdu:
        return "urdu"

    if has_english:
        return "roman"

    return "unknown"


def normalize_text(text: str) -> str:
    """
    Cleans the transcript so every downstream AI module
    receives standardized text.
    """

    return clean_text(text)


def normalize_transcript(text: str) -> NormalizedTranscript:
    """
    Entry point for the normalization stage.
    """

    normalized = normalize_text(text)

    return NormalizedTranscript(
        raw_text=text,
        normalized_text=normalized,
        language=detect_language(text),
        confidence=1.0
    )