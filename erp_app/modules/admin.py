import streamlit as st
from database.models import User
from database.db_manager import get_db

def run_admin_module():
    st.header("Admin Console 🛡️")
    db = next(get_db())
    
    st.subheader("System Users")
    users = db.query(User).all()
    
    for u in users:
        with st.expander(f"{u.username} ({u.role.value})"):
            st.write(f"Email: {u.email}")
            st.write(f"Active: {u.is_active}")
            if st.button(f"Deactivate {u.username}", key=u.id):
                db.delete(u)
                db.commit()
                st.rerun()
