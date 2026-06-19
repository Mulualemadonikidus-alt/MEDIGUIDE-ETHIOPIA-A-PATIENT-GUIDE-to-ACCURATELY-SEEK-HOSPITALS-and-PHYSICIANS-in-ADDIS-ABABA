import os
import json
import requests
import google.generativeai as genai
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

SERPER_KEY = os.environ.get("SERPER_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def audit_personnel():
    if not os.path.exists(DB_PATH):
        print("Error: Database file hospitals.json does not exist. Run hospital discovery first.", file=sys.stderr)
        sys.exit(1)
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        hospitals = json.load(f)
        
    if not hospitals:
        print("Error: Hospital index matrix is currently empty.", file=sys.stderr)
        sys.exit(1)

    if not SERPER_KEY or not GEMINI_KEY:
        print("Error: Missing secure execution environment credentials.", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    for h in hospitals:
        headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
        payload = json.dumps({"q": f"doctors specialists physicians profiles at {h['name']} Addis Ababa"})
        
        try:
            res = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
            res.raise_for_status()
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
            print(f"Warning: Skipping record generation loops for {h['name']}: {e}", file=sys.stderr)
            continue

    # Commit the newly linked clinical rosters
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)
    print("Physician synchronization process successfully completed.")

if __name__ == "__main__":
    audit_personnel()
