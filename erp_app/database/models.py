from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, Date, DateTime, ForeignKey, Enum, create_engine
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
from utils.time_utils import get_ist, get_ist_date

Base = declarative_base()

# --- Enums for consistent status tracking ---
class ProjectStatus(enum.Enum):
    PLANNED = "Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

class UserRole(enum.Enum):
    OWNER = "Owner"
    DIRECTOR = "Director"
    ACCOUNTANT = "Accounting Staff"

class TransactionType(enum.Enum):
    INCOME = "Income"
    EXPENSE = "Expense"

# --- Organizational Structure ---
class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    fiscal_year_start = Column(Date)
    base_currency = Column(String(10), default="INR")
    registration_number = Column(String(50))
    address = Column(Text)
    
    branches = relationship("Branch", back_populates="company")

class Branch(Base):
    __tablename__ = 'branches'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    
    company = relationship("Company", back_populates="branches")

# --- Core User Management ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)  # Display Name
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ACCOUNTANT)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_ist)

    activity_logs = relationship("ActivityLog", back_populates="user")

class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(255), nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, default=get_ist)
    
    user = relationship("User", back_populates="activity_logs")

# --- 1. Project Management ---
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    client = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNED)
    total_budget = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    description = Column(Text)
    progress = Column(Integer, default=0) # 0-100%

# --- 3. Purchase & vendor Management ---
class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    rating = Column(Integer, default=3) # 1-5

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    order_date = Column(Date, default=get_ist_date)
    expected_delivery = Column(Date)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    status = Column(String(20), default="Pending") # Pending, Approved, Delivered
    
    vendor = relationship("Vendor")

# --- 4. Store & Inventory ---
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    current_stock = Column(Integer, default=0)
    unit = Column(String(20)) # e.g., kg, pcs, liters
    min_stock_alert = Column(Integer, default=10)
    location = Column(String(100))
    last_updated = Column(DateTime, default=get_ist)

# --- 6. Machinery & Vehicles ---
class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50)) # Machinery / Vehicle
    purchase_date = Column(Date)
    last_service_date = Column(Date)
    next_service_due = Column(Date)
    status = Column(String(20), default="Active") # Active, Maintenance, Retired

class AssetLog(Base):
    __tablename__ = 'asset_logs'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    date = Column(Date, default=get_ist_date)
    hours_used = Column(Float, default=0.0)
    fuel_consumed = Column(Float, default=0.0)
    notes = Column(Text)

# --- 7. Finance ---
class FinanceRecord(Base):
    __tablename__ = 'finance_records'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=get_ist_date)
    type = Column(Enum(TransactionType))
    category = Column(String(100))
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    exchange_rate = Column(Float, default=1.0)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    description = Column(String(255))
    payment_method = Column(String(50)) # Cash, Bank Transfer, Cheque

# --- 8 & 9. HR & Labour ---
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50)) # Manager, Worker, Contractor
    department = Column(String(50))
    joining_date = Column(Date)
    salary = Column(Float, default=0.0)
    contract_type = Column(String(20)) # Permanent, Contract
    is_active = Column(Boolean, default=True)

class Payroll(Base):
    __tablename__ = 'payroll'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    month = Column(String(7)) # Format: YYYY-MM
    basic_salary = Column(Float)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float)
    status = Column(String(20), default="Pending") # Paid, Pending

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    date = Column(Date, default=get_ist_date)
    status = Column(String(20)) # Present, Absent, Leave
    hours_worked = Column(Float, default=8.0)

# --- 5. Production Logs ---
class ProductionLog(Base):
    __tablename__ = 'production_logs'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=get_ist_date)
    project_id = Column(Integer, ForeignKey('projects.id'))
    quantity_produced = Column(Float, default=0.0)
    efficiency = Column(Float) # Calculated efficiency percentage
    waste_generated = Column(Float, default=0.0)
    notes = Column(Text)

# --- 10. Software & Digital Assets ---
class SoftwareAsset(Base):
    __tablename__ = 'software_assets'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20))
    license_key = Column(String(100))
    expiry_date = Column(Date)
    status = Column(String(20), default="Active") # Active, Expired, Pending Update
    assigned_to = Column(String(100)) # e.g., 'IT Dept', 'Design Team'

# --- 11. Maintenance (Preventive & Predictive) ---
class MaintenanceSchedule(Base):
    __tablename__ = 'maintenance_schedules'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    task_name = Column(String(100), nullable=False)
    scheduled_date = Column(Date)
    performed_date = Column(Date)
    status = Column(String(20), default="Scheduled") # Scheduled, Completed, Overdue
    cost = Column(Float, default=0.0)
    technician = Column(String(100))
    
    asset = relationship("Asset")

# --- 12. Accounts Payable & Receivable ---
class Invoice(Base): # Accounts Receivable
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    invoice_number = Column(String(50), unique=True)
    date_issued = Column(Date, default=get_ist_date)
    due_date = Column(Date)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="Unpaid") # Unpaid, Paid, Partially Paid
    
    project = relationship("Project")

class Bill(Base): # Accounts Payable
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    po_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=True)
    bill_number = Column(String(50))
    date_received = Column(Date, default=get_ist_date)
    due_date = Column(Date)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="Unpaid") # Unpaid, Paid
    
    vendor = relationship("Vendor")
    purchase_order = relationship("PurchaseOrder")

# --- 13. Health, Safety & Environment (HSE) ---
class HSERecord(Base):
    __tablename__ = 'hse_records'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=get_ist_date)
    project_id = Column(Integer, ForeignKey('projects.id'))
    incident_type = Column(String(50)) # Near Miss, Injury, Inspection
    description = Column(Text)
    action_taken = Column(Text)
    reported_by = Column(String(100))
    status = Column(String(20), default="Open") # Open, Closed

# --- 14. Quality Control (QC) ---
class QualityCheck(Base):
    __tablename__ = 'quality_checks'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=get_ist_date)
    production_id = Column(Integer, ForeignKey('production_logs.id'))
    parameter = Column(String(100)) # e.g., Strength, Finish, Dimensions
    result = Column(String(50)) # Pass, Fail
    remarks = Column(Text)

# --- 15. Document Management (DMS) ---
class DocumentAsset(Base):
    __tablename__ = 'document_assets'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    category = Column(String(50)) # Contract, Drawing, License
    file_path = Column(String(255))
    upload_date = Column(DateTime, default=get_ist)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

# --- 16. Training & Skills ---
class TrainingRecord(Base):
    __tablename__ = 'training_records'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    training_name = Column(String(100))
    date_completed = Column(Date)
    expiry_date = Column(Date, nullable=True)
    score = Column(String(20))

# --- 17. CRM & Client Management ---
class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    company = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    status = Column(String(20), default="Lead") # Lead, Active, Inactive
    created_at = Column(DateTime, default=get_ist)

    projects = relationship("Project", back_populates="client_rel")
    contracts = relationship("Contract", back_populates="client")

# --- 18. Contract Management ---
class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'))
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    contract_value = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="Draft") # Draft, Signed, Terminated, Completed
    terms = Column(Text)
    
    client = relationship("Client", back_populates="contracts")
    project = relationship("Project")

# Manually add relationships to Project to avoid re-defining the class
Project.client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
Project.client_rel = relationship("Client", back_populates="projects")

# --- 19. System Configuration & Settings ---
class SystemSetting(Base):
    __tablename__ = 'system_settings'
    id = Column(Integer, primary_key=True)
    category = Column(String(50)) # e.g., 'General', 'Security', 'Themes'
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text)
    description = Column(Text)

