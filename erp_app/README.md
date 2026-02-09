# Enterprise ERP System 🏗️

A comprehensive, production-ready ERP system built with Streamlit and Python.

## 🚀 Quick Start

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

3.  **First Login**
    The system comes with a built-in "Seed Data" function.
    Log in with the **Owner** account to initialize sample data.

    **Default Credentials:**
    -   **Owner**: `owner@company.com` / `admin123`
    -   **Director**: `director@company.com` / `admin123`
    -   **Accountant**: `accounts@company.com` / `admin123`

## 📂 Project Structure

-   `app.py`: Main entry point.
-   `auth/`: Authentication logic & role management.
-   `modules/`: Feature modules (Projects, Finance, HR, Inventory, etc.).
-   `database/`: Database models (SQLAlchemy) & connection handling.
-   `ui/`: Custom CSS & UI components.
-   `utils/`: Helper scripts (e.g., Data Seeder).

## 🛠️ Configuration

### Database
By default, the app uses **SQLite** for zero-config portability (`erp.db`).
To use **PostgreSQL** or **Supabase**:
1.  Create a `.env` file in the root directory.
2.  Add your connection string:
    ```env
    DATABASE_URL=postgresql://user:password@host:port/dbname
    ```

## 📦 Modules Included

1.  **Project Management**: Track projects, budgets, and status.
2.  **Finance**: Income/Expense tracking, Ledger, Cash Flow.
3.  **Inventory**: Stock management, Low stock alerts.
4.  **HR & Payroll**: Employee management, automated payroll generation.
5.  **Admin Console**: User management and system settings.
6.  **Reports**: Export data to CSV/Excel.
7.  **Planning, Plant, Machinery**: (Placeholder modules for future expansion).

## 🎨 UI/UX

-   **White/Corporate Theme**: Clean, professional interface.
-   **Sidebar Navigation**: Role-based access control.
-   **Interactive Charts**: Powered by Plotly.

## 🔒 Security

-   **Authentication**: Secure login with bcrypt password hashing.
-   **RBAC**: Role-Based Access Control enforcing permissions.
-   **Audit Logs**: Tracking critical user actions.
