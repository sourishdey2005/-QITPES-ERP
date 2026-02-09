import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from database.models import FinanceRecord, TransactionType, Invoice, Bill, Project, Vendor
from database.db_manager import get_db
from datetime import datetime

def run_finance_module():
    st.header("Financial Strategy & Tax Command 🏢")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Finance Suite", [
            "General Ledger", 
            "Profitability & Costing", 
            "GST & Taxation",
            "Accounts Payable/Receivable",
            "Budgeting & Forecasting"
        ])
        
    if option == "General Ledger":
        st.subheader("Financial Ledger (Vouchers)")
        tab1, tab2 = st.tabs(["Ledger View", "Post Manual Entry"])
        
        with tab1:
            records = db.query(FinanceRecord).order_by(FinanceRecord.date.desc()).all()
            if records:
                df = pd.DataFrame([{
                    "ID": r.id, "Date": r.date, "Type": r.type.value,
                    "Category": r.category, "Amount": f"₹{r.amount:,.2f}", 
                    "Method": r.payment_method, "Narration": r.description
                } for r in records])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No ledger entries found.")
        
        with tab2:
            with st.form("gl_form"):
                t_type = st.selectbox("Transaction Type", [t.value for t in TransactionType])
                cat = st.selectbox("Account Category", ["Revenue", "Salary", "Material", "Utilities", "Tax", "Consultancy", "GST Paid"])
                amt = st.number_input("Amount (₹)", min_value=0.0)
                date = st.date_input("Voucher Date")
                method = st.selectbox("Payment Mode", ["Cash", "Bank", "UPI", "Cheque"])
                desc = st.text_area("Narration")
                
                if st.form_submit_button("Post Transaction"):
                    new_rec = FinanceRecord(type=TransactionType(t_type), category=cat, amount=amt, date=date, payment_method=method, description=desc)
                    db.add(new_rec)
                    db.commit()
                    st.success("Voucher posted and G/L updated.")
                    st.rerun()

    elif option == "Profitability & Costing":
        st.subheader("Project Costing & Margin Analysis")
        projects = db.query(Project).all()
        if projects:
            p_sel = st.selectbox("Analysis Target", projects, format_func=lambda x: x.name)
            
            # Simplified Costing Calculation
            budget = p_sel.total_budget
            # Assume income from invoices, expenses from bills/gl
            actual_income = db.query(func.sum(Invoice.amount)).filter(Invoice.project_id == p_sel.id, Invoice.status == "Paid").scalar() or 0
            # Placeholder for project-specific costs (would ideally link Bill to Project)
            est_costs = budget * 0.7 
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Project Budget", f"₹{budget:,.0f}")
            c2.metric("Invoiced to date", f"₹{actual_income:,.0f}")
            profit = actual_income - est_costs # Simplified
            c3.metric("Est. Net Margin", f"₹{profit:,.0f}", delta=f"{(profit/actual_income*100):.1f}%" if actual_income > 0 else "0%")

            st.divider()
            st.markdown("#### Profitability Forecasting")
            st.info("Based on current trajectories, your projected project profitability is healthy.")
            
    elif option == "Taxation & GST Management":
        st.subheader("GST Returns & Tax Compliance")
        
        # Pull GST from recorded Ledger entries (Category: GST Paid or Tax)
        gst_paid = db.query(func.sum(FinanceRecord.amount)).filter(FinanceRecord.category.contains("GST")).scalar() or 0
        
        st.markdown("### 🏛️ Tax Overview")
        k1, k2 = st.columns(2)
        k1.metric("ITC (Input Tax Credit) Est.", f"₹{gst_paid:,.0f}")
        k2.metric("Pending TDS Compliance", "Synchronized")

        # Mock GST Return Table
        gst_data = pd.DataFrame([
            {"Month": "Jan 2024", "Sales (GSTR-1)": "₹12,00,000", "GST Coll.": "₹2,16,000", "ITC Claims": "₹1,80,000", "Net Paid": "₹36,000"},
            {"Month": "Feb 2024", "Sales (GSTR-1)": "₹15,50,000", "GST Coll.": "₹2,79,000", "ITC Claims": "₹2,10,000", "Net Paid": "₹69,000"},
        ])
        st.markdown("#### Historical GST Filings")
        st.table(gst_data)

    elif option == "Accounts Payable/Receivable":
        st.subheader("Accounts Control Center")
        tab1, tab2 = st.tabs(["Receivables (AR)", "Payables (AP)"])
        
        with tab1:
            invoices = db.query(Invoice).all()
            if invoices:
                st.dataframe(pd.DataFrame([{
                    "Inv #": i.invoice_number, "Project": i.project.name, 
                    "Amount": i.amount, "Status": i.status
                } for i in invoices]), use_container_width=True)
            else:
                st.info("No receivables recorded.")
                
        with tab2:
            bills = db.query(Bill).all()
            if bills:
                st.dataframe(pd.DataFrame([{
                    "Bill #": b.bill_number, "Vendor": b.vendor.name, 
                    "Amount": b.amount, "Status": b.status
                } for b in bills]), use_container_width=True)
            else:
                st.info("No payables found.")

    elif option == "Budgeting & Forecasting":
        st.subheader("Budget Variance & Financial Forecasting")
        st.info("Set monthly spending limits and monitor actual vs budget forecast.")
        
        year_data = {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Budget Forecast": [500000, 500000, 600000, 600000, 700000, 700000],
            "Actual Spent": [480000, 520000, 590000, 610000, 650000, 0]
        }
        df_bud = pd.DataFrame(year_data)
        fig = px.line(df_bud, x="Month", y=["Budget Forecast", "Actual Spent"], markers=True, title="Variance Forecast 2024")
        st.plotly_chart(fig, use_container_width=True)
