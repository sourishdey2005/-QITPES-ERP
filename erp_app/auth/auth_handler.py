import streamlit as st
import bcrypt
from database.models import User, UserRole
from database.db_manager import SessionLocal
from datetime import datetime

class AuthHandler:
    def __init__(self):
        self.db = SessionLocal()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, stored_hash, password):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())

    def login(self, email, password):
        """Authenticates user and sets session state"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if user and self.verify_password(user.password_hash, password):
            if not user.is_active:
                return False, "Account is disabled."
            
            # Set Session State
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user.id
            st.session_state['username'] = user.username
            st.session_state['role'] = user.role.value
            return True, "Login successful"
            
        return False, "Invalid email or password"

    def logout(self):
        """Clear session state"""
        st.session_state.clear()
        
    def check_access(self, required_roles):
        """Check if current user has access to the page/module"""
        if 'role' not in st.session_state:
            return False
        
        current_role = st.session_state['role']
        # Owner has access to everything
        if current_role == UserRole.OWNER.value:
            return True
        
        if current_role in required_roles:
            return True
            
        return False

    def reset_password(self, email, new_password):
        """Resets the password for a given user email"""
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = self.hash_password(new_password)
            self.db.commit()
            return True, "Password updated successfully"
        return False, "User not found"

    def create_user(self, username, email, password, role=UserRole.ACCOUNTANT):
        """Function to create new users (also used for self-registration)"""
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            return False, "An account with this email already exists"
        
        hashed = self.hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed,
            role=role
        )
        self.db.add(new_user)
        self.db.commit()
        return True, "User created successfully. Please login."
