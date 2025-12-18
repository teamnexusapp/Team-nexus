from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from utils.utils import get_current_user
from schemas import MessageRequest, MessageResponse


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# ---------------- Database Dependency ----------------


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# ---------------- Chat Endpoint ----------------


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def chat_bot(
    request: MessageRequest,
    db: db_dependency,
    user: user_dependency
):
    # Fetch current user
    user_id = user["id"]
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Unauthorized!")

    try:
        # Generate localized AI reply
        language = getattr(db_user.language_preference, "value", "en")
        print(f"Generating chat reply in language: {language}")
        reply = generate_localized_insight(
            prompt=request.message,
            language=language
        )
        print(f"Reply generated (first 200 chars): {reply[:200]}...")

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {e}"
        )
