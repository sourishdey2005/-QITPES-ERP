import os
from sqlalchemy import text
from database.db_manager import engine
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    # List of columns to add (Table, Column, Type, Default)
    # Note: Using SQLAlchemy types/syntax that is generally compatible
    migrations = [
        ("users", "company_id", "INTEGER", "NULL"),
        ("users", "branch_id", "INTEGER", "NULL"),
        ("projects", "currency", "VARCHAR(10)", "'INR'"),
        ("projects", "company_id", "INTEGER", "NULL"),
        ("projects", "branch_id", "INTEGER", "NULL"),
        ("projects", "client_id", "INTEGER", "NULL"),
        ("purchase_orders", "currency", "VARCHAR(10)", "'INR'"),
        ("finance_records", "currency", "VARCHAR(10)", "'INR'"),
        ("finance_records", "exchange_rate", "FLOAT", "1.0"),
        ("finance_records", "company_id", "INTEGER", "NULL"),
        ("finance_records", "branch_id", "INTEGER", "NULL")
    ]
    
    with engine.connect() as conn:
        for table, column, col_type, default in migrations:
            try:
                print(f"Adding {column} to {table}...")
                # Raw SQL remains similar, but now executed via SQLAlchemy engine
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}"))
                conn.commit()
            except Exception as e:
                # Handle cases where column already exists (Error code or message check)
                err_msg = str(e).lower()
                if "duplicate" in err_msg or "already exists" in err_msg:
                    print(f"Column {column} already exists in {table}.")
                else:
                    print(f"Error migrating {table}.{column}: {e}")
        
    print("Migration check completed.")

if __name__ == "__main__":
    run_migrations()
