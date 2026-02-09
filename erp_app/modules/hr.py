import streamlit as st
import pandas as pd
from database.models import Employee, Payroll, Attendance, TrainingRecord
from database.db_manager import get_db
from datetime import datetime
from utils.time_utils import get_ist_date

def run_hr_module():
    st.header("Human Resource & Workforce Management 👥")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("HR Suite", [
            "Staff Onboarding", 
            "Workforce Directory", 
            "Payroll & Benefits", 
            "Training & Skill Matrix",
            "Shift & Attendance Management"
        ])
        
    if option == "Staff Onboarding":
        st.subheader("New Employee Registration")
        with st.form("new_emp"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Full Name*")
            role = col2.selectbox("Designation", ["Manager", "Staff", "Supervisor", "Driver", "Worker", "Engineer"])
            dept = col1.text_input("Department (e.g., Accounts, Site 1, IT)")
            salary = col2.number_input("Monthly Salary (₹)", min_value=0.0)
            joined = col1.date_input("Joining Date")
            type_ = col2.selectbox("Contract Type", ["Permanent", "Contract", "Probation"])
            
            if st.form_submit_button("✅ Register Personnel"):
                if name:
                    new_emp = Employee(name=name, role=role, department=dept, salary=salary, joining_date=joined, contract_type=type_, is_active=True)
                    db.add(new_emp)
                    db.commit()
                    st.success(f"Personnel '{name}' onboarded successfully.")
                else:
                    st.error("Name is required.")

    elif option == "Workforce Directory":
        st.subheader("Dynamic Workforce Table")
        emps = db.query(Employee).all()
        if emps:
            df = pd.DataFrame([{
                "ID": e.id, "Name": e.name, "Role": e.role,
                "Dept": e.department, "Salary": f"₹{e.salary:,.0f}", 
                "Status": "Active" if e.is_active else "Inactive",
                "Contract": e.contract_type
            } for e in emps])
            
            # Filters
            col_s1, col_s2 = st.columns(2)
            search = col_s1.text_input("🔍 Search Name/Dept")
            if search:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("Modify Employee Profile")
            emp_sel = st.selectbox("Select Profile", emps, format_func=lambda x: f"{x.name} ({x.role})")
            with st.expander("Edit Personal Details"):
                with st.form("edit_emp"):
                    e_name = st.text_input("Internal Name", value=emp_sel.name)
                    e_active = st.checkbox("Current Active Staff", value=emp_sel.is_active)
                    if st.form_submit_button("Update Profile"):
                        emp_sel.name = e_name
                        emp_sel.is_active = e_active
                        db.commit()
                        st.success("Synchronized successfully.")
                        st.rerun()

    elif option == "Payroll & Benefits":
        st.subheader("Advanced Payroll Processor")
        month = st.date_input("Select Month for Processing").strftime("%Y-%m")
        active_emps = db.query(Employee).filter(Employee.is_active == True).all()
        
        if st.button(f"🚀 Execute Payroll for {month}"):
            payroll_data = []
            for emp in active_emps:
                # Basic calculation logic
                deductions = emp.salary * 0.05 # Mock PT/Contribution
                net = emp.salary - deductions
                payroll_data.append({
                    "Employee": emp.name, 
                    "Gross Pay": f"₹{emp.salary:,.2f}", 
                    "Tax/Ded.": f"-₹{deductions:,.2f}", 
                    "Net Payable": f"₹{net:,.2f}"
                })
                # Commit to DB
                new_p = Payroll(employee_id=emp.id, month=month, basic_salary=emp.salary, deductions=deductions, net_salary=net, status="Paid")
                db.add(new_p)
            
            db.commit()
            st.success(f"Payroll cycles completed for {month}")
            st.table(pd.DataFrame(payroll_data))

    elif option == "Training & Skill Matrix":
        st.subheader("Employee Skill Development & Certificates")
        tab1, tab2 = st.tabs(["Active Matrix", "Record Training"])
        
        with tab1:
            records = db.query(TrainingRecord).all()
            if records:
                st.dataframe(pd.DataFrame([{
                    "Employee": r.employee.name if r.employee else "N/A",
                    "Training": r.training_name,
                    "Completed": r.date_completed,
                    "Result": r.score
                } for r in records]))
            else:
                st.info("No training records found. Build your skill matrix now.")
                
        with tab2:
            emps = db.query(Employee).all()
            with st.form("training_form"):
                e_sel = st.selectbox("Personnel", emps, format_func=lambda x: x.name)
                t_name = st.text_input("Training Name (e.g., HSE Safety, Advanced Crane Op)")
                date = st.date_input("Completion Date")
                score = st.selectbox("Performance", ["Excellent", "Proficient", "Average", "Needs Improvement"])
                
                if st.form_submit_button("Add to Matrix"):
                    new_tr = TrainingRecord(employee_id=e_sel.id, training_name=t_name, date_completed=date, score=score)
                    db.add(new_tr)
                    db.commit()
                    st.success("Skill Matrix updated.")

    elif option == "Shift & Attendance Management":
        st.subheader("Site Shifts & Time Tracking")
        st.info("Log attendance relative to assigned site shifts.")
        
        date_sel = st.date_input("Attendance Date", value=get_ist_date())
        emps = db.query(Employee).filter(Employee.is_active == True).all()
        
        with st.form("shift_att"):
            st.write(f"Attendance for **{date_sel.strftime('%d-%b-%Y')}**")
            att_updates = []
            for e in emps:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{e.name}**")
                shift = c2.selectbox("Shift", ["General", "Night", "Overtime"], key=f"shift_{e.id}")
                status = c3.selectbox("Status", ["Present", "Absent", "Leave"], key=f"stat_{e.id}")
                att_updates.append((e.id, status))
                
            if st.form_submit_button("Commit Site Attendance"):
                for eid, stat in att_updates:
                    new_att = Attendance(employee_id=eid, date=date_sel, status=stat)
                    db.add(new_att)
                db.commit()
                st.success("Site attendance synchronization complete.")
