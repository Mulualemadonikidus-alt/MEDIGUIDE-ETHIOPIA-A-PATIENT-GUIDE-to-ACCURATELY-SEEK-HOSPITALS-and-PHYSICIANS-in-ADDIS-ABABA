import os
import json
import requests
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

SERPER_KEY = os.environ.get("SERPER_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def audit_personnel():
    if not os.path.exists(DB_PATH):
        print("Database not initialized yet. Run hospital discovery first.")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        hospitals = json.load(f)
        
    if not hospitals:
        print("Hospital index matrix is currently empty.")
        return

    if not SERPER_KEY or not GEMINI_KEY:
        print("Error: Missing secure execution environment credentials.")
        return

    print(f"Beginning active roster cross-matching for {len(hospitals)} centers...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    for h in hospitals:
        print(f"Scanning medical rosters for: {h['name']}...")
        
        # Execute query for doctors belonging to this target facility
        headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
        payload = json.dumps({"q": f"doctors specialists physicians profiles at {h['name']} Addis Ababa"})
        
        try:
            res = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
            search_info = str(res.json().get("organic", []))[:3000]
            
            prompt = f"""
            Based on this search data for doctors working at {h['name']}:
            {search_info}
            
            Generate a JSON array of clinical departments and their specialists matching this precise scheme structural array:
            [
              {{
                "dep": "Department Name (e.g., Cardiology)",
                "docs": [
                  {{
                    "name": "Dr. Full Name",
                    "sub": "Sub-specialty details",
                    "edu": "MD, Fellowship training tracking details"
                  }}
                ]
              }}
            ]
            """
            
            ai_res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            h["specs"] = json.loads(ai_res.text.strip())
            
        except Exception as e:
            print(f"Skipping lookup for {h['name']} due to routine variance: {e}")
            continue

    # Commit the newly linked clinical rosters to the shared absolute path database
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)
    print("Physician synchronization process successfully completed.")

if __name__ == "__main__":
    audit_personnel()
