import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
from dotenv import load_dotenv

load_dotenv()

# --- Database Configuration ---
# Default to SQLite for portability, but allow robust Postgres via env vars
# Example ENV: DATABASE_URL=postgresql://user:pass@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///erp.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Thread-safe session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

def get_db():
    """Dependency for DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
