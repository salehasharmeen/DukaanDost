import re
from rapidfuzz import fuzz, process

# ================================================================
# NUMBER WORD MAPPING
# Expanded with common Punjabi pronunciation/spelling variants so
# fewer words need to rely on the fuzzy fallback at all. Roman-script
# entries kept (harmless even if rarely spoken) since they cost nothing.
# ================================================================
NUMBER_MAP = {
    "zero": 0,
    "ek": 1, "aik": 1, "one": 1, "ik": 1,
    "do": 2, "two": 2, "dou": 2,
    "teen": 3, "three": 3, "tin": 3,
    "char": 4, "four": 4, "chaar": 4,
    "panj": 5, "panch": 5, "five": 5,
    "che": 6, "chay": 6, "six": 6, "chhay": 6,
    "saat": 7, "seven": 7, "sat": 7,
    "ath": 8, "eight": 8, "aath": 8,
    "nau": 9, "nine": 9,
    "dus": 10, "ten": 10, "das": 10,
    "gyaara": 11, "eleven": 11,
    "baara": 12, "twelve": 12, "bara": 12,
    "tera": 13, "thirteen": 13,
    "choda": 14, "fourteen": 14, "chaudah": 14,
    "pandra": 15, "fifteen": 15, "pandrah": 15,
    "solah": 16, "sixteen": 16,
    "sattara": 17, "seventeen": 17,
    "athaara": 18, "eighteen": 18,
    "unnis": 19, "nineteen": 19,
    "vee": 20, "bis": 20, "twenty": 20,
    "tees": 30, "thirty": 30,
    "chaalees": 40, "forty": 40, "chalees": 40,
    "panjah": 50, "pachaas": 50, "fifty": 50,
    "saath": 60, "sixty": 60,
    "sattar": 70, "seventy": 70,
    "assi": 80, "eighty": 80,
    "nabbe": 90, "ninety": 90,

    "صفر": 0,

    "ایک": 1, "اک": 1, "اکّ": 1,

    "دو": 2, "ڈو": 2, "دوو": 2,

    "تین": 3, "تیں": 3,

    "چار": 4, "چور": 4, "چا": 4,

    "پانچ": 5, "پنج": 5, "پنچ": 5, "پانج": 5, "پنجھ": 5, "پنجہ": 5,

    "چھ": 6, "چھے": 6, "چھی": 6, "چھا": 6,

    "سات": 7, "ست": 7, "ساط": 7, "سط": 7,

    "آٹھ": 8, "اٹھ": 8, "آت": 8, "اط": 8,

    "نو": 9, "نووی": 90, "نووے": 90, "نوں ": 9,

    "دس": 10, "دص": 10,

    "گیارہ": 11, "گیاراں": 11,

    "بارہ": 12, "باراں": 12,

    "تیرہ": 13, "تیراں": 13,

    "چودہ": 14, "چوداں": 14,

    "پندرہ": 15, "پندراں": 15,

    "سولہ": 16, "سولاں": 16,

    "سترہ": 17, "ستراں": 17,

    "اٹھارہ": 18, "اٹھاراں": 18,

    "انیس": 19, "انیں": 19,

    "بیس": 20, "بیں": 20,

    "پچیس": 25, "پچیں": 25,

    "تیس": 30, "تیں ": 30,

    "پینتیس": 35,

    "چالیس": 40, "چالیں": 40,

    "پینتالیس": 45,

    "پچاس": 50, "پچپن": 55, "پنجاہ": 50,

    "ساٹھ": 60, "سٹھ": 60,

    "ستر": 70, "سٹر": 70,

    "اسی": 80, "اسّی": 80,

    "نوے": 90, "نواں": 90,
}

MULTIPLIERS = {
    "so": 100, "sau": 100, "hundred": 100, "sou": 100,
    "hazaar": 1000, "hazar": 1000, "k": 1000, "thousand": 1000,
    "lakh": 100_000, "lac": 100_000, "laakh": 100_000,
    "karod": 10_000_000, "crore": 10_000_000,

    "سو": 100, "صد": 100, "سوں": 100,

    "ہزار": 1000, "هزار": 1000, "ہذار": 1000,

    "لاکھ": 100_000, "لاک": 100_000,

    "کروڑ": 10_000_000, "کرور": 10_000_000,
}

