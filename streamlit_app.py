import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Oscars Job Radar", page_icon="🏆", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
# Streamlit secrets handle the credentials securely in the cloud
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

sheet_file = client.open("Student Job Database")
jobs_sheet = sheet_file.worksheet("Jobs")
banned_sheet = sheet_file.worksheet("Banned_Keywords")

# --- UI HEADER ---
st.title("🏆 Oscars Job Radar")

# Fetch data
raw_data = jobs_sheet.get_all_values()

if len(raw_data) > 1:
    last_updated = raw_data[0][1]
    st.info(f"🔄 **Database synced by Mini-PC on:** {last_updated}")
    
    # Format data for display
    headers = raw_data[1]
    rows = raw_data[2:]
    df = pd.DataFrame(rows, columns=headers)
    
    # --- NEW: Reorder columns to put 'Link' on the far left ---
    # We safely check if the columns exist, then rearrange them
    preferred_order = ["Link", "Job Title", "Company", "Location", "Type"]
    df = df[[col for col in preferred_order if col in df.columns]]
    
    # --- RENDER INTERACTIVE TABLE ---
    st.dataframe(
        df,
        column_config={
            "Link": st.column_config.LinkColumn(
                "View",               # Makes the header shorter
                display_text="🚀",     # Turns the long URL into a simple rocket button
                width="small"          # Keeps the column as narrow as possible
            ),
            "Job Title": st.column_config.TextColumn(
                "Job Title", 
                width="medium"         # Shrunk down from 'large'
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )
else:
    st.warning("No jobs found in the database. Waiting for Mini-PC to sync...")

# --- BANNED KEYWORD MANAGER ---
st.divider()
st.subheader("🚫 Block a Job Title")
st.write("Type a word here (like 'manager' or 'nurse'). The Mini-PC will permanently hide any jobs containing this word on its next run.")

col1, col2 = st.columns([3, 1])
with col1:
    new_ban = st.text_input("Keyword to block:", label_visibility="collapsed")
with col2:
    if st.button("Block Keyword", use_container_width=True):
        if new_ban:
            banned_sheet.append_row([new_ban.lower().strip()])
            st.success(f"'{new_ban}' added to the block list!")
