"""
Name Normalizer
================
Converts Urdu/Punjabi script names to a normalized Roman form
so customer search works regardless of which script the original
voice transcript used.

This does NOT do full linguistic transliteration (that's a much
bigger NLP problem) — it does practical phonetic mapping for the
common name characters seen in your dataset, which covers the
vast majority of real shopkeeper customer names.
"""

import re

# Character-level Urdu -> Roman phonetic mapping
# Covers common name-building characters seen in your dataset
URDU_CHAR_MAP = {
    "ا": "a", "آ": "aa", "ب": "b", "پ": "p", "ت": "t", "ٹ": "t",
    "ث": "s", "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d",
    "ڈ": "d", "ذ": "z", "ر": "r", "ڑ": "r", "ز": "z", "ژ": "zh",
    "س": "s", "ش": "sh", "ص": "s", "ض": "z", "ط": "t", "ظ": "z",
    "ع": "a", "غ": "gh", "ف": "f", "ق": "q", "ک": "k", "گ": "g",
    "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "o", "ہ": "h",
    "ھ": "h", "ء": "", "ی": "i", "ے": "e", "ئ": "i",
}

# Known common names — exact mapping takes priority over
# character-by-character conversion (much more accurate)
KNOWN_NAME_MAP = {
    "اکمل": "akmal", "علی": "ali", "احمد": "ahmad", "عثمان": "usman",
    "حسن": "hassan", "حسین": "hussain", "بلال": "bilal", "حمزہ": "hamza",
    "طارق": "tariq", "عمران": "imran", "اسد": "asad", "عدیل": "adeel",
    "کامران": "kamran", "فہد": "fahad", "زبیر": "zubair", "نعیم": "naeem",
    "اقبال": "iqbal", "فاطمہ": "fatima", "سارہ": "sara", "عائشہ": "ayesha",
    "ثنا": "sana", "نادیہ": "nadia", "حرا": "hira", "ماریہ": "maria",
    "زارا": "zara", "امجد": "amjad", "شاہد": "shahid", "راشد": "rashid",
    "ساجد": "sajid", "واحد": "waheed", "نوید": "naveed", "سعید": "saeed",
    "جمیل": "jameel", "اسلم": "aslam", "اکرم": "akram", "انور": "anwar",
    "تنویر": "tanveer", "منصور": "mansoor", "ظہیر": "zaheer", "بشیر": "bashir",
    "منیر": "munir", "ناصر": "nasir", "طاہر": "tahir", "عامر": "aamir",
    "وقار": "waqar", "بابر": "babar", "فیصل": "faisal", "جنید": "junaid",
    "خالد": "khalid", "باجی": "baji", "استاد": "ustad", "صاحب": "sahab",
    "زینہ": "zeena", "زینب": "zainab", "نیدہ": "needa", "یاسر": "yasir",
}


def normalize_name(name: str) -> str:
    """
    Convert a name (Urdu script or Roman) into a normalized
    lowercase Roman form for consistent searching.
    """
    if not name:
        return ""

    name = name.strip()

    # Already Roman/ASCII — just lowercase it
    if name.isascii():
        return name.lower()

    # Known exact match — most accurate
    if name in KNOWN_NAME_MAP:
        return KNOWN_NAME_MAP[name]

    # Fallback: character-by-character phonetic conversion
    result = []
    for char in name:
        result.append(URDU_CHAR_MAP.get(char, ""))
    return "".join(result).lower()


def names_match(name1: str, name2: str, threshold: int = 80) -> bool:
    """
    Fuzzy-match two names after normalization.
    Used for customer search across scripts.
    """
    from rapidfuzz import fuzz
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2:
        return False
    return fuzz.ratio(n1, n2) >= threshold


if __name__ == "__main__":
    # Quick tests
    tests = [
        ("اکمل", "akmal"),
        ("علی", "ali"),
        ("باجی", "baji"),
        ("زینہ", "zeena"),
    ]
    for urdu, expected in tests:
        result = normalize_name(urdu)
        status = "✅" if result == expected else "❌"
        print(f"{status} normalize_name('{urdu}') = '{result}' (expected '{expected}')")

    print()
    print("Match test:", names_match("اکمل", "akmal"))
    print("Match test:", names_match("اکمل", "akmel"))  # typo tolerance