# ================================================================
# FUSED AMOUNT TOKENS (canonical forms — known-good spellings)
# These are the "anchor" spellings. Anything NOT an exact match
# falls through to fuzzy matching against this same dictionary,
# so new Whisper misspellings are caught automatically without
# needing a manual dictionary update every time.
# ================================================================
FUSED_AMOUNTS = {
    "اکسو": 110, "اکسور": 110,
    "ڈیرسو": 150, "ڈیڑھسو": 150, "دیرسو": 150, "دیرزو": 150, "دیرزور": 150,
    "ڈھائیسو": 250, "ڈھائیسور": 250, "ڈائسو": 250, "ڈیٹسو": 250, "ٹائیسو": 250,
    "تنسو": 300, "تینسو": 300, "تنسور": 300, "تنسوڑ": 300,
    "چارسو": 400, "چیسو": 400, "چارسور": 400, "شارسو": 400,
    "پنسو": 500, "پانسو": 500, "پنسوڑ": 500, "پانسوڑ": 500,
    "پانجسو": 500, "پانسونی": 500, "تپنسو": 500, "پنجار": 500, "پنسول": 500, "پانچہ": 500,
    "پنچوڑ": 550,
    "سیسو": 600, "چھسو": 600,
    "ستسو": 700, "ستسوک": 700, "ستسوڑ": 700, "ساچھو": 700, "ساتسو": 700,
    "اٹھسو": 800, "اٹھسور": 800,
    "نوسو": 900, "نوسور": 900,
    "ستڑھ": 350, "تھاڑے": 350,
    "ڈیرہزار": 1500, "ڈیڑھہزار": 1500,
    "ڈھائیہزار": 2500,
    "اکسپلیتر": 150,
}

# How close a word must be (0-100) to a known fused-amount token
# before we trust the fuzzy match. Raised to 78 after finding that
# 72 caused false positives — e.g. the standalone word "ہزار"
# ("thousand") fuzzy-matched "ڈیرہزار" (1500) at 72.7%, corrupting
# otherwise-correct compound numbers like "دو ہزار" (2000).
FUSED_AMOUNT_FUZZY_THRESHOLD = 78

# ================================================================
# UNIFIED NUMBER/MULTIPLIER RESOLVER (long-term fix)
# ================================================================
# WHY THIS EXISTS:
# extract_word_amount() used to check `if w in NUMBER_MAP` /
# `if w in MULTIPLIERS` directly. Any Whisper misspelling not
# already an exact dictionary key (e.g. "پنچ" instead of "پنج")
# silently fell through as NO match — and because of how the
# multiplier math works (`if current == 0: current = 1`), a missed
# number word doesn't error out, it quietly produces a WRONG but
# valid-looking number (e.g. "پنچ سو" / 500 became "100"). We were
# fixing these one misspelling at a time as testing surfaced them,
# which doesn't scale — there are unlimited possible garblings.
#
# THE FIX: apply the same exact-match-then-fuzzy-match pattern
# already proven safe for FUSED_AMOUNTS (above) to NUMBER_MAP and
# MULTIPLIERS too. Every call site that resolves a word to a number
# now automatically gets fuzzy coverage, so future Whisper
# misspellings are caught without needing a manual dictionary edit
# every time. Threshold 80 was tested against real transcripts and
# correctly separates true number-words from ordinary Punjabi
# vocabulary (names, verbs, nouns) with zero false positives in
# testing — see test cases in project notes.
WORD_NUMBER_FUZZY_THRESHOLD = 80

_NUMBER_AND_MULT_KEYS = list(NUMBER_MAP.keys()) + list(MULTIPLIERS.keys())

def resolve_number_word(word: str):
    """
    Single source of truth for 'what number/multiplier does this word
    mean'. Returns (value, kind) where kind is 'number' or
    'multiplier', or (None, None) if the word isn't confidently a
    number/multiplier (e.g. it's a name, verb, or unrelated noun).
    """
    if word in NUMBER_MAP:
        return NUMBER_MAP[word], "number"
    if word in MULTIPLIERS:
        return MULTIPLIERS[word], "multiplier"

    # Skip fuzzy matching for very short words — high false-positive
    # risk on short tokens (e.g. 2-letter particles).
    if len(word) < 3:
        return None, None

    best = process.extractOne(word, _NUMBER_AND_MULT_KEYS, scorer=fuzz.ratio)
    if best and best[1] >= WORD_NUMBER_FUZZY_THRESHOLD:
        matched_key = best[0]
        if matched_key in NUMBER_MAP:
            return NUMBER_MAP[matched_key], "number"
        return MULTIPLIERS[matched_key], "multiplier"

    return None, None

