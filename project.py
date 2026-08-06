import streamlit as st
import pandas as pd
import json
import random
import os
from datetime import datetime, date

# --- CONFIGURATION: MASTER SECURITY ACCESS ---
ADMIN_USER = "lnp_inspector"
ADMIN_PASS = "monrovia2027"

# Path to our local data storage file
DATA_FILE = "data.json"

# Complete official geographic profiles of Liberia 
LIBERIA_COUNTIES = [
    "Bomi", "Bong", "Gbarpolu", "Grand Bassa", "Grand Cape Mount", 
    "Grand Gedeh", "Grand Kru", "Lofa", "Margibi", "Maryland", 
    "Montserrado", "Nimba", "River Cess", "River Gee", "Sinoe"
]

# Police offence categorisation models
OFFENCE_CATEGORIES = [
    "Unprofessional Conduct / Misbehaviour",
    "Arbitrary Detention or Arrest",
    "Extortion / Bribery Request",
    "Failure to Process/Investigate Case",
    "Traffic Compliance Extortion",
    "Gender-Based Violence Reporting Failure",
    "General Public Offence / Encroachment"
]

# 1. Page Configuration Setup (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Liberia National Grievance Portal",
    page_icon="🇱🇷",
    layout="wide"
)

# Initialize Session Authentication States
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# 2. NATIVE FILE STORAGE LOADING LOGIC
if "grievance_db" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.grievance_db = pd.DataFrame(data)
        except Exception:
            st.session_state.grievance_db = pd.DataFrame()
    else:
        st.session_state.grievance_db = pd.DataFrame()

# 3. Main System Workspace Layout Header
st.title("🇱🇷 National Public Grievance & Accountability Portal")
st.write("Official Government Blueprint Initiative — Republic of Liberia Police Accountability Dashboard.")
st.markdown("---")

# 4. Mode Selection Controller Segment
portal_mode = st.radio(
    "🧭 Select System Interface Mode:", 
    ["Citizen Complaint Desk", "LNP Command Center Dashboard"],
    horizontal=True
)

st.markdown("---")

