import streamlit as st
import pandas as pd
from database.models import InventoryItem
from database.db_manager import get_db

def run_inventory_module():
    st.header("Inventory & Store 📦")
    db = next(get_db())
    
    with st.sidebar:
        option = st.radio("Inventory", ["Stock Overview", "Log Stock Entry", "Manage Items"])

    if option == "Log Stock Entry":
        col1, col2 = st.columns(2)
        with col1.form("stock_form"):
            st.subheader("Update / Add Item")
            name = st.text_input("Item Name")
            cat = st.selectbox("Category", ["Raw Material", "Tools", "Chemicals", "Spares"])
            qty = st.number_input("In/Out Quantity (+/-)", value=0)
            min_stock = st.number_input("Min Alert Level", value=10)
            
            if st.form_submit_button("Submit"):
                item = db.query(InventoryItem).filter(InventoryItem.name == name).first()
                if item:
                    item.current_stock += qty
                    st.success(f"Updated {name}. New Stock: {item.current_stock}")
                else:
                    new_item = InventoryItem(name=name, category=cat, current_stock=qty, min_stock_alert=min_stock)
                    db.add(new_item)
                    st.success(f"Added new item {name}")
                db.commit()

    elif option == "Manage Items":
        st.subheader("Inventory Master Management")
        items = db.query(InventoryItem).all()
        if not items:
            st.info("No items to manage.")
        else:
            item_to_edit = st.selectbox("Select SKU", items, format_func=lambda x: f"{x.name} ({x.category})")
            
            with st.form("edit_inv_form"):
                e_name = st.text_input("Name", value=item_to_edit.name)
                e_cat = st.text_input("Category", value=item_to_edit.category)
                e_stock = st.number_input("Stock Level", value=item_to_edit.current_stock)
                e_min = st.number_input("Min Alert", value=item_to_edit.min_stock_alert)
                
                if st.form_submit_button("Update SKU Details"):
                    item_to_edit.name = e_name
                    item_to_edit.category = e_cat
                    item_to_edit.current_stock = e_stock
                    item_to_edit.min_stock_alert = e_min
                    db.commit()
                    st.success("Item updated.")
                    st.rerun()

            if st.button("🔴 DELETE SKU PERMANENTLY"):
                db.delete(item_to_edit)
                db.commit()
                st.success("Item removed from inventory.")
                st.rerun()

    elif option == "Stock Overview":
        items = db.query(InventoryItem).all()
        if items:
            df = pd.DataFrame([{
                "ID": i.id, "Name": i.name, "Cat": i.category,
                "Qty": i.current_stock, "Alert": i.min_stock_alert,
                "Status": "⚠️ LOW" if i.current_stock <= i.min_stock_alert else "OK"
            } for i in items])
            st.dataframe(df, use_container_width=True)
            
            low_stock_count = len(df[df['Status'] == "⚠️ LOW"])
            if low_stock_count > 0:
                st.warning(f"{low_stock_count} items are low on stock!")
        else:
            st.info("Inventory list is currently empty.")
