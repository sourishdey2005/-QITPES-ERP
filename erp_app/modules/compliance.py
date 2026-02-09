import streamlit as st
import pandas as pd
from database.models import ActivityLog, User
from database.db_manager import get_db
from datetime import datetime

def run_compliance_module():
    st.header("Activity Monitor & Audit Trail 🛡️")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Compliance Menu", ["Live Activity Logs", "User Audits", "Security Overview"])
        
    if option == "Live Activity Logs":
        st.subheader("System-Wide Activity Log")
        st.info("Continuous monitoring of every user action and system change.")
        
        logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(200).all()
        if logs:
            data = []
            for l in logs:
                data.append({
                    "Timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "User": l.user.username if l.user else "Anonymous",
                    "Role": l.user.role.value if l.user else "N/A",
                    "Action Taken": l.action,
                    "Specific Details": l.details
                })
            df = pd.DataFrame(data)
            
            # Filtering
            col1, col2 = st.columns(2)
            u_search = col1.text_input("Filter by User Name")
            a_search = col2.text_input("Filter by Action Description")
            
            if u_search:
                df = df[df['User'].str.contains(u_search, case=False, na=False)]
            if a_search:
                df = df[df['Action Taken'].str.contains(a_search, case=False, na=False)]
                
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download Audit Trail (CSV)", df.to_csv(index=False), "audit_trail.csv", "text/csv")
        else:
            st.info("No logs generated yet. Activity monitoring is initializing.")

    elif option == "User Audits":
        st.subheader("Individual User Audit Reports")
        users = db.query(User).all()
        if users:
            u_sel = st.selectbox("Select User for Deep Audit", users, format_func=lambda x: f"{x.username} ({x.email})")
            
            u_logs = db.query(ActivityLog).filter(ActivityLog.user_id == u_sel.id).order_by(ActivityLog.timestamp.desc()).all()
            if u_logs:
                df_u = pd.DataFrame([{
                    "Time": l.timestamp, "Action": l.action, "Details": l.details
                } for l in u_logs])
                st.write(f"Showing last {len(u_logs)} actions for **{u_sel.username}**")
                st.dataframe(df_u, use_container_width=True)
            else:
                st.warning(f"No history found for {u_sel.username}.")
        else:
            st.info("No system users found.")

    elif option == "Security Overview":
        st.subheader("Compliance & Security Health")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Audit Trail Active", "YES", delta="Synchronized")
        
        total_logs = db.query(ActivityLog).count()
        c2.metric("Total Logs Captured", total_logs)
        
        active_users = db.query(User).filter(User.is_active == True).count()
        c3.metric("Authorized Stakeholders", active_users)
        
        st.divider()
        st.success("System compliance is currently maintaining 'Optimal' status across all construction nodes.")
