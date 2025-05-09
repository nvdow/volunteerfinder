import streamlit as st
import pandas as pd
import numpy as np
import datetime
import webbrowser
import os
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="NVIDIA Volunteer Finder",
    page_icon="🚀",
    layout="centered"
)

# NVIDIA colors
NVIDIA_GREEN = "#76B900"
NVIDIA_BLUE = "#00A3E0"
NVIDIA_ORANGE = "#FF8C00"
NVIDIA_BLACK = "#000000"

# Custom CSS with NVIDIA colors
st.markdown("""
<style>
    .stButton button {
        background-color: #76B900;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #00A3E0;
        color: white;
    }
    .stSelectbox > div > div {
        background-color: white;
        color: #000000;
    }
    h1, h2, h3 {
        color: #76B900;
    }
    .stDataFrame {
        border: 2px solid #76B900;
    }
    .reportview-container {
        background-color: white;
    }
    .main {
        background-color: white;
    }
    .volunteer-card {
        background-color: #f8f9fa;
        border: 1px solid #eaeaea;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for tracking selections
if 'selections' not in st.session_state:
    st.session_state.selections = {}
    
if 'last_reset' not in st.session_state:
    st.session_state.last_reset = datetime.now()
    
# Function to check if a week has passed and reset counts
def check_and_reset_week():
    current_time = datetime.now()
    if (current_time - st.session_state.last_reset).days >= 7:
        st.session_state.selections = {}
        st.session_state.last_reset = current_time
        return True
    return False

# Title and description
st.title("NVIDIA Volunteer Finder")
st.subheader("Find available volunteers for insider chats")

# Load data
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def load_data():
    try:
        # Read the CSV file
        df = pd.read_csv('volunteers.csv')
        
        # Clean up the data
        # Trim whitespace from string columns and column names
        df = df.rename(columns=lambda x: x.strip())
        
        for col in df.columns:
            if df[col].dtype == object:  # Only process string columns
                df[col] = df[col].astype(str).str.strip()
        
        # Fill missing values
        df = df.fillna({'Business Unit': 'Not Specified', 'Timezone': 'Not Specified', 'CRG': 'Not Specified'})
        
        # Fix any problematic employee numbers (remove closing parenthesis if present)
        if 'Employee #' in df.columns:
            df['Employee #'] = df['Employee #'].astype(str).str.replace(')', '', regex=False)
        
        # Drop duplicates based on all columns except Employee #
        # This keeps the volunteer's multiple CRGs but removes exact duplicates
        df = df.drop_duplicates()
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load the volunteer data
df = load_data()

if df is not None:
    # Check if a week has passed to reset selection counts
    reset_occurred = check_and_reset_week()
    if reset_occurred:
        st.success("Weekly volunteer selection counts have been reset.")
    
    # Convert volunteer names to dict for selection tracking
    if 'selections' not in st.session_state:
        st.session_state.selections = {name: 0 for name in df['Insider Volunteers'].unique()}
    
    # New volunteers might have been added
    for name in df['Insider Volunteers'].unique():
        if name not in st.session_state.selections:
            st.session_state.selections[name] = 0
    
    # Filter out volunteers who have been selected 2+ times this week
    # Create a unique identifier based on Insider Volunteers and CRG to handle multiple CRGs
    available_names = [name for name in df['Insider Volunteers'].unique() 
                      if st.session_state.selections.get(name, 0) < 2]
    
    available_df = df[df['Insider Volunteers'].isin(available_names)]
    
    # Create a centered filter section
    st.markdown("### Filter Volunteers")
    
    # Stack filters vertically instead of using columns
    # CRG Filter
    crg_options = ['All'] + sorted(df['CRG'].unique().tolist())
    selected_crg = st.selectbox('Filter by CRG', crg_options)
    
    # Timezone Filter
    timezone_options = ['All'] + sorted(df['Timezone'].unique().tolist())
    selected_timezone = st.selectbox('Filter by Timezone', timezone_options)
    
    # Business Unit Filter
    bu_options = ['All'] + sorted(df['Business Unit'].unique().tolist())
    selected_bu = st.selectbox('Filter by Business Unit', bu_options)
    
    # Apply filters
    filtered_df = available_df.copy()
    
    if selected_crg != 'All':
        filtered_df = filtered_df[filtered_df['CRG'] == selected_crg]
    
    if selected_timezone != 'All':
        filtered_df = filtered_df[filtered_df['Timezone'] == selected_timezone]
    
    if selected_bu != 'All':
        filtered_df = filtered_df[filtered_df['Business Unit'] == selected_bu]
    
    # Drop duplicates to show each volunteer only once in the results
    # We'll keep the first CRG/Group combination for each volunteer
    display_df = filtered_df.drop_duplicates(subset=['Insider Volunteers'])
    
    # Display number of results
    st.markdown("---")
    st.write(f"Found {len(display_df)} volunteers matching your criteria")
    
    # Show up to 5 volunteers
    display_df = display_df.head(5)
    
    if not display_df.empty:
        # Display volunteers in a vertical stack instead of columns
        for i, (idx, row) in enumerate(display_df.iterrows()):
            volunteer_name = row['Insider Volunteers']
            
            # Create a card-like container for each volunteer
            with st.container():
                st.markdown(f"""
                <div class="volunteer-card">
                    <h3 style="color: {NVIDIA_GREEN};">{volunteer_name}</h3>
                    <p><strong>CRG:</strong> {row['CRG']}</p>
                    <p><strong>Timezone:</strong> {row['Timezone']}</p>
                    <p><strong>Business Unit:</strong> {row['Business Unit']}</p>
                    <p><strong>Email:</strong> {row['Email']}</p>
                    <p><strong>Selected this week:</strong> {st.session_state.selections.get(volunteer_name, 0)} times</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a unique key for each button
                if st.button("Schedule", key=f"btn_{i}_{volunteer_name}"):
                    # Increment selection count
                    st.session_state.selections[volunteer_name] = st.session_state.selections.get(volunteer_name, 0) + 1
                    
                    # Open outlook scheduler
                    email = row['Email']
                    st.balloons()
                    outlook_url = f"mailto:{email}?subject=NVIDIA%20Insider%20Chat%20Request&body=Hello%20{volunteer_name},%0A%0AI%20would%20like%20to%20schedule%20you%20for%20an%20insider%20chat.%0A%0ABest%20regards,"
                    
                    # Use JavaScript to open the URL
                    js = f"""<script>window.open("{outlook_url}", "_blank");</script>"""
                    st.markdown(js, unsafe_allow_html=True)
                    
                    # Show success message
                    st.success(f"Scheduling {volunteer_name}! Outlook should open automatically.")
                    
                    # Force a rerun to update the UI
                    st.experimental_rerun()
    else:
        st.warning("No volunteers match your criteria or all matching volunteers have reached their weekly limit.")
else:
    st.error("Failed to load volunteer data. Please check if the CSV file exists and is properly formatted.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #76B900;'>"
    "© NVIDIA Corporation. Created with Streamlit."
    "</div>", 
    unsafe_allow_html=True
) 
