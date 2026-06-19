import os
import json
import requests
import google.generativeai as genai

# Force absolute path coordination so files match app.py location exactly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

SERPER_KEY = os.environ.get("SERPER_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def run_research():
    if not SERPER_KEY or not GEMINI_KEY:
        print("Error: Missing secure execution environment variables.")
        return
    
    print("Launching live crawling system for Addis Ababa medical nodes...")
    
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    payload = json.dumps({
        "q": "best specialized hospitals clinics contact address Addis Ababa Ethiopia",
        "num": 15
    })
    
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
        search_results = response.json()
    except Exception as e:
        print(f"Network error: {e}")
        return

    raw_intelligence = str(search_results.get("organic", []))[:5000]

    # Initialize modern Gemini interface 
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analyze this raw search intelligence data for Addis Ababa healthcare facilities:
    {raw_intelligence}
    
    Generate a clean JSON list of objects matching this exact database schema model:
    {{
      "id": 1,
      "name": "Official Hospital Name",
      "am": "Amharic Name translation if known",
      "type": "Public" or "Private",
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
    """
    
    try:
        # Request native structured JSON handling directly from the AI model
        ai_response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        parsed_data = json.loads(ai_response.text.strip())
        
        # Verify and merge with existing database structures
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Saved {len(parsed_data)} live infrastructure entities to {DB_PATH}")
        
    except Exception as e:
        print(f"Processing error during dataset transformation: {e}")

if __name__ == "__main__":
    run_research()
