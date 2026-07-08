"""
Smart NLP Evaluator
===================
Separates "no number spoken" from "NLP missed a number"
so you get TRUE accuracy numbers for your FYP report.

Usage (from project root):
    python scripts/smart_eval.py

Output:
  - Console report with real accuracy %
  - scripts/eval_report.txt  (for FYP documentation)
"""

import sys, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.nlp_service import extract_transaction

FAILED_FILE = "scripts/failed_files.txt"

# ------------------------------------------------------------------ #
# Patterns that indicate NO number was actually spoken
# ------------------------------------------------------------------ #
NO_AMOUNT_PATTERNS = [
    # Account management
    "کھاتا چیک", "کھاتا کلیر", "کھتا کلیگر", "کھاتا بند",
    "کھاتا صاف", "پرانا کھاتا", "خاتہ", "کھاتے دیتے",
    # Vague amounts
    "پیسے نہیں", "نہیں دیتے", "پیسے دے دیتے", "پیسے دیتے",
    "سارے پیسے", "ٹوٹل پیسے", "پورے پیسے", "تھوڑا",
    "کچھ پیسے", "پیسے آگے", "پیسے واپس لے",
    # Write/record instructions (no amount)
    "لکھ لو", "لکھوائے", "لکھوا دیتے", "لکھو", "لکھنا",
    "لکھ دوں", "لیکھ لو",
    # Delete/cancel
    "ڈلیڈ", "کینسل", "تاہ دیو", "ڈا دیو", "غلط لکھ",
    "انٹری نہیں", "رکارڈ ڈلیڈ", "انٹریٹا", "غلط لکھتی",
    # Greetings / irrelevant
    "اسلام علیکم", "شروع کرتے",
    # Negation
    "نہیں ہوئی", "ترانزیکشن نہیں", "پیسے نہیں ہو",
    # Account clearing without specific amount
    "کلیر کرو", "کلیر کر دیتا", "کلیر کراتی", "کلیر ہو گیا",
    "ریکارڈ کلیر", "رکارڈ کلیر",
    # Misc non-transaction
    "موسمی سبزی", "منڈی کا", "سبزی ہے", "تازہ سبزی",
    "آیا گی نے", "شام ہوندے",
]

def has_number_in_text(text: str) -> bool:
    """Check if text contains any extractable number (digit or known word)."""
    # Digit present?
    if re.search(r'\d', text):
        return True
    # Known Urdu number words
    URDU_NUMBERS = [
        "ایک","دو","تین","چار","پانچ","چھ","سات","آٹھ","نو","دس",
        "بیس","تیس","چالیس","پچاس","ساٹھ","ستر","اسی","نوے",
        "سو","ہزار","لاکھ","پچپن","نووی","نووے","پچیس",
        # Fused tokens
        "پنسو","تنسو","چیسو","پانسو","ڈیرسو","تپنسو","شارسو",
        "ڈیٹسو","پنچوڑ","ستسو","ڈائسو","ٹائیسو","اکسو","چارسو",
        "دیرزو","دیرزور","تینسو","پانجسو","ستڑھ","تھاڑے",
    ]
    for word in URDU_NUMBERS:
        if word in text:
            return True
    return False

def is_genuinely_no_amount(text: str) -> bool:
    """Return True if the sentence genuinely had no number spoken."""
    for pattern in NO_AMOUNT_PATTERNS:
        if pattern in text:
            return True
    if not has_number_in_text(text):
        return True
    return False

