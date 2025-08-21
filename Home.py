import streamlit as st
# Set Streamlit layout to wide for full window - must be the first Streamlit command
st.set_page_config(layout="wide")

import pandas as pd
import hashlib
import sqlite3
from src.db_utils import create_user_db

def main():
    # Initialize session state variables if they don't exist
    if 'clicked_rfp' not in st.session_state:
        st.session_state.clicked_rfp = None
        
    # Custom CSS for background and styling
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
        .rfp-title-btn {
            background-color: transparent !important;
            color: #0066cc !important;
            text-align: left !important;
            font-weight: normal !important;
            border: none !important;
            padding: 0 !important;
            text-decoration: underline !important;
            cursor: pointer !important;
            box-shadow: none !important;
        }
        .rfp-title-btn:hover {
            color: #003d7a !important;
        }
        .stSelectbox>div>div {
            background-color: #e6f0ff;
        }
        .rfp-details {
            background-color: #f0f5ff;
            border-left: 4px solid #0066cc;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        
        /* Row-level scrolling text container */
        .row-scroll-container {
            width: 100%;
            overflow: hidden;
            background-color: #f0f6ff;
            color: #24497a;
            border-radius: 4px;
            margin: 2px 0;
            height: 22px;
        }
        
        /* Scrolling text animation */
        .row-scroll-text {
            display: inline-block;
            white-space: nowrap;
            padding-left: 100%;
            animation: row-scroll 20s linear infinite;
        }
        
        @keyframes row-scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
        
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
        
        .event-chip {
            display: inline-block;
            padding: 5px 15px;
            margin: 0 10px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 20px;
        }
        
        .event-date {
            font-weight: bold;
            margin-right: 5px;
        }
        
        .event-time {
            opacity: 0.9;
        }
        </style>
        ''', unsafe_allow_html=True)
        
    # Initialize database
    create_user_db()
    
    st.markdown('<h1 style="color:#24497a;text-align:center;margin-bottom:0.5em;">RFP Dashboard</h1>', unsafe_allow_html=True)
    df = load_data()
    
    # No details panel - removed as requested
    
    # Note: Removed redundant navigation buttons as sidebar navigation works correctly
        
    # Add headers
    header1, header2, header3, header4 = st.columns([3, 2, 2, 2])
    with header1:
        st.markdown('<div style="font-weight:bold;color:#24497a;">RFP Title</div>', unsafe_allow_html=True)
    with header2:
        st.markdown('<div style="font-weight:bold;color:#24497a;">RM</div>', unsafe_allow_html=True)
    with header3:
        st.markdown('<div style="font-weight:bold;color:#24497a;">Status</div>', unsafe_allow_html=True)
    with header4:
        st.markdown('<div style="font-weight:bold;color:#24497a;">Due Dates</div>', unsafe_allow_html=True)
    
    # Add spacing between header and first row
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    edited_df = df.copy()
    # Reset index to avoid issues with row access
    df = df.reset_index(drop=True)
    for i in range(len(df)):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            # Make RFP titles directly clickable
            title = df.loc[i, 'title']
            # Convert to string in case it's a float or NaN
            title_str = str(title) if pd.notna(title) else ""
            title_id = f"title_{i}_{hashlib.md5(title_str.encode()).hexdigest()[:8]}"
            if st.button(title, key=title_id):
                # Store the selected RFP in session state for the details page
                st.session_state.clicked_rfp = df.loc[i].to_dict()
                # Navigate to the details page
                try:
                    st.switch_page("pages/3_Details.py")
                except Exception as e:
                    st.error(f"Error navigating to Details page: {e}")
                    st.info("Please use the sidebar to navigate to the Details page")
        with col2:
            # Dropdown for Tagged RM - use predefined list
            predefined_rms = ["", "Sagar Shah", "Hardik Shah", "Harshit Bhadani", "Ruchira Nanda", "Utkarsh Chandra", "Emily Zhang", "John Doe"]
            rm_hash = hashlib.md5(str(df.loc[i].values).encode()).hexdigest()
            rm_key = f"rm_{i}_{rm_hash}"
            
            # Get current RM value
            current_rm = str(df.loc[df.index[i], 'RM']) if pd.notna(df.loc[df.index[i], 'RM']) else ""
            
            # Add current RM to list if not already there
            if current_rm and current_rm not in predefined_rms:
                predefined_rms.append(current_rm)
            
            # Find the index of the current RM in the predefined list
            try:
                current_rm_index = predefined_rms.index(current_rm)
            except ValueError:
                # If not found, default to empty (first item)
                current_rm_index = 0
                
            tagged_rm = st.selectbox(
                "Tagged RM Selection",
                predefined_rms,
                index=current_rm_index,
                key=rm_key,
                label_visibility="collapsed"
            )
            if tagged_rm != df.loc[df.index[i], 'RM']:
                edited_df.loc[df.index[i], 'RM'] = tagged_rm
                save_data(edited_df)
                st.rerun()
            else:
                edited_df.loc[df.index[i], 'RM'] = tagged_rm
        with col3:
            # Generate a unique key for this row
            row_hash = hashlib.md5(str(df.loc[i].values).encode()).hexdigest()
            key = f"status_{i}_{row_hash}"
            # Get current status value
            current_status = df.loc[df.index[i], 'status']
            
            # Create status options list with empty option first
            status_options = ['', 'accepted', 'not accepted', 'In progress', 'in progress']
            
            # Find the index of the current status in the options
            try:
                status_index = status_options.index(current_status)
            except ValueError:
                # If not found, default to empty option
                status_index = 0
                
            status = st.selectbox(
                "Status Selection",
                status_options,
                index=status_index,
                key=key,
                label_visibility="collapsed"
            )
            if status != df.loc[df.index[i], 'status']:
                edited_df.loc[df.index[i], 'status'] = status
                save_data(edited_df)
                st.rerun()
            else:
                edited_df.loc[df.index[i], 'status'] = status
        with col4:
            # Display the due dates information with moving text
            due_dates = df.loc[i, 'due dates']
            
            # Handle both NaN and 'nan' string cases
            if pd.isna(due_dates) or due_dates == 'nan' or not due_dates:
                st.write("No due dates available")
            # Check if we have JSON due dates
            elif isinstance(due_dates, str) and (due_dates.startswith('[') or due_dates.strip().startswith('[')):
                try:
                    import json
                    # Clean up the JSON string - remove any leading/trailing whitespace
                    clean_due_dates = due_dates.strip()
                    events = json.loads(clean_due_dates)
                    
                    if events and len(events) > 0:
                        # Display the first event's date as static text at the top
                        first_event = events[0]
                        due_date = first_event.get('due_date', '')
                        
                        # Create moving text with all events
                        events_text = ""
                        for event in events:
                            event_name = event.get('event', '')
                            date = event.get('due_date', '')
                            time = event.get('due_time', '')
                            events_text += f"{event_name}: {date} {time} | "
                        
                        # Show all dates in the scrolling text
                        st.markdown(f"""
                        <div class="row-scroll-container">
                            <div class="row-scroll-text">{events_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.write("Due dates format error")
                except Exception as e:
                    # Fall back to displaying an error message
                    st.write(f"Error parsing due dates")
            else:
                # If it's not JSON, just display as is
                st.write(due_dates)

# Database functions
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None


def load_data():
    # Use the expanded CSV file
    df = pd.read_csv('expanded_rfp_data.csv')
    
    # Replace string 'nan' with actual NaN values
    for col in df.columns:
        df[col] = df[col].apply(lambda x: pd.NA if x == 'nan' else x)
        
    # Convert RM and status columns to string to handle empty values correctly
    if 'RM' in df.columns:
        df['RM'] = df['RM'].astype(str).replace('nan', '')
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).replace('nan', '')
    
    # Create a sort_date column if it doesn't exist
    if 'sort_date' not in df.columns:
        df['sort_date'] = None
        print("Created sort_date column as it was missing")
    
    # Extract earliest date from due_dates JSON for sorting
    for idx, row in df.iterrows():
        if pd.notna(row.get('due dates')) and isinstance(row['due dates'], str) and row['due dates'].startswith('['):
            try:
                import json
                # Try to parse the JSON
                due_dates_json = json.loads(row['due dates'])
                # Extract all dates for sorting
                if due_dates_json and isinstance(due_dates_json, list) and len(due_dates_json) > 0:
                    # Get all dates from the events
                    dates = []
                    for event in due_dates_json:
                        if isinstance(event, dict) and 'due_date' in event:
                            date_str = event.get('due_date', '')
                            if date_str:
                                dates.append(date_str)
                    
                    # Use the earliest date for sorting
                    if dates:
                        # Convert to standard format (YYYY-MM-DD) for comparison
                        std_dates = []
                        for date_str in dates:
                            # Handle DD/MM/YYYY format
                            if '/' in date_str:
                                parts = date_str.split('/')
                                if len(parts) == 3:
                                    std_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                                    std_dates.append(std_date)
                        
                        # Find the earliest date
                        if std_dates:
                            std_dates.sort()
                            df.at[idx, 'sort_date'] = std_dates[0]
            except:
                # Keep as None if parsing fails
                pass
    
    # Map status values to accepted/not accepted/In progress if needed
    status_mapping = {
        'in progress': 'In progress',  # Update to map to the new value
        'not taken': 'not accepted'
    }
    df['status'] = df['status'].map(lambda x: status_mapping.get(str(x).lower(), x))
    
    # Handle date formatting for sorting but don't filter out rows with missing dates
    try:
        # Convert sort_date to datetime format
        df['sort_date'] = pd.to_datetime(df['sort_date'], errors='coerce')
        # Create a temporary copy with all rows and sort them
        sorted_df = df.sort_values(by='sort_date', ascending=True, na_position='last')
        # Use the sorted index but keep all rows
        df = sorted_df
    except Exception as e:
        # If sorting fails, don't sort
        pass
        
    return df

def save_data(df):
    df.to_csv('expanded_rfp_data.csv', index=False)

def extract_due_dates(df):
    """Extract and format due dates from all RFPs for display"""
    import json
    
    all_events = []
    
    for idx, row in df.iterrows():
        if pd.notna(row.get('due dates')) and isinstance(row['due dates'], str) and row['due dates'].startswith('['):
            try:
                # Extract RFP title
                rfp_title = str(row.get('title', 'Unnamed RFP'))
                
                # Parse due dates JSON
                due_dates_json = json.loads(row['due dates'])
                
                if due_dates_json and isinstance(due_dates_json, list):
                    for event in due_dates_json:
                        if isinstance(event, dict) and 'event' in event and 'due_date' in event:
                            event_name = event.get('event', '')
                            due_date = event.get('due_date', '')
                            due_time = event.get('due_time', '')
                            
                            # Create a formatted event string
                            event_str = f"{rfp_title} - {event_name}: {due_date} {due_time}"
                            all_events.append({
                                'rfp': rfp_title,
                                'event': event_name,
                                'date': due_date,
                                'time': due_time,
                                'formatted': event_str
                            })
            except Exception as e:
                # Silently continue if there's an error
                pass
                
    return all_events

def display_due_dates_marquee(df):
    """Display due dates in a scrolling marquee"""
    events = extract_due_dates(df)
    
    if events:
        # Start the scrolling container
        st.markdown('<div class="scrolling-container"><div class="scrolling-text">', unsafe_allow_html=True)
        
        # Format all events as HTML
        events_html = ""
        for event in events:
            events_html += f"<span class='event-chip'>{event['rfp']} - {event['event']}: <span class='event-date'>{event['date']}</span> <span class='event-time'>{event['time']}</span></span>"
        
        # Close the scrolling container
        st.markdown(f"{events_html}</div></div>", unsafe_allow_html=True)
    else:
        # No events found - show a simple message
        st.info("No upcoming events found in RFP data.")

if __name__ == '__main__':
    main()
