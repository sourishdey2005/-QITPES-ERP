from faker import Faker
import random
from datetime import datetime, timedelta
from database.models import User, UserRole, Project, ProjectStatus, FinanceRecord, TransactionType, InventoryItem, Employee, Vendor
from database.db_manager import SessionLocal, get_db

fake = Faker()

def seed_database():
    print("Starting seeder...")
    db = SessionLocal()
    
    # Check if data exists
    if db.query(User).count() > 0:
        print("Database seems populated. Skipping seeder.")
        db.close()
        return

    # --- Users ---
    default_users = [
        {"email": "owner@company.com", "role": UserRole.OWNER, "name": "System Owner"},
        {"email": "director@company.com", "role": UserRole.DIRECTOR, "name": "Operations Director"},
        {"email": "accounts@company.com", "role": UserRole.ACCOUNTANT, "name": "Senior Accountant"},
    ]
    
    # Hash password 'admin123' for all demo users
    # In a real app, use the auth handler method, but for seeding 
    # we can use a known hash or call the handler if available.
    # Here I'll mock a simple bcrypt hash for 'admin123'
    # generated via: bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
    hashed_pw = "$2b$12$eX.Y.Z.1.2.3.4.5.6.7.8.9.0.1.2.3.4.5.6.7.8.9.0.1.2.3" # Placeholder
    # Actually, let's just import bcrypt here to be safe
    import bcrypt
    real_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
    
    for u in default_users:
        user = User(
            username=u["name"],
            email=u["email"],
            password_hash=real_hash, 
            role=u["role"]
        )
        db.add(user)
    
    # --- Projects ---
    for _ in range(5):
        start = fake.date_between(start_date='-1y', end_date='today')
        proj = Project(
            name=f"{fake.city()} Construction",
            client=fake.company(),
            start_date=start,
            end_date=start + timedelta(days=random.randint(30, 365)),
            status=random.choice(list(ProjectStatus)),
            total_budget=random.uniform(50000, 500000),
            progress=random.randint(0, 100),
            description=fake.catch_phrase()
        )
        db.add(proj)

    # --- Inventory ---
    items = ["Cement", "Steel Rods", "Bricks", "Sand", "Paint", "Tiles", "Glass", "Wood", "Pipes", "Wires"]
    for item in items:
        inv = InventoryItem(
            name=item,
            category="Raw Material",
            current_stock=random.randint(0, 500),
            unit="units",
            min_stock_alert=50,
            location=f"Warehouse {random.choice(['A', 'B'])}"
        )
        db.add(inv)

    # --- Finance ---
    for _ in range(20):
        t_type = random.choice(list(TransactionType))
        fin = FinanceRecord(
            date=fake.date_between(start_date='-3m', end_date='today'),
            type=t_type,
            category=random.choice(["Sales", "Materials", "Service", "Labour"]),
            amount=random.uniform(100, 5000),
            description=fake.sentence(),
            payment_method=random.choice(["Cash", "Bank Transfer"])
        )
        db.add(fin)
        
    # --- Employees ---
    for _ in range(10):
        emp = Employee(
            name=fake.name(),
            role=random.choice(["Manager", "Engineer", "Laborer", "Driver"]),
            department=random.choice(["Civil", "Electrical", "Admin"]),
            salary=random.uniform(2000, 8000),
            joining_date=fake.date_between(start_date='-2y', end_date='today'),
            is_active=True
        )
        db.add(emp)

    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
