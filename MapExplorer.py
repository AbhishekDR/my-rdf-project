from google import genai
from rdflib import Graph
import os

# --- 1. SETUP THE DATA (The "Body") ---
g = Graph()
try:
    # Make sure practice.ttl is in the same folder!
    g.parse("map_data.ttl", format="turtle")
    print("✓ Map data loaded successfully.")
except Exception as e:
    print(f"✗ Failed to load map data: {e}")

# --- 2. SETUP THE LLM (The "Brain") ---
# Use your actual key here
client = genai.Client(api_key="AIzaSyBxKK12vx_sG-ZYaxAay0VQXwtVepJydEE")

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
        model="gemini-2.0-flash",
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