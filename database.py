from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Read DB URL from environment (Render) or fallback to SQLite (local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./omacareapp.db")

# Fix for Render Postgres
if DATABASE_URL.startswith("postgresql"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg2://"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