# ================================================================
# INTENT: DELETE / CANCEL
# ================================================================
DELETE_KEYWORDS_URDU = [
    "ڈلیڈ", "ڈیلیٹ", "کینسل", "ختم", "ہٹاؤ", "ہٹا دو", "مٹاؤ",
    "تاہ دیو", "تاہ دو", "ڈا دیو", "ڈا دو", "غلط",
    "انٹری نہیں", "رکارڈ ڈلیڈ", "رکارڈ گلت",
]
DELETE_KEYWORDS_ROMAN = [
    "delete", "cancel", "remove", "undo", "wrong", "ghalat",
    "hatao", "mitao", "cancel karo",
]

def detect_delete_intent(text: str) -> bool:
    t = text.lower()
    for kw in DELETE_KEYWORDS_URDU:
        if kw in text:
            return True
    for kw in DELETE_KEYWORDS_ROMAN:
        if kw in t:
            return True
    return False

# ================================================================
# TRANSACTION KEYWORDS
# ================================================================
DEBIT_KEYWORDS = [
    "udhaar", "diya", "diye", "dita", "ditta", "ditay", "dittay",
    "pay", "paid", "deya", "bheje", "bheja", "send", "sent", "diti",
    "dia", "diay", "diyaa",
    "دیا", "دیے", "بھیجا", "بھیجے", "ادھار", "ادا", "دتا",
    "دیتے", "دیتا", "دے دیتا", "دے دیتے",
    "خریدے", "خریدا",
]
CREDIT_KEYWORDS = [
    "mile", "milay", "mili", "mily", "milia", "miliae", "mila",
    "received", "receive", "wapis", "jama", "vasool", "aagaye",
    "liye", "liya",
    "ملے", "ملی", "ملا", "ملیں", "واپس", "جمع", "وصول", "آگئے", "لیے", "لیا",
    "بیچے", "بیچا",
]

# ================================================================
# NAME DATA
# ================================================================
NAME_TRIGGERS_ROMAN = {"ko", "nu", "ne", "ton", "da", "de", "di", "wala", "walay", "kay", "ka", "ki", "noon"}
NAME_TRIGGERS_URDU  = {"کو", "نے", "نو", "نوں", "کا", "کی", "کے", "والا", "والے", "تون", "دا", "مو", "ڈا"}

# ================================================================
# HONORIFICS / RELATIONSHIP TERMS (long-term fix for name extraction)
# ================================================================
# Bug found: "علی بھائی نے پانچہ دیتا" (Ali-brother gave 500) — the
# word immediately before the trigger "نے" is "بھائی" (brother, a
# term of address), NOT the actual name "علی" which comes one word
# earlier. The old Strategy 2 stopped at the first word before the
# trigger regardless of whether it was a real name or just a title,
# so it picked "بھائی" instead of "علی".
#
# Fix: when walking backward from the trigger word, SKIP any word
# that is a known honorific/relationship term, continuing further
# back until a real name candidate is found. This is a small, closed
# set (titles are finite, unlike names which are effectively
# infinite) — fixing the CATEGORY of error rather than adding more
# names to a list that can never be complete.
HONORIFICS_AND_RELATIONS = {
    "بھائی", "صاحب", "صاحبہ", "باجی", "استاد", "جی", "بہن",
    "چاچا", "ماما", "خالہ", "پھپھو", "دادا", "دادی", "نانا", "نانی",
    "انکل", "آنٹی",
    "bhai", "bhaji", "sahab", "sahib", "baji", "ustad", "ji",
    "chacha", "mama", "khala", "uncle", "aunty",
}

