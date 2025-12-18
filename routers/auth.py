from datetime import datetime, timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import OTP, Users, LanguageEnum
from schemas import CreateUserRequest, Token
from utils.utils import bcrypt_context, authenticate_user, create_access_token, generate_otp, hash_otp, send_otp_sms, verify_otp_hash
from fastapi.security import OAuth2PasswordRequestForm
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import os

load_dotenv()

firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_creds:
    raise ValueError("FIREBASE_CREDENTIALS environment variable is not set!")

try:
    # Try to parse it as JSON directly (Render case)
    cred_dict = json.loads(firebase_creds)
except json.JSONDecodeError:
    # If it fails, treat it as a file path (local dev case)
    with open(firebase_creds, "r") as f:
        cred_dict = json.load(f)

cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Dependency to get DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp_registration(
    db: db_dependency,
    create_user_request: CreateUserRequest
):
    # Check if email or username already exists
    existing = db.query(Users).filter(
        or_(Users.email == create_user_request.email,
            Users.username == create_user_request.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Email or username already exists"
        )

    # Generate OTP
    otp_code = generate_otp()  # e.g., 4-digit
    otp_hashed = hash_otp(otp_code)
    expires_at = datetime.utcnow() + timedelta(minutes=5)  # 5 min expiry

    # Save OTP in DB
    otp_record = OTP(
        phone=create_user_request.phone_number,
        otp_hashed=otp_hashed,
        attempts=0,
        is_used=False,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    # Send OTP via SMS (Firebase or other provider)
    send_otp_sms(create_user_request.phone_number,
                 f"Your verification code is {otp_code}")

    return {
        "message": f"OTP sent to {create_user_request.phone_number}",
        "phone_number": create_user_request.phone_number
    }

# --------------------------
# Step 2: Verify OTP & create user
# --------------------------


@router.post("/verify-otp", status_code=status.HTTP_201_CREATED)
async def verify_otp_registration(
    db: db_dependency,
    phone_number: str = Body(...),
    otp_code: str = Body(...),
    create_user_request: CreateUserRequest = Body(...)
):
    # Get the latest OTP for this phone
    otp_record = db.query(OTP).filter(
        OTP.phone == phone_number,
        OTP.is_used == False
    ).order_by(OTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(
            status_code=400, detail="OTP not found. Please request a new one.")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired.")

    if not verify_otp_hash(otp_code, otp_record.otp_hashed):
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    # Mark OTP as used
    otp_record.is_used = True
    db.commit()

    # Create user
    hashed_password = bcrypt_context.hash(create_user_request.password)
    new_user = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=hashed_password,
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,
        is_verified=True,
        language_preference=create_user_request.language_preference or LanguageEnum.ENGLISH
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


# Login endpoint

@router.post("/token", response_model=Token)
async def login_in_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user!"
        )

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}


# Logout endpoint (placeholder)

@router.post("/logout")
async def logout_user():
    return {"message": "Logout successful"}
