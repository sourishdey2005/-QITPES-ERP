import streamlit as st
import pandas as pd
from database.models import HSERecord, DocumentAsset, Project
from database.db_manager import get_db
from datetime import datetime

def run_site_ops_module():
    st.header("Site Operations & Compliance 🏗️")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Ops Menu", [
            "HSE Management (Health & Safety)", 
            "DMS (Document Management)", 
            "Workflow & Approvals"
        ])
        
    if option == "HSE Management (Health & Safety)":
        st.subheader("HSE Incident & Inspection Tracker")
        tab1, tab2 = st.tabs(["Log HSE Entry", "Inspection History"])
        
        projects = db.query(Project).all()
        
        with tab1:
            with st.form("hse_form"):
                col1, col2 = st.columns(2)
                p_sel = col1.selectbox("Site Location", projects, format_func=lambda x: x.name)
                i_type = col2.selectbox("Entry Type", ["Safety Inspection", "Near Miss", "Site Injury", "Environmental Check"])
                
                desc = st.text_area("Observation / Incident Details")
                action = st.text_area("Corrective Action Taken")
                reporter = st.text_input("Reported By")
                
                if st.form_submit_button("🚨 Submit HSE Report"):
                    new_hse = HSERecord(project_id=p_sel.id, incident_type=i_type, description=desc, action_taken=action, reported_by=reporter)
                    db.add(new_hse)
                    db.commit()
                    st.success("HSE Record synchronized to Central Safety Register.")
                    
        with tab2:
            hses = db.query(HSERecord).all()
            if hses:
                st.dataframe(pd.DataFrame([{
                    "Date": h.date, "Site": h.project.name if h.project else "N/A",
                    "Type": h.incident_type, "Reporter": h.reported_by, "Status": h.status
                } for h in hses]), use_container_width=True)
            else:
                st.info("No HSE incidents recorded. Site safety is currently optimal.")

    elif option == "DMS (Document Management)":
        st.subheader("Centralized Document Management System")
        tab1, tab2 = st.tabs(["Asset Repository", "Upload New Asset"])
        
        with tab1:
            docs = db.query(DocumentAsset).all()
            if docs:
                st.dataframe(pd.DataFrame([{
                    "ID": d.id, "Title": d.title, "Category": d.category,
                    "Project": d.project.name if d.project else "Global", "Uploaded": d.upload_date
                } for d in docs]))
            else:
                st.info("Repository empty. Upload site drawings or contracts.")
                
        with tab2:
            projects = db.query(Project).all()
            with st.form("dms_form"):
                title = st.text_input("Document Title*")
                cat = st.selectbox("Category", ["Drawing", "Contract", "Permit", "License", "Insurance"])
                p_sel = st.selectbox("Link to Project", projects, format_func=lambda x: x.name)
                # Placeholder for real file handling
                st.write("---")
                st.caption("Simulator: Files would be stored securely in the cloud/on-prem vault.")
                
                if st.form_submit_button("📂 Upload to DMS"):
                    if title:
                        new_doc = DocumentAsset(title=title, category=cat, project_id=p_sel.id)
                        db.add(new_doc)
                        db.commit()
                        st.success("Document vaulted successfully.")
                    else:
                        st.error("Title needed.")

    elif option == "Workflow & Approvals":
        st.subheader("Workflow & Approval Engine Status")
        st.info("Monitor cross-module requests awaiting management sign-off.")
        
        # Real-time search for 'Pending' statuses across POs and Bills
        from database.models import PurchaseOrder, Bill
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.status == "Pending").all()
        bills = db.query(Bill).filter(Bill.status == "Unpaid").all()
        
        st.markdown(f"#### ⏳ Critical Approvals Pending ({len(pos) + len(bills)})")
        
        cola, colb = st.columns(2)
        cola.metric("PO Approvals", len(pos))
        colb.metric("Bill Settlements", len(bills))
        
        if pos:
            st.write("**Purchase Orders Awaiting Sign-off:**")
            st.dataframe(pd.DataFrame([{ "ID": p.id, "Vendor": p.vendor.name, "Amount": p.total_amount } for p in pos]))
        
        if bills:
            st.write("**Invoices Awaiting Cash Release:**")
            st.dataframe(pd.DataFrame([{ "ID": b.id, "Vendor": b.vendor.name, "Amount": b.amount } for b in bills]))
