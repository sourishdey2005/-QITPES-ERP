import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# --- Database Configuration ---
# Priority 1: Environment Variable
# Priority 2: Streamlit Secrets (for Cloud deployment)
# Priority 3: Local SQLite (Desktop development)

# Check for DATABASE_URL in st.secrets if available (Streamlit Cloud best practice)
try:
    SECRET_URL = st.secrets.get("DATABASE_URL")
except:
    SECRET_URL = None

# Ensure the database is always in the project root regardless of where the app is started
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "erp.db")

DATABASE_URL = os.getenv("DATABASE_URL") or SECRET_URL or f"sqlite:///{DB_PATH}"

# Clear warning for Cloud users
if "sqlite" in DATABASE_URL and (os.getenv("STREAMLIT_SERVER_GATHER_USAGE_STATS") or os.getenv("SHIBBOLETH_ENABLED")):
    print("⚠️ WARNING: Running with SQLite on an ephemeral cloud filesystem.")
    print("Data will be LOST when the app sleeps or restarts. Use a remote database for production.")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Thread-safe session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized successfully at: {DB_PATH}")

def get_db():
    """Dependency for DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
