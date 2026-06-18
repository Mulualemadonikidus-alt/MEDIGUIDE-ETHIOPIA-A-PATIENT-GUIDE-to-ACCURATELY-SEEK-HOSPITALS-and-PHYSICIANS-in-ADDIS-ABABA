import streamlit as st
import json
import os

st.set_page_config(page_title="MediGuide Ethiopia Panel", layout="wide", page_icon="⚕️")

def load_db():
    with open('hospitals.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open('hospitals.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.title("⚕️ MediGuide Ethiopia — Admin Control Center")
st.caption("Autonomic Operational Workspace for Monitoring Addis Ababa Healthcare Matrices")

db = load_db()

# --- HIGH LEVEL PERFORMANCE MATRIX ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Active Centers", len(db))
m2.metric("Public Institutions", len([h for h in db if h['type'] == 'Public']))
m3.metric("Private Centers", len([h for h in db if h['type'] == 'Private']))
m4.metric("Total Tracked Specialists", sum([len(s.get('docs', [])) for h in db for s in h.get('specs', [])]))

# --- COMPONENT TABS AREA ---
tab_edit, tab_sync = st.tabs(["✏️ Edit Live Directories", "🔄 Run Pipeline Worker Manual Overrides"])

with tab_edit:
    st.subheader("Data Matrix Modification Grid")
    hospital_names = [h["name"] for h in db]
    selected_name = st.selectbox("Select Healthcare Center Node to Audit:", hospital_names)
    
    # Locate targeted profile references
    h_idx = next(i for i, h in enumerate(db) if h["name"] == selected_name)
    target_h = db[h_idx]
    
    c1, c2, c3 = st.columns(3)
    target_h["name"] = c1.text_input("Hospital English Handle:", target_h["name"])
    target_h["am"] = c2.text_input("Amharic Local Name:", target_h["am"])
    target_h["type"] = c3.selectbox("Institutional Type:", ["Public", "Private", "NGO"], index=["Public", "Private", "NGO"].index(target_h["type"]))
    
    c4, c5, c6 = st.columns(3)
    target_h["phone"] = c4.text_input("Verified Hotline Number:", target_h["phone"])
    target_h["web"] = c5.text_input("Target Clinical Roster Domain Link:", target_h["web"])
    target_h["badge"] = c6.text_input("Verification Badge Text Highlight:", target_h["badge"])
    
    target_h["desc"] = st.text_area("Institutional Service Profile Description:", target_h["desc"])
    
    st.markdown("#### Staff Roster Payload Matrix JSON View")
    specs_text = st.text_area("Clinical Departments Mapping payload:", json.dumps(target_h["specs"], indent=2, ensure_ascii=False), height=250)
    
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

with tab_sync:
    st.subheader("Manual Operational Trigger Mechanisms")
    st.warning("Running manual updates logs execution over top of the scheduled workflows. Ensure your environment variable credentials match.")
    
    col_a, col_b = st.columns(2)
    if col_a.button("⚡ Force Run: Weekly New Facility Search"):
        with st.spinner("Invoking search scraper pipelines..."):
            os.system("python research_hospitals.py")
            st.success("Discovery workflow finalized execution loops successfully.")
            
    if col_b.button("🧬 Force Run: Bi-Weekly Physician Roster Audit"):
        with st.spinner("Executing live domain crawling algorithms..."):
            os.system("python research_personnel.py")
            st.success("Roster data framework updates synchronized.")

# --- FOOTER EMBED PREVIEW AREA ---
st.markdown("---")
st.subheader("Live Web Client Framework Mirror View Check")
st.caption("This embedded view shows the active index portal template mapping layout exactly as your patients see it.")
st.components.v1.html(open("index.html", "r", encoding="utf-8").read(), height=600, scrolling=True)