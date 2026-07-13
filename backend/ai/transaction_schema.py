from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    ADD_TRANSACTION = "ADD_TRANSACTION"
    QUERY_BALANCE = "QUERY_BALANCE"
    UPDATE_TRANSACTION = "UPDATE_TRANSACTION"
    DELETE_TRANSACTION = "DELETE_TRANSACTION"
    UNKNOWN = "UNKNOWN"


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    UNKNOWN = "unknown"


class NormalizedTranscript(BaseModel):
    raw_text: str
    normalized_text: str
    language: str = "unknown"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TransactionEntity(BaseModel):
    person_name: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: TransactionType = TransactionType.UNKNOWN
    item: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    payment_mode: Optional[str] = None
    currency: str = "PKR"
    transaction_date: Optional[str] = None
    description: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class AmbiguityResult(BaseModel):
    needs_followup: bool = False
    question: Optional[str] = None
    missing_fields: List[str] = Field(default_factory=list)


class TransactionUnderstanding(BaseModel):
    raw_text: str

    normalized_text: str

    intent: IntentType = IntentType.UNKNOWN

    transactions: List[TransactionEntity] = Field(default_factory=list)

    validation: ValidationResult = Field(default_factory=ValidationResult)

    ambiguity: AmbiguityResult = Field(default_factory=AmbiguityResult)

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)