from ai.transaction_schema import (
    TransactionEntity,
    AmbiguityResult,
)


def detect_ambiguity(
    transactions: list[TransactionEntity],
) -> AmbiguityResult:
    """
    Checks whether the extracted transactions contain enough
    information to be safely stored.

    Returns a follow-up question if clarification is needed.
    """

    if not transactions:
        return AmbiguityResult(
            needs_followup=True,
            question="I couldn't understand the transaction. Can you say it again?",
            missing_fields=["transaction"],
        )

    for tx in transactions:

        # Missing person
        if not tx.person_name:
            return AmbiguityResult(
                needs_followup=True,
                question="Who is this transaction for?",
                missing_fields=["person_name"],
            )

        # Missing amount
        if tx.amount is None or tx.amount <= 0:
            return AmbiguityResult(
                needs_followup=True,
                question="How much was the transaction?",
                missing_fields=["amount"],
            )

        # Missing transaction type
        if tx.transaction_type.value == "unknown":
            return AmbiguityResult(
                needs_followup=True,
                question="Was this money given or received?",
                missing_fields=["transaction_type"],
            )

    return AmbiguityResult(
        needs_followup=False,
        question=None,
        missing_fields=[],
    )