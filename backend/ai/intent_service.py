import re
from rapidfuzz import fuzz, process


def detect_intent(text: str) -> str:
    """
    Detect whether the input is a QUERY (asking for info)
    or a TRANSACTION (recording a ledger entry).

    Uses fuzzy matching because Whisper transcription of Urdu/Punjabi
    is noisy — the same spoken word can come out as slightly different
    spellings each time (e.g. "حساب" vs "حصاب", "دکھاؤ" vs "دکھائو").
    Exact string matching misses these; fuzzy matching catches them.

    TWO LONG-TERM FIXES BAKED IN HERE (see comments below):
      1. Exact matching now checks WORD TOKENS, not raw substrings.
         (Bug found: "بتاؤں" contains "بتاؤ" as a literal substring,
         so the old `if keyword in text` check misclassified plain
         transaction sentences that merely happened to contain a
         longer word built on a query verb's root.)
      2. Fuzzy matching is skipped entirely if the sentence contains
         any recognized number/multiplier word. Real transactions
         almost always state an amount; real queries almost never do.
         This prevents short, common Punjabi words (e.g. "کلو" =
         kilogram) from fuzzy-matching short query keywords (e.g.
         "کل" = total) and misrouting real transactions.
    """

    QUERY_KEYWORDS_ROMAN = [
        "hisaab", "hisab", "balance", "ledger", "khata",
        "kitna", "kitni", "kinna", "kinni",
        "dikhao", "dikha", "dasao", "dasa", "wekho", "dekho", "batao",
        "show", "display", "record", "records",
        "summary", "total", "report", "baqi", "baaqui",
    ]

    QUERY_KEYWORDS_URDU = [
        "حساب", "بیلنس", "کھاتہ", "کھاتا", "کتنا", "کتنی",
        "دکھاؤ", "دکھا", "بتاؤ", "دیکھو", "دکھاتا",
        "خلاصہ", "کل", "باقی", "رپورٹ",
    ]

    # Any word that means a number or a multiplier. Used as a gate:
    # if present, this sentence is very likely a transaction, so we
    # don't let an ambiguous fuzzy keyword match override that.
    # Kept as a flat set here (rather than importing from
    # ai/nlp_service.py) to keep intent_service.py independent, as
    # in the existing architecture — update both files together if
    # new number-word variants are added to nlp_service.py.
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

    text_lower = text.lower()
    words_lower = text_lower.split()
    words_raw   = text.split()

    # 1. EXACT match on WORD TOKENS — not substring-in-whole-string.
    #    Fixes false positives like "بتاؤں" matching "بتاؤ".
    for keyword in QUERY_KEYWORDS_ROMAN:
        if keyword in words_lower:
            return "query"

    for keyword in QUERY_KEYWORDS_URDU:
        if keyword in words_raw:
            return "query"

    # 2. If a number/multiplier word is present, trust it strongly:
    #    skip fuzzy matching and classify as transaction. This avoids
    #    short common words (e.g. "کلو") fuzzy-matching short query
    #    keywords (e.g. "کل") and misrouting real transactions.
    has_number_signal = bool(re.search(r"\d", text)) or any(
        w in NUMBER_OR_MULTIPLIER_WORDS for w in words_lower
    )
    if has_number_signal:
        return "transaction"

    # 3. Fuzzy fallback — catches Whisper misspellings of query verbs
    #    (e.g. "حصاب" vs "حساب"). Only reached when no number word
    #    is present, since a genuine query rarely states an amount.
    #    Length >= 3 and threshold 80 avoid false positives on short
    #    common grammatical particles (دا/تنیا/etc).
    for word in words_raw:
        if len(word) < 3:
            continue

        best_urdu = process.extractOne(word, QUERY_KEYWORDS_URDU, scorer=fuzz.ratio)
        if best_urdu and best_urdu[1] >= 80:
            return "query"

        if word.isascii():
            best_roman = process.extractOne(word, QUERY_KEYWORDS_ROMAN, scorer=fuzz.ratio)
            if best_roman and best_roman[1] >= 80:
                return "query"

    return "transaction"