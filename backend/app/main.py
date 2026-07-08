from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from faster_whisper import WhisperModel

from ai.nlp_service import extract_transaction
from ai.query_service import process_voice_query
from ai.intent_service import detect_intent
from database.database import get_db
from models.pydantic_models import (
    TransactionCreate, SignupRequest, LoginRequest, TokenResponse,
)
from models.user import User
from services.transaction_service import (
    create_transaction,
    get_transactions,
    get_customer_summary,
    get_system_summary,
)
from services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user,
)

import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("Loading Whisper Model...")
model = WhisperModel("medium", device="cpu", compute_type="int8")
print("Whisper Ready")


# ------------------------------------------------------------------ #
#  HEALTH CHECK
# ------------------------------------------------------------------ #
@app.get("/")
def home():
    return {"message": "Punjabi Ledger Backend Running"}


# ------------------------------------------------------------------ #
#  AUTH — signup / login
# ------------------------------------------------------------------ #
@app.post("/signup", response_model=TokenResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        shop_name=req.shop_name,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token, user_id=user.id, email=user.email, shop_name=user.shop_name
    )


@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token, user_id=user.id, email=user.email, shop_name=user.shop_name
    )


# ------------------------------------------------------------------ #
#  PROFILE — get current logged-in user's info (for Profile screen)
# ------------------------------------------------------------------ #
@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "shop_name": current_user.shop_name,
    }


# ------------------------------------------------------------------ #
#  TRANSACTION ENDPOINTS — all scoped to the logged-in user
# ------------------------------------------------------------------ #
@app.get("/transactions")
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transactions(db, user_id=current_user.id)


@app.get("/customer/{customer_name}")
def customer_ledger(
    customer_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_summary(db, customer_name, user_id=current_user.id)


@app.get("/summary")
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_system_summary(db, user_id=current_user.id)


# ------------------------------------------------------------------ #
#  VOICE QUERY  (text-based)
# ------------------------------------------------------------------ #
@app.post("/voice-query/")
def voice_query(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = process_voice_query(query)
    if result["query_type"] == "customer_balance":
        return {"query_type": "customer_balance",
                "result": get_customer_summary(db, result["customer_name"], user_id=current_user.id)}
    if result["query_type"] == "all_transactions":
        transactions = get_transactions(db, user_id=current_user.id)
        return {"query_type": "all_transactions", "total": len(transactions), "data": transactions}
    return {"message": "Query not understood", "query": query}


# ------------------------------------------------------------------ #
#  UNIFIED ASSISTANT (text in -> transaction OR query out)
# ------------------------------------------------------------------ #
@app.post("/assistant/")
def assistant(
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    intent = detect_intent(text)

    if intent == "query":
        query_result = process_voice_query(text)
        if query_result["query_type"] == "customer_balance":
            customer_name = query_result.get("customer_name")
            if not customer_name:
                return {"intent": "query", "error": "Could not detect customer name"}
            return {"intent": "query", "query_type": "customer_balance",
                    "result": get_customer_summary(db, customer_name, user_id=current_user.id)}
        if query_result["query_type"] == "all_transactions":
            transactions = get_transactions(db, user_id=current_user.id)
            return {"intent": "query", "query_type": "all_transactions",
                    "total": len(transactions), "data": transactions}
        if query_result["query_type"] == "summary":
            return {"intent": "query", "query_type": "summary",
                    "result": get_system_summary(db, user_id=current_user.id)}
        return {"intent": "query", "error": "Query type not understood", "raw": text}

    extracted = extract_transaction(text)

    if extracted.get("warning") == "prompt_bleed":
        return {"intent": "unclear", "message": "Audio was unclear, please try again",
                "transcript": text}

    if extracted.get("warning") == "delete_intent":
        return {
            "intent": "delete",
            "message": f"Delete request detected for: {extracted['person_name']}",
            "person_name": extracted["person_name"],
        }

    transaction = TransactionCreate(
        person_name=extracted["person_name"],
        amount=extracted["amount"],
        transaction_type=extracted["transaction_type"],
        description=extracted["description"],
        transcript=extracted["transcript"],
    )
    saved = create_transaction(db, transaction, user_id=current_user.id)
    return {"intent": "transaction", "transaction_id": saved.id, "data": extracted}


# ------------------------------------------------------------------ #
#  AUDIO TRANSCRIPTION + TRANSACTION SAVE
# ------------------------------------------------------------------ #
@app.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    segments, info = model.transcribe(
        file_path,
        beam_size=5,
        language="ur",
        initial_prompt="پیسے دیے ملے روپے ہزار سو لیے",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    transcript = " ".join(segment.text for segment in segments).strip()

    print("\n====================")
    print("TRANSCRIPT:", transcript)
    print("====================\n")

    intent = detect_intent(transcript)

    if intent == "query":
        query_result = process_voice_query(transcript)

        if query_result["query_type"] == "customer_balance":
            customer_name = query_result.get("customer_name")
            if not customer_name:
                return {"intent": "query", "error": "Could not detect customer name",
                        "transcript": transcript}
            return {"intent": "query", "query_type": "customer_balance",
                    "result": get_customer_summary(db, customer_name, user_id=current_user.id),
                    "transcript": transcript}

        if query_result["query_type"] == "all_transactions":
            transactions = get_transactions(db, user_id=current_user.id)
            return {"intent": "query", "query_type": "all_transactions",
                    "total": len(transactions), "data": transactions, "transcript": transcript}

        if query_result["query_type"] == "summary":
            return {"intent": "query", "query_type": "summary",
                    "result": get_system_summary(db, user_id=current_user.id),
                    "transcript": transcript}

        return {"intent": "query", "error": "Query type not understood", "transcript": transcript}

    extracted = extract_transaction(transcript)

    if extracted.get("warning") == "prompt_bleed":
        return {"message": "Audio unclear, nothing saved", "transcript": transcript,
                "warning": "prompt_bleed", "intent": "unclear"}

    if extracted.get("warning") == "delete_intent":
        return {"message": "Delete command detected",
                "person_name": extracted["person_name"],
                "warning": "delete_intent", "intent": "delete"}

    transaction = TransactionCreate(
        person_name=extracted["person_name"],
        amount=extracted["amount"],
        transaction_type=extracted["transaction_type"],
        description=extracted["description"],
        transcript=extracted["transcript"],
    )
    saved_transaction = create_transaction(db, transaction, user_id=current_user.id)
    return {"message": "Transaction saved successfully",
            "transaction_id": saved_transaction.id, "data": extracted,
            "intent": "transaction"}