import streamlit as st
import hashlib
import time 
import re
from section import dashboardver2_1
from datetime import datetime
from section.utils.helper import insert_user, insert_admin, get_admin_by_username, get_user_by_username

st.set_page_config(page_title='Dashboard', layout='wide')

# Dummy admin key
VALID_ADMIN_KEY = 13102002

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Check if the email has a valid format (contains @ and .)"""
    return '@' in email and '.' in email.split('@')[-1]

def signup(user_type, user_id, username, password, email, admin_key=None):
    if not all([user_id, username, password, email]):
        return False, "Please fill in all fields."
    
    if not is_valid_email(email):
        return False, "Invalid email format. Must contain '@' and a domain (e.g., '.com')."
    
    if user_type == "Admin":
        if not admin_key:
            return False, "Admin Key is required for Admin signup."
        try:
            if int(admin_key.strip()) != VALID_ADMIN_KEY:
                return False, "Invalid Admin Key."
        except ValueError:
            return False, "Admin Key must be a number."
    
    timestamp = datetime.now()
    hashed_password = hash_password(password)
    
    try:
        role = user_type
        if user_type == "User":
            insert_user(user_id, username, hashed_password, email, timestamp, role)
        elif user_type == "Admin":
            insert_admin(user_id, username, hashed_password, email, timestamp, role)
        
        return True, f"{user_type} signed up successfully!"
    
    except Exception as e:
        if "duplicate" in str(e).lower():
            return False, "Username, Email, or ID already exists."
        return False, "Signup failed. Please check your details and try again."


def login(username, password):
    hashed_pw = hash_password(password)

    user = get_user_by_username(username)
    if user and user.get('password') == hashed_pw:
        st.session_state.user_role = "user" 
        return True, f"Welcome, {username} (User)!"

    admin = get_admin_by_username(username)
    if admin and admin.get('password') == hashed_pw:
        st.session_state.user_role = "admin"  
        return True, f"Welcome, {username} (Admin)!"

    return False, "Invalid username or password."


def main():
    # If already logged in, show the dashboard
    if 'login_success' in st.session_state and st.session_state.login_success:
        dashboardver2_1.show_dashboard()  # Call the function to show the dashboard
        return  # Exit to prevent rendering the login/signup forms

    st.title("🔐 Login")

    page = st.radio("Select Action", ["Login", "Signup"])

    if page == "Signup":
        st.subheader("📝 Signup Form")

        if "signup_success" not in st.session_state:
            st.session_state.signup_success = False

        if st.session_state.signup_success:
            st.success("User signed up and stored in database.")
            st.session_state.signup_success = False  # Reset flag
            st.stop()  # Prevent form from showing again immediately

        with st.form("signup_form"):
            user_type = st.selectbox("Choose User Type", ["User", "Admin"])
            user_id = st.text_input("User ID")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            admin_key = st.text_input("Admin Key", type="password") if user_type == "Admin" else None

            submitted = st.form_submit_button("Signup")
            if submitted:
                success, message = signup(user_type, user_id, username, password, email, admin_key)
                if success:
                    st.session_state.signup_success = True
                    st.rerun()  # Refresh the page after successful signup
                else:
                    st.error(message)

    elif page == "Login":
        st.subheader("🔑 Login Form")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            success, message = login(username, password)
            if success:
                st.success("Login successful! Redirecting to dashboard...")
                st.session_state.login_success = True  # Set login success flag
                st.session_state.username = username  # Store username in session state
                time.sleep(1.5)  # Wait for a moment before switching
                st.rerun()  # Trigger rerun to show the dashboard
            else:
                st.error(message)

if __name__ == "__main__":
    main()
