import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import Project
from database.db_manager import get_db

def run_planning_module():
    st.header("Planning & Estimation 🗓️")
    db = next(get_db())
    
    projects = db.query(Project).all()
    if not projects:
        st.info("Start by creating a project in the Project Management module to begin planning.")
        return
        
    with st.sidebar:
        option = st.radio("Planning Actions", ["Budget Estimation", "Resource Loading", "Milestone Tracking"])

    if option == "Budget Estimation":
        st.subheader("Detailed Project Budget Estimation")
        p_sel = st.selectbox("Select Project for Deep Estimation", projects, format_func=lambda x: f"{x.name} (Target: ₹{x.total_budget:,.0f})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🧱 Material Breakdown")
            mat_cement = st.number_input("Cement/Binding (Est. ₹)", min_value=0.0)
            mat_steel = st.number_input("Steel/Structure (Est. ₹)", min_value=0.0)
            mat_sand = st.number_input("Sand/Aggregate (Est. ₹)", min_value=0.0)
            mat_misc = st.number_input("Misc Materials (Est. ₹)", min_value=0.0)
            total_mat = mat_cement + mat_steel + mat_sand + mat_misc
            
        with col2:
            st.markdown("##### 👷 Resource & Indirects")
            labour_daily = st.number_input("Skilled & Unskilled Labour (Est. ₹)", min_value=0.0)
            consultancy = st.number_input("Consultancy & Architects (Est. ₹)", min_value=0.0)
            safety = st.number_input("Safety & Security (Est. ₹)", min_value=0.0)
            contingency = st.slider("Contingency Buffer (%)", 0, 20, 5)
            
            total_indirect = labour_daily + consultancy + safety
            sub_total = total_mat + total_indirect
            buffer_amt = sub_total * (contingency / 100)
            grand_total = sub_total + buffer_amt

        st.divider()
        st.subheader("Estimation Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Grand Total Estimate", f"₹{grand_total:,.0f}")
        m2.metric("Target Budget", f"₹{p_sel.total_budget:,.0f}")
        variance = p_sel.total_budget - grand_total
        m3.metric("Variance", f"₹{variance:,.0f}", delta=variance)

        if st.button("💾 Lock Estimation"):
            st.success(f"Final estimate locked for {p_sel.name}.")

    elif option == "Resource Loading":
        st.subheader("Human & Machinery Resource Loading")
        st.write("Visual allocation of workforce across project phases.")
        
        # Resource Loading Visualization
        df_res = pd.DataFrame([
            {"Phase": "Excavation", "Labour Units": 15, "Machinery Units": 5},
            {"Phase": "Foundation", "Labour Units": 30, "Machinery Units": 3},
            {"Phase": "Slab Casting", "Labour Units": 45, "Machinery Units": 8},
            {"Phase": "Brickwork", "Labour Units": 25, "Machinery Units": 1},
        ])
        fig = px.bar(df_res, x="Phase", y=["Labour Units", "Machinery Units"], barmode="group", title="Resource Loading Plan")
        st.plotly_chart(fig, use_container_width=True)

    elif option == "Milestone Tracking":
        st.subheader("Milestone & Phase Planning")
        p_sel = st.selectbox("Select Project for Timeline", projects, format_func=lambda x: x.name)
        
        milestones = [
            {"Task": "Site Cleanup", "Start": p_sel.start_date, "Duration": 7},
            {"Task": "Foundation", "Start": p_sel.start_date + timedelta(days=7), "Duration": 30},
            {"Task": "Structure", "Start": p_sel.start_date + timedelta(days=37), "Duration": 90},
            {"Task": "Finishing", "Start": p_sel.start_date + timedelta(days=127), "Duration": 60}
        ]
        
        df_m = pd.DataFrame(milestones)
        df_m['End'] = df_m.apply(lambda x: x['Start'] + timedelta(days=x['Duration']), axis=1)
        
        fig = px.timeline(df_m, x_start="Start", x_end="End", y="Task", color="Task", title=f"Gantt Chart: {p_sel.name}")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
