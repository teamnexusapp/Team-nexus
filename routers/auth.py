from datetime import datetime, timedelta
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import OTP, PasswordResetToken, PendingUser, RoleEnum, Users, LanguageEnum
from schemas import CreateUserRequest, ForgotPasswordRequest, ResetPasswordRequest, Token, LoginRequest
from utils.utils import bcrypt_context, authenticate_user, create_access_token, generate_otp, hash_otp, send_password_reset_email, verify_otp_hash, send_otp_email, send_otp_sms
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

load_dotenv()

USE_SMS = os.getenv("USE_SMS", "false").lower() == "true"

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
    print("Received send-otp request:", create_user_request.dict())

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

    # Create OTP and pending user in DB
    try:
        # Clear previous OTPs and pending registrations
        db.query(OTP).filter(
            OTP.phone == create_user_request.phone_number,
            OTP.is_used == False
        ).delete()
        db.query(PendingUser).filter(
            PendingUser.phone_number == create_user_request.phone_number
        ).delete()

        # OTP record
        otp_record = OTP(
            phone=create_user_request.phone_number,
            otp_hashed=otp_hashed,
            attempts=0,
            is_used=False,
            expires_at=expires_at
        )
        db.add(otp_record)

        # Pending user record
        pending_user = PendingUser(
            phone_number=create_user_request.phone_number,
            email=create_user_request.email,
            username=create_user_request.username,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            role=RoleEnum(create_user_request.role),
            language_preference=LanguageEnum(
                create_user_request.language_preference),
            expires_at=expires_at
        )
        db.add(pending_user)

        db.commit()
        db.refresh(otp_record)

    except Exception as e:
        db.rollback()
        print("[ERROR] DB transaction failed:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to create OTP and pending user. Please try again."
        )

    # Send OTP (outside DB transaction)
    print("USE_SMS:", USE_SMS)
    try:
        if USE_SMS:
            print("Sending OTP via SMS to:", create_user_request.phone_number)
            send_otp_sms(
                create_user_request.phone_number,
                f"Your verification code is {otp_code}"
            )
            print("OTP SMS sent successfully!")
        else:
            print("Sending OTP via email to:", create_user_request.email)
            send_otp_email(create_user_request.email, otp_code)
            print("OTP email sent successfully!")

    except Exception as e:
        print("[ERROR] Failed to send OTP:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP. Please check server logs."
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
        hashed_password=pending_user.hashed_password,
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
    data: LoginRequest,
    db: db_dependency,
    # form_data: OAuth2PasswordRequestForm = Depends(),

):
    user = authenticate_user(data.email, data.password, db)
    # user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user!"
        )

    token = create_access_token(
      
        email=user.email,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}


# Forgot Password Logic

@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordRequest, db: db_dependency):
    user = db.query(Users).filter(Users.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found!")
    token = str(uuid.uuid4())
    reset_token = PasswordResetToken(
        user_id=user.id, token=token, expires_at=datetime.utcnow() + timedelta(minutes=5))
    db.add(reset_token)
    db.commit()
    send_password_reset_email(
        to_email=user.email, reset_token=reset_token.token)
    return {"message": "Password reset email sent successfully."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPasswordRequest, db: db_dependency):
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(Users).filter(Users.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    user.hashed_password = bcrypt_context.hash(data.new_password)
    db.delete(reset_record)
    db.commit()

    return {"message": "Password has been reset successfully"}


# Logout endpoint (placeholder)

@router.post("/logout")
async def logout_user():
    return {"message": "Logout successful"}
