
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from starlette import status
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import random
import requests
import os



bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", 5))


def authenticate_user(username: str, password: str, db):
    db_user = db.query(Users).filter(Users.username == username).first()
    if not db_user:
        return False
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return False
    return db_user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
   encode = {'sub': username, 'id': user_id, 'role': role}
   expires = datetime.now(timezone.utc) + expires_delta
   encode.update({'exp': expires})
   return jwt.encode(encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'),
                             algorithms=os.getenv('ALGORITHM'))
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user!')
        return {'username': username, 'id': user_id, 'user_role': user_role}
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


def send_otp_sms(phone_number: str, message: str):
    # For testing, just print
    print(f"Sending SMS to {phone_number}: {message}")


# for real sms integration
# ..................................
# from twilio.rest import Client

# def send_otp_sms(phone_number: str, message: str):
#     client = Client(account_sid, auth_token)
#     client.messages.create(
#         body=message,
#         from_='+1234567890',  # Twilio phone
#         to=phone_number
#     )

