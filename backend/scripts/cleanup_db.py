"""
Database Cleanup Script
========================
Lists all transactions and lets you delete bad/test entries
(e.g. ones with null person_name, null created_at, or amount=0
from early Swagger testing) before your demo.

Usage (from project root, backend venv activated):
    python scripts/cleanup_db.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal
from models.transaction import Transaction

def list_all():
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).order_by(Transaction.id).all()
        print(f"\nFound {len(transactions)} total transactions\n")
        print(f"{'ID':<5} {'Name':<15} {'Amount':<10} {'Type':<8} {'Created At':<25} {'Transcript'}")
        print("-" * 110)
        for t in transactions:
            name      = t.person_name or "NULL"
            amount    = t.amount if t.amount is not None else "NULL"
            ttype     = t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type
            created   = str(t.date) if t.date else "NULL"
            transcript = (t.transcript[:40] + "...") if t.transcript and len(t.transcript) > 40 else (t.transcript or "")
            print(f"{t.id:<5} {name:<15} {str(amount):<10} {str(ttype):<8} {created:<25} {transcript}")
        return transactions
    finally:
        db.close()


def find_bad_entries():
    """
    Find entries that are TRULY junk — not just zero-amount.
    Many zero-amount transcripts are legitimate demo data
    (e.g. real Punjabi sentences the NLP correctly extracted
    a name from, just no number was spoken). Those are KEPT.

    Only flags entries that are:
      - Completely missing name/date/type (actual data corruption)
      - Pure noise transcripts (very short, no real words)
      - Explicit test/delete/cancel command transcripts
    """
    JUNK_PHRASES = [
        "ڈلیڈ", "کینسل", "تاہ دیو", "ڈا دیو", "غلط لکھتی",
        "انٹری نہیں", "رکارڈ ڈلیڈ", "انٹریٹا", "رکارڈ گلت",
        "اسلام علیکم", "ترانزیکشن نہیں", "دلیڈ کر دو",
        "پیسے دیے ملے روپے ہزار سو لیے",  # whisper prompt bleed signature
    ]

    db = SessionLocal()
    try:
        transactions = db.query(Transaction).all()
        bad = []
        for t in transactions:
            issues = []
            transcript = t.transcript or ""

            # Real corruption — these are genuinely broken records
            if not t.person_name or t.person_name.strip() == "":
                issues.append("missing name")
            if not t.date:
                issues.append("missing date")
            if not t.transaction_type:
                issues.append("missing type")

            # Junk transcripts — delete/cancel commands, prompt bleed, greetings
            if any(phrase in transcript for phrase in JUNK_PHRASES):
                issues.append("junk/command transcript")

            # Very short noise (less than 3 words, no real content)
            if len(transcript.split()) <= 2 and t.amount == 0:
                issues.append("too short / noise")

            if issues:
                bad.append((t, issues))
        return bad
    finally:
        db.close()


def delete_by_ids(ids: list[int]):
    db = SessionLocal()
    try:
        deleted = 0
        for tid in ids:
            t = db.query(Transaction).filter(Transaction.id == tid).first()
            if t:
                db.delete(t)
                deleted += 1
        db.commit()
        print(f"\n[INFO] Deleted {deleted} transactions.")
    finally:
        db.close()


def delete_all():
    db = SessionLocal()
    try:
        count = db.query(Transaction).delete()
        db.commit()
        print(f"\n[INFO] Deleted ALL {count} transactions. Fresh start.")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  DATABASE CLEANUP TOOL")
    print("=" * 60)

    list_all()

    bad = find_bad_entries()
    if bad:
        print(f"\n{'=' * 60}")
        print(f"  FOUND {len(bad)} LIKELY BAD/TEST ENTRIES")
        print(f"{'=' * 60}")
        for t, issues in bad:
            print(f"  ID {t.id}: {', '.join(issues)}  ← {t.transcript or '(no transcript)'}")

    print(f"\n{'=' * 60}")
    print("  OPTIONS")
    print(f"{'=' * 60}")
    print("  1. Delete only the bad entries listed above")
    print("  2. Delete specific IDs (you type them)")
    print("  3. Delete ALL transactions (fresh start for demo)")
    print("  4. Do nothing, just exit")

    choice = input("\nChoose an option (1-4): ").strip()

    if choice == "1":
        if bad:
            ids = [t.id for t, _ in bad]
            confirm = input(f"Delete {len(ids)} bad entries? (y/yes/no): ").strip().lower()
            if confirm in ("y", "yes"):
                delete_by_ids(ids)
            else:
                print("Cancelled, nothing deleted.")
        else:
            print("No bad entries found.")

    elif choice == "2":
        raw = input("Enter IDs separated by commas (e.g. 3,7,12): ").strip()
        ids = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
        confirm = input(f"Delete IDs {ids}? (y/yes/no): ").strip().lower()
        if confirm in ("y", "yes"):
            delete_by_ids(ids)
        else:
            print("Cancelled, nothing deleted.")

    elif choice == "3":
        confirm = input("Type 'DELETE ALL' to confirm wiping the entire table: ").strip()
        if confirm == "DELETE ALL":
            delete_all()
        else:
            print("Cancelled.")

    else:
        print("No changes made.")

    print("\nDone. Run this script again anytime to check your data.\n")