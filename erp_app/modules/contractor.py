import streamlit as st
import pandas as pd
from database.models import Employee, Attendance
from database.db_manager import get_db
from datetime import datetime
from utils.time_utils import get_ist_date

def run_contractor_module():
    st.header("Contractor & Labour Management 🤝")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Actions", ["Workforce View", "Daily Attendance", "Manage Workers"])
        
    if option == "Workforce View":
        st.subheader("Global Workforce Directory")
        # Filter for Contractors/Sub-contract labor specifically if needed, 
        # but usually shows all site workers
        workers = db.query(Employee).filter(Employee.is_active == True).all()
        if workers:
            data = [{
                "ID": w.id,
                "Worker Name": w.name,
                "Role/Trade": w.role or "Helper",
                "Daily Rate (₹)": f"₹{w.salary:,.2f}",
                "Joining Date": w.joining_date,
                "Contract": w.contract_type or "Contract"
            } for w in workers]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Export Option
            st.download_button("📥 Export Workforce List", df.to_csv(index=False), "workforce.csv", "text/csv")
        else:
            st.info("No active workforce found. Register workers in 'Manage Workers'.")

    elif option == "Daily Attendance":
        st.subheader("Site Attendance Logger")
        date_sel = st.date_input("Service Date", value=get_ist_date())
        
        workers = db.query(Employee).filter(Employee.is_active == True).all()
        
        if not workers:
            st.error("Operation Failed: No active workers found in the database.")
        else:
            st.write(f"Logging for: **{date_sel.strftime('%A, %d %b %Y')}**")
            
            # Using a table-like input form
            with st.form("att_batch_form"):
                updates = []
                for w in workers:
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.write(f"👤 **{w.name}**\n\n*{w.role or 'General'}")
                    
                    # Fetch existing if daily entry already made
                    existing = db.query(Attendance).filter(Attendance.employee_id == w.id, Attendance.date == date_sel).first()
                    
                    status_idx = ["Present", "Absent", "Half Day", "Leave"].index(existing.status if existing and existing.status in ["Present", "Absent", "Half Day", "Leave"] else "Present")
                    
                    stat = c2.selectbox("Status", ["Present", "Absent", "Half Day", "Leave"], index=status_idx, key=f"c_att_{w.id}")
                    hrs = c3.number_input("Hours", min_value=0.0, max_value=24.0, value=float(existing.hours_worked if existing else 8.0), key=f"c_hrs_{w.id}")
                    
                    updates.append((w.id, stat, hrs))
                
                if st.form_submit_button("✅ Save Daily Logs"):
                    for w_id, s, h in updates:
                        entry = db.query(Attendance).filter(Attendance.employee_id == w_id, Attendance.date == date_sel).first()
                        if entry:
                            entry.status = s
                            entry.hours_worked = h
                        else:
                            new_e = Attendance(employee_id=w_id, date=date_sel, status=s, hours_worked=h)
                            db.add(new_e)
                    db.commit()
                    st.success("Attendance records updated successfully.")

    elif option == "Manage Workers":
        tab_list, tab_reg = st.tabs(["Update/Remove Workers", "Register New Personnel"])
        
        with tab_reg:
            st.subheader("Register Site Workforce")
            with st.form("reg_worker"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Full Name*")
                role = col2.text_input("Trade/Skill (e.g. Electrician, Plumbler)")
                wage = col1.number_input("Daily Rate (₹)", min_value=0.0)
                type_ = col2.selectbox("Contract Type", ["Contract", "Daily Wage", "Permanent"])
                joined = col1.date_input("Joining Date")
                
                if st.form_submit_button("Onboard Worker"):
                    if name:
                        new_w = Employee(name=name, role=role, salary=wage, contract_type=type_, joining_date=joined, is_active=True)
                        db.add(new_w)
                        db.commit()
                        st.success(f"Successfully registered {name}.")
                        st.rerun()
                    else:
                        st.error("Worker name is mandatory.")

        with tab_list:
            st.subheader("Workforce Master Maintenance")
            workers = db.query(Employee).all()
            if workers:
                w_sel = st.selectbox("Select Worker to Modify", workers, format_func=lambda x: f"{x.name} ({x.role or 'General'})")
                
                with st.form("edit_worker_form"):
                    col1, col2 = st.columns(2)
                    e_name = col1.text_input("Update Name", value=w_sel.name)
                    e_role = col2.text_input("Update Trade", value=w_sel.role or "")
                    e_wage = col1.number_input("Update Rate (₹)", value=float(w_sel.salary or 0))
                    e_status = col2.checkbox("Active Member", value=w_sel.is_active)
                    
                    if st.form_submit_button("💾 Save Profile Changes"):
                        w_sel.name = e_name
                        w_sel.role = e_role
                        w_sel.salary = e_wage
                        w_sel.is_active = e_status
                        db.commit()
                        st.success("Profile updated.")
                        st.rerun()
                
                st.divider()
                if st.button("🔴 DELETE WORKER PERMANENTLY"):
                    db.delete(w_sel)
                    db.commit()
                    st.success("Worker removed from database.")
                    st.rerun()
            else:
                st.info("No workers registered yet.")