COMMON_NAMES = {
    "ahmad", "ali", "usman", "hassan", "hussain", "bilal", "hamza", "tariq",
    "imran", "asad", "adeel", "kamran", "fahad", "zubair", "naeem", "iqbal",
    "fatima", "sara", "ayesha", "sana", "nadia", "hira", "maria", "zara",
    "amjad", "shahid", "rashid", "sajid", "waheed", "naveed", "saeed", "jameel",
    "aslam", "akram", "anwar", "tanveer", "mansoor", "zaheer", "bashir", "munir",
    "nasir", "tahir", "aamir", "waqar", "babar", "faisal", "junaid", "khalid",
    "latif", "majid", "nadeem", "pervaiz", "qasim", "riaz", "saleem", "waseem",
    "raza", "asif", "arif", "aziz", "danish", "farhan", "ghulam", "haroon",
    "irfan", "jawad", "kashif", "luqman", "mubashir", "noman", "omar", "parvez",
    "yasar", "yaser", "yasir", "nida", "needa", "zaina", "akmal",
    "bhaji", "bhai", "ustard", "ustad", "ammi",
    "احمد", "علی", "عثمان", "حسن", "حسین", "بلال", "حمزہ", "طارق",
    "عمران", "اسد", "عدیل", "کامران", "فہد", "زبیر", "نعیم", "اقبال",
    "فاطمہ", "سارہ", "عائشہ", "ثنا", "نادیہ", "حرا", "ماریہ", "زارا",
    "امجد", "شاہد", "راشد", "ساجد", "واحد", "نوید", "سعید", "جمیل",
    "اسلم", "اکرم", "انور", "تنویر", "منصور", "ظہیر", "بشیر", "منیر",
    "ناصر", "طاہر", "عامر", "وقار", "بابر", "فیصل", "جنید", "خالد",
    "یاسر", "نیدہ", "رضا", "بلال", "باجی", "استاد", "اکمل",
}

# Fuzzy threshold for matching a garbled name token (e.g. "اکھمل")
# against a known name (e.g. "اکمل"). Slightly stricter than amounts
# since names are shorter and more sensitive to false positives.
NAME_FUZZY_THRESHOLD = 80

# ================================================================
# PROMPT BLEED DETECTION
# ================================================================
PROMPT_BLEED_SIGNATURE = "پیسے دیے ملے روپے ہزار سو لیے"

def is_prompt_bleed(text: str) -> bool:
    return PROMPT_BLEED_SIGNATURE in text

# ================================================================
# WHISPER ERROR NORMALIZATION (exact known fixes — kept for speed,
# fuzzy matching below is the safety net for anything NOT in here)
# ================================================================
WHISPER_CORRECTIONS = {
    "noodho": "do", "dho": "do", "dou": "do",
    "hjaar": "hazaar", "huzar": "hazaar",
    "tausand": "hazaar", "thauzand": "hazaar",
    "mili": "mile", "mily": "mile", "milia": "mile",
    "soda": "so", "saunda": "so", "sou": "so",
    "rupees": "rupay", "rupe": "rupay", "rupee": "rupay",
    "paisay": "paise", "paisa": "paise",
    "deti": "dita", "deta": "dita", "diay": "diya",
    "sent": "bheja", "send": "bheja",
    "paid": "diya", "pay": "diya",
    "aek": "ek", "chaur": "char", "punj": "panj",
    "diyaa": "diya", "diaa": "diya",
    "milay": "mile", "milaye": "mile",
    "hazer": "hazaar", "hazzar": "hazaar",
    "lak": "lakh", "lac": "lakh",
    "kror": "karod",
    "rupaey": "rupay", "rupaye": "rupay",
}

def normalize_whisper_errors(text: str) -> str:
    words = text.split()
    return " ".join(WHISPER_CORRECTIONS.get(word, word) for word in words)

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = normalize_whisper_errors(text)
    return text

# ================================================================
# TRANSACTION TYPE DETECTION
# ================================================================
def detect_transaction_type(text: str) -> str:
    cleaned = clean_text(text)
    words = cleaned.split()
    for word in words:
        if word in DEBIT_KEYWORDS:  return "debit"
        if word in CREDIT_KEYWORDS: return "credit"
    roman_debit  = [k for k in DEBIT_KEYWORDS  if k.isascii()]
    roman_credit = [k for k in CREDIT_KEYWORDS if k.isascii()]
    roman_words  = [w for w in words if w.isascii() and len(w) > 2]
    for word in roman_words:
        best_d = process.extractOne(word, roman_debit,  scorer=fuzz.ratio)
        if best_d and best_d[1] >= 80: return "debit"
        best_c = process.extractOne(word, roman_credit, scorer=fuzz.ratio)
        if best_c and best_c[1] >= 80: return "credit"
    return "debit"

