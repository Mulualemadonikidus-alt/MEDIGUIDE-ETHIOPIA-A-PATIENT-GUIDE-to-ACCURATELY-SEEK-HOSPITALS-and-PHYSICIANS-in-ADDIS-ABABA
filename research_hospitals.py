import os
import json
import requests
import google.generativeai as genai
import sys

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
        # Initialize Gemini interface 
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        
        # Request native structured JSON handling directly from the AI model
        ai_response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        parsed_data = json.loads(ai_response.text.strip())
        
        if not isinstance(parsed_data, list):
            raise ValueError("Gemini engine response did not compile into a valid array sequence list.")

        # Save to shared absolute path database
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Discovered and saved {len(parsed_data)} live infrastructure entities.")
        
    except Exception as e:
        print(f"Gemini transformation or JSON validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_research()
