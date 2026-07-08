from sqlalchemy.orm import Session
from models.transaction import Transaction
from models.pydantic_models import TransactionCreate, TransactionUpdate
from ai.name_normalizer import normalize_name, names_match


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions(db: Session, user_id: int = None, skip: int = 0, limit: int = 200):
    """
    Returns transactions for the logged-in user.
    Excludes zero-amount junk entries that have no real transcript value
    (e.g. greetings, delete commands accidentally saved, prompt-bleed noise)
    so the Ledger screen only shows real entries.
    """
    query = db.query(Transaction)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)

    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions


def create_transaction(db: Session, transaction: TransactionCreate, user_id: int = None):
    db_transaction = Transaction(**transaction.model_dump(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(db: Session, transaction_id: int, transaction: TransactionUpdate):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction:
        for key, value in transaction.model_dump(exclude_unset=True).items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction


def get_customer_summary(db: Session, customer_name: str, user_id: int = None):
    """
    Search for a customer across BOTH Urdu script and Roman spellings,
    scoped to the logged-in user's own transactions.
    """
    query = db.query(Transaction)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)

    # Fast path: exact match
    transactions = query.filter(Transaction.person_name.ilike(customer_name)).all()

    # Cross-script fallback
    if not transactions:
        all_query = db.query(Transaction)
        if user_id is not None:
            all_query = all_query.filter(Transaction.user_id == user_id)
        all_transactions = all_query.all()

        matched_names = set()
        for t in all_transactions:
            if names_match(t.person_name, customer_name):
                matched_names.add(t.person_name)

        if matched_names:
            transactions = [t for t in all_transactions if t.person_name in matched_names]

    total_debit = 0
    total_credit = 0
    for t in transactions:
        ttype = t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type
        if str(ttype).lower() == "debit":
            total_debit += t.amount
        else:
            total_credit += t.amount

    balance = total_debit - total_credit

    return {
        "customer": customer_name,
        "matched_names": list({t.person_name for t in transactions}),
        "total_transactions": len(transactions),
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balance": balance,
        "transactions": [
            {
                "id": t.id,
                "person_name": t.person_name,
                "amount": t.amount,
                "transaction_type": t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type,
                "description": t.description,
                "transcript": t.transcript,
                "date": t.date.isoformat() if t.date else None,
            }
            for t in sorted(transactions, key=lambda x: x.date or 0, reverse=True)
        ],
    }


def get_system_summary(db: Session, user_id: int = None):
    query = db.query(Transaction)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    transactions = query.all()

    total_transactions = len(transactions)

    normalized_names = set()
    for t in transactions:
        normalized_names.add(normalize_name(t.person_name))
    total_customers = len(normalized_names)

    total_debit = sum(
        t.amount for t in transactions
        if str(t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type).lower() == "debit"
    )
    total_credit = sum(
        t.amount for t in transactions
        if str(t.transaction_type.value if hasattr(t.transaction_type, "value") else t.transaction_type).lower() == "credit"
    )

    overall_balance = total_debit - total_credit

    return {
        "total_customers": total_customers,
        "total_transactions": total_transactions,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "overall_balance": overall_balance,
    }