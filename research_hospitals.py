import os
import json
import requests
from google import genai
from google.genai import types

def load_database():
    with open('hospitals.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(data):
    with open('hospitals.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_weekly_hospital_search():
    print("Initiating autonomic weekly search for newly identified Addis Ababa clinics...")
    db = load_database()
    existing_names = {h['name'].lower() for h in db}
    
    # query local clinical search indices using public Serper/Google engine API keys
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        print("Missing API key configuration.")
        return
        
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": "newly opened specialty clinic hospital medical center Addis Ababa, Ethiopia",
      "gl": "et",
      "num": 10
    })
    headers = {
      'X-API-KEY': api_key,
      'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload).json()
        search_results = response.get('organic', [])
    except Exception as e:
        print(f"Network discovery error: {e}")
        return

    # Initialize Gemini API Client
    ai_key = os.environ.get("GEMINI_API_KEY")
    ai_client = genai.Client(api_key=ai_key) if ai_key else None

    new_discoveries = 0

    for item in search_results:
        title = item.get('title')
        snippet = item.get('snippet', '')
        link = item.get('link', '')
        
        # Determine if this search entry mentions a hospital not in our database
        is_novel = True
        for name in existing_names:
            if name in title.lower() or title.lower() in name:
                is_novel = False
                break
                
        if is_novel and ai_client:
            print(f"Analyzing unmapped medical node candidate: {title}")
            
            # Format unstructured snippets cleanly using structured data generations
            prompt = f"""
            Extract the entity info into our precise JSON structure.
            Candidate Title: {title}
            Context Snippet: {snippet}
            Target Link: {link}
            
            Return raw valid JSON following this format:
            {{
              "name": "Full English Name",
              "am": "Amharic Name if inferable, else leave empty string",
              "type": "Public" or "Private" or "NGO",
              "est": year integer or null,
              "beds": integer or null,
              "addr": "Approximate sub-city or street name in Addis Ababa",
              "phone": "Inferred contact number or empty string",
              "appt": "Walk-in OPD or contact center",
              "web": "{link}",
              "fb": "",
              "tg": "",
              "coords": "Approximate coordinates string based on location",
              "badge": "Short highlights tagline less than 8 words",
              "desc": "A concise informative single paragraph about what they treat.",
              "tags": ["lowercase","keywords","matching","specialties"],
              "specs": []
            }}
            """
            try:
                ai_response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                structured_data = json.loads(ai_response.text)
                
                # Assign a unique tracking token ID
                structured_data["id"] = max([h["id"] for h in db]) + 1
                db.append(structured_data)
                existing_names.add(structured_data["name"].lower())
                new_discoveries += 1
            except Exception as ex:
                print(f"Structured AI parsing exception: {ex}")
                
    if new_discoveries > 0:
        save_database(db)
        print(f"Autonomic framework successfully appended {new_discoveries} new centers.")
    else:
        print("No unmapped clinical footprints discovered this week.")

if __name__ == "__main__":
    run_weekly_hospital_search()