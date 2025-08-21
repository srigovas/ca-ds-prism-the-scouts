import streamlit as st
# Signup Page - set_page_config must be the first Streamlit command
st.set_page_config(layout="wide")

import sqlite3
import webbrowser
import time
from src.db_utils import create_user_db

def add_user(username, password):
    """Add a new user to the database. Returns True if successful, False if username already exists."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()

# Custom CSS for styling
st.markdown(
    '''
    <style>
    body {
        background-color: #f6f7fb;
    }
    .main {
        background-color: #f6f7fb;
    }
    .block-container {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        padding: 2rem 2rem 2rem 2rem;
        margin-top: 2rem;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-weight: bold;
    }
    </style>
    ''', unsafe_allow_html=True)

# Create the user database if it doesn't exist
create_user_db()

st.markdown('<h1 style="color:#24497a;text-align:center;margin-bottom:1.5em;">Sign Up</h1>', unsafe_allow_html=True)

# Center the form using columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Create form
    with st.form(key='signup_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        confirm_password = st.text_input('Confirm Password', type='password')
        submit_button = st.form_submit_button(label='Sign Up')
    
    # Handle form submission outside of the form context
    if submit_button:
        if not username or not password:
            st.error('Please enter both username and password')
        elif password != confirm_password:
            st.error('Passwords do not match')
        else:
            if add_user(username, password):
                st.success('Account created successfully! You can now log in.')
                # Redirect to login page after 2 seconds
                time.sleep(2)
                try:
                    st.switch_page("pages/1_Login")
                except Exception as e:
                    st.error(f"Error navigating to Login: {e}")
                    st.info("Please use the sidebar to navigate to the Login page")
            else:
                st.error('Username already exists. Please choose a different username.')
    
    # Note: Removed redundant navigation buttons as sidebar navigation works correctly