# ================================================================
# AMOUNT EXTRACTION
# ================================================================
def extract_numeric_amount(text: str):
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def extract_fused_amount(text: str):
    """
    Two-tier lookup:
      1. Exact match against FUSED_AMOUNTS (fast, zero false-positive risk)
      2. Fuzzy match against the SAME dictionary (catches new Whisper
         misspellings like پنچو -> پنسو, 500, without needing a manual
         dictionary entry for every possible variant)
    """
    words = text.split()
    sadhe_active = False

    for word in words:
        if word == "ساڑھے":
            sadhe_active = True
            continue

        # Tier 1: exact match
        if word in FUSED_AMOUNTS:
            val = FUSED_AMOUNTS[word]
            if sadhe_active:
                val += 50
                sadhe_active = False
            return float(val)

        # Tier 2: fuzzy match (only for plausible-length words that
        # are NOT already a recognized number/multiplier on their own —
        # this prevents e.g. the standalone word "ہزار" (1000) from
        # fuzzy-matching "ڈیرہزار" (1500) and corrupting compound
        # numbers like "دو ہزار" = 2000)
        if len(word) >= 3 and word not in NUMBER_MAP and word not in MULTIPLIERS:
            best = process.extractOne(word, list(FUSED_AMOUNTS.keys()), scorer=fuzz.ratio)
            if best and best[1] >= FUSED_AMOUNT_FUZZY_THRESHOLD:
                matched_key = best[0]
                val = FUSED_AMOUNTS[matched_key]
                if sadhe_active:
                    val += 50
                    sadhe_active = False
                return float(val)

        sadhe_active = False

    return None


def extract_word_amount(text: str):
    """
    NOTE on 'نو' ambiguity: in Punjabi/Urdu, 'نو' can mean either the
    digit 9 OR the grammatical particle "to/towards" (e.g. "حبیب نو" =
    "to Habib"). We cannot distinguish these by spelling alone, so as
    a practical heuristic: skip 'نو' as a number if it's the very
    FIRST word-level number token seen and is immediately preceded by
    a non-number word (likely a name) — this is the dominant real-world
    pattern ("X نو ..." = "to X ..."), and prevents it from polluting
    amount extraction when a separate real amount word appears later
    in the same sentence.

    NUMBER/MULTIPLIER RESOLUTION: uses resolve_number_word() instead of
    raw `if w in NUMBER_MAP` checks, so Whisper misspellings of number
    words are caught via fuzzy matching automatically (see resolver
    definition above for full rationale).
    """
    WEIGHT_UNITS = {"کلو", "کلوگرام", "گرام", "لیٹر", "ملی", "درجن", "پیس", "بیک", "بیگ"}
    words = text.split()
    total = 0.0
    current = 0.0
    found = False
    sadhe_pending = False

    for i, w in enumerate(words):
        if w in ("ساڑھے", "saarhe", "saadhe"):
            sadhe_pending = True
            continue
        if w in WEIGHT_UNITS:
            current = 0.0
            found = False
            continue

        # Ambiguous "نو" particle-vs-digit handling: if this is the
        # first number-like token and the previous word is NOT a
        # number/multiplier itself, treat نو as the grammatical
        # particle "to" and skip it, rather than the digit 9.
        if w == "نو" and not found and i > 0:
            prev = words[i - 1]
            if prev not in mod_number_check(prev):
                continue

        value, kind = resolve_number_word(w)
        if kind == "number":
            current += value
            found = True
        elif kind == "multiplier":
            mult = value
            if current == 0: current = 1
            if mult >= 1000:
                total += current * mult
                current = 0.0
            else:
                current *= mult
            if sadhe_pending:
                current += mult / 2
                sadhe_pending = False
            found = True

    total += current
    return float(total) if (found and total > 0) else None


def mod_number_check(word):
    """Helper: returns NUMBER_MAP/MULTIPLIERS membership set for a word check."""
    result = set()
    if word in NUMBER_MAP:
        result.add(word)
    if word in MULTIPLIERS:
        result.add(word)
    return result


def extract_amount(text: str) -> float:
    cleaned = clean_text(text)
    return (extract_numeric_amount(cleaned)
            or extract_fused_amount(cleaned)
            or extract_word_amount(cleaned)
            or 0.0)

