import os
import json
import requests
import google.generativeai as genai

# Grab environment variables passed down safely from app.py
SERPER_KEY = os.environ.get("SERPER_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

DB_PATH = "hospitals.json"

def run_research():
    if not SERPER_KEY or not GEMINI_KEY:
        print("Missing required API orchestration configuration variables.")
        return
    
    print("Initiating web discovery sweeps for Addis Ababa healthcare nodes...")
    
    # 1. Query the Serper Google Search Engine Layer
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    payload = json.dumps({"q": "specialized hospitals medical centers in Addis Ababa Ethiopia address phone"})
    
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
        search_results = response.json()
    except Exception as e:
        print(f"Network processing bottleneck occurred: {e}")
        return

    # 2. Package raw intelligence data for processing
    raw_data_dump = str(search_results.get("organic", []))[:4000] 

    # 3. Configure Gemini context engines
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are an expert medical database cleaner. Analyze this raw text data concerning healthcare centers in Addis Ababa:
    {raw_data_dump}
    
    Convert this information into a valid, minified JSON array of objects representing unique hospitals. 
    Each object MUST strict match this exact structural schema dictionary layout format:
    {{
      "id": 1,
      "name": "Official English Hospital Name",
      "am": "Amharic Translation if known or empty string",
      "type": "Public" or "Private",
      "est": 2000,
      "beds": 100,
      "addr": "Sub-City location details",
      "phone": "Telephone hotline string",
      "appt": "Walk-in",
      "web": "URL string",
      "badge": "Verified Info",
      "desc": "Short overview text summary descriptive analysis",
      "tags": ["general", "emergency"],
      "specs": []
    }}
    Return ONLY the clean raw valid minified JSON array. Do not append markdown wrapper blocks or code tags.
    """
    
    try:
        ai_response = model.generate_content(prompt)
        cleaned_text = ai_response.text.strip()
        
        # Strip potential markdown wrappers securely
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        parsed_json = json.loads(cleaned_text.strip())
        
        # Commit freshly discovered updates straight to the database layer
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        print("Live database successfully populated with fresh discovery arrays.")
        
    except Exception as e:
        print(f"Parsing engine exception run handled: {e}")

if __name__ == "__main__":
    run_research()
