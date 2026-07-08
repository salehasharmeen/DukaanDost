import re
from rapidfuzz import fuzz, process

# -----------------------------
# QUERY KEYWORD LISTS
# Kept in sync with ai/intent_service.py — same words, same fuzzy tolerance,
# same exact-match-on-word-tokens fix, same number-signal gating.
# -----------------------------

BALANCE_KEYWORDS_ROMAN = [
    "hisaab", "hisab", "balance", "khata", "ledger",
    "kitna", "kitni", "kinna", "kinni", "baqi", "baaqui",
]

BALANCE_KEYWORDS_URDU = [
    "حساب", "بیلنس", "کھاتہ", "کھاتا", "کتنا", "کتنی", "باقی", "دکھاتا",
]

ALL_TRANSACTION_KEYWORDS_ROMAN = [
    "transactions", "entries", "record", "records",
    "summary", "total", "report", "sab", "saara", "tamam",
]

ALL_TRANSACTION_KEYWORDS_URDU = [
    "خلاصہ", "کل", "رپورٹ", "سب", "سارا", "تمام",
]

# Same number/multiplier gate as intent_service.py — if present,
# fuzzy query-type matching is skipped (see detect_query_type below).
NUMBER_OR_MULTIPLIER_WORDS = {
    "صفر", "ایک", "اک", "اکّ", "دو", "ڈو", "دوو", "تین", "تیں",
    "چار", "چور", "چا", "پانچ", "پنج", "پنچ", "پانج", "پنجھ", "پنجہ",
    "چھ", "چھے", "چھی", "چھا", "سات", "ست", "ساط", "سط",
    "آٹھ", "اٹھ", "آت", "اط", "نو", "نووی", "نووے",
    "دس", "دص", "گیارہ", "گیاراں", "بارہ", "باراں", "تیرہ", "تیراں",
    "چودہ", "چوداں", "پندرہ", "پندراں", "سولہ", "سولاں", "سترہ", "ستراں",
    "اٹھارہ", "اٹھاراں", "انیس", "انیں", "بیس", "بیں", "پچیس", "پچیں",
    "تیس", "پینتیس", "چالیس", "چالیں", "پینتالیس",
    "پچاس", "پچپن", "پنجاہ", "ساٹھ", "سٹھ", "ستر", "سٹر",
    "اسی", "اسّی", "نوے", "نواں",
    "سو", "صد", "سوں", "ہزار", "هزار", "ہذار", "لاکھ", "لاک",
    "کروڑ", "کرور",
    "ek", "aik", "ik", "do", "dou", "teen", "tin", "char", "chaar",
    "panj", "panch", "che", "chay", "chhay", "saat", "sat", "ath",
    "aath", "nau", "dus", "das",
    "so", "sau", "sou", "hazaar", "hazar", "k", "lakh", "lac",
    "laakh", "karod", "crore",
}

# Words to skip when extracting a customer name from a query
QUERY_STOP_WORDS_ROMAN = {
    "da", "de", "di", "hisaab", "hisab", "balance", "khata", "ledger",
    "dikhao", "dikha", "dasao", "dasa", "wekho", "dekho", "batao",
    "show", "display", "ka", "ki", "kay", "nu", "ko", "ne", "ton",
    "kitna", "kitni", "kinna", "kinni", "baqi", "wala", "walay",
}

QUERY_STOP_WORDS_URDU = {
    "کا", "کی", "کے", "کو", "نے", "سے", "ڈا",
    "حساب", "بیلنس", "کھاتہ", "کھاتا", "دکھاؤ", "بتاؤ", "دیکھو", "دکھاتا", "کھاو",
    "کتنا", "کتنی", "باقی", "و",
}


# -----------------------------
# HELPERS
# -----------------------------

def clean_query(text: str) -> str:
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_number_signal(text: str) -> bool:
    if re.search(r"\d", text):
        return True
    words = text.lower().split()
    return any(w in NUMBER_OR_MULTIPLIER_WORDS for w in words)


