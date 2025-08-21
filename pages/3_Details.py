import streamlit as st
# Set page config must be the first Streamlit command
st.set_page_config(page_title="RFP Details", layout="wide")

import pandas as pd
import time
import sqlite3
import sys
import os
import base64
import hashlib
import json

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db_utils import create_user_db

def main():
    # Initialize session state if not exists
    if 'clicked_rfp' not in st.session_state:
        st.session_state.clicked_rfp = None
        
    # Initialize session state for the currently displayed document
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
        
    if 'document_title' not in st.session_state:
        st.session_state.document_title = 'RFP Document'
        
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
        .stSelectbox>div>div {
            background-color: #e6f0ff;
        }
        .detail-card {
            background-color: #f0f5ff;
            border-left: 4px solid #0066cc;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        .detail-header {
            font-size: 1.4rem;
            color: #24497a;
            margin-bottom: 1rem;
        }
        .field-label {
            font-weight: bold;
            color: #24497a;
        }
        .field-value {
            margin-bottom: 0.8rem;
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
        </style>
        ''', unsafe_allow_html=True)
    
    st.markdown('<h1 style="color:#24497a;text-align:center;margin-bottom:0.5em;">RFP Details</h1>', unsafe_allow_html=True)
    
    # Check if an RFP was selected
    if st.session_state.clicked_rfp is None:
        st.info("No RFP selected. Please select an RFP from the dashboard.")
        if st.button("Return to Dashboard"):
            try:
                st.switch_page("Home.py")
            except Exception as e:
                st.error(f"Error navigating to Home: {e}")
                st.info("Please use the sidebar to navigate to the Home page")
    else:
        # Display RFP details
        rfp = st.session_state.clicked_rfp
        
        # Create a layout with two columns for the header: title and button
        header_col1, header_col2 = st.columns([3, 1])
        
        # Title header (left)
        with header_col1:
            st.markdown(f"<div class='detail-header'>{rfp['title']}</div>", unsafe_allow_html=True)
            
        # Comparison score button (right)
        with header_col2:
            if st.button("View Comparison Score", type="primary"):
                # Use document_comparison column from CSV instead of comparison_report
                if 'document_comparison' in rfp and rfp['document_comparison']:
                    st.session_state.show_comparison_score = True
                else:
                    st.warning("No comparison report available for this RFP.")
            
        # Show comparison score if button was clicked
        if 'show_comparison_score' in st.session_state and st.session_state.show_comparison_score:
            with st.expander("Comparison Analysis", expanded=True):
                st.markdown("<h3 style='text-align: center; color: #24497a;'>Document & Capability Analysis</h3>", unsafe_allow_html=True)
                
                # Add RFP Document link at the top
                if 'rfp link' in rfp and rfp['rfp link']:
                    doc_col1, doc_col2 = st.columns([4, 1])
                    with doc_col1:
                        st.markdown(f"<h5 style='margin-bottom:0px;'>📄 <span style='color:#495057;'>RFP Document:</span> {os.path.basename(rfp['rfp link'])}</h5>", unsafe_allow_html=True)
                    with doc_col2:
                        if st.button("📋 View Document", key="view_rfp_from_comparison"):
                            # Use the correct state variable (current_document instead of current_doc)
                            st.session_state.show_comparison_score = False
                            # Close the current expander
                            st.session_state.document_title = "RFP Document"
                            st.session_state.current_document = rfp['rfp link']
                            st.rerun()
                
                st.markdown("<hr style='margin-top:10px;margin-bottom:15px'>", unsafe_allow_html=True)
                
                # Score metrics at the top
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    if 'document_score' in rfp and rfp['document_score']:
                        try:
                            score_value = float(rfp['document_score'])
                            # Color based on score
                            if score_value >= 80:
                                st.markdown(f"<div style='background-color:#d4edda;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#155724;'>Document Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#155724;'>{score_value}%</h2></div>", 
                                            unsafe_allow_html=True)
                            elif score_value >= 60:
                                st.markdown(f"<div style='background-color:#fff3cd;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#856404;'>Document Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#856404;'>{score_value}%</h2></div>", 
                                            unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='background-color:#f8d7da;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#721c24;'>Document Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#721c24;'>{score_value}%</h2></div>", 
                                            unsafe_allow_html=True)
                        except (ValueError, TypeError):
                            # If score is not a number, just display it as text
                            st.metric("Document Match Score", rfp['document_score'])
                with metrics_col2:
                    if 'capability_score' in rfp and rfp['capability_score']:
                        try:
                            cap_score = float(rfp['capability_score'])
                            # Color based on score
                            if cap_score >= 80:
                                st.markdown(f"<div style='background-color:#d4edda;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#155724;'>Capability Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#155724;'>{cap_score}%</h2></div>", 
                                            unsafe_allow_html=True)
                            elif cap_score >= 60:
                                st.markdown(f"<div style='background-color:#fff3cd;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#856404;'>Capability Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#856404;'>{cap_score}%</h2></div>", 
                                            unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='background-color:#f8d7da;padding:10px;border-radius:5px;'>"
                                            f"<h4 style='text-align:center;margin:0;color:#721c24;'>Capability Match Score</h4>"
                                            f"<h2 style='text-align:center;margin:0;color:#721c24;'>{cap_score}%</h2></div>", 
                                            unsafe_allow_html=True)
                        except (ValueError, TypeError):
                            st.metric("Capability Match Score", rfp['capability_score'])
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Document comparison section
                if 'document_comparison' in rfp and rfp['document_comparison']:
                    st.markdown("<h4 style='color:#24497a;'>🔍 Document Analysis</h4>", unsafe_allow_html=True)
                    try:
                        # Try to use the document_comparison directly if it's text content
                        if isinstance(rfp['document_comparison'], str):
                            if rfp['document_comparison'].startswith('/'):  # It's a file path
                                try:
                                    with open(rfp['document_comparison'], 'r') as f:
                                        comparison_text = f.read()
                                except Exception as e:
                                    st.error(f"Could not read document comparison file: {e}")
                                    comparison_text = "Unable to read comparison file"
                            else:  # It's direct content
                                comparison_text = rfp['document_comparison']
                            
                            # Try to parse as JSON for prettier display
                            try:
                                import json
                                comparison_data = json.loads(comparison_text)
                                if isinstance(comparison_data, dict):
                                    # Create a nice UI for the comparison data
                                    for section, content in comparison_data.items():
                                        # Use a container with header instead of nested expander
                                        st.markdown(f"<h4 style='color:#24497a;margin-top:20px;'>{section.replace('_', ' ').title()}</h4>", unsafe_allow_html=True)
                                        if section == "best_matching_rfp_link" and isinstance(content, str) and content.startswith('/'):
                                            file_name = os.path.basename(content)
                                            button_key = f"btn_{hashlib.md5(content.encode()).hexdigest()}"
                                            try:
                                                if os.path.exists(content):
                                                    with open(content, 'rb') as file:
                                                        st.download_button(
                                                            label=f"📥 Download {file_name}",
                                                            data=file,
                                                            file_name=file_name,
                                                            mime="application/octet-stream",
                                                            key=button_key
                                                        )
                                            except Exception as e:
                                                st.error(f"Error with file: {e}")
                                            continue
                                        with st.container():
                                            # Handle lists - like previous_rfp_matches
                                            if isinstance(content, list):
                                                for idx, item in enumerate(content):
                                                    if isinstance(item, dict):
                                                        # Create an expander for each item
                                                        item_title = item.get('title', f'Item #{idx+1}')
                                                        with st.expander(f"⚡ {item_title}"):
                                                            # Create columns for better layout
                                                            cols = st.columns([2, 1])
                                                            
                                                            # Column 1: Key details
                                                            with cols[0]:
                                                                # Display all keys except rfp_link
                                                                for key, value in item.items():
                                                                    if key != 'rfp_link':
                                                                        if key in ['match_score', 'similarity', 'score'] and isinstance(value, (int, float, str)):
                                                                            try:
                                                                                score_val = float(value)
                                                                                # Color-coded score
                                                                                color = '#4CAF50' if score_val >= 80 else '#FFC107' if score_val >= 60 else '#FF5722'
                                                                                st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: <span style='color:{color};font-weight:bold;'>{score_val:.1f}%</span>", unsafe_allow_html=True)
                                                                            except:
                                                                                st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                                                        else:
                                                                            st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                                            
                                                            # Column 2: Download button if rfp_link exists
                                                            with cols[1]:
                                                                if "rfp_link" in item and isinstance(item["rfp_link"], str) and item["rfp_link"].startswith('/'):
                                                                    file_name = os.path.basename(item["rfp_link"])
                                                                    button_key = f"doc_list_btn_{idx}_{hashlib.md5(item['rfp_link'].encode()).hexdigest()}"
                                                                    try:
                                                                        if os.path.exists(item["rfp_link"]):
                                                                            with open(item["rfp_link"], 'rb') as file:
                                                                                st.download_button(
                                                                                    label=f"📥 Download Document",
                                                                                    data=file,
                                                                                    file_name=file_name,
                                                                                    mime="application/octet-stream",
                                                                                    key=button_key
                                                                                )
                                                                    except Exception as e:
                                                                        st.error(f"Error with file: {e}")
                                            # Handle dictionaries
                                            elif isinstance(content, dict):
                                                for key, value in content.items():
                                                    # Handle nested dictionaries with special formatting
                                                    if isinstance(value, dict):
                                                        st.markdown(f"**{key.replace('_', ' ').title()}**:")
                                                        for sub_key, sub_value in value.items():
                                                            if sub_key in ['match_score', 'similarity', 'score'] and isinstance(sub_value, (int, float, str)):
                                                                try:
                                                                    score_val = float(sub_value)
                                                                    color = '#4CAF50' if score_val >= 80 else '#FFC107' if score_val >= 60 else '#FF5722'
                                                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{sub_key.replace('_', ' ').title()}</strong>: <span style='color:{color};font-weight:bold;'>{score_val:.1f}%</span>", unsafe_allow_html=True)
                                                                except:
                                                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{sub_key.replace('_', ' ').title()}</strong>: {sub_value}", unsafe_allow_html=True)
                                                            else:
                                                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{sub_key.replace('_', ' ').title()}</strong>: {sub_value}", unsafe_allow_html=True)
                                                    elif key in ['match_score', 'similarity', 'score'] and isinstance(value, (int, float, str)):
                                                        try:
                                                            score_val = float(value)
                                                            color = '#4CAF50' if score_val >= 80 else '#FFC107' if score_val >= 60 else '#FF5722'
                                                            st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: <span style='color:{color};font-weight:bold;'>{score_val:.1f}%</span>", unsafe_allow_html=True)
                                                        except:
                                                            st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                                    else:
                                                        st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                            else:
                                                st.write(content)
                                else:
                                    # Just show as formatted text if it's not a dictionary
                                    st.json(comparison_data)
                            except json.JSONDecodeError:
                                # Not JSON, show as regular text in a nice box
                                st.markdown(
                                    f"<div style='background-color:#f8f9fa;padding:15px;border-radius:5px;'>"
                                    f"<p style='white-space:pre-wrap;'>{comparison_text}</p></div>",
                                    unsafe_allow_html=True
                                )
                    except Exception as e:
                        st.error(f"Could not process document comparison data: {e}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
                        
                # Capability comparison section
                if 'capabilty comparison' in rfp and rfp['capabilty comparison']:
                    st.markdown("<h4 style='color:#24497a;'>✓ Capability Analysis</h4>", unsafe_allow_html=True)
                    try:
                        # Try to use the capability comparison directly if it's text content
                        if isinstance(rfp['capabilty comparison'], str):
                            if rfp['capabilty comparison'].startswith('/'):  # It's a file path
                                try:
                                    with open(rfp['capabilty comparison'], 'r') as f:
                                        capability_text = f.read()
                                except Exception as e:
                                    st.error(f"Could not read capability comparison file: {e}")
                                    capability_text = "Unable to read capability file"
                            else:  # It's direct content
                                capability_text = rfp['capabilty comparison']
                            
                            # Try to parse as JSON for prettier display
                            try:
                                import json
                                capability_data = json.loads(capability_text)
                                if isinstance(capability_data, dict):
                                    for capability, details in capability_data.items():
                                        # Handle best_matching_rfp_link (single file link)
                                        if capability == "best_matching_rfp_link" and isinstance(details, str) and details.startswith('/'):
                                            file_name = os.path.basename(details)
                                            # Add 'cap_' prefix to make the key unique from document comparison buttons
                                            button_key = f"cap_btn_{hashlib.md5(details.encode()).hexdigest()}"
                                            try:
                                                if os.path.exists(details):
                                                    with open(details, 'rb') as file:
                                                        st.download_button(
                                                            label=f"📥 Download {file_name}",
                                                            data=file,
                                                            file_name=file_name,
                                                            mime="application/octet-stream",
                                                            key=button_key
                                                        )
                                            except Exception as e:
                                                st.error(f"Error with file: {e}")
                                            continue
                                            
                                        # Handle previous_rfp_matches (list of items with rfp_links)
                                        elif capability == "previous_rfp_matches" and isinstance(details, list):
                                            # Display as an expander for each match item
                                            for idx, item in enumerate(details):
                                                if isinstance(item, dict):
                                                    # Create an expander for each match with a meaningful title
                                                    match_title = item.get('rfp_title', f'Match #{idx+1}')
                                                    with st.expander(f"⚡ {match_title}"):
                                                        # Create columns for better layout
                                                        cols = st.columns([2, 1])
                                                        
                                                        # Column 1: Key details
                                                        with cols[0]:
                                                            # Display all keys except rfp_link
                                                            for key, value in item.items():
                                                                if key != 'rfp_link':
                                                                    if key == 'match_score' and isinstance(value, (int, float, str)):
                                                                        try:
                                                                            score_val = float(value)
                                                                            # Color-coded score
                                                                            color = '#4CAF50' if score_val >= 80 else '#FFC107' if score_val >= 60 else '#FF5722'
                                                                            st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: <span style='color:{color};font-weight:bold;'>{score_val:.1f}%</span>", unsafe_allow_html=True)
                                                                        except:
                                                                            st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                                                    else:
                                                                        st.markdown(f"<strong>{key.replace('_', ' ').title()}</strong>: {value}", unsafe_allow_html=True)
                                                        
                                                        # Column 2: Download button if rfp_link exists
                                                        with cols[1]:
                                                            if "rfp_link" in item and isinstance(item["rfp_link"], str) and item["rfp_link"].startswith('/'):
                                                                file_name = os.path.basename(item["rfp_link"])
                                                                # Use single quotes for dictionary keys inside f-string to avoid syntax error
                                                                button_key = f"prev_rfp_btn_{idx}_{hashlib.md5(item['rfp_link'].encode()).hexdigest()}"
                                                                try:
                                                                    if os.path.exists(item["rfp_link"]):
                                                                        with open(item["rfp_link"], 'rb') as file:
                                                                            st.download_button(
                                                                                label=f"📥 Download RFP",
                                                                                data=file,
                                                                                file_name=file_name,
                                                                                mime="application/octet-stream",
                                                                                key=button_key
                                                                            )
                                                                except Exception as e:
                                                                    st.error(f"Error with file: {e}")
                                            continue
                                        # Use container and header instead of nested expander
                                        st.markdown(f"<h5 style='color:#24497a;margin-top:20px;'>{capability.replace('_', ' ').title()}</h5>", unsafe_allow_html=True)
                                        with st.container():
                                            if isinstance(details, dict):
                                                # If it has match score, display it prominently
                                                if 'match_score' in details:
                                                    score = details['match_score']
                                                    try:
                                                        score_val = float(score)
                                                        # Color-coded score
                                                        if score_val >= 80:
                                                            st.markdown(f"<span style='background-color:#d4edda;padding:3px 8px;border-radius:10px;color:#155724'><b>Match: {score}%</b></span>", unsafe_allow_html=True)
                                                        elif score_val >= 60:
                                                            st.markdown(f"<span style='background-color:#fff3cd;padding:3px 8px;border-radius:10px;color:#856404'><b>Match: {score}%</b></span>", unsafe_allow_html=True)
                                                        else:
                                                            st.markdown(f"<span style='background-color:#f8d7da;padding:3px 8px;border-radius:10px;color:#721c24'><b>Match: {score}%</b></span>", unsafe_allow_html=True)
                                                    except (ValueError, TypeError):
                                                        st.write(f"**Match Score:** {score}")
                                                
                                                # Show the rest of the details
                                                for k, v in details.items():
                                                    if k != 'match_score':  # Skip the match score as we already displayed it
                                                        st.markdown(f"**{k.replace('_', ' ').title()}**: {v}")
                                            elif isinstance(details, list):
                                                for item in details:
                                                    if isinstance(item, dict):
                                                        for k, v in item.items():
                                                            st.markdown(f"**{k.replace('_', ' ').title()}**: {v}")
                                                        st.markdown("---")
                                                    else:
                                                        st.write(item)
                                            else:
                                                st.write(details)
                                else:
                                    st.json(capability_data)
                            except json.JSONDecodeError:
                                # Not JSON, show as regular text in a nice box
                                st.markdown(
                                    f"<div style='background-color:#f8f9fa;padding:15px;border-radius:5px;'>"
                                    f"<p style='white-space:pre-wrap;'>{capability_text}</p></div>",
                                    unsafe_allow_html=True
                                )
                    except Exception as e:
                        st.error(f"Could not process capability comparison data: {e}")
                        
                # Removed legacy comparison_report code since it's been replaced by document_comparison
                        
                if st.button("Close"):
                    st.session_state.show_comparison_score = False
        
        # Small row for basic details at top
        col_info1, col_info2, col_info3 = st.columns([1, 1, 1])
        with col_info1:
            st.markdown("**Due Dates:**")
            # Check if we have JSON due dates
            due_dates = rfp.get('due dates', '')
            if isinstance(due_dates, str) and due_dates.startswith('['):
                try:
                    import json
                    events = json.loads(due_dates)
                    if events and len(events) > 0:
                        # Create moving text with all events
                        events_text = ""
                        for event in events:
                            event_name = event.get('event', '')
                            date = event.get('due_date', '')
                            time = event.get('due_time', '')
                            events_text += f"{event_name}: {date} {time} | "
                        
                        # Show scrolling text with all dates
                        st.markdown(f"""
                        <div class="row-scroll-container">
                            <div class="row-scroll-text">{events_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    # Fall back to displaying the raw data
                    st.write(due_dates)
            else:
                # If it's not JSON, display last date
                st.write(rfp.get('last date', 'No date available'))
        with col_info2:
            # Status dropdown with the same options as Home page
            st.markdown("**Status:**")
            # Get current status value
            current_status = rfp.get('status', '')
            
            # Create status options list with empty option first
            status_options = ['', 'Accepted', 'Not Accepted', 'In Progress']
            
            # Find the index of the current status in the options
            try:
                status_index = status_options.index(current_status)
            except ValueError:
                # If not found, default to empty option
                status_index = 0
            
            # Generate unique key based on RFP title
            status_key = f"detail_status_{hashlib.md5(str(rfp['title']).encode()).hexdigest()}"
            
            status = st.selectbox(
                "Status Selection",
                status_options,
                index=status_index,
                key=status_key,
                label_visibility="collapsed"
            )
            
            # Save changes if status has been updated
            if status != current_status:
                # Load full dataframe
                df = load_data()
                
                # Find the row with matching title and update status
                for i, row in df.iterrows():
                    if str(row['title']) == str(rfp['title']):
                        df.at[i, 'status'] = status
                        # Update the session state value too
                        st.session_state.clicked_rfp['status'] = status
                        save_data(df)
                        break
                        
        with col_info3:
            # RM dropdown with predefined list
            st.markdown("**RM:**")
            # Predefined list of RMs
            predefined_rms = ["", "Sagar Shah", "Hardik Shah", "Harshit Bhadani", "Ruchira Nanda", "Utkarsh Chandra"]
            
            # Get current RM
            current_rm = rfp.get('RM', '')
            
            # Add current RM to list if not already there
            if current_rm and current_rm not in predefined_rms:
                predefined_rms.append(current_rm)
            
            # Find the index of the current RM
            try:
                current_rm_index = predefined_rms.index(current_rm)
            except ValueError:
                current_rm_index = 0
                
            # Generate unique key
            rm_key = f"detail_rm_{hashlib.md5(str(rfp['title']).encode()).hexdigest()}"
            
            tagged_rm = st.selectbox(
                "Tagged RM Selection",
                predefined_rms,
                index=current_rm_index,
                key=rm_key,
                label_visibility="collapsed"
            )
            
            # Save changes if RM has been updated
            if tagged_rm != current_rm:
                # Load full dataframe
                df = load_data()
                
                # Find the row with matching title and update RM
                for i, row in df.iterrows():
                    if str(row['title']) == str(rfp['title']):
                        df.at[i, 'RM'] = tagged_rm
                        # Update the session state value too
                        st.session_state.clicked_rfp['RM'] = tagged_rm
                        save_data(df)
                        break
        
        st.markdown("---")
        
        # Create two columns for summary and PDF
        left_col, right_col = st.columns([0.5, 0.5])
        
        # Left column: Summary
        with left_col:
            st.subheader("Summary")
            
            # Check if summary link exists and try to read from it
            if 'summary link' in rfp and rfp['summary link']:
                try:
                    # Try to read the file content
                    if os.path.exists(rfp['summary link']):
                        with open(rfp['summary link'], 'r') as f:
                            summary_content = f.read()
                        
                        # Display in a scrollable container
                        st.markdown(f"""<div style="height: 400px; overflow-y: auto; padding: 15px; 
                                    border: 1px solid #e6e9ef; border-radius: 5px; background-color: #f9f9f9;">
                                    {summary_content}</div>""", unsafe_allow_html=True)
                    else:
                        # If it's a URL or non-existent file
                        st.info(f"Summary link: {rfp['summary link']}")
                        st.warning("The summary file could not be found locally. Please provide a valid file path.")
                except Exception as e:
                    st.error(f"Error loading summary: {e}")
            else:
                st.info("No summary file available for this RFP.")
            
            # Addendum section
            st.subheader("Addendum")
            has_addendum = False
            
            # Handle different formats of addendum data
            if 'addendum' in rfp and rfp['addendum']:
                try:
                    if isinstance(rfp['addendum'], str) and rfp['addendum'].startswith('['):
                        try:
                            # Parse the JSON data - using triple quotes to handle any escape characters
                            addendum_string = rfp['addendum'].strip()
                            addendum_data = json.loads(addendum_string)
                            
                            
                            if addendum_data and len(addendum_data) > 0:
                                st.write(f"**Number of addenda:** {len(addendum_data)}")
                                
                                # Create hyperlinks for each addendum
                                for i, item in enumerate(addendum_data):
                                    has_addendum = True
                                    # Extract date and link from the item
                                    for date, link in item.items():
                                        # Always show the hyperlink regardless of file existence
                                        link_key = f"addendum_{i}_{date}"
                                        display_text = f"Addendum of {rfp['title']} dated {date}"
                                        
                                        # Create a button styled as a link
                                        if st.button(display_text, key=link_key):
                                            # Set the addendum document as the current document
                                            st.session_state.current_document = link
                                            st.session_state.document_title = f"Addendum dated {date}"
                                            # Rerun to update the display
                                            st.rerun()
                        except Exception as e:
                            st.error(f"Error parsing addendum JSON: {e}")
                            # Add a fallback display for error cases
                            st.warning("Could not display addendum links due to parsing error.")
                            
                            # Only show samples if we need to demonstrate functionality
                            if st.checkbox("Show sample addendum links", key="show_sample_addendum"):
                                st.info("Sample addendum links (placeholder)")
                                st.button(f"Sample addendum of {rfp['title']} dated 15-08-2025", key="sample_addendum_1")
                                st.button(f"Sample addendum of {rfp['title']} dated 20-08-2025", key="sample_addendum_2")
                except Exception as e:
                    st.error(f"Error parsing addendum data: {e}")
            else:
                st.info(f"No addendum data found for {rfp['title']}")
                    
            # Fallback to counter-based approach if JSON parsing fails or isn't applicable
            if not has_addendum and 'addendum counter' in rfp and str(rfp['addendum counter']).isdigit() and int(rfp['addendum counter']) > 0:
                count = int(rfp['addendum counter'])
                st.write(f"**Number of addenda:** {count}")
                
                if 'addendum last updated date' in rfp and rfp['addendum last updated date']:
                    st.write(f"**Last updated:** {rfp['addendum last updated date']}")
                
                # Create expandable sections for each addendum
                for i in range(1, count + 1):
                    with st.expander(f"Addendum {i}"):
                        st.write(f"Addendum {i} details would appear here. Currently this is a placeholder for demonstration.")
            
            if not has_addendum and ('addendum counter' not in rfp or not str(rfp.get('addendum counter', '')).isdigit() or int(rfp.get('addendum counter', 0)) <= 0):
                st.info("No data updated")
            
            # Corrigendum section
            st.subheader("Corrigendum")
            has_corrigendum = False
            
            # Handle different formats of corrigendum data
            if 'corrigendum' in rfp and rfp['corrigendum']:
                try:
                    if isinstance(rfp['corrigendum'], str) and rfp['corrigendum'].startswith('['):
                        try:
                            # Parse the JSON data - using strip to remove whitespace
                            corrigendum_string = rfp['corrigendum'].strip()
                            corrigendum_data = json.loads(corrigendum_string)
                            if corrigendum_data and len(corrigendum_data) > 0:
                                st.write(f"**Number of corrigenda:** {len(corrigendum_data)}")
                            
                            # Create hyperlinks for each corrigendum
                            for i, item in enumerate(corrigendum_data):
                                has_corrigendum = True
                                # Extract date and link from the item
                                for date, link in item.items():
                                    # Always show the hyperlink regardless of file existence
                                    link_key = f"corrigendum_{i}_{date}"
                                    display_text = f"Corrigendum of {rfp['title']} dated {date}"
                                    
                                    # Create a button styled as a link
                                    if st.button(display_text, key=link_key):
                                        # Set the corrigendum document as the current document
                                        st.session_state.current_document = link
                                        st.session_state.document_title = f"Corrigendum dated {date}"
                                        # Rerun to update the display
                                        st.rerun()
                        except Exception as e:
                            st.error(f"Error parsing corrigendum JSON: {e}")
                            st.warning("Could not display corrigendum links due to parsing error.")
                            
                            # Only show samples if we need to demonstrate functionality
                            if st.checkbox("Show sample corrigendum links", key="show_sample_corrigendum"):
                                st.info("Sample corrigendum links (placeholder)")
                                st.button(f"Sample corrigendum of {rfp['title']} dated 15-08-2025", key="sample_corrigendum_1")
                                st.button(f"Sample corrigendum of {rfp['title']} dated 20-08-2025", key="sample_corrigendum_2")
                except Exception as e:
                    st.error(f"Error parsing corrigendum data: {e}")
            else:
                st.info(f"No corrigendum data found for {rfp['title']}")
                    
            # Fallback to counter-based approach if JSON parsing fails or isn't applicable
            if not has_corrigendum and 'corrigendum counter' in rfp and str(rfp['corrigendum counter']).isdigit() and int(rfp['corrigendum counter']) > 0:
                count = int(rfp['corrigendum counter'])
                st.write(f"**Number of corrigenda:** {count}")
                
                if 'corrigendum last updated date' in rfp and rfp['corrigendum last updated date']:
                    st.write(f"**Last updated:** {rfp['corrigendum last updated date']}")
                
                # Create expandable sections for each corrigendum
                for i in range(1, count + 1):
                    with st.expander(f"Corrigendum {i}"):
                        st.write(f"Corrigendum {i} details would appear here. Currently this is a placeholder for demonstration.")
            
            if not has_corrigendum and ('corrigendum counter' not in rfp or not str(rfp.get('corrigendum counter', '')).isdigit() or int(rfp.get('corrigendum counter', 0)) <= 0):
                st.info("No data updated")
        
        # Right column: PDF viewer
        with right_col:
            # Check if a specific document is selected to display
            current_doc = st.session_state.current_document
            doc_title = st.session_state.document_title
            
            if current_doc:
                # Display the selected document (addendum or corrigendum)
                st.subheader(doc_title)
                
                # Button to go back to RFP
                if st.button("Back to RFP Document"):
                    st.session_state.current_document = None
                    st.session_state.document_title = "RFP Document"
                    st.rerun()
                    
                display_pdf(current_doc)
            else:
                # Default: Display the RFP document
                st.subheader("RFP Document")
                
                if 'rfp link' in rfp and rfp['rfp link']:
                    # Display PDF using embed technique
                    display_pdf(rfp['rfp link'])
                else:
                    st.info("No PDF document available for this RFP.")
        
        # Navigation button to return to dashboard
        if st.button("Return to Dashboard"):
            try:
                st.switch_page("Home.py")
            except Exception as e:
                st.error(f"Error navigating to Home: {e}")
                st.info("Please use the sidebar to navigate to the Home page")

def load_data():
    """Loads data from CSV and adds sorting columns."""
    try:
        # Load data from CSV file
        df = pd.read_csv('expanded_rfp_data.csv')
        
        # Convert RM and status columns to string to handle empty values correctly
        if 'RM' in df.columns:
            df['RM'] = df['RM'].astype(str)
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str)
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
        
def save_data(df):
    """Saves the DataFrame to the CSV file"""
    df.to_csv('expanded_rfp_data.csv', index=False)

def read_text_file(file_path):
    """Reads a text file and returns its contents."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"

def display_pdf(file_path):
    """Displays a PDF file in the app using an HTML iframe."""
    if not file_path:
        return
    
    if not os.path.exists(file_path):
        st.error(f"PDF file not found: {file_path}")
        # Create a placeholder for demo purposes
        st.info("This is a placeholder for the PDF viewer. In a production environment, this would display the actual PDF document.")
        st.markdown(f"""<div style="width:100%; height:600px; border:1px solid #ccc; display:flex; align-items:center; justify-content:center;">
                    <div style="text-align:center">
                    <h3>PDF Document Viewer</h3>
                    <p>The document at {file_path} would be displayed here.</p>
                    </div>
                    </div>""", unsafe_allow_html=True)
        return
    
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Embedding PDF in HTML
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")
        # Create a fallback display
        st.info("Could not load the PDF. Here's a placeholder instead.")
        st.markdown(f"""<div style="width:100%; height:600px; border:1px solid #ccc; display:flex; align-items:center; justify-content:center;">
                    <div style="text-align:center">
                    <h3>PDF Document Viewer</h3>
                    <p>There was an error loading the document.</p>
                    </div>
                    </div>""", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
