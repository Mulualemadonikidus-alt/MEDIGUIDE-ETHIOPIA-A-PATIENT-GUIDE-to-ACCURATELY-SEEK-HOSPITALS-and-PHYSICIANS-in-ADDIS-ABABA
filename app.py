import streamlit as st
import json
import os

st.set_page_config(page_title="MediGuide Ethiopia Panel", layout="wide", page_icon="⚕️")

# Force absolute path tracking 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FIXED: Pointing to the correct, single standard filename
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

def load_db():
    if not os.path.exists(DB_PATH):
        # FIXED: Return empty list. Do NOT create a fake seed file that overwrites real data.
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

# --- HIGH LEVEL PERFORMANCE MATRIX ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Active Centers", len(db))
m2.metric("Public Institutions", len([h for h in db if h.get('type') == 'Public']))
m3.metric("Private Centers", len([h for h in db if h.get('type') == 'Private']))
m4.metric("Total Tracked Specialists", sum([len(s.get('docs', [])) for h in db for s in h.get('specs', [])]))

# --- COMPONENT TABS AREA ---
tab_edit, tab_sync = st.tabs(["✏️ Edit Live Directories", "🔄 Run Pipeline Worker"])

with tab_edit:
    st.subheader("Data Matrix Modification Grid")
    
    if not db:
        st.info("📂 The database (`hospitals.json`) is currently empty. The GitHub Action Autonomic Scheduler will populate this file during its next automated run.")
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
                except Exception:
                    st.error("Invalid nested array payload framework format. Fix structure rules.")

                if st.button("Commit Roster Rectifications to Database"):
                    db[h_idx] = target_h
                    save_db(db)
                    st.balloons()
                    st.success("Verified changes saved to local directory! (Note: changes made here will persist until the next GitHub action override).")
                    st.rerun()
            except StopIteration:
                st.error("Record selection pointer mismatch.")

with tab_sync:
    st.subheader("Automated Operational Pipelines")
    st.info("💡 **Architectural Security Update:** Streamlit Cloud uses ephemeral containers. Running scrapers directly from this UI causes permanent data loss when the container goes to sleep.")
    st.write("To protect your data framework, all web scraping has been securely delegated to your **GitHub Actions Autonomic Scheduler**.")
    
    # Directly link to your GitHub Action for manual triggers
    st.markdown("[👉 Click here to Manually Trigger the Scraper inside GitHub Actions](https://github.com/Mulualemadonikidus-alt/MEDIGUIDE-ETHIOPIA-A-PATIENT-GUIDE-to-ACCURATELY-SEEK-HOSPITALS-and-PHYSICIANS-in-ADDIS-ABABA/actions/workflows/autonomic_scheduler.yml)")

# --- FOOTER EMBED PREVIEW AREA ---
st.markdown("---")
st.subheader("Live Web Client Framework Mirror View Check")
if os.path.exists(os.path.join(BASE_DIR, "index.html")):
    st.components.v1.html(open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8").read(), height=600, scrolling=True)
else:
    st.info("Add an index.html file to your repository root directory to enable live layout checks.")
