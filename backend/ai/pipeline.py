from ai.normalizer import normalize_transcript
from ai.intent_service import detect_intent
from ai.llm_parser import parse_transaction
from ai.validator import validate_transactions
from ai.ambiguity import detect_ambiguity


def process_transaction(transcript: str):
    """
    Main AI pipeline.

    Flow:

    Transcript
        ↓
    Normalization
        ↓
    Intent Detection
        ↓
    LLM Parsing
        ↓
    Validation
        ↓
    Ambiguity Detection
    """

    # Step 1
    normalized = normalize_transcript(transcript)

    # Step 2
    intent = detect_intent(normalized.normalized_text)

    # Step 3
    transactions = parse_transaction(normalized.normalized_text)

    # Step 4
    validation = validate_transactions(transactions)

    # Step 5
    ambiguity = detect_ambiguity(transactions)

    return {
        "normalized": normalized,
        "intent": intent,
        "transactions": transactions,
        "validation": validation,
        "ambiguity": ambiguity,
    }

