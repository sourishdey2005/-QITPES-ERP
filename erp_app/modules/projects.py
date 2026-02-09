import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import Session
from database.models import Project, ProjectStatus
from database.db_manager import get_db
from datetime import datetime, timedelta
from utils.time_utils import get_ist

def run_projects_module():
    st.header("Project Management 🏗️")
    
    db = next(get_db())
    
    # --- Sidebar Actions ---
    with st.sidebar:
        st.subheader("Manage Projects")
        action = st.radio("Actions", ["View All", "Create New", "Management", "Analytics"])
    
    # --- Create Project ---
    if action == "Create New":
        st.subheader("New Project Master")
        with st.form("new_project_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Project Name")
            client = col2.text_input("Client Name")
            budget = col1.number_input("Total Budget (₹)", min_value=0.0)
            status = col2.selectbox("Status", [s.value for s in ProjectStatus])
            start_date = col1.date_input("Start Date")
            end_date = col2.date_input("End Date")
            desc = st.text_area("Description")
            
            submitted = st.form_submit_button("Create Project")
            if submitted:
                new_proj = Project(
                    name=name, client=client, total_budget=budget,
                    status=ProjectStatus(status), start_date=start_date,
                    end_date=end_date, description=desc
                )
                db.add(new_proj)
                db.commit()
                st.success(f"Project '{name}' created successfully!")
                st.rerun()
                
    # --- View Projects ---
    elif action == "View All":
        projects = db.query(Project).all()
        if projects:
            data = [{
                "ID": p.id, "Name": p.name, "Client": p.client,
                "Budget": f"₹{p.total_budget:,.2f}", "Status": p.status.value,
                "Progress": f"{p.progress}%", "Start": p.start_date
            } for p in projects]
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            selected_id = st.selectbox("Select Project for Details", df['ID'])
            if selected_id:
                proj = db.query(Project).get(selected_id)
                st.write(f"**Description:** {proj.description}")
        else:
            st.info("No projects found. Create one!")

    # --- Management (Edit/Delete) ---
    elif action == "Management":
        st.subheader("Project Maintenance")
        projects = db.query(Project).all()
        if not projects:
            st.info("No projects to manage.")
        else:
            proj_to_edit = st.selectbox("Select Project to Update", projects, format_func=lambda x: f"{x.id}: {x.name}")
            
            with st.form("edit_project_form"):
                col1, col2 = st.columns(2)
                e_name = col1.text_input("Project Name", value=proj_to_edit.name)
                e_client = col2.text_input("Client Name", value=proj_to_edit.client)
                e_budget = col1.number_input("Total Budget", value=proj_to_edit.total_budget)
                e_status = col2.selectbox("Status", [s.value for s in ProjectStatus], index=[s.value for s in ProjectStatus].index(proj_to_edit.status.value))
                e_progress = col1.slider("Progress %", 0, 100, proj_to_edit.progress)
                e_desc = st.text_area("Description", value=proj_to_edit.description or "")
                
                if st.form_submit_button("Update Project Details"):
                    proj_to_edit.name = e_name
                    proj_to_edit.client = e_client
                    proj_to_edit.total_budget = e_budget
                    proj_to_edit.status = ProjectStatus(e_status)
                    proj_to_edit.progress = e_progress
                    proj_to_edit.description = e_desc
                    db.commit()
                    st.success("Project updated successfully!")
                    st.rerun()

            st.divider()
            if st.button("🔴 DELETE PROJECT PERMANENTLY"):
                if st.session_state.get('confirm_delete') == proj_to_edit.id:
                    db.delete(proj_to_edit)
                    db.commit()
                    st.success("Project deleted.")
                    st.session_state['confirm_delete'] = None
                    st.rerun()
                else:
                    st.session_state['confirm_delete'] = proj_to_edit.id
                    st.warning("Click again to confirm deletion. This cannot be undone.")

    # --- Analytics ---
    elif action == "Analytics":
        st.subheader("Advanced Project Analytical Platform 📊")
        projects = db.query(Project).all()
        
        if projects:
            # Prepare Data
            df = pd.DataFrame([{ 
                "ID": p.id,
                "Name": p.name,
                "Client": p.client,
                "Budget": p.total_budget,
                "Status": p.status.value,
                "Progress": p.progress,
                "Start": pd.to_datetime(p.start_date),
                "End": pd.to_datetime(p.end_date)
            } for p in projects])
            
            # --- ROW 1: CORE KPIs ---
            st.markdown("### 🔑 Core Performance Indicators")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            total_projects = len(df)
            active_count = len(df[df['Status'] == ProjectStatus.ACTIVE.value])
            total_budget = df['Budget'].sum()
            avg_progress = df['Progress'].mean()
            
            kpi1.metric("Total Projects", total_projects)
            kpi2.metric("Active Projects", active_count)
            kpi3.metric("Portfolio Value", f"₹{total_budget:,.0f}")
            kpi4.metric("Avg. Completion", f"{avg_progress:.1f}%")
            
            # --- ROW 2: DETAILED KPIs ---
            st.markdown("### 📈 Tactical Metrics")
            kpi5, kpi6, kpi7, kpi8 = st.columns(4)
            
            completed_count = len(df[df['Status'] == ProjectStatus.COMPLETED.value])
            unique_clients = df['Client'].nunique()
            avg_budget = df['Budget'].mean()
            upcoming_deadlines = len(df[(df['End'] >= get_ist()) & (df['End'] <= get_ist() + timedelta(days=30))])
            
            kpi5.metric("Completed", completed_count)
            kpi6.metric("Unique Clients", unique_clients)
            kpi7.metric("Avg. Project Value", f"₹{avg_budget:,.0f}")
            kpi8.metric("Deadlines (30d)", upcoming_deadlines)
            
            # --- ROW 3: HIGHLIGHTS ---
            st.markdown("### 🏆 Portfolio Highlights")
            kpi9, kpi10, kpi11, kpi12 = st.columns(4)
            
            largest_project = df.loc[df['Budget'].idxmax()]['Name'] if not df.empty else "N/A"
            planned_count = len(df[df['Status'] == ProjectStatus.PLANNED.value])
            on_hold_count = len(df[df['Status'] == ProjectStatus.ON_HOLD.value])
            high_value_count = len(df[df['Budget'] > avg_budget])
            
            kpi9.metric("Largest Project", largest_project)
            kpi10.metric("Planned Projects", planned_count)
            kpi11.metric("Projects On-Hold", on_hold_count)
            kpi12.metric("High-Value (>Avg)", high_value_count)

            st.divider()
            
            # --- VISUALIZATIONS ---
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                # Status Distribution
                fig_status = px.pie(df, names='Status', title='Project Portfolio by Status',
                                   color_discrete_sequence=px.colors.qualitative.Prism)
                st.plotly_chart(fig_status, use_container_width=True)
                
            with col_v2:
                # Top Clients by Budget
                client_spend = df.groupby('Client')['Budget'].sum().sort_values(ascending=False).reset_index()
                fig_client = px.bar(client_spend, x='Client', y='Budget', title='Top Clients by Investment Value',
                                   labels={'Budget': 'Total Budget (₹)'}, color='Budget')
                st.plotly_chart(fig_client, use_container_width=True)

            # Budget vs Progress Scatter
            st.markdown("### 🔍 Strategic Overview")
            fig_scatter = px.scatter(df, x='Budget', y='Progress', size='Budget', color='Status',
                                    hover_name='Name', title='Budget vs. Completion Matrix',
                                    labels={'Budget': 'Project Budget (₹)', 'Progress': 'Phase Percentage (%)'})
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        else:
            st.info("Add projects to the system to unlock advanced analytics.")