# ================================================================
# PERSON NAME EXTRACTION
# ================================================================
_ALL_STOP = (
    {"ko","nu","ne","se","to","ton","da","di","de","liye","liyey","diya","diye",
     "diyae","ditta","ditay","dittay","milay","mile","mil","wapis","jama","rupay",
     "paise","ka","ki","kay","wala","walay","aur","bhi","udhaar","hazaar","hazar",
     "lakh","karod","crore","so","sau"}
    | {"کو","نے","سے","کا","کی","کے","والا","والے","دیا","دیے","ملے","ملا","ملی",
       "واپس","جمع","روپے","پیسے","ادھار","لیے","لیا","بھی","اور","ہزار","سو",
       "لاکھ","کروڑ","نوں","تون","مو","ڈا"}
)
_ALL_TRIGGERS = NAME_TRIGGERS_ROMAN | NAME_TRIGGERS_URDU

def _is_number_word(word: str) -> bool:
    return word in NUMBER_MAP or word in MULTIPLIERS or word in FUSED_AMOUNTS

def _format_name(word: str) -> str:
    return word.capitalize() if word.isascii() else word


def _fuzzy_match_known_name(word: str):
    """
    NEW: catches garbled name transcriptions like 'اکھمل' -> 'اکمل'.
    Only triggers for words NOT already an exact match (checked by caller),
    and requires a high similarity score to avoid false positives on
    short/common words.
    """
    if len(word) < 3:
        return None
    candidates = [n for n in COMMON_NAMES if not n.isascii()] if not word.isascii() else \
                 [n for n in COMMON_NAMES if n.isascii()]
    if not candidates:
        return None
    best = process.extractOne(word, candidates, scorer=fuzz.ratio)
    if best and best[1] >= NAME_FUZZY_THRESHOLD:
        return best[0]
    return None


def extract_person_name(text: str) -> str:
    cleaned = clean_text(text)
    words = cleaned.split()

    # Strategy 1: exact known name anywhere in sentence
    for word in words:
        if word in COMMON_NAMES or word.capitalize() in COMMON_NAMES:
            return _format_name(word)

    # Strategy 1b: FUZZY known name match (new) — catches Whisper
    # garbling a real name into something close but not exact,
    # e.g. "اکھمل" said for "اکمل" (Akmal).
    for word in words:
        if _is_number_word(word) or word in _ALL_STOP or word in _ALL_TRIGGERS:
            continue
        fuzzy_name = _fuzzy_match_known_name(word)
        if fuzzy_name:
            return _format_name(fuzzy_name)

    # Strategy 2: word immediately BEFORE a trigger word, skipping
    # past any honorific/relationship term (بھائی, صاحب, باجی, etc.)
    # to find the real name candidate underneath it.
    for i, word in enumerate(words):
        if word in _ALL_TRIGGERS and i > 0:
            j = i - 1
            while j >= 0 and words[j] in HONORIFICS_AND_RELATIONS:
                j -= 1
            if j >= 0:
                candidate = words[j]
                if not _is_number_word(candidate) and candidate not in _ALL_STOP:
                    return _format_name(candidate)

    # Strategy 3: first word that is not a number, multiplier, or stop word
    for word in words:
        if not _is_number_word(word) and word not in _ALL_STOP:
            return _format_name(word)

    return "Unknown"

# ================================================================
# DESCRIPTION GENERATION
# ================================================================
def generate_description(transaction_type: str, person_name: str, amount: float) -> str:
    if transaction_type == "debit":
        return f"Paid {amount:.0f} to {person_name}"
    elif transaction_type == "credit":
        return f"Received {amount:.0f} from {person_name}"
    return f"Entry for {person_name}"

# ================================================================
# MAIN PIPELINE
# ================================================================
def extract_transaction(text: str) -> dict:
    if is_prompt_bleed(text):
        return {
            "person_name": "Unknown",
            "amount": 0.0,
            "transaction_type": "unknown",
            "description": "Audio unclear — no transaction detected",
            "transcript": text,
            "warning": "prompt_bleed",
        }

    if detect_delete_intent(text):
        person_name = extract_person_name(text)
        return {
            "person_name": person_name,
            "amount": 0.0,
            "transaction_type": "delete",
            "description": f"Delete entry for {person_name}",
            "transcript": text,
            "warning": "delete_intent",
        }

    transaction_type = detect_transaction_type(text)
    amount           = extract_amount(text)
    person_name      = extract_person_name(text)
    description      = generate_description(transaction_type, person_name, amount)

    return {
        "person_name": person_name,
        "amount": amount,
        "transaction_type": transaction_type,
        "description": description,
        "transcript": text,
    }