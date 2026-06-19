import os
import json
import requests
from google import genai
from google.genai import types
import sys
import time

# Force absolute path coordination so files match app.py location exactly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

SERPER_KEY = os.environ.get("SERPER_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def run_research():
    if not SERPER_KEY or not GEMINI_KEY:
        print("Error: Missing secure execution environment variables.", file=sys.stderr)
        sys.exit(1)
    
    print("Launching live crawling system for Addis Ababa medical nodes...")
    
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    payload = json.dumps({
        "q": "best specialized hospitals clinics contact address Addis Ababa Ethiopia",
        "num": 15
    })
    
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
        response.raise_for_status()
        search_results = response.json()
    except Exception as e:
        print(f"Network error from Serper API: {e}", file=sys.stderr)
        sys.exit(1)

    organic = search_results.get("organic", [])
    if not organic:
        print("Error: Serper API returned zero organic search results. Check your Serper API Key or quota.", file=sys.stderr)
        sys.exit(1)

    raw_intelligence = str(organic)[:5000]

    try:
        client = genai.Client(api_key=GEMINI_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = f"""
    Analyze this raw search intelligence data for Addis Ababa healthcare facilities:
    {raw_intelligence}
    
    Generate a clean JSON list of objects matching this exact database schema model:
    [
      {{
        "id": 1,
        "name": "Official Hospital Name",
        "am": "Amharic Name translation if known",
        "type": "Public",
        "est": 1990,
        "beds": 150,
        "addr": "Specific sub-city area location info",
        "phone": "Telephone contact number",
        "appt": "Walk-in or Referral required",
        "web": "Website URL link string",
        "badge": "Specialty Center Highlight",
        "desc": "Short overview summary statement of their strengths",
        "tags": ["cardiology", "maternity"],
        "specs": []
      }}
    ]
    """
    
    # --- EXPONENTIAL BACKOFF RETRY ENGINE ---
    ai_response = None
    max_retries = 4
    for attempt in range(max_retries):
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            break  # Exit the retry loop upon a successful request
        except Exception as e:
            err_msg = str(e)
            # Check if the error is due to a server exception or rate limit
            if "503" in err_msg or "UNAVAILABLE" in err_msg or "ResourceExhausted" in err_msg:
                if attempt < max_retries - 1:
                    delay = 3 * (2 ** attempt)  # Delay intervals: 3s, 6s, 12s
                    print(f"Warning: Gemini server busy (503/UNAVAILABLE). Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(delay)
                    continue
            print(f"Gemini transformation or JSON validation error: {e}", file=sys.stderr)
            sys.exit(1)

    if not ai_response:
        print("Error: Failed to obtain response from Gemini after multiple retry loops.", file=sys.stderr)
        sys.exit(1)

    try:
        parsed_data = json.loads(ai_response.text.strip())
        if not isinstance(parsed_data, list):
            raise ValueError("Gemini engine response did not compile into a valid array sequence list.")

        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Discovered and saved {len(parsed_data)} live infrastructure entities.")
        
    except Exception as e:
        print(f"JSON Validation or Parsing Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_research()
