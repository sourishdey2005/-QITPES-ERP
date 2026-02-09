import streamlit as st
import pandas as pd
from database.models import Employee, Attendance
from database.db_manager import get_db
from datetime import datetime
from utils.time_utils import get_ist_date

def run_labour_module():
    st.header("Labour Management 👷")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Labour Actions", ["Workforce View", "Daily Attendance", "Management Console"])
        
    if option == "Workforce View":
        st.subheader("Workforce Directory")
        # Assuming role "Worker" or "Labour" for this module
        workers = db.query(Employee).filter(Employee.is_active == True).all()
        if workers:
            data = [{
                "ID": w.id,
                "Name": w.name,
                "Skill/Role": w.role or "Unskilled",
                "Daily Wage (₹)": w.salary or 0,
                "Joined": w.joining_date
            } for w in workers]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total Active Workforce: {len(workers)}")
        else:
            st.info("No active workers found. Use Management Console to register them.")

    elif option == "Daily Attendance":
        st.subheader("Post Daily Attendance")
        date_sel = st.date_input("Attendance Date", value=get_ist_date())
        workers = db.query(Employee).filter(Employee.is_active == True).all()
        
        if not workers:
            st.error("No workers registered.")
        else:
            with st.form("attendance_form"):
                st.write("Mark Status for Today:")
                attendance_list = []
                for w in workers:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    col1.write(f"**{w.name}** ({w.role or 'Worker'})")
                    status = col2.selectbox("Status", ["Present", "Absent", "Half Day", "Leave"], key=f"att_{w.id}")
                    hours = col3.number_input("Hrs", min_value=0.0, max_value=24.0, value=8.0, key=f"hrs_{w.id}")
                    attendance_list.append((w.id, status, hours))
                
                if st.form_submit_button("✅ Submit Attendance"):
                    for w_id, stat, hrs in attendance_list:
                        # Check if already exists for this date
                        existing = db.query(Attendance).filter(Attendance.employee_id == w_id, Attendance.date == date_sel).first()
                        if existing:
                            existing.status = stat
                            existing.hours_worked = hrs
                        else:
                            new_att = Attendance(employee_id=w_id, date=date_sel, status=stat, hours_worked=hrs)
                            db.add(new_att)
                    db.commit()
                    st.success(f"Attendance recorded for {date_sel}")

    elif option == "Management Console":
        tab1, tab2 = st.tabs(["Register Labour", "Edit/Remove Records"])
        
        with tab1:
            st.subheader("Onboard New Labour")
            with st.form("new_labour"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Full Name*")
                role = col2.text_input("Skill/Title (e.g. Mason, Helper)")
                wage = col1.number_input("Daily Wage (₹)", min_value=0.0)
                joined = col2.date_input("Joining Date")
                
                if st.form_submit_button("Register Worker"):
                    if name:
                        new_w = Employee(name=name, role=role, salary=wage, joining_date=joined, contract_type="Labour", is_active=True)
                        db.add(new_w)
                        db.commit()
                        st.success(f"Registered {name}")
                        st.rerun()
                    else:
                        st.error("Name is required.")

        with tab2:
            st.subheader("Manage Workforce Data")
            workers = db.query(Employee).all()
            if workers:
                w_sel = st.selectbox("Select Worker", workers, format_func=lambda x: f"{x.name} ({x.role})")
                with st.form("edit_labour"):
                    e_name = st.text_input("Name", value=w_sel.name)
                    e_role = st.text_input("Role", value=w_sel.role or "")
                    e_wage = st.number_input("Daily Wage (₹)", value=float(w_sel.salary or 0))
                    e_active = st.checkbox("Active Status", value=w_sel.is_active)
                    
                    if st.form_submit_button("Update Worker"):
                        w_sel.name = e_name
                        w_sel.role = e_role
                        w_sel.salary = e_wage
                        w_sel.is_active = e_active
                        db.commit()
                        st.success("Record updated.")
                        st.rerun()
                
                if st.button("🔴 PERMANENT DELETE"):
                    db.delete(w_sel)
                    db.commit()
                    st.success("Worker deleted.")
                    st.rerun()
            else:
                st.info("No workers to manage.")
