from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from models import Users, UserProfile
from database import SessionLocal
from schema import UpdateUserProfileRequest, UserProfileResponse
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/user",
    tags=["user"]
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')




@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User Not Found!")
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    return {
        'username': user_model.username,
        'email': user_model.email,
        'first_name': user_model.first_name,
        'last_name': user_model.last_name,
        'role': user_model.role,
        'phone_number': user_model.phone_number
    }


@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency):
     user_id = user['id']
     user = db.query(Users).filter(Users.id == user_id).first()
     if not user:
         raise HTTPException(status_code=401, detail="User Not Found!")
     user_profile = db.query(UserProfile).filter(
         UserProfile.user_id == user_id).first()
     if user_profile:
         db.delete(user_profile)
     db.delete(user)
     db.commit()
     return {"message": "User deleted"}




@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_profile(user: user_dependency, db: db_dependency):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user['id']).first()
    if not profile:
        profile = UserProfile(user_id=user['id'])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def update_profile(update_request:  UpdateUserProfileRequest, user: user_dependency, db: db_dependency):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user['id']).first()
    if not profile:
       profile = UserProfile(user_id=user['id'])
       db.add(profile)
       db.commit()
       db.refresh(profile)
    for key, value in update_request.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile





