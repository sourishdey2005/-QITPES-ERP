import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# --- Database Configuration Logic ---
def get_database_url():
    # Priority 1: Environment Variable
    # Priority 2: Streamlit Secrets
    # Priority 3: Local SQLite
    
    url = os.getenv("DATABASE_URL")
    if url:
        return url
        
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except:
        pass
        
    # Default to SQLite
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "erp.db")
    return f"sqlite:///{db_path}"

DATABASE_URL = get_database_url()
# Needed for UI indicators
DB_PATH = DATABASE_URL.split("///")[-1] if "sqlite" in DATABASE_URL else "Remote Postgres"

# Clear warning for Cloud users
if "sqlite" in DATABASE_URL and (os.getenv("STREAMLIT_SERVER_GATHER_USAGE_STATS") or os.getenv("SHIBBOLETH_ENABLED")):
    print("⚠️ WARNING: Running with SQLite on an ephemeral cloud filesystem.")

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