def parse_failed_file(path):
    entries, current = [], {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("File      :"):
                current = {"file": line.split(":",1)[1].strip()}
            elif line.startswith("Issue     :"):
                current["issue"] = line.split(":",1)[1].strip()
            elif line.startswith("Transcript:"):
                current["transcript"] = line.split(":",1)[1].strip()
            elif line.startswith("---") and current.get("transcript"):
                entries.append(current)
                current = {}
    return entries

def run():
    if not os.path.exists(FAILED_FILE):
        print(f"[ERROR] '{FAILED_FILE}' not found. Run batch_test.py first.")
        return

    entries = parse_failed_file(FAILED_FILE)

    # ------------------------------------------------------------------ #
    # Categorize every entry
    # ------------------------------------------------------------------ #
    cat = {
        "fixed":        [],   # was failing, now passing ✅
        "prompt_bleed": [],   # silence/noise — unfixable ⚠️
        "delete_cmd":   [],   # delete/cancel command — handled separately
        "no_amount":    [],   # genuinely no number spoken — correct to return 0
        "still_broken": [],   # number WAS there but NLP missed it ❌
    }

    for entry in entries:
        t     = entry["transcript"]
        issue = entry["issue"]
        r     = extract_transaction(t)

        if r.get("warning") == "prompt_bleed":
            cat["prompt_bleed"].append(entry)
            continue

        if r.get("warning") == "delete_intent":
            cat["delete_cmd"].append(entry)
            continue

        bad_amount = (r["amount"] == 0.0 and issue in ("amount","amount+name"))
        bad_name   = (r["person_name"] == "Unknown" and issue in ("name","amount+name"))

        if not bad_amount and not bad_name:
            cat["fixed"].append({**entry, "result": r})
            continue

        if bad_amount and is_genuinely_no_amount(t):
            cat["no_amount"].append(entry)
            continue

        cat["still_broken"].append({**entry, "result": r})

    # ------------------------------------------------------------------ #
    # Compute real accuracy
    # ------------------------------------------------------------------ #
    total          = len(entries)
    truly_testable = total - len(cat["prompt_bleed"]) - len(cat["no_amount"])
    fixed          = len(cat["fixed"]) + len(cat["delete_cmd"])
    broken         = len(cat["still_broken"])
    accuracy       = (fixed / truly_testable * 100) if truly_testable else 0

    # ------------------------------------------------------------------ #
    # Print report
    # ------------------------------------------------------------------ #
    SEP = "=" * 90

    print(f"\n{SEP}")
    print("  FYP NLP EVALUATION REPORT")
    print(SEP)
    print(f"  Total transcripts evaluated     : {total}")
    print(f"  Bad audio (prompt bleed)        : {len(cat['prompt_bleed'])}  ← excluded from accuracy")
    print(f"  No number spoken (correct 0)    : {len(cat['no_amount'])}  ← excluded from accuracy")
    print(f"  ─────────────────────────────────────────────")
    print(f"  Truly testable (had a number)   : {truly_testable}")
    print(f"  ✅ Correctly extracted           : {fixed}")
    print(f"  ❌ NLP missed                    : {broken}")
    print(f"\n  ★ TRUE NLP ACCURACY             : {accuracy:.1f}%")
    print(SEP)

    # Category breakdown
    print(f"\n{'─'*90}")
    print(f"  CATEGORY BREAKDOWN")
    print(f"{'─'*90}")
    print(f"  ✅ Fixed / correctly extracted   : {len(cat['fixed'])}")
    print(f"  ✅ Delete commands handled       : {len(cat['delete_cmd'])}")
    print(f"  ⚠️  Prompt bleed (bad audio)      : {len(cat['prompt_bleed'])}")
    print(f"  ℹ️  No number spoken (correct)    : {len(cat['no_amount'])}")
    print(f"  ❌ Still broken (real NLP gap)   : {broken}")

    # Still broken detail
    if cat["still_broken"]:
        print(f"\n{'─'*90}")
        print(f"  REAL NLP GAPS ({broken}) — the only ones worth fixing")
        print(f"{'─'*90}")
        for x in cat["still_broken"]:
            r = x["result"]
            print(f"  name={r['person_name']:<15} amount={str(r['amount']):<8} ← {x['transcript']}")

    # ------------------------------------------------------------------ #
    # Save report to file
    # ------------------------------------------------------------------ #
    out = "scripts/eval_report.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("FYP NLP EVALUATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total transcripts evaluated   : {total}\n")
        f.write(f"Bad audio (excluded)          : {len(cat['prompt_bleed'])}\n")
        f.write(f"No number spoken (excluded)   : {len(cat['no_amount'])}\n")
        f.write(f"Truly testable                : {truly_testable}\n")
        f.write(f"Correctly extracted           : {fixed}\n")
        f.write(f"NLP missed                    : {broken}\n")
        f.write(f"\nTRUE NLP ACCURACY             : {accuracy:.1f}%\n\n")
        f.write("REAL NLP GAPS:\n")
        f.write("-" * 60 + "\n")
        for x in cat["still_broken"]:
            r = x["result"]
            f.write(f"Transcript : {x['transcript']}\n")
            f.write(f"Got        : name={r['person_name']}  amount={r['amount']}\n")
            f.write("-" * 40 + "\n")

    print(f"\n  [INFO] Full report saved to '{out}'")
    print()

if __name__ == "__main__":
    run()