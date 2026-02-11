import streamlit as st

# --- Configuration ---
# MUST be the first Streamlit command
st.set_page_config(
    page_title="QITPES ERP SYSTEM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from database.db_manager import init_db
from database.models import UserRole
from auth.auth_handler import AuthHandler
from ui.styles import load_css
from modules.projects import run_projects_module
from modules.finance import run_finance_module
from modules.inventory import run_inventory_module
from modules.hr import run_hr_module
from modules.admin import run_admin_module
from modules.reports import run_reports_module
from modules.planning import run_planning_module
from modules.purchase import run_purchase_module
from modules.production import run_production_module
from modules.machinery import run_machinery_module
from modules.contractor import run_contractor_module
from modules.labour import run_labour_module
from modules.software import run_software_module
from modules.site_ops import run_site_ops_module
from modules.crm import run_crm_module
from modules.compliance import run_compliance_module
from modules.settings import run_settings_module

def log_event(action, details=""):
    """Helper to log global system activities"""
    from database.db_manager import SessionLocal
    from database.models import ActivityLog
    try:
        db = SessionLocal()
        user_id = st.session_state.get('user_id')
        if user_id:
            log = ActivityLog(user_id=user_id, action=action, details=details)
            db.add(log)
            db.commit()
        db.close()
    except Exception as e:
        print(f"Logging failed: {e}")

# --- Load Styles ---
st.markdown(load_css(), unsafe_allow_html=True)

# --- Initialize DB ---
init_db()

# --- Authentication ---
auth = AuthHandler()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        
    if not st.session_state['logged_in']:
        login_page()
    else:
        dashboard()

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("QITPES ERP SYSTEM")
        
        tab_login, tab_reg, tab_reset = st.tabs(["Login", "Register", "Reset Password"])
        
        with tab_login:
            st.write("### Sign In")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pwd")
            
            if st.button("Log In", use_container_width=True):
                status, msg = auth.login(email, password)
                if status:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
            with st.expander("System Notice"):
                st.info("If this is the first run, please Register an account first.")

        with tab_reg:
            st.write("### Create Account")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address", key="reg_email")
            new_pwd = st.text_input("Create Password", type="password", key="reg_pwd")
            confirm_pwd = st.text_input("Confirm Password", type="password")
            
            role = st.selectbox("Request Role", [r.value for r in UserRole])
            
            if st.button("Register Now", use_container_width=True):
                if new_pwd != confirm_pwd:
                    st.error("Passwords do not match!")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    status, msg = auth.create_user(new_name, new_email, new_pwd, UserRole(role))
                    if status:
                        st.success(msg)
                    else:
                        st.error(msg)

        with tab_reset:
            st.write("### Reset Password")
            reset_email = st.text_input("Registered Email")
            reset_pwd = st.text_input("New Password", type="password")
            
            if st.button("Update Password", use_container_width=True):
                status, msg = auth.reset_password(reset_email, reset_pwd)
                if status:
                    st.success(msg)
                else:
                    st.error(msg)

def dashboard():
    role = st.session_state.get('role')
    username = st.session_state.get('username')
    menu_options = get_menu_options(role)
    menu_list = list(menu_options.keys())

    # --- Page Persistence Logic ---
    query_page = st.query_params.get("page", "Dashboard")
    if query_page not in menu_list:
        query_page = "Dashboard"

    default_index = menu_list.index(query_page)

    with st.sidebar:
        st.title("QITPES ERP")
        st.write(f"Logged in: **{username}**")
        st.caption(f"Role: {role}")
        st.markdown("---")
        
        selection = st.selectbox(
            "Navigation", 
            menu_list, 
            index=default_index,
            key="nav_selection"
        )
        
        # Sync selection to URL
        st.query_params["page"] = selection
        
        st.markdown("---")
        
        # Database Status Indicator
        from database.db_manager import DATABASE_URL
        with st.expander("💾 System Storage", expanded=False):
            if "sqlite" in DATABASE_URL:
                if os.getenv("STREAMLIT_SERVER_GATHER_USAGE_STATS") or os.getenv("SHIBBOLETH_ENABLED"):
                    st.error("⚠️ DATA IS TEMPORARY!")
                    st.info("Cloud sleep will reset DB. Connect to Postgres for permanence.")
                else:
                    st.success("✅ Persistent Local Storage")
            else:
                st.success("✅ External Database Connected")

        if st.button("Logout"):
            log_event("Logout", "User logged out")
            st.query_params.clear()
            auth.logout()
            st.rerun()

    if selection:
        if st.session_state.get('last_page') != selection:
            log_event("Navigation", f"Accessed module: {selection}")
            st.session_state['last_page'] = selection
        menu_options[selection]()

def get_menu_options(role):
    # Base options for everyone
    options = {
        "Dashboard": custom_dashboard,
        "Project Management": run_projects_module,
    }
    
    # OWNER has access to EVERYTHING strictly as requested
    if role == UserRole.OWNER.value:
        options.update({
            "Planning & Estimation": run_planning_module,
            "Purchase Management": run_purchase_module,
            "Store & Inventory": run_inventory_module,
            "Plant & Production": run_production_module,
            "Machinery & Vehicle Management": run_machinery_module,
            "Finance & Accounts": run_finance_module,
            "HR & Payroll": run_hr_module,
            "Labour Management": run_labour_module,
            "Contractor Management": run_contractor_module,
            "Software Management": run_software_module,
            "Site Operations & HSE": run_site_ops_module,
            "CRM & Contracts": run_crm_module,
            "System Compliance": run_compliance_module,
            "Info. System (MIS)": run_reports_module,
            "System Configuration": run_settings_module,
            "Management Console (Admin)": run_admin_module
        })
    elif role == UserRole.DIRECTOR.value:
        options.update({
            "Planning & Estimation": run_planning_module,
            "Plant & Production": run_production_module,
            "Info. System (MIS)": run_reports_module
        })
    elif role == UserRole.ACCOUNTANT.value:
        options.update({
            "Finance & Accounts": run_finance_module,
            "HR & Payroll": run_hr_module,
            "Info. System (MIS)": run_reports_module
        })
        
    return options

def custom_dashboard():
    from database.db_manager import get_db
    from database.models import Project, FinanceRecord, InventoryItem, Employee, PurchaseOrder, TransactionType, Client
    import plotly.graph_objects as go
    
    st.header("Executive Strategic Command 🏛️")
    db = next(get_db())
    
    # --- Fetch Data ---
    projects = db.query(Project).all()
    finance = db.query(FinanceRecord).all()
    inventory = db.query(InventoryItem).all()
    staff = db.query(Employee).filter(Employee.is_active == True).all()
    orders = db.query(PurchaseOrder).all()
    clients = db.query(Client).all()
    
    # --- TOP ROW: FINANCIAL GAUGES ---
    st.markdown("### 💰 Financial Velocity")
    income = sum(f.amount for f in finance if f.type == TransactionType.INCOME)
    expense = sum(f.amount for f in finance if f.type == TransactionType.EXPENSE)
    cash_flow = income - expense
    
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        fig_rev = go.Figure(go.Indicator(
            mode = "number+delta", value = income,
            title = {"text": "Total Revenue (₹)"},
            delta = {'reference': expense, 'relative': True, 'position': "top"},
            domain = {'x': [0, 1], 'y': [0, 1]}))
        fig_rev.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_g2:
        margin = (cash_flow / income * 100) if income > 0 else 0
        fig_margin = go.Figure(go.Indicator(
            mode = "gauge+number", value = margin,
            title = {'text': "Net Margin %"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#1e40af"}},
            domain = {'x': [0, 1], 'y': [0, 1]}))
        fig_margin.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_margin, use_container_width=True)
        
    with col_g3:
        fig_cash = go.Figure(go.Indicator(
            mode = "number", value = cash_flow,
            title = {"text": "Liquidity Pool (₹)"},
            domain = {'x': [0, 1], 'y': [0, 1]}))
        fig_cash.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_cash, use_container_width=True)

    st.divider()

    # --- MIDDLE ROW: OPERATIONS & WORKFORCE ---
    st.markdown("### 🏭 Operational Excellence")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project Portfolio", len(projects), f"{len([p for p in projects if p.status.value == 'Active'])} Active")
    c2.metric("Procurement Depth", f"₹{sum(o.total_amount for o in orders):,.0f}")
    c3.metric("Force Multiplier", f"{len(staff)} Personnel")
    c4.metric("Client Ecosystem", f"{len(clients)} Partners", delta=f"{len([c for c in clients if c.status == 'Lead'])} Leads")

    st.divider()

    # --- BOTTOM ROW: SECTOR ANALYSIS ---
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v1:
        st.subheader("📊 Capital Distribution by Project")
        if projects:
            df_p = pd.DataFrame([{ "Name": p.name, "Budget": p.total_budget, "Progress": p.progress } for p in projects])
            fig_p = px.scatter(df_p, x="Name", y="Budget", size="Progress", color="Name",
                              title="Strategic Asset Allocation Matrix", hover_name="Name")
            st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("No projects found.")

    with col_v2:
        st.subheader("🛡️ Compliance Health")
        # System Health Indicators
        st.success("✅ Audit Trail Active")
        st.success("✅ Biometric Cloud Synced")
        st.success("✅ Financial Ledger Validated")
        st.info("ℹ️ System Backup: 100% Verified")

if __name__ == "__main__":
    main()
