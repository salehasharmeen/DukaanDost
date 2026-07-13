from ai.transaction_schema import (
    TransactionEntity,
    ValidationResult,
    TransactionType,
)


VALID_TRANSACTION_TYPES = {
    TransactionType.CREDIT,
    TransactionType.DEBIT,
}


def validate_transaction(
    transaction: TransactionEntity,
) -> ValidationResult:

    result = ValidationResult()

    # Person
    if not transaction.person_name:
        result.errors.append("Missing person name.")

    # Amount
    if transaction.amount is None:
        result.errors.append("Missing amount.")

    elif transaction.amount <= 0:
        result.errors.append("Amount must be greater than zero.")

    # Transaction type
    if transaction.transaction_type not in VALID_TRANSACTION_TYPES:
        result.errors.append("Invalid transaction type.")

    # Currency
    if not transaction.currency:
        result.warnings.append("Currency not provided.")

    result.is_valid = len(result.errors) == 0

    return result


def validate_transactions(
    transactions: list[TransactionEntity],
) -> ValidationResult:

    final_result = ValidationResult()

    for transaction in transactions:

        validation = validate_transaction(transaction)

        final_result.errors.extend(validation.errors)
        final_result.warnings.extend(validation.warnings)

    final_result.is_valid = len(final_result.errors) == 0

    return final_result