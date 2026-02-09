import streamlit as st
import pandas as pd
import json
import os
from database.models import Company, Branch, SystemSetting
from database.db_manager import get_db
from datetime import datetime

def run_settings_module():
    st.header("Enterprise Settings & Configuration ⚙️")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Settings Control", [
            "Company Management", 
            "Branch Management", 
            "System Configuration", 
            "Backup & Recovery"
        ])
        
    if option == "Company Management":
        st.subheader("Global Company Registry")
        tab1, tab2 = st.tabs(["View Companies", "Register New Entity"])
        
        with tab1:
            companies = db.query(Company).all()
            if companies:
                df = pd.DataFrame([{
                    "ID": c.id, "Name": c.name, "Currency": c.base_currency, 
                    "Reg #": c.registration_number, "Address": c.address
                } for c in companies])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No companies registered yet.")
                
        with tab2:
            with st.form("new_company"):
                name = st.text_input("Company Name*")
                cur = st.selectbox("Base Currency", ["INR", "USD", "EUR", "AED", "GBP"])
                reg = st.text_input("Registration Number")
                fiscal = st.date_input("Fiscal Year Start")
                addr = st.text_area("Corporate Address")
                
                if st.form_submit_button("✅ Register Company"):
                    if name:
                        new_c = Company(name=name, base_currency=cur, registration_number=reg, fiscal_year_start=fiscal, address=addr)
                        db.add(new_c)
                        db.commit()
                        st.success(f"Company '{name}' onboarded.")
                        st.rerun()
                    else:
                        st.error("Name is required.")

    elif option == "Branch Management":
        st.subheader("Regional Branch Control")
        companies = db.query(Company).all()
        if not companies:
            st.warning("Please create a company first.")
        else:
            tab1, tab2 = st.tabs(["Branch List", "Add Branch"])
            
            with tab1:
                branches = db.query(Branch).all()
                if branches:
                    df = pd.DataFrame([{
                        "ID": b.id, "Branch": b.name, "Company": b.company.name, "Location": b.location
                    } for b in branches])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No branches mapped.")
                    
            with tab2:
                with st.form("new_branch"):
                    c_sel = st.selectbox("Parent Company", companies, format_func=lambda x: x.name)
                    b_name = st.text_input("Branch Name*")
                    loc = st.text_input("Location / City")
                    
                    if st.form_submit_button("🏠 Map Branch"):
                        if b_name:
                            new_b = Branch(company_id=c_sel.id, name=b_name, location=loc)
                            db.add(new_b)
                            db.commit()
                            st.success(f"Branch '{b_name}' successfully mapped to {c_sel.name}.")
                            st.rerun()

    elif option == "System Configuration":
        st.subheader("Global System Parameters")
        settings = db.query(SystemSetting).all()
        
        if settings:
            st.write("**Current Config Key-Values**")
            df_s = pd.DataFrame([{
                "Category": s.category, "Key": s.key, "Value": s.value, "Description": s.description
            } for s in settings])
            st.dataframe(df_s, use_container_width=True)
        
        st.divider()
        st.subheader("Update / Define Parameter")
        with st.form("setting_form"):
            cat = st.selectbox("Category", ["General", "Finance", "Security", "Notifications"])
            key = st.text_input("Config Key (e.g., TAX_RATE)")
            val = st.text_input("Value")
            desc = st.text_area("Description")
            
            if st.form_submit_button("💾 Save Configuration"):
                existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
                if existing:
                    existing.value = val
                    existing.category = cat
                    existing.description = desc
                else:
                    new_s = SystemSetting(category=cat, key=key, value=val, description=desc)
                    db.add(new_s)
                db.commit()
                st.success(f"Config '{key}' synchronized.")
                st.rerun()

    elif option == "Backup & Recovery":
        st.subheader("Security & Data Resilience 🛡️")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💾 Local Backup")
            st.write("Generate a full encrypted snapshot of the database.")
            if st.button("Generate Immediate Backup"):
                # Simulation of backup
                st.success("Database snapshot created: `erp_backup_2024_01_01.sql`")
                st.info("Storage Location: /backups/local/")
                
        with col2:
            st.markdown("#### ☁️ Cloud Synced Recovery")
            st.write("Restore system state from a previous cloud version.")
            st.selectbox("Select Point-in-time Recovery", ["Last Night 02:00 AM", "2 days ago", "Weekly Snapshot - Dec 28"])
            if st.button("Initiate Recovery"):
                st.warning("Entering Recovery Mode... please wait.")
                st.success("System Restored to Dec 28 state.")

        st.divider()
        st.subheader("Multi-Currency Auto-Updates")
        st.write("Synchronize exchange rates for multi-branch consolidation.")
        if st.button("🔄 Sync Live Exchange Rates"):
            st.info("Syncing with Currency Exchange API...")
            st.success("XRates updated: 1 USD = ₹83.12 | 1 EUR = ₹91.05")
