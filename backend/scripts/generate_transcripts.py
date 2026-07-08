from faster_whisper import WhisperModel
import os

RAW_AUDIO_FOLDER = "datasets/raw_audio"
TRANSCRIPT_FOLDER = "datasets/transcripts"

os.makedirs(
    TRANSCRIPT_FOLDER,
    exist_ok=True
)

print("Loading Whisper Model...")

model = WhisperModel("medium", device="cpu", compute_type="int8")

print("Whisper Ready")

audio_files = [
    file for file in os.listdir(RAW_AUDIO_FOLDER)
    if file.endswith((".ogg", ".wav", ".mp3", ".m4a"))
]

print(f"Found {len(audio_files)} audio files")

for index, audio_file in enumerate(audio_files, start=1):

    audio_path = os.path.join(
        RAW_AUDIO_FOLDER,
        audio_file
    )

    print(f"\n[{index}/{len(audio_files)}] Processing: {audio_file}")

    segments, info = model.transcribe(
        file_path,
        beam_size=5,
        language="ur",        # Urdu model handles Punjabi far better
        initial_prompt="پیسے دیے ملے روپے ہزار سو لیے",  # Seeds model with domain vocab
        vad_filter=True,       # Silero VAD — filters out silence/noise
        vad_parameters=dict(min_silence_duration_ms=500)
    )

    transcript = " ".join(
        segment.text
        for segment in segments
    ).strip()

    transcript_filename = (
        os.path.splitext(audio_file)[0]
        + ".txt"
    )

    transcript_path = os.path.join(
        TRANSCRIPT_FOLDER,
        transcript_filename
    )

    with open(
        transcript_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(transcript)

    print("Transcript saved:")
    print(transcript)

print("\nAll transcripts generated successfully.")