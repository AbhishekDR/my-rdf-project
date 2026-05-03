from google import genai
from rdflib import Graph
import os
from dotenv import load_dotenv

# --- 1. SETUP THE DATA (The "Body") ---
g = Graph()
try:
    # Make sure practice.ttl is in the same folder!
    g.parse("map_data.ttl", format="turtle")
    print("✓ Map data loaded successfully.")
except Exception as e:
    print(f"✗ Failed to load map data: {e}")

# Get the key
raw_key = os.getenv("GOOGLE_API_KEY")

# --- BULLETPROOF CHECK ---
if raw_key is None:
    print("❌ CRITICAL: GOOGLE_API_KEY is None. load_dotenv() failed to find or read your .env file.")
    # Attempt a direct path load if OneDrive is being weird
    dotenv_path = os.path.join(os.getcwd(), '.env')
    print(f"Searching for .env at: {dotenv_path}")
elif not raw_key.startswith("AIza"):
    print(f"❌ CRITICAL: Key was found but it doesn't start with 'AIza'. It starts with: '{raw_key[:5]}'")
else:
    print(f"✅ Key loaded successfully. Length: {len(raw_key)} characters.")

# Force clean the key just in case of hidden characters
api_key = raw_key.strip() if raw_key else None
# --- 2. SETUP THE LLM (The "Brain") ---
# Use your actual key here
client = genai.Client(api_key="AIzaSyBOb-wXgTglU-5A9vb1gbAupdRKHXxhlJs")

SYSTEM_PROMPT = """
You are a SPARQL expert for NDS map data.
Schema:
- Prefix: nds: <http://nds.map/schema#>
- Classes: Road, Lane, TrafficFeature
- Properties: nds:name, nds:speedLimit, nds:hasLane, nds:hasFeature, nds:material, nds:connectsTo
Return ONLY the raw SPARQL code. No markdown.
"""

# --- 3. THE MAGIC FUNCTION ---
def ask_the_map(user_question):
    # Step A: Generate SPARQL
    response = client.models.generate_content(
        model="gemini-flash-latest",
        config={'system_instruction': SYSTEM_PROMPT},
        contents=user_question
    )
    sparql_query = response.text.strip().replace("```sparql", "").replace("```", "")
    
    print(f"\n[Generated SPARQL]:\n{sparql_query}")

    # Step B: Execute against local data
    try:
        results = g.query(sparql_query)
        print("\n[Results]:")
        if len(results) == 0:
            print("No matches found in the map.")
        for row in results:
            # This prints all variables found in the SELECT
            print(" | ".join(str(item) for item in row))
    except Exception as e:
        print(f"Error running query: {e}")

# --- 4. RUN IT ---
if __name__ == "__main__":
    while True:
        question = input("\nAsk about the map (or type 'exit'): ")
        if question.lower() == 'exit':
            break
        ask_the_map(question)