import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import Asset, AssetLog, MaintenanceSchedule
from database.db_manager import get_db
from datetime import datetime, timedelta
from utils.time_utils import get_ist, get_ist_date

def run_machinery_module():
    st.header("Machinery & Asset Management 🚜")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Asset Control", [
            "Fleet & Asset List", 
            "Register Asset", 
            "Usage Logs", 
            "Preventive Maintenance",
            "Maintenance History"
        ])
        
    if option == "Register Asset":
        st.subheader("Asset & Fleet Onboarding")
        with st.form("reg_asset"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Asset Name / Model*")
            a_type = col2.selectbox("Asset Category", ["Machinery", "Vehicle", "Fleet", "Tools", "Office Asset"])
            purchase = col1.date_input("Purchase Date")
            status = col2.selectbox("Initial Status", ["Active", "Maintenance", "Standby"])
            
            if st.form_submit_button("Onboard Asset"):
                if name:
                    new_a = Asset(name=name, type=a_type, purchase_date=purchase, status=status)
                    db.add(new_a)
                    db.commit()
                    st.success(f"Asset '{name}' added to {a_type} category.")
                    st.rerun()

    elif option == "Fleet & Asset List":
        st.subheader("Central Asset Registry")
        assets = db.query(Asset).all()
        if assets:
            data = [{
                "ID": a.id, "Asset": a.name, "Type": a.type, 
                "Status": a.status, "Age (Days)": (get_ist_date() - a.purchase_date).days if a.purchase_date else 0
            } for a in assets]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            a_sel = st.selectbox("Select Asset to Manage", assets, format_func=lambda x: f"{x.name} ({x.type})")
            if st.button("🔴 Retire Asset"):
                a_sel.status = "Retired"
                db.commit()
                st.success("Asset retired from service.")
                st.rerun()
        else:
            st.info("Direct assets found.")

    elif option == "Usage Logs":
        st.subheader("Daily Usage & Fuel Tracking")
        assets = db.query(Asset).filter(Asset.status != "Retired").all()
        if not assets:
            st.warning("Register assets first.")
        else:
            with st.form("usage_form"):
                col1, col2 = st.columns(2)
                a_sel = col1.selectbox("Asset", assets, format_func=lambda x: x.name)
                date = col2.date_input("Date")
                hours = col1.number_input("Hours Used", min_value=0.0)
                fuel = col2.number_input("Fuel Consumed (Ltrs)", min_value=0.0)
                notes = st.text_area("Observations")
                
                if st.form_submit_button("Post Log"):
                    new_log = AssetLog(asset_id=a_sel.id, date=date, hours_used=hours, fuel_consumed=fuel, notes=notes)
                    db.add(new_log)
                    db.commit()
                    st.success("Usage log recorded.")

    elif option == "Preventive Maintenance":
        st.subheader("Preventive Maintenance Scheduler 🛠️")
        tab1, tab2 = st.tabs(["Upcoming Schedule", "Create Schedule"])
        
        with tab1:
            schedules = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.status != "Completed").all()
            if schedules:
                data = [{
                    "ID": s.id, "Asset": s.asset.name, "Task": s.task_name,
                    "Date": s.scheduled_date, "Status": s.status
                } for s in schedules]
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                s_sel = st.selectbox("Update Schedule Status", schedules, format_func=lambda x: f"{x.task_name} for {x.asset.name}")
                colx, coly = st.columns(2)
                cost = colx.number_input("Actual Service Cost (₹)", min_value=0.0)
                if coly.button("Complete Service"):
                    s_sel.status = "Completed"
                    s_sel.performed_date = get_ist_date()
                    s_sel.cost = cost
                    # Also update Asset status back to Active
                    s_sel.asset.status = "Active"
                    db.commit()
                    st.success("Maintenance task marked as completed.")
                    st.rerun()
            else:
                st.info("No pending maintenance scheduled.")
                
        with tab2:
            assets = db.query(Asset).all()
            with st.form("maint_form"):
                a_sel = st.selectbox("Select Asset for Maintenance", assets, format_func=lambda x: x.name)
                task = st.text_input("Maintenance Task (e.g. Engine Oil Change)")
                date = st.date_input("Scheduled Date", value=get_ist_date() + timedelta(days=30))
                
                if st.form_submit_button("Schedule Task"):
                    new_ms = MaintenanceSchedule(asset_id=a_sel.id, task_name=task, scheduled_date=date, status="Scheduled")
                    db.add(new_ms)
                    db.commit()
                    st.success(f"Task scheduled for {a_sel.name}.")

    elif option == "Maintenance History":
        st.subheader("Service & Repair History")
        history = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.status == "Completed").all()
        if history:
            df = pd.DataFrame([{
                "Asset": h.asset.name, "Task": h.task_name, "Date": h.performed_date, "Cost": f"₹{h.cost:,.2f}"
            } for h in history])
            st.dataframe(df, use_container_width=True)
            
            total_maint = sum(h.cost for h in history)
            st.metric("Total Maintenance Spend", f"₹{total_maint:,.2f}")
        else:
            st.info("No service history found.")
