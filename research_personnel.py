import os
import json
import requests
from google import genai
from google.genai import types
import sys
import time

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

    try:
        client = genai.Client(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}", file=sys.stderr)
        sys.exit(1)

    for h in hospitals:
        headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
        payload = json.dumps({"q": f"doctors specialists physicians profiles at {h['name']} Addis Ababa"})
        
        try:
            res = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
            res.raise_for_status()
            search_info = str(res.json().get("organic", []))[:3000]
        except Exception as e:
            print(f"Warning: Skipping Serper tracking logic for {h['name']}: {e}", file=sys.stderr)
            continue
            
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
        
        # --- EXPONENTIAL BACKOFF LOOP FOR ROSTER LOOPS ---
        ai_res = None
        max_retries = 4
        for attempt in range(max_retries):
            try:
                ai_res = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                break
            except Exception as e:
                err_msg = str(e)
                if "503" in err_msg or "UNAVAILABLE" in err_msg or "ResourceExhausted" in err_msg:
                    if attempt < max_retries - 1:
                        delay = 3 * (2 ** attempt)
                        print(f"Warning: Gemini busy indexing {h['name']}. Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                print(f"Warning: Bypassing structural build tracking for {h['name']} due to persistent AI faults: {e}", file=sys.stderr)
                break

        if ai_res:
            try:
                h["specs"] = json.loads(ai_res.text.strip())
            except Exception as e:
                print(f"Warning: Generated invalid data object notation format output for {h['name']}: {e}", file=sys.stderr)

    # Save data structure changes
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)
    print("Physician synchronization process successfully completed.")

if __name__ == "__main__":
    audit_personnel()
