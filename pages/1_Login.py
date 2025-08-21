import streamlit as st
# Login Page - set_page_config must be the first Streamlit command
st.set_page_config(layout="wide")

import sqlite3
import webbrowser
import time
from src.db_utils import create_user_db

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

st.markdown('<h1 style="color:#24497a;text-align:center;margin-bottom:1.5em;">Login</h1>', unsafe_allow_html=True)

# Center the form using columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form(key='login_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button(label='Login')
        
        if submit_button:
            if check_user(username, password):
                st.success('Login successful!')
                st.session_state.logged_in = True
                st.session_state.username = username
                # Redirect to home after successful login
                st.success("Login successful! Redirecting to dashboard...")
                time.sleep(2)
                try:
                    st.switch_page("Home")
                except Exception as e:
                    st.error(f"Error navigating to Home: {e}")
                    st.info("Please use the sidebar to navigate to the Home page")
            else:
                st.error('Invalid username or password')
    
    # Note: Removed redundant navigation buttons as sidebar navigation works correctly

def check_user(username, password):
    """Check if user credentials are valid"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None
