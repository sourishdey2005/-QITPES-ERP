import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import Project, ProductionLog, QualityCheck
from database.db_manager import get_db
from datetime import datetime, timedelta

def run_production_module():
    st.header("Plant & Production Management 🏭")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Control Panel", ["Daily Logging", "Quality Control (QC)", "Log History", "Production Analytics"])
        
    if option == "Daily Logging":
        st.subheader("New Production Log Entry")
        projects = db.query(Project).all()
        if not projects:
            st.error("Please create projects first to link production data.")
        else:
            with st.form("prod_form"):
                col1, col2 = st.columns(2)
                p_sel = col1.selectbox("Assign to Project/Site", projects, format_func=lambda x: x.name)
                item_name = col2.text_input("Product / Batch Name*", placeholder="e.g. Concrete Batch A")
                
                qty = col1.number_input("Output Quantity", min_value=0.0, step=1.0)
                unit = col2.selectbox("Unit", ["Units", "Tons", "m³", "kg", "Blocks"])
                
                waste = col1.number_input("Waste Generated", min_value=0.0, step=0.1)
                eff = col2.slider("Estimated Efficiency (%)", 0, 100, 85)
                
                log_date = st.date_input("Production Date")
                notes = st.text_area("Production Notes")
                
                if st.form_submit_button("🚀 Post Production Log"):
                    if not item_name:
                        st.error("Product Name is required.")
                    else:
                        detailed_notes = f"Item: {item_name} | Unit: {unit} | {notes}"
                        new_log = ProductionLog(project_id=p_sel.id, quantity_produced=qty, waste_generated=waste, efficiency=eff, date=log_date, notes=detailed_notes)
                        db.add(new_log)
                        db.commit()
                        st.success(f"Log for '{item_name}' saved.")
                        st.rerun()

    elif option == "Quality Control (QC)":
        st.subheader("Quality Assurance & Inspection 🧪")
        tab1, tab2 = st.tabs(["QC Inspections", "Inspection Ledger"])
        
        logs = db.query(ProductionLog).order_by(ProductionLog.date.desc()).all()
        
        with tab1:
            if not logs:
                st.info("No production logs to inspect.")
            else:
                st.markdown("#### Record New Quality Check")
                log_sel = st.selectbox("Select Batch/Log", logs, format_func=lambda x: f"ID {x.id}: {x.notes[:30]} ({x.date})")
                
                with st.form("qc_form"):
                    col1, col2 = st.columns(2)
                    param = col1.text_input("Parameter (e.g. Compression Strength)")
                    res = col2.selectbox("Result", ["Pass", "Fail", "Pending Re-test"])
                    remarks = st.text_area("Inspector Remarks")
                    
                    if st.form_submit_button("💾 Save QC Result"):
                        new_qc = QualityCheck(production_id=log_sel.id, parameter=param, result=res, remarks=remarks)
                        db.add(new_qc)
                        db.commit()
                        st.success("Quality inspection recorded.")
                        
        with tab2:
            qcs = db.query(QualityCheck).all()
            if qcs:
                st.dataframe(pd.DataFrame([{
                    "Date": q.date, "Batch ID": q.production_id, 
                    "Parameter": q.parameter, "Result": q.result, "Remarks": q.remarks
                } for q in qcs]), use_container_width=True)
                
    elif option == "Log History":
        st.subheader("Production & Inspection History")
        logs = db.query(ProductionLog).all()
        if logs:
            df = pd.DataFrame([{
                "ID": l.id, "Date": l.date, "Project": l.project.name if l.project else "N/A",
                "Output": l.quantity_produced, "Efficiency": f"{l.efficiency}%"
            } for l in logs])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No history found.")

    elif option == "Production Analytics":
        st.subheader("Performance Intelligence")
        logs = db.query(ProductionLog).all()
        if logs:
            df = pd.DataFrame([{ "Date": l.date, "Output": l.quantity_produced, "Waste": l.waste_generated } for l in logs])
            st.metric("Total Plant Yield", f"{df['Output'].sum():,.0f} Units")
            fig = px.bar(df, x="Date", y="Output", title="Output Quantity over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for analytics.")
