from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from starlette import status
from database import SessionLocal
from sqlalchemy.orm import Session
from schema import CreateUserRequest, Token
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_depedency = Annotated[Session, Depends(get_db)]




def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


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


# endpoints

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_depedency, create_user_request: CreateUserRequest):
   existing = db.query(Users).filter(or_(
       Users.email == create_user_request.email, Users.username == create_user_request.username)).first()
   if existing:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details='Email or Username already used!')
   new_user = Users(
       email=create_user_request.email,
       username=create_user_request.username,
       first_name=create_user_request.first_name,
       last_name=create_user_request.last_name,
       hashed_password=bcrypt_context.hash(create_user_request.password),
       role=create_user_request.role,
       phone_number=create_user_request.phone_number
   )

   db.add(new_user)
   db.commit()
   db.refresh(new_user)


     


@router.post("/token", response_model=Token)
async def login_in_token(db: db_depedency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
     user = authenticate_user(form_data.username, form_data.password, db)
     if not user:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user!')
     token = create_access_token(
           user.username, user.id, user.role, timedelta(minutes=20))
     return {'access_token': token, 'token_type': 'bearer'}


@router.post("/logout")
async def logout_user():
  
    return {"message": "Logout successful"}
