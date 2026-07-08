"""
Batch Audio Test Script
=======================
Loops through all .wav and .ogg files in datasets/raw_audio/,
hits the /transcribe/ endpoint for each one, and prints a results table.

Flags:
  ❌ AMOUNT   → amount == 0.0
  ❌ NAME     → person_name == "Unknown"
  ✅          → everything extracted correctly

Usage:
  Make sure your FastAPI server is running first:
      uvicorn main:app --reload

  Then in a separate terminal, from your project root:
      python scripts/batch_test.py
"""

import os
import requests
import time
import random

# ------------------------------------------------------------------ #
# CONFIG — adjust if needed
# ------------------------------------------------------------------ #
API_URL       = "http://127.0.0.1:8000/transcribe/"
AUDIO_FOLDER  = "datasets/raw_audio"
SUPPORTED_EXT = (".wav", ".ogg")
DELAY_BETWEEN = 0.5   # seconds between requests (be kind to CPU)
# ------------------------------------------------------------------ #

def run_batch_test():
    audio_files = [
        f for f in os.listdir(AUDIO_FOLDER)
        if f.lower().endswith(SUPPORTED_EXT)
    ]

    if not audio_files:
        print(f"[ERROR] No .wav or .ogg files found in '{AUDIO_FOLDER}'")
        return

    audio_files.sort()
    total = len(audio_files)
    print(f"\nFound {total} audio files in '{AUDIO_FOLDER}'\n")
    print("Starting batch test... (this will take a while)\n")
    print("=" * 100)

    random.seed(42)
    audio_files = random.sample(audio_files, 50)
    audio_files.sort()

    success       = 0
    failed_amount = 0
    failed_name   = 0
    failed_both   = 0
    errors        = 0
    failures      = []

    for i, filename in enumerate(audio_files, 1):
        file_path = os.path.join(AUDIO_FOLDER, filename)

        print(f"[{i}/{total}] {filename}", end=" ... ", flush=True)

        try:
            with open(file_path, "rb") as f:
                mime = "audio/wav" if filename.lower().endswith(".wav") else "audio/ogg"
                response = requests.post(
                    API_URL,
                    files={"file": (filename, f, mime)},
                    timeout=60
                )

            if response.status_code != 200:
                print(f"HTTP {response.status_code} ❌ SERVER ERROR")
                errors += 1
                failures.append({
                    "file": filename, "issue": f"HTTP {response.status_code}",
                    "transcript": "-", "name": "-", "amount": "-", "type": "-",
                })
                continue

            data        = response.json().get("data", {})
            transcript  = data.get("transcript", "")
            person_name = data.get("person_name", "Unknown")
            amount      = data.get("amount", 0.0)
            tx_type     = data.get("transaction_type", "?")

            bad_amount = (amount == 0.0)
            bad_name   = (person_name == "Unknown")

            if bad_amount and bad_name:
                flag = "❌ AMOUNT + NAME"
                failed_both += 1
                failures.append({"file": filename, "issue": "amount+name",
                                  "transcript": transcript, "name": person_name,
                                  "amount": amount, "type": tx_type})
            elif bad_amount:
                flag = "❌ AMOUNT"
                failed_amount += 1
                failures.append({"file": filename, "issue": "amount",
                                  "transcript": transcript, "name": person_name,
                                  "amount": amount, "type": tx_type})
            elif bad_name:
                flag = "❌ NAME"
                failed_name += 1
                failures.append({"file": filename, "issue": "name",
                                  "transcript": transcript, "name": person_name,
                                  "amount": amount, "type": tx_type})
            else:
                flag = "✅"
                success += 1

            short_transcript = (transcript[:60] + "...") if len(transcript) > 60 else transcript
            print(f"{flag}")
            print(f"    Transcript : {short_transcript}")
            print(f"    Name: {person_name:<20}  Amount: {amount:<10}  Type: {tx_type}")

        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR — is the server running?")
            errors += 1
            break

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            errors += 1

        time.sleep(DELAY_BETWEEN)

    # SUMMARY
    print("\n" + "=" * 100)
    print("BATCH TEST COMPLETE")
    print("=" * 100)
    print(f"  Total files     : {total}")
    print(f"  ✅ Fully parsed  : {success}")
    print(f"  ❌ Amount = 0   : {failed_amount}")
    print(f"  ❌ Name unknown : {failed_name}")
    print(f"  ❌ Both failed  : {failed_both}")
    print(f"  ❌ Server errors: {errors}")
    print(f"  Success rate    : {success/total*100:.1f}%")

    if failures:
        print(f"\n{'=' * 100}")
        print(f"FAILED FILES ({len(failures)} total)")
        print(f"{'=' * 100}")
        print(f"{'#':<4} {'File':<35} {'Issue':<15} {'Name':<15} {'Amount':<10} {'Transcript'}")
        print("-" * 100)
        for j, f in enumerate(failures, 1):
            short = (f['transcript'][:45] + "...") if len(str(f['transcript'])) > 45 else f['transcript']
            print(f"{j:<4} {f['file']:<35} {f['issue']:<15} {str(f['name']):<15} {str(f['amount']):<10} {short}")

        output_path = "scripts/failed_files.txt"
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("FAILED FILES REPORT\n")
            out.write("=" * 80 + "\n\n")
            for f in failures:
                out.write(f"File      : {f['file']}\n")
                out.write(f"Issue     : {f['issue']}\n")
                out.write(f"Name      : {f['name']}\n")
                out.write(f"Amount    : {f['amount']}\n")
                out.write(f"Type      : {f['type']}\n")
                out.write(f"Transcript: {f['transcript']}\n")
                out.write("-" * 40 + "\n")
        print(f"\n[INFO] Failure details saved to '{output_path}'")

    print()


if __name__ == "__main__":
    run_batch_test()