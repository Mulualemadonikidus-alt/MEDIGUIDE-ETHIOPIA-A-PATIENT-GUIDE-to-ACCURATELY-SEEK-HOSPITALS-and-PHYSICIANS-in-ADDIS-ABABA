import streamlit as st
import json
import os
import subprocess
import sys

st.set_page_config(page_title="MediGuide Ethiopia Panel", layout="wide", page_icon="⚕️")

# Resolve absolute tracking paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return []
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

# --- INSTANT SNAPSHOT METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Active Centers", len(db))
m2.metric("Public Institutions", len([h for h in db if h.get('type') == 'Public']))
m3.metric("Private Centers", len([h for h in db if h.get('type') == 'Private']))
m4.metric("Tracked Specialists", sum([len(s.get('docs', [])) for h in db for s in h.get('specs', [])]))

tab_edit, tab_sync = st.tabs(["✏️ Edit Live Directories", "🔄 Run Pipeline Worker Manual Overrides"])

with tab_edit:
    st.subheader("Data Matrix Modification Grid")
    if not db:
        st.info("📂 The database (hospitals.json) is currently empty. Head to the pipeline tab to execute an autonomous search query.")
        if st.button("➕ Seed Database with Baseline Structure"):
            sample_node = [{
                "id": 1,
                "name": "Tikur Anbessa (Black Lion) Hospital",
                "am": "ጥቁር አንበሳ ሆስፒታል",
                "type": "Public",
                "est": 1964,
                "beds": 800,
                "addr": "Lideta Sub-City, Addis Ababa",
                "phone": "+251 11 155 1211",
                "appt": "Walk-in / Referral",
                "web": "https://www.aau.edu.et",
                "badge": "National Referral Center",
                "desc": "The primary public university referral hospital in Ethiopia.",
                "tags": ["oncology", "cardiology", "pediatrics"],
                "specs": []
            }]
            save_db(sample_node)
            st.success("Baseline structural node generated! Reloading framework...")
            st.rerun()
    else:
        hospital_names = [h["name"] for h in db if "name" in h]
        selected_name = st.selectbox("Select Healthcare Center Node to Audit:", hospital_names)
        
        if selected_name:
            h_idx = next(i for i, h in enumerate(db) if h.get("name") == selected_name)
            target_h = db[h_idx]
            
            c1, c2, c3 = st.columns(3)
            target_h["name"] = c1.text_input("Hospital English Handle:", target_h.get("name", ""))
            target_h["am"] = c2.text_input("Amharic Local Name:", target_h.get("am", ""))
            target_h["type"] = c3.selectbox("Institutional Type:", ["Public", "Private", "NGO"], index=["Public", "Private", "NGO"].index(target_h.get("type", "Public")))
            
            c4, c5, c6 = st.columns(3)
            target_h["phone"] = c4.text_input("Verified Hotline Number:", target_h.get("phone", ""))
            target_h["web"] = c5.text_input("Official Link:", target_h.get("web", ""))
            target_h["badge"] = c6.text_input("Verification Highlight Badge:", target_h.get("badge", ""))
            
            target_h["desc"] = st.text_area("Service Profile Description:", target_h.get("desc", ""))
            
            specs_text = st.text_area("Clinical Departments (JSON Array):", json.dumps(target_h.get("specs", []), indent=2, ensure_ascii=False), height=200)
            try:
                target_h["specs"] = json.loads(specs_text)
            except Exception:
                st.error("Invalid internal JSON structure inside specialized fields.")

            if st.button("Commit Changes to Database"):
                db[h_idx] = target_h
                save_db(db)
                st.success("Changes deployed safely to database matrix.")
                st.rerun()

with tab_sync:
    st.subheader("Manual Operational Trigger Mechanisms")
    st.markdown("Invoking these workers activates background search instances using your system API Secrets.")
    
    # Securely retrieve secret keys from Streamlit Cloud Environment
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    serper_key = st.secrets.get("SERPER_API_KEY", "")
    
    if not gemini_key or not serper_key:
        st.error("🚨 Cloud deployment API keys are missing. Verify your keys are stored securely inside the Streamlit App Secret console.")
    
    col_a, col_b = st.columns(2)
    
    # Inject secrets into background processes seamlessly
    env_context = os.environ.copy()
    env_context["GEMINI_API_KEY"] = gemini_key
    env_context["SERPER_API_KEY"] = serper_key
    
    if col_a.button("⚡ Force Run: Weekly New Hospital Deep Search"):
        if gemini_key and serper_key:
            with st.spinner("Autonomous Agents executing search queries via Serper & Gemini..."):
                script_path = os.path.join(BASE_DIR, "research_hospitals.py")
                result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, env=env_context)
                if result.returncode == 0:
                    st.success("Discovery workflow finalized execution loops successfully.")
                    st.rerun()
                else:
                    st.error(f"Execution Error: {result.stderr}")
                    
    if col_b.button("🧬 Force Run: Bi-Weekly Physician Roster Audit"):
        if gemini_key and serper_key:
            with st.spinner("Crawling clinician rosters..."):
                script_path = os.path.join(BASE_DIR, "research_personnel.py")
                result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, env=env_context)
                if result.returncode == 0:
                    st.success("Roster synchronization complete.")
                    st.rerun()
                else:
                    st.error(f"Execution Error: {result.stderr}")

# --- HTML PREVIEW FALLBACK AND DETECTOR ---
st.markdown("---")
st.subheader("Live Web Client View Mirror")
html_options = ["index.html", "index.html.html"]
target_html = next((f for f in html_options if os.path.exists(os.path.join(BASE_DIR, f))), None)

if target_html:
    with open(os.path.join(BASE_DIR, target_html), "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=650, scrolling=True)
else:
    st.info("Upload an index.html file to your root directory to map your front-end preview canvas here.")
