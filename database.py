from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

password = os.getenv("PASSWORD")

#SQLALCHEMY_DATABASE_URL = "sqlite:///./omacareapp.db"
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@localhost/fert_app_database"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base =  declarative_base()
