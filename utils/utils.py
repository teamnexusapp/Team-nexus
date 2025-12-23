
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from starlette import status
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
from dotenv import load_dotenv
import os


load_dotenv()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", 5))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SENDER_EMAIL = os.getenv("SENDGRID_SENDER_EMAIL")
SENDGRID_SENDER_NAME = os.getenv("SENDGRID_SENDER_NAME")





def authenticate_user(email: str, password: str, db):
    db_user = db.query(Users).filter(Users.email == email).first()
    if not db_user:
        return False
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return False
    return db_user


def create_access_token(email: str, user_id: int, role: str, expires_delta: timedelta):
   encode = {'sub': email, 'id': user_id, 'role': role}
   expires = datetime.now(timezone.utc) + expires_delta
   encode.update({'exp': expires})
   return jwt.encode(encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'),
                             algorithms=os.getenv('ALGORITHM'))
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user!')
        return {'username': email, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user!')


#............. otp...............#

def generate_otp(length=4):
   return str(random.randint(10**(length-1), 10**length - 1))


def hash_otp(otp: str) -> str:
    return bcrypt_context.hash(otp)

def verify_otp_hash(plain_otp: str, hashed_otp: str) -> bool:
    return bcrypt_context.verify(plain_otp, hashed_otp)



#...............implimenting sendgrid emailing service.................#

def send_otp_email(to_email: str, otp_code: str):
   
    print(
        f"[DEBUG] From: {SENDGRID_SENDER_EMAIL}, To: {to_email}, OTP: {otp_code}")

    if not SENDGRID_API_KEY or not SENDGRID_SENDER_EMAIL or not SENDGRID_SENDER_NAME:
        raise ValueError("SendGrid environment variables not set correctly.")

    if "@" not in to_email:
        raise ValueError(f"Invalid recipient email: {to_email}")

    message = Mail(
        from_email=SENDGRID_SENDER_EMAIL,
        to_emails=to_email,
        subject="Your Verification Code",
        html_content=f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>Email Verification</h2>
            <p>Your verification code is:</p>
            <h1>{otp_code}</h1>
            <p>This code expires in 5 minutes.</p>
        </div>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[DEBUG] SendGrid response status: {response.status_code}")
        if response.status_code not in (200, 202):
            raise Exception(
                f"Failed to send email: {response.status_code}, {response.body}")
        print(f"OTP sent successfully to {to_email}")
    except Exception as e:
        print(f"SendGrid error: {e}")
        raise e




def send_password_reset_email(to_email: str, reset_token: str):
   
    print(
        f"[DEBUG] Sending password reset email to {to_email}, Token: {reset_token}")

    if not SENDGRID_API_KEY or not SENDGRID_SENDER_EMAIL or not SENDGRID_SENDER_NAME:
        raise ValueError("SendGrid environment variables not set correctly.")
    if "@" not in to_email:
        raise ValueError(f"Invalid recipient email: {to_email}")

   
    reset_link = f"https://fertipath.onrender.com/reset_password?token={reset_token}"
    message = Mail(
        from_email=SENDGRID_SENDER_EMAIL,
        to_emails=to_email,
        subject="Reset Your Password",
        html_content=f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none;">Reset Password</a>
            <p>This link will expire in 15 minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
        </div>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[DEBUG] SendGrid response status: {response.status_code}")
        if response.status_code not in (200, 202):
            raise Exception(
                f"Failed to send password reset email: {response.status_code}, {response.body}")
        print(f"Password reset email sent successfully to {to_email}")
    except Exception as e:
        print(f"SendGrid error: {e}")
        raise e





# implimenting sendgrid emailing service

def send_otp_sms(phone_number: str, message: str):
    # For testing, just print
    print(f"Sending SMS to {phone_number}: {message}")


