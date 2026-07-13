from rapidfuzz import fuzz, process
import re

from ai.transaction_schema import IntentType
from ai.nlp_service import (
    detect_delete_intent,
    NUMBER_MAP,
    MULTIPLIERS,
)


QUERY_KEYWORDS_ROMAN = [
    "hisaab", "hisab", "balance", "ledger", "khata",
    "kitna", "kitni", "kinna", "kinni",
    "dikhao", "dikha", "dasao", "dasa",
    "wekho", "dekho", "batao",
    "show", "display", "record", "records",
    "summary", "total", "report", "baqi",
]

QUERY_KEYWORDS_URDU = [
    "حساب", "بیلنس", "کھاتہ", "کھاتا",
    "کتنا", "کتنی",
    "دکھاؤ", "دکھا",
    "بتاؤ",
    "دیکھو",
    "خلاصہ",
    "کل",
    "باقی",
    "رپورٹ",
]

UPDATE_KEYWORDS = [
    "update",
    "change",
    "replace",
    "correct",
    "edit",
    "modify",
    "بدل",
    "تبدیل",
    "درست",
]



def _is_correction(text: str) -> bool:
    """
    Detect whether the user is correcting a previous transaction.

    Examples:
    - nahi 300 nahi 500
    - no make it 500
    - 300 ki jagah 500
    - 300 ke bajaye 500
    - 300 instead 500
    """

    t = text.lower()

    correction_phrases = [
        "nahi",
        "nahi.",
        "no",
        "instead",
        "make it",
        "replace",
        "change",
        "correct",
        "ki jagah",
        "ke bajaye",
        "instead of",

        "نہیں",
        "کی جگہ",
        "کے بجائے",
        "بدل",
        "تبدیل",
        "درست",
    ]

    for phrase in correction_phrases:
        if phrase in t or phrase in text:
            return True

    return False


def _contains_number_signal(text: str) -> bool:
    words = text.lower().split()

    if any(ch.isdigit() for ch in text):
        return True

    for word in words:
        if word in NUMBER_MAP:
            return True
        if word in MULTIPLIERS:
            return True

    return False


def detect_intent(text: str) -> IntentType:

    if not text.strip():
        return IntentType.UNKNOWN

    if detect_delete_intent(text):
        return IntentType.DELETE_TRANSACTION

    text_lower = text.lower()
    words_lower = text_lower.split()
    words_raw = text.split()

    # Self-correction
    if _is_correction(text):
        return IntentType.UPDATE_TRANSACTION

    # Explicit update commands
    for keyword in UPDATE_KEYWORDS:
        if keyword in text_lower or keyword in text:
            return IntentType.UPDATE_TRANSACTION

    # Exact query match
    for keyword in QUERY_KEYWORDS_ROMAN:
        if keyword in words_lower:
            return IntentType.QUERY_BALANCE

    for keyword in QUERY_KEYWORDS_URDU:
        if keyword in words_raw:
            return IntentType.QUERY_BALANCE

    # Number present → likely transaction
    if _contains_number_signal(text):
        return IntentType.ADD_TRANSACTION

    # Fuzzy query detection
    for word in words_raw:

        if len(word) < 3:
            continue

        best = process.extractOne(
            word,
            QUERY_KEYWORDS_URDU,
            scorer=fuzz.ratio
        )

        if best and best[1] >= 80:
            return IntentType.QUERY_BALANCE

        if word.isascii():
            best = process.extractOne(
                word.lower(),
                QUERY_KEYWORDS_ROMAN,
                scorer=fuzz.ratio
            )

            if best and best[1] >= 80:
                return IntentType.QUERY_BALANCE

    return IntentType.ADD_TRANSACTION