def extract_customer_name_from_query(text: str):
    cleaned = clean_query(text.lower())
    words_lower = cleaned.split()
    original_words = clean_query(text).split()

    TRIGGER_WORDS = {"da", "de", "di", "ka", "ki", "kay", "nu", "ko", "ne",
                     "کا", "کی", "کے", "کو", "نے", "دا", "ڈا"}

    all_stop = QUERY_STOP_WORDS_ROMAN | QUERY_STOP_WORDS_URDU

    for i, word in enumerate(words_lower):
        if word in TRIGGER_WORDS and i > 0:
            candidate = original_words[i - 1]
            candidate_lower = words_lower[i - 1]
            if candidate_lower not in all_stop:
                return candidate.capitalize() if candidate.isascii() else candidate

    for i, word in enumerate(words_lower):
        if word not in all_stop:
            candidate = original_words[i]
            return candidate.capitalize() if candidate.isascii() else candidate

    return None


# -----------------------------
# QUERY TYPE DETECTION
# Uses the SAME exact-on-word-tokens + number-gated-fuzzy approach as
# intent_service.py, so the two stay aligned: if detect_intent() says
# "query", this function should virtually always find a matching
# query_type too — and if detect_intent() says "transaction" (because
# of a number signal), this function will independently agree.
# -----------------------------

def detect_query_type(text: str) -> str:
    words_lower = text.lower().split()
    words_raw   = text.split()

    # 1. EXACT match on WORD TOKENS — not substring-in-whole-string.
    #    (Same fix as intent_service.py: avoids e.g. a longer word
    #    that merely contains a keyword as a substring.)
    for keyword in BALANCE_KEYWORDS_ROMAN:
        if keyword in words_lower:
            return "customer_balance"
    for keyword in BALANCE_KEYWORDS_URDU:
        if keyword in words_raw:
            return "customer_balance"

    for keyword in ALL_TRANSACTION_KEYWORDS_ROMAN:
        if keyword in words_lower:
            return "all_transactions"
    for keyword in ALL_TRANSACTION_KEYWORDS_URDU:
        if keyword in words_raw:
            return "all_transactions"

    # 2. Number-signal gate — if the sentence states an amount, it's
    #    almost certainly not a query (queries ask ABOUT amounts, they
    #    don't usually STATE one). Skip fuzzy matching entirely in
    #    that case to avoid e.g. "کلو" (kilogram) fuzzy-matching "کل"
    #    (total) and misclassifying a real transaction.
    if has_number_signal(text):
        return "unknown"

    # 3. Fuzzy fallback — Urdu (catches Whisper noise like کھاتا/دکھاتا
    #    variants). Threshold 80, min length 3 — matches
    #    intent_service.py, since short words like "دا"/"تنیا" were
    #    false-matching at 65-75%.
    for word in words_raw:
        if len(word) < 3:
            continue

        best_balance_urdu = process.extractOne(word, BALANCE_KEYWORDS_URDU, scorer=fuzz.ratio)
        if best_balance_urdu and best_balance_urdu[1] >= 80:
            return "customer_balance"

        best_all_urdu = process.extractOne(word, ALL_TRANSACTION_KEYWORDS_URDU, scorer=fuzz.ratio)
        if best_all_urdu and best_all_urdu[1] >= 80:
            return "all_transactions"

        if word.isascii():
            best_balance_roman = process.extractOne(word, BALANCE_KEYWORDS_ROMAN, scorer=fuzz.ratio)
            if best_balance_roman and best_balance_roman[1] >= 80:
                return "customer_balance"

            best_all_roman = process.extractOne(word, ALL_TRANSACTION_KEYWORDS_ROMAN, scorer=fuzz.ratio)
            if best_all_roman and best_all_roman[1] >= 80:
                return "all_transactions"

    return "unknown"


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------

def process_voice_query(text: str) -> dict:
    query_type = detect_query_type(text)
    customer_name = extract_customer_name_from_query(text)

    return {
        "query_type": query_type,
        "customer_name": customer_name,
        "original_query": text,
    }



 