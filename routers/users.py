from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from models import Users, UserProfile
from database import SessionLocal
from schemas import UpdateUserProfileRequest, UserProfileResponse, UpdateLangaugeRequest
from utils.utils import get_current_user
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
    db_user  = db.query(Users).filter(Users.id == user['id']).first()
    return {
        'username': db_user.username,
        'email': db_user.email,
        'first_name': db_user.first_name,
        'last_name': db_user.last_name,
        'role': db_user.role,
        'phone_number': db_user.phone_number,
        'preferred_language': db_user.language_preference
    }

@router.patch("/update_language_choice", status_code=status.HTTP_200_OK)
async def update_language_choice(data: UpdateLangaugeRequest, user: user_dependency, db: db_dependency):
     db_user = db.query(Users).filter(Users.id == user["id"]).first()
     if not db_user:
         raise HTTPException(status_code=401, detail="User Not Found!")
     
     db_user.language_preference = data.language_preference
     db.commit()
     db.refresh(db_user)
     return {
         "message": "Language preference updated successfully",
         "language_preference": db_user.language_preference.value
     }

      




@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency):
     user_id = user['id']
     db_user = db.query(Users).filter(Users.id == user_id).first()
     if not db_user:
         raise HTTPException(status_code=401, detail="User Not Found!")
     user_profile = db.query(UserProfile).filter(
         UserProfile.user_id == user_id).first()
     if user_profile:
         db.delete(user_profile)
     db.delete(db_user)
     db.commit()
     return {"message": "User deleted"}




@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_profile(user: user_dependency, db: db_dependency):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user['id']).first()
    if not profile:
        profile = UserProfile(user_id=user["id"])
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    return profile
        

@router.patch("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def update_profile(update_request:UpdateUserProfileRequest, user: user_dependency, db: db_dependency):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user['id']).first()
    if not profile:
       profile = UserProfile(user_id=user['id'])
       db.add(profile)
       db.commit()
       db.refresh(profile)
    update_data = update_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile





