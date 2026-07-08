"""
NLP-Only Test Script
====================
Reads transcripts from scripts/failed_files.txt (or any failed_files report)
and tests NLP extraction WITHOUT running Whisper or hitting the API.

Runs in under 5 seconds.

Usage:
    python scripts/test_nlp_only.py

To test ALL transcripts (not just failures), set READ_ALL_TRANSCRIPTS = True
"""

import sys
import os
import re

# Point to your project's ai/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai.nlp_service import extract_transaction

# ------------------------------------------------------------------ #
# CONFIG
# ------------------------------------------------------------------ #
FAILED_FILE = "scripts/failed_files.txt"

# ------------------------------------------------------------------ #
# PARSE failed_files.txt
# ------------------------------------------------------------------ #
def parse_failed_file(path: str):
    entries = []
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return entries

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Each block is separated by dashes
    blocks = content.split("-" * 40)

    for block in blocks:
        block = block.strip()
        if not block or block.startswith("FAILED"):
            continue

        entry = {}
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("File      :"):
                entry["file"] = line.split(":", 1)[1].strip()
            elif line.startswith("Transcript:"):
                entry["transcript"] = line.split(":", 1)[1].strip()
            elif line.startswith("Issue     :"):
                entry["original_issue"] = line.split(":", 1)[1].strip()
            elif line.startswith("Name      :"):
                entry["old_name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Amount    :"):
                try:
                    entry["old_amount"] = float(line.split(":", 1)[1].strip())
                except:
                    entry["old_amount"] = 0.0

        if "transcript" in entry and entry["transcript"]:
            entries.append(entry)

    return entries


# ------------------------------------------------------------------ #
# MAIN
# ------------------------------------------------------------------ #
def run():
    entries = parse_failed_file(FAILED_FILE)
    if not entries:
        print("No entries to test.")
        return

    print(f"\nTesting {len(entries)} transcripts from failed_files.txt")
    print("=" * 100)

    now_passing  = []
    still_name   = []
    still_amount = []
    still_both   = []
    prompt_bleed = []

    for e in entries:
        transcript    = e["transcript"]
        old_issue     = e.get("original_issue", "")
        old_name      = e.get("old_name", "Unknown")
        old_amount    = e.get("old_amount", 0.0)

        result = extract_transaction(transcript)
        new_name   = result["person_name"]
        new_amount = result["amount"]
        warning    = result.get("warning", "")

        if warning == "prompt_bleed":
            prompt_bleed.append(e)
            continue

        bad_amount = (new_amount == 0.0)
        bad_name   = (new_name == "Unknown")

        if bad_amount and bad_name:
            still_both.append({**e, "new_name": new_name, "new_amount": new_amount})
        elif bad_amount:
            still_amount.append({**e, "new_name": new_name, "new_amount": new_amount})
        elif bad_name:
            still_name.append({**e, "new_name": new_name, "new_amount": new_amount})
        else:
            now_passing.append({**e, "new_name": new_name, "new_amount": new_amount})

    # ---- SUMMARY ----
    total = len(entries)
    print(f"\n{'=' * 100}")
    print(f"RESULTS SUMMARY")
    print(f"{'=' * 100}")
    print(f"  Total tested            : {total}")
    print(f"  ✅ NOW PASSING          : {len(now_passing)}")
    print(f"  🔕 Prompt bleed (skipped): {len(prompt_bleed)}")
    print(f"  ❌ Still amount = 0     : {len(still_amount)}")
    print(f"  ❌ Still name unknown   : {len(still_name)}")
    print(f"  ❌ Still both failed    : {len(still_both)}")
    fixed = len(now_passing) + len(prompt_bleed)
    print(f"\n  Fixed by new NLP        : {fixed}/{total} ({fixed/total*100:.1f}%)")

    # ---- NOW PASSING ----
    if now_passing:
        print(f"\n{'=' * 100}")
        print(f"✅ NOW PASSING ({len(now_passing)})")
        print(f"{'=' * 100}")
        for r in now_passing:
            print(f"  {r['new_name']:<18} {str(r['new_amount']):<8}  ← {r['transcript'][:65]}")

    # ---- STILL FAILING ----
    still_all = still_amount + still_name + still_both
    if still_all:
        print(f"\n{'=' * 100}")
        print(f"❌ STILL FAILING ({len(still_all)}) — these transcripts need more NLP work")
        print(f"{'=' * 100}")
        print(f"  {'Issue':<12} {'Name':<18} {'Amount':<8} Transcript")
        print(f"  {'-'*90}")
        for r in still_all:
            issue = "both" if r in still_both else ("amount" if r in still_amount else "name")
            short = r["transcript"][:65]
            print(f"  {issue:<12} {r['new_name']:<18} {str(r['new_amount']):<8} {short}")

    print()


if __name__ == "__main__":
    run()