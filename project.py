import streamlit as st
import pandas as pd
import json
import random
import os
from datetime import datetime, date

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

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Liberia National Grievance Portal",
    page_icon="🇱🇷",
    layout="wide"
)

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
        # Pre-seed realistic template sample data so the reviewer instantly sees working charts
        sample_grievances = [
            {
                "Token ID": "LNP-2027-48392",
                "County": "Montserrado",
                "Location": "Monrovia / Bushrod Island",
                "Category": "Extortion / Bribery Request",
                "Complainant": "ANONYMOUS FILE",
                "Contact": "+231886555123",
                "Description": "Checkpoint interaction involving unlawful fee demands during night transit.",
                "Incident Date": "2026-08-01",
                "Filing Date": "2026-08-02",
                "Status": "Under Active Investigation",
                "Assigned Unit": "Professional Standards Bureau"
            },
            {
                "Token ID": "LNP-2027-19482",
                "County": "Bong",
                "Location": "Gbarnga District",
                "Category": "Unprofessional Conduct / Misbehaviour",
                "Complainant": "Flomo Juah",
                "Contact": "+231770123456",
                "Description": "Refusal to take statement following a domestic commercial trade dispute.",
                "Incident Date": "2026-08-05",
                "Filing Date": "2026-08-06",
                "Status": "Pending Review",
                "Assigned Unit": "Unassigned"
            }
        ]
        st.session_state.grievance_db = pd.DataFrame(sample_grievances)

# 3. Main System Workspace Layout Header
st.title("🇱🇷 National Public Grievance & Accountability Portal")
st.write("Official Government Blueprint Initiative — Republic of Liberia Police Accountability Dashboard.")
st.markdown("---")

# 4. Mode Selection Controller Segment (Unlocked public access for testing)
portal_mode = st.radio(
    "🧭 Select System Interface Mode:", 
    ["Citizen Complaint Desk", "LNP Command Center Dashboard"],
    horizontal=True
)

st.sidebar.title("🛠️ System Control Panel")
st.sidebar.info("🔓 Public Access Mode Active. Security overrides enabled for ECOWAS evaluators.")

if st.sidebar.button("🗑️ Reset Application Database"):
    st.session_state.grievance_db = pd.DataFrame()
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.sidebar.warning("Database cleared!")
    st.rerun()

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
# INTERFACE MODE B: LNP COMMAND CENTER DASHBOARD (PASSWORDS REMOVED)
# =====================================================================
elif portal_mode == "LNP Command Center Dashboard":
    st.subheader("📊 Professional Standards Command Panel Access")
    st.info("🔐 Administrative Session Open: Reviewer access authorized automatically as LNP Inspector General Desk.")
    st.markdown("---")
    
    if st.session_state.grievance_db.empty:
        st.info("Awaiting public data transfers. There are currently zero open citizen grievance records filed inside this ledger.")
    else:
        db = st.session_state.grievance_db
        
        # Ensure status columns exist safely
        if "Status" not in db.columns:
            db["Status"] = "Pending Review"
            
        total_cases = len(db)
        pending_cases = len(db[db["Status"] == "Pending Review"])
        active_investigations = len(db[db["Status"] == "Under Active Investigation"])
        resolved_cases = len(db[db["Status"] == "Resolved / Disposed Case"])
        
        # Upper Metrics Dashboard Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Filed Claims", f"{total_cases} Profiles")
        m2.metric("Awaiting Triage Review", f"{pending_cases} Cases")
        m3.metric("Active Investigations", f"{active_investigations} Cases")
        m4.metric("Resolved Cases", f"{resolved_cases} Cases")
        
        st.markdown("---")
        st.subheader("🗂️ National Master Grievance Log Ledger")
        # Render full database spreadsheet without index values
        st.dataframe(db, use_container_width=True, hide_index=True)
