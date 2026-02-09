import sqlite3
import os

db_path = "erp.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of columns to add (Table, Column, Type, Default)
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
    
    for table, column, col_type, default in migrations:
        try:
            print(f"Adding {column} to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {column} already exists in {table}.")
            else:
                print(f"Error migrating {table}.{column}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration completed.")
else:
    print("No existing database found. Fresh start will be handled by app initialization.")
