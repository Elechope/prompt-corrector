"""
Database configuration and session management module.
Provides the SQLAlchemy engine, declarative base, and dependency injection generator.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# Resolve the absolute path to the assets directory to store the SQLite database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure assets directory exists
os.makedirs(ASSETS_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(ASSETS_DIR, 'dictionary.db')}"

# check_same_thread=False is required for SQLite in FastAPI (which uses multiple threads)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency generator that yields a database session.
    Ensures the session is closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
