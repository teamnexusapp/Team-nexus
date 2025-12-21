from datetime import datetime, timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import OTP, PendingUser, Users, LanguageEnum
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
        or_(
            Users.email == create_user_request.email,
            Users.username == create_user_request.username
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )

    otp_code = generate_otp()
    otp_hashed = hash_otp(otp_code)
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    try:
        # Clear previous OTPs
        db.query(OTP).filter(
            OTP.phone == create_user_request.phone_number,
            OTP.is_used == False
        ).delete()

        # Clear previous pending registrations
        db.query(PendingUser).filter(
            PendingUser.phone_number == create_user_request.phone_number
        ).delete()

        # Create OTP
        otp_record = OTP(
            phone=create_user_request.phone_number,
            otp_hashed=otp_hashed,
            attempts=0,
            is_used=False,
            expires_at=expires_at
        )
        db.add(otp_record)

        # Create pending user
        pending_user = PendingUser(
            phone_number=create_user_request.phone_number,
            email=create_user_request.email,
            username=create_user_request.username,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            role=create_user_request.role,
            language_preference=create_user_request.language_preference,
            expires_at=expires_at
        )
        db.add(pending_user)

        db.commit()
        db.refresh(otp_record)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP. Please try again."
        )

    # Send OTP (outside transaction)
    send_otp_sms(
        create_user_request.phone_number,
        f"Your verification code is {otp_code}"
    )

    return {
        "message": "OTP sent successfully",
        "verification_id": otp_record.verification_id
    }



# Step 2: Verify OTP & create user


@router.post("/verify-otp", status_code=status.HTTP_201_CREATED)
async def verify_otp_registration(
    db: db_dependency,
    verification_id: str = Body(...),
    otp_code: str = Body(...),
   
):
    # Get the latest OTP for this phone
    otp_record = db.query(OTP).filter(
        OTP.verification_id == verification_id,
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
    pending_user = db.query(PendingUser).filter(
        PendingUser.phone_number == otp_record.phone
    ).first()

    if not pending_user:
        raise HTTPException(
            status_code=400, detail="Registration data not found")

    # Create user
   
    new_user = Users(
        email=pending_user.email,
        username=pending_user.username,
        first_name=pending_user.first_name,
        last_name=pending_user.last_name,
        hashed_password= pending_user.hashed_password,
        role=pending_user.role,
        phone_number=otp_record.phone,
        is_verified=True,
        language_preference=pending_user.language_preference or LanguageEnum.ENGLISH
    )

    db.add(new_user)
    db.delete(pending_user)
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
