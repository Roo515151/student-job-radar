import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Oscars Job Radar", page_icon="🏆", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

sheet_file = client.open("Student Job Database")
jobs_sheet = sheet_file.worksheet("Jobs")
banned_sheet = sheet_file.worksheet("Banned_Keywords")

# --- UI HEADER ---
st.title("🏆 Oscars Job Radar")

# Fetch data
try:
    raw_data = jobs_sheet.get_all_records()
except Exception:
    raw_data = []

if raw_data:
    df = pd.DataFrame(raw_data)
    
    st.info(f"🔄 **Database live.** Tracking {len(df)} jobs across a rolling 7-day window.")
    
    # Hide the ugly Hash ID from the user
    if "Hash ID" in df.columns:
        df = df.drop(columns=["Hash ID"])
        
    # Reorder columns
    preferred_order = ["Link", "Priority", "Job Title", "Company", "Location", "Last Seen"]
    df = df[[col for col in preferred_order if col in df.columns]]
    
    # --- RENDER INTERACTIVE TABLE ---
    st.dataframe(
        df,
        column_config={
            "Link": st.column_config.LinkColumn(
                "View",               
                display_text="👀",     
                width="small"          
            ),
            "Job Title": st.column_config.TextColumn(
                "Job Title", 
                width="medium"         
            ),
            "Priority": st.column_config.TextColumn(
                "Priority",
                width="small"
            ),
            "Last Seen": st.column_config.DateColumn(
                "Last Seen",
                format="MMM DD"
            )
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )
else:
    st.warning("No jobs found in the database. Waiting to sync...")

# --- BANNED KEYWORD MANAGER ---
st.divider()
st.subheader("🚫 Block a Job Title")
st.write("Type a word here (like 'manager' or 'nurse'). The search will permanently hide any jobs containing this word in due course.")

col1, col2 = st.columns([3, 1])
with col1:
    new_ban = st.text_input("Keyword to block:", label_visibility="collapsed")
with col2:
    if st.button("Block Keyword", use_container_width=True):
        if new_ban:
            banned_sheet.append_row([new_ban.lower().strip()])
            st.success(f"'{new_ban}' added to the block list!")
