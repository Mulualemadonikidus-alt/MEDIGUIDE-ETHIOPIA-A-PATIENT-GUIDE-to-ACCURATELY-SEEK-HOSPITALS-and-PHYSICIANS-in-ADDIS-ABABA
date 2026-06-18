import streamlit as st
import json
import os

st.set_page_config(page_title="MediGuide Ethiopia Panel", layout="wide", page_icon="⚕️")

# Force absolute path tracking to prevent container routing glitches
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

def load_db():
    if not os.path.exists(DB_PATH):
        default_matrix = []
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_matrix, f, indent=2, ensure_ascii=False)
        return default_matrix
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.title("⚕️ MediGuide Ethiopia — Admin Control Center")
st.caption("Autonomic Operational Workspace for Monitoring Addis Ababa Healthcare Matrices")

db = load_db()

# --- HIGH LEVEL PERFORMANCE MATRIX ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Active Centers", len(db))
m2.metric("Public Institutions", len([h for h in db if h.get('type') == 'Public']))
m3.metric("Private Centers", len([h for h in db if h.get('type') == 'Private']))
m4.metric("Total Tracked Specialists", sum([len(s.get('docs', [])) for h in db for s in h.get('specs', [])]))

# --- COMPONENT TABS AREA ---
tab_edit, tab_sync = st.tabs(["✏️ Edit Live Directories", "🔄 Run Pipeline Worker Manual Overrides"])

with tab_edit:
    st.subheader("Data Matrix Modification Grid")
    
    # DEFENSIVE CHECK: Handle empty database safely instead of crashing
    if not db:
        st.info("📂 The database (`hospitals.json`) is currently empty. Go to the 'Run Pipeline Worker Manual Overrides' tab to populate it automatically, or seed your database right now using the button below.")
        if st.button("➕ Seed Database with Baseline Structure"):
            sample_node = [{
                "id": 1,
                "name": "Tikur Anbessa (Black Lion) Hospital",
                "am": "ጥቁር አንበሳ ሆስፒታል",
                "type": "Public",
                "est": 1964,
                "beds": 800,
                "addr": "Lideta Sub-City",
                "phone": "+251 11 155 1211",
                "appt": "Walk-in",
                "web": "https://www.aau.edu.et",
                "badge": "National Referral Center",
                "desc": "Primary public referral facility.",
                "tags": ["oncology", "cardiology"],
                "specs": []
            }]
            save_db(sample_node)
            st.success("Baseline structural node generated successfully! Refreshing workspace...")
            st.rerun()
    else:
        hospital_names = [h["name"] for h in db if "name" in h]
        selected_name = st.selectbox("Select Healthcare Center Node to Audit:", hospital_names)
        
        if selected_name:
            try:
                # Locate targeted profile references safely
                h_idx = next(i for i, h in enumerate(db) if h.get("name") == selected_name)
                target_h = db[h_idx]
                
                c1, c2, c3 = st.columns(3)
                target_h["name"] = c1.text_input("Hospital English Handle:", target_h.get("name", ""))
                target_h["am"] = c2.text_input("Amharic Local Name:", target_h.get("am", ""))
                
                current_type = target_h.get("type", "Public")
                type_options = ["Public", "Private", "NGO"]
                type_idx = type_options.index(current_type) if current_type in type_options else 0
                target_h["type"] = c3.selectbox("Institutional Type:", type_options, index=type_idx)
                
                c4, c5, c6 = st.columns(3)
                target_h["phone"] = c4.text_input("Verified Hotline Number:", target_h.get("phone", ""))
                target_h["web"] = c5.text_input("Target Clinical Roster Domain Link:", target_h.get("web", ""))
                target_h["badge"] = c6.text_input("Verification Badge Text Highlight:", target_h.get("badge", ""))
                
                target_h["desc"] = st.text_area("Institutional Service Profile Description:", target_h.get("desc", ""))
                
                st.markdown("#### Staff Roster Payload Matrix JSON View")
                specs_text = st.text_area("Clinical Departments Mapping payload:", json.dumps(target_h.get("specs", []), indent=2, ensure_ascii=False), height=250)
                
                try:
                    target_h["specs"] = json.loads(specs_text)
                    st.success("JSON validation checks complete.")
                except Exception:
                    st.error("Invalid nested array payload framework format. Fix structure rules.")

                if st.button("Commit Roster Rectifications to Database"):
                    db[h_idx] = target_h
                    save_db(db)
                    st.balloons()
                    st.success("Verified changes saved to local directory data framework layer.")
                    st.rerun()
            except StopIteration:
                st.error("Record selection pointer mismatch.")

with tab_sync:
    st.subheader("Manual Operational Trigger Mechanisms")
    st.warning("Running manual updates executes code directly on top of the container instance.")
    
    col_a, col_b = st.columns(2)
    if col_a.button("⚡ Force Run: Weekly New Facility Search"):
        with st.spinner("Invoking search scraper pipelines..."):
            os.system("python research_hospitals.py")
            st.success("Discovery workflow finalized execution loops successfully.")
            st.rerun()
            
    if col_b.button("🧬 Force Run: Bi-Weekly Physician Roster Audit"):
        with st.spinner("Executing live domain crawling algorithms..."):
            os.system("python research_personnel.py")
            st.success("Roster data framework updates synchronized.")
            st.rerun()

# --- FOOTER EMBED PREVIEW AREA ---
st.markdown("---")
st.subheader("Live Web Client Framework Mirror View Check")
if os.path.exists(os.path.join(BASE_DIR, "index.html")):
    st.components.v1.html(open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8").read(), height=600, scrolling=True)
else:
    st.info("Add an index.html file to your repository root directory to enable live layout checks.")
