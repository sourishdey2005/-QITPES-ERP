import streamlit as st
import pandas as pd
from database.models import SoftwareAsset
from database.db_manager import get_db
from datetime import datetime
from utils.time_utils import get_ist_date

def run_software_module():
    st.header("Software & License Management 💻")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Software Menu", ["Asset Overview", "Register License", "Manage Licenses"])
        
    if option == "Asset Overview":
        st.subheader("Digital Asset Inventory")
        assets = db.query(SoftwareAsset).all()
        if assets:
            data = []
            for a in assets:
                # Basic expiry check
                status = a.status
                if a.expiry_date and a.expiry_date < get_ist_date():
                    status = "🔴 Expired"
                
                data.append({
                    "ID": a.id,
                    "Software Name": a.name,
                    "Version": a.version or "N/A",
                    "License Key": "********" if a.license_key else "None",
                    "Assigned To": a.assigned_to or "Unassigned",
                    "Expiry": a.expiry_date,
                    "Status": status
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            expired_recs = len([d for d in data if "Expired" in str(d['Status'])])
            if expired_recs > 0:
                st.error(f"Attention: {expired_recs} software licenses have expired!")
        else:
            st.info("No software assets recorded yet.")

    elif option == "Register License":
        st.subheader("Onboard New Software/License")
        with st.form("reg_software"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Software Title*")
            ver = col2.text_input("Version (e.g. 2024.1)")
            key = col1.text_input("License/Product Key")
            expiry = col2.date_input("Expiry Date")
            assign = st.text_input("Owner / Department")
            
            if st.form_submit_button("✅ Register Software"):
                if name:
                    new_s = SoftwareAsset(name=name, version=ver, license_key=key, expiry_date=expiry, assigned_to=assign)
                    db.add(new_s)
                    db.commit()
                    st.success(f"Successfully registered {name}.")
                    st.rerun()
                else:
                    st.error("Software Title is required.")

    elif option == "Manage Licenses":
        st.subheader("Edit/Maintenance Console")
        assets = db.query(SoftwareAsset).all()
        if assets:
            s_sel = st.selectbox("Select Software Asset", assets, format_func=lambda x: f"{x.name} (v{x.version})")
            
            with st.form("edit_software"):
                col1, col2 = st.columns(2)
                e_name = col1.text_input("Name", value=s_sel.name)
                e_ver = col2.text_input("Version", value=s_sel.version or "")
                e_key = col1.text_input("Key", value=s_sel.license_key or "")
                e_expiry = col2.date_input("Expiry", value=s_sel.expiry_date)
                e_status = st.selectbox("Status", ["Active", "Expired", "Pending Update"], index=["Active", "Expired", "Pending Update"].index(s_sel.status if s_sel.status in ["Active", "Expired", "Pending Update"] else "Active"))
                
                if st.form_submit_button("💾 Save Updates"):
                    s_sel.name = e_name
                    s_sel.version = e_ver
                    s_sel.license_key = e_key
                    s_sel.expiry_date = e_expiry
                    s_sel.status = e_status
                    db.commit()
                    st.success("Software record updated.")
                    st.rerun()
            
            st.divider()
            if st.button("🔴 PERMANENTLY DELETE RECORD"):
                db.delete(s_sel)
                db.commit()
                st.success("Asset removed.")
                st.rerun()
        else:
            st.info("No software available to manage.")
