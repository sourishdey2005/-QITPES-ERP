import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import Client, Contract, Project
from database.db_manager import get_db
from datetime import datetime

def run_crm_module():
    st.header("Mini CRM & Contract Management 🤝")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("CRM Menu", ["Client Directory", "Contract Master", "Generate Contract", "CRM Analytics"])
        
    if option == "Client Directory":
        st.subheader("Client & Lead Management")
        tab1, tab2 = st.tabs(["View Clients", "Add New Client"])
        
        with tab1:
            clients = db.query(Client).all()
            if clients:
                df = pd.DataFrame([{
                    "ID": c.id, "Name": c.name, "Company": c.company or "Individual",
                    "Email": c.email, "Phone": c.phone, "Status": c.status
                } for c in clients])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No clients found. Start by adding a new lead.")
        
        with tab2:
            with st.form("new_client"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Full Name*")
                comp = col2.text_input("Company Name")
                email = col1.text_input("Email")
                phone = col2.text_input("Phone")
                addr = st.text_area("Address")
                status = st.selectbox("Status", ["Lead", "Active", "Inactive"])
                
                if st.form_submit_button("✅ Onboard Client"):
                    if name:
                        new_c = Client(name=name, company=comp, email=email, phone=phone, address=addr, status=status)
                        db.add(new_c)
                        db.commit()
                        st.success(f"Client '{name}' added successfully.")
                        st.rerun()
                    else:
                        st.error("Name is required.")

    elif option == "Contract Master":
        st.subheader("Construction & Service Contracts")
        contracts = db.query(Contract).all()
        if contracts:
            df = pd.DataFrame([{
                "ID": c.id, "Title": c.title, "Client": c.client.name if c.client else "N/A",
                "Value": f"₹{c.contract_value:,.2f}", "Status": c.status, "Expiry": c.end_date
            } for c in contracts])
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            c_sel = st.selectbox("Select Contract to Manage", contracts, format_func=lambda x: f"{x.title} ({x.client.name if x.client else 'N/A'})")
            with st.form("edit_contract"):
                e_status = st.selectbox("Update Status", ["Draft", "Signed", "Terminated", "Completed"], 
                                      index=["Draft", "Signed", "Terminated", "Completed"].index(c_sel.status if c_sel.status in ["Draft", "Signed", "Terminated", "Completed"] else "Draft"))
                e_terms = st.text_area("Contract Terms", value=c_sel.terms or "")
                
                if st.form_submit_button("💾 Save Contract Changes"):
                    c_sel.status = e_status
                    c_sel.terms = e_terms
                    db.commit()
                    st.success("Contract updated.")
                    st.rerun()
        else:
            st.info("No contracts found. Use 'Generate Contract' to create one.")

    elif option == "Generate Contract":
        st.subheader("New Contract Lifecycle")
        clients = db.query(Client).all()
        projects = db.query(Project).all()
        
        if not clients:
            st.error("Register a client first.")
        else:
            with st.form("new_contract"):
                title = st.text_input("Contract Title* (e.g., Construction Agreement Site A)")
                c_sel = st.selectbox("Link to Client", clients, format_func=lambda x: f"{x.name} ({x.company or 'Individual'})")
                p_sel = st.selectbox("Link to Project (Optional)", [None] + projects, format_func=lambda x: x.name if x else "No Project Linked")
                val = st.number_input("Contract Value (₹)", min_value=0.0)
                
                col1, col2 = st.columns(2)
                start = col1.date_input("Start Date")
                end = col2.date_input("End Date")
                
                terms = st.text_area("Special Terms / Clauses")
                
                if st.form_submit_button("📝 Draft Contract"):
                    if title:
                        new_cnt = Contract(
                            title=title, client_id=c_sel.id, project_id=p_sel.id if p_sel else None,
                            contract_value=val, start_date=start, end_date=end, terms=terms, status="Draft"
                        )
                        db.add(new_cnt)
                        db.commit()
                        st.success(f"Contract '{title}' drafted.")
                    else:
                        st.error("Title is required.")

    elif option == "CRM Analytics":
        st.subheader("Client & Contract Insights 📊")
        clients = db.query(Client).all()
        contracts = db.query(Contract).all()
        
        if clients:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Clients", len(clients))
            c2.metric("Active Leads", len([c for c in clients if c.status == "Lead"]))
            
            total_cv = sum(c.contract_value for c in contracts)
            c3.metric("Pipeline Value", f"₹{total_cv:,.0f}")
            
            st.divider()
            col_l, col_r = st.columns(2)
            
            with col_l:
                # Client Status
                df_c = pd.DataFrame([{ "Status": c.status } for c in clients])
                fig_c = px.pie(df_c, names="Status", title="Client Conversion Status", hole=0.4)
                st.plotly_chart(fig_c, use_container_width=True)
                
            with col_r:
                # Contract Value by Status
                if contracts:
                    df_v = pd.DataFrame([{ "Status": c.status, "Value": c.contract_value } for c in contracts])
                    fig_v = px.bar(df_v, x="Status", y="Value", color="Status", title="Contract Value by Status")
                    st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.info("Insufficient data for CRM analytics.")
