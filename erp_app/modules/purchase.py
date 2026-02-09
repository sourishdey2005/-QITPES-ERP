import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import Vendor, PurchaseOrder
from database.db_manager import get_db
from datetime import datetime, timedelta
from utils.time_utils import get_ist, get_ist_date

def run_purchase_module():
    st.header("Purchase Management 🛒")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Options", ["Vendor List", "Manage Vendors", "Create PO", "Track Orders", "Purchase Analytics"])
        
    if option == "Vendor List":
        st.subheader("Our Registered Vendors")
        vendors = db.query(Vendor).all()
        if vendors:
            data = []
            for v in vendors:
                data.append({
                    "ID": v.id,
                    "Company Name": v.name,
                    "Contact Person": v.contact_person or "N/A",
                    "Phone": v.phone or "N/A",
                    "Email": v.email or "N/A",
                    "Rating": "⭐" * (v.rating if v.rating else 0)
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Export option placeholder
            st.download_button("📥 Export Vendor List", df.to_csv(index=False), "vendors.csv", "text/csv")
        else:
            st.info("No vendors found. Go to 'Manage Vendors' to add your first partner.")

    elif option == "Manage Vendors":
        tab1, tab2 = st.tabs(["Add New Vendor", "Update/Delete Vendor"])
        
        with tab1:
            st.subheader("Register New Partner")
            with st.form("new_vendor_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Company Name*")
                contact = col2.text_input("Contact Person")
                phone = col1.text_input("Phone Number")
                email = col2.text_input("Email Address")
                rating = st.slider("Quality/Reliability Rating", 1, 5, 3)
                
                if st.form_submit_button("✅ Onboard Vendor"):
                    if name:
                        new_v = Vendor(name=name, contact_person=contact, phone=phone, email=email, rating=rating)
                        db.add(new_v)
                        db.commit()
                        st.success(f"Vendor '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Company Name is required.")

        with tab2:
            st.subheader("Vendor Master Maintenance")
            vendors = db.query(Vendor).all()
            if vendors:
                v_to_edit = st.selectbox("Select Vendor", vendors, format_func=lambda x: f"{x.name} (ID: {x.id})")
                with st.form("edit_v"):
                    e_name = st.text_input("Company Name", value=v_to_edit.name)
                    e_contact = st.text_input("Contact Person", value=v_to_edit.contact_person or "")
                    e_phone = st.text_input("Phone", value=v_to_edit.phone or "")
                    e_email = st.text_input("Email", value=v_to_edit.email or "")
                    e_rating = st.slider("Rating", 1, 5, v_to_edit.rating if v_to_edit.rating else 3)
                    
                    if st.form_submit_button("💾 Save Changes"):
                        v_to_edit.name = e_name
                        v_to_edit.contact_person = e_contact
                        v_to_edit.phone = e_phone
                        v_to_edit.email = e_email
                        v_to_edit.rating = e_rating
                        db.commit()
                        st.success("Vendor details updated.")
                        st.rerun()
                
                st.divider()
                if st.button("🔴 DELETE VENDOR PERMANENTLY"):
                    if st.session_state.get('v_del_id') == v_to_edit.id:
                        db.delete(v_to_edit)
                        db.commit()
                        st.success("Vendor removed.")
                        st.session_state['v_del_id'] = None
                        st.rerun()
                    else:
                        st.session_state['v_del_id'] = v_to_edit.id
                        st.warning("Click again to confirm PERMANENT deletion.")
            else:
                st.info("No vendors registered yet.")

    elif option == "Create PO":
        st.subheader("Generate Purchase Order")
        vendors = db.query(Vendor).all()
        if not vendors:
            st.error("You must register a Vendor first.")
        else:
            with st.form("po_form"):
                col1, col2 = st.columns(2)
                v_sel = col1.selectbox("Vendor Selection", vendors, format_func=lambda x: x.name)
                po_ref = col2.text_input("PO Reference #", value=f"PO-{get_ist().strftime('%Y%m%d%H%M')}")
                
                amt = col1.number_input("Total Order Amount (₹)", min_value=0.0)
                date = col2.date_input("Expected Delivery Date")
                
                notes = st.text_area("Order Notes / Item Specifications")
                
                st.caption("Status will be set to 'Pending' by default for approval workflow.")
                
                if st.form_submit_button("📝 Generate Purchase Order"):
                    new_po = PurchaseOrder(
                        vendor_id=v_sel.id, 
                        total_amount=amt, 
                        expected_delivery=date,
                        status="Pending"
                    )
                    db.add(new_po)
                    db.commit()
                    st.success(f"PO {po_ref} generated for {v_sel.name}.")

    elif option == "Track Orders":
        st.subheader("PO Tracking & Status Management")
        
        status_filter = st.multiselect("Filter by Status", ["Pending", "Approved", "Delivered", "Cancelled"], default=["Pending", "Approved"])
        
        query = db.query(PurchaseOrder)
        if status_filter:
            query = query.filter(PurchaseOrder.status.in_(status_filter))
            
        orders = query.all()
        
        if orders:
            data = [{
                "PO ID": p.id,
                "Vendor": p.vendor.name,
                "Amount": f"₹{p.total_amount:,.2f}",
                "Delivery Date": p.expected_delivery,
                "Current Status": p.status
            } for p in orders]
            
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            
            st.divider()
            st.subheader("Update Order Status")
            o_to_update = st.selectbox("Select PO to Update", orders, format_func=lambda x: f"PO {x.id} - {x.vendor.name} (Amount: ₹{x.total_amount})")
            
            col_s1, col_s2 = st.columns([2, 1])
            new_status = col_s1.selectbox("New Status", ["Pending", "Approved", "Delivered", "Cancelled"], index=["Pending", "Approved", "Delivered", "Cancelled"].index(o_to_update.status if o_to_update.status in ["Pending", "Approved", "Delivered", "Cancelled"] else "Pending"))
            
            if col_s2.button("Update Status"):
                o_to_update.status = new_status
                db.commit()
                st.success(f"PO {o_to_update.id} updated to {new_status}")
                st.rerun()
                
            if st.button("🧺 DELETE PO RECORD"):
                db.delete(o_to_update)
                db.commit()
                st.success("Order record wiped.")
                st.rerun()
        else:
            st.info("No orders matching your criteria.")

    elif option == "Purchase Analytics":
        st.subheader("Purchase & Procurement Intelligence 📈")
        orders = db.query(PurchaseOrder).all()
        vendors = db.query(Vendor).all()
        
        if orders:
            df = pd.DataFrame([{
                "Vendor": p.vendor.name,
                "Amount": p.total_amount,
                "Status": p.status,
                "Date": pd.to_datetime(p.order_date),
                "Delivery": pd.to_datetime(p.expected_delivery)
            } for p in orders])

            # --- SECTION 1: FINANCIAL KPIs ---
            st.markdown("### 💰 Financial Procurement Stats")
            f1, f2, f3, f4 = st.columns(4)
            
            total_spend = df['Amount'].sum()
            avg_order = df['Amount'].mean()
            max_order = df['Amount'].max()
            min_order = df['Amount'].min()
            
            f1.metric("Total Procurement", f"₹{total_spend:,.0f}")
            f2.metric("Avg. Order Value", f"₹{avg_order:,.0f}")
            f3.metric("Largest PO", f"₹{max_order:,.0f}")
            f4.metric("Smallest PO", f"₹{min_order:,.0f}")

            # --- SECTION 2: ORDER LOGISTICS ---
            st.markdown("### 📦 Order & Logistics KPIs")
            l1, l2, l3, l4 = st.columns(4)
            
            total_orders = len(df)
            pending_count = len(df[df['Status'] == "Pending"])
            delivered_val = df[df['Status'] == "Delivered"]['Amount'].sum()
            success_rate = (len(df[df['Status'].isin(["Approved", "Delivered"])]) / total_orders * 100) if total_orders > 0 else 0
            
            l1.metric("Total POs issued", total_orders)
            l2.metric("Pending Approval", pending_count)
            l3.metric("Material Received", f"₹{delivered_val:,.0f}")
            l4.metric("Success Rate", f"{success_rate:.1f}%")

            # --- SECTION 3: VENDOR & STRATEGY ---
            st.markdown("### 🤝 Vendor & Strategy KPIs")
            v1, v2, v3, v4 = st.columns(4)
            
            active_vendors = df['Vendor'].nunique()
            top_vendor = df.groupby('Vendor')['Amount'].sum().idxmax()
            upcoming_deliveries = len(df[(df['Delivery'] >= get_ist()) & (df['Status'] != "Delivered")])
            daily_burn = total_spend / 30 # Simple estimate for a month
            
            v1.metric("Active Vendors", active_vendors)
            v2.metric("Top Partner", top_vendor[:15] + "..." if len(top_vendor) > 15 else top_vendor)
            v3.metric("Upcoming Deliv.", upcoming_deliveries)
            v4.metric("Est. Monthly Burn", f"₹{daily_burn:,.0f}")

            st.divider()

            # --- VISUALIZATIONS ---
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Spend by Vendor
                fig_vendor = px.pie(df, values='Amount', names='Vendor', hole=0.4,
                                   title='Procurement Value by Vendor',
                                   color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_vendor, use_container_width=True)
            
            with col_chart2:
                # Status Breakdown
                status_grouped = df.groupby('Status').size().reset_index(name='Count')
                fig_status = px.bar(status_grouped, x='Status', y='Count', color='Status',
                                   title='Order Volume by Lifecycle Stage',
                                   color_discrete_map={"Pending": "#fbbf24", "Approved": "#3b82f6", "Delivered": "#10b981", "Cancelled": "#ef4444"})
                st.plotly_chart(fig_status, use_container_width=True)

            # Timeline of Spending
            st.markdown("### 📅 Spending Timeline")
            df_time = df.sort_values("Date")
            fig_time = px.line(df_time, x="Date", y="Amount", markers=True,
                              title="PO Value Trend Over Time",
                              labels={"Amount": "Order Amount (₹)", "Date": "Issue Date"})
            st.plotly_chart(fig_time, use_container_width=True)
            
        else:
            st.info("Insufficient data for detailed procurement analytics. Issue your first PO to see metrics.")