# =====================================================================
# INTERFACE MODE A: CITIZEN COMPLAINT DESK
# =====================================================================
if portal_mode == "Citizen Complaint Desk":
    st.subheader("📝 Public Grievance Intake Window")
    st.write("Fill out this automated form to lodge an incident query. All inputs are logged securely.")
    
    with st.form("citizen_grievance_form", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            county = st.selectbox("Select County of Occurrence:", LIBERIA_COUNTIES)
            incident_city = st.text_input("City / District Area:", placeholder="e.g., Kakata or Buchanan")
            offence_type = st.selectbox("Grievance Primary Category:", OFFENCE_CATEGORIES)
            
        with col_c2:
            is_anonymous = st.checkbox("File Anonymously (Hide Your Personal Identity Information)", value=True)
            complainant_name = st.text_input("Your Full Name (Leave blank if Anonymous is checked):", value="")
            contact_number = st.text_input("Mobile Phone Number (Used to route automated SMS status alerts):")
            
        st.markdown("---")
        incident_details = st.text_area("Comprehensive Description of the Incident (Include names, vehicle numbers, or officer badge details):")
        incident_date = st.date_input("Date of Incident Occurrence:", max_value=date.today())
        
        submit_complaint = st.form_submit_button("🚀 Submit Secure Grievance to Headquarters")

    if submit_complaint:
        if not incident_details.strip():
            st.error("⚠️ Record Rejected: Please include descriptive text details explaining the incident occurrence.")
        elif not contact_number.strip():
            st.error("⚠️ Record Rejected: Mobile Phone Number value is required to push transaction alerts.")
        else:
            token_id = "LNP-2027-" + str(random.randint(10000, 99999))
            final_name = "ANONYMOUS FILE" if is_anonymous or not complainant_name.strip() else complainant_name.strip()
            
            new_grievance = {
                "Token ID": token_id,
                "County": county,
                "Location": incident_city.strip() if incident_city.strip() else "Unknown",
                "Category": offence_type,
                "Complainant": final_name,
                "Contact": contact_number.strip(),
                "Description": incident_details.strip(),
                "Incident Date": str(incident_date),
                "Filing Date": str(date.today()),
                "Status": "Pending Review",
                "Assigned Unit": "Unassigned"
            }
            
            st.session_state.grievance_db = pd.concat(
                [st.session_state.grievance_db, pd.DataFrame([new_grievance])], 
                ignore_index=True
            )
            
            # Save data securely to our native json file
            try:
                records = st.session_state.grievance_db.to_dict(orient="records")
                with open(DATA_FILE, "w") as f:
                    json.dump(records, f, indent=4)
            except Exception as e:
                st.error(f"Error saving data: {e}")
            
            st.success("🎉 Grievance Logged Successfully with Police Headquarters!")
            st.info(
                "🔑 **Your Tracking Token Number is:** `" + token_id + "`\n\n"
                "📝 *Keep this tracking number safe. An automated SMS alert has been scheduled to transmit status updates to " + contact_number.strip() + ".*"
            )

# =====================================================================
# INTERFACE MODE B: LNP COMMAND CENTER DASHBOARD
# =====================================================================
elif portal_mode == "LNP Command Center Dashboard":
    st.subheader("🔒 Professional Standards Command Panel Access")
    
    if not st.session_state.admin_authenticated:
        st.warning("Access Restricted: Unauthorized entry points are logged.")
        
        with st.form("admin_auth_gate", clear_on_submit=False):
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                entered_user = st.text_input("Administrative User ID:")
            with col_l2:
                entered_pass = st.text_input("Administrative Password Key:", type="password")
            
            click_login = st.form_submit_button("🔓 Authenticate Command Access")
            
        if click_login:
            if entered_user == ADMIN_USER and entered_pass == ADMIN_PASS:
                st.session_state.admin_authenticated = True
                st.success("✅ Credentials verified successfully! Loading National Case Files Database Ledger...")
                st.rerun()
            else:
                st.error("❌ Authentication Refused: Incorrect credentials key values submitted.")
    else:
        st.success("🔐 Administrative Session Active: Authorized as LNP Inspector General Desk.")
        
        if st.button("🚪 Close Secure Command Session"):
            st.session_state.admin_authenticated = False
            st.rerun()
            
        st.markdown("---")
        
        if st.session_state.grievance_db.empty:
            st.info("Awaiting public data transfers. There are currently zero open citizen grievance records filed inside this ledger.")
        else:
            db = st.session_state.grievance_db
            
            total_cases = len(db)
            pending_cases = len(db[db["Status"] == "Pending Review"])
            active_investigations = len(db[db["Status"] == "Under Active Investigation"])
            resolved_cases = len(db[db["Status"] == "Resolved / Disposed Case"])
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Filed Claims", f"{total_cases} Profiles")
            m2.metric("Awaiting Triage Review", f"{pending_cases} Cases", delta="-Action Required" if pending_cases > 0 else "Clear")
            m3.metric("Active Field Investigations", f"{active_investigations} Open")
            m4.metric("Disposed/Closed Files", f"{resolved_cases} Complete")
            
            st.markdown("---")
            st.subheader("📋 Central Grievance Matrix Case Audit Log")
            
            display_rows = []
            for index, row in db.iterrows():
                file_dt = datetime.strptime(str(row["Filing Date"]), "%Y-%m-%d").date()
                days_elapsed = (date.today() - file_dt).days
                days_left = 30 - days_elapsed
                
                if row["Status"] == "Resolved / Disposed Case":
                    countdown_indicator = "✅ Closed"
                elif days_left < 0:
                    countdown_indicator = "🚨 OVERDUE: " + str(abs(days_left)) + " Days Past"
                else:
                    countdown_indicator = "⏳ " + str(days_left) + " Days Left"
                    
                display_rows.append({
                    "Token Key": row["Token ID"],
                    "County Location": row["County"],
                    "Complainant Profile": row["Complainant"],
                    "Violation Category": row["Category"],
                    "Current Pipeline Status": row["Status"],
                    "Assigned Office Unit": row["Assigned Unit"],
                    "Filing Date Stamp": row["Filing Date"],
                    "30-Day Disposal Clock": countdown_indicator
                })
                
            st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("🛠️ Claim Triage & Case Status Management Panel")
            
            target_token = st.selectbox("Choose Case Token Key To Action:", db["Token ID"].unique())
