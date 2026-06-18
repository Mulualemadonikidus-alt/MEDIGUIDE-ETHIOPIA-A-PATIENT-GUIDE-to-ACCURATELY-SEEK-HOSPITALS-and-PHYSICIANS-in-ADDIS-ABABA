import os
import json
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# 1. Define the correct, unified database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospitals.json')

def load_database():
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_database(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_biweekly_roster_audit():
    print("Initiating autonomic bi-weekly audit of medical specialist rosters...")
    db = load_database()
    ai_key = os.environ.get("GEMINI_API_KEY")
    if not ai_key:
        print("AI engine API key unconfigured.")
        return
    ai_client = genai.Client(api_key=ai_key)
    
    modified = False

    for hospital in db:
        url = hospital.get("web")
        # Only crawl if a valid specific landing domain exists
        if not url or "aau.edu.et" in url or "google.com" in url:
            continue
            
        print(f"Scraping roster updates from target node domain: {hospital.get('name', 'Unknown')} ({url})")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            html_raw = requests.get(url, headers=headers, timeout=15).text
            soup = BeautifulSoup(html_raw, 'html.parser')
            
            # Extract plain text, eliminating excess script markup noise
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
            page_text = " ".join(soup.get_text().split())[:10000] # Cap text buffer input
            
            prompt = f"""
            Analyze the following scraped text from the official website of {hospital.get('name', 'the hospital')}. 
            Identify all medical specialists, consultants, sub-specialists, surgeons, and clinical departments listed.
            Update the current 'specs' array structure below to reflect current active practitioners and medical services accurately.

            Current Specs Array Matrix to update:
            {json.dumps(hospital.get('specs', []))}

            Scraped Source Text:
            {page_text}

            Return a valid JSON array matching the exact structure of the 'specs' schema. Keep existing entries if they are still relevant, or modify/add new ones found in the source text.
            Schema structure: [{{ "n": "Specialty Dept Title", "icon": "â™¥", "subs": ["Subspecialty 1"], "docs": ["Dr. Name"] }}]
            """

            ai_response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            updated_specs = json.loads(ai_response.text)
            if updated_specs and isinstance(updated_specs, list):
                hospital["specs"] = updated_specs
                # Dynamically augment descriptive index search tags based on updated medical services
                new_tags = set(hospital.get("tags", []))
                for s in updated_specs:
                    new_tags.add(s.get("n", "").lower().split()[0] if s.get("n") else "")
                    for sub in s.get("subs", []):
                        new_tags.add(sub.lower().split()[0] if sub else "")
                
                # Remove empty strings from tags if any slipped through
                new_tags.discard("")
                hospital["tags"] = list(new_tags)[:25]
                modified = True
                print(f"Roster profile sync complete for {hospital.get('name', 'Unknown')}")
                
        except Exception as e:
            print(f"Failed to crawl specialist roster for node {hospital.get('name', 'Unknown')}: {e}")
            
    if modified:
        save_database(db)
        print("Global database index synced with latest physician rosters. Database updated successfully.")
    else:
        print("No physician modifications registered during this cycle. Database remains unchanged.")

if __name__ == "__main__":
    run_biweekly_roster_audit()
