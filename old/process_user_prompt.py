"""
Test script to categorize books using Ollama (llama3)
"""

import pyodbc
import urllib.request
import urllib.error
import json

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3"


def generate_prompt(subject, limit=10, column_name="Value", dest_column_name="ai_category"):
    """Generate a generic prompt for categorizing column values"""
    prompt = f"""
You are generating classification categories for a database column.

Subject domain: {subject}
Source column: {column_name}
Destination column: {dest_column_name}

Task:
Generate exactly {limit} distinct categories that could classify values in this column.

Constraints:
- Categories must be widely recognized genres or types within the subject domain.
- Use full names only (for example: "Science Fiction", NOT "SF").
- Do NOT use abbreviations.
- Do NOT use audience or age-based categories (no Young Adult, Children, YA, etc.).
- Do NOT use vague academic fields (for example: "Science").
- Each category should be 1–3 words.
- All categories must be unique and clearly different.

Output rules:
- Output ONLY the result.
- No explanations.
- No extra text.
- No line breaks.
- No abbreviations.

Format strictly as:
'[Category1,Category2,...,Categoryn]'
"""
    return prompt


def call_ollama(prompt):
    """Call Ollama API"""
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        data = json.dumps({
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
            
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None


def get_categories(subject, limit, column_name, dest_column_name):
    """Categorization"""
    
    # Generate the prompt
    prompt = generate_prompt(subject, limit, column_name, dest_column_name)
    
    # print(f"\nPrompt sent to Llama3:\n{prompt}\n")
    # print("-"*60)
    
    # Call Ollama
    print("Calling Ollama (llama3)...")
    result = call_ollama(prompt)
    
    if result:
        print(result)
        categories = result.strip("[]").split(",") # later - c.strip()
        categories = [c.strip() for c in categories]

        return categories
    else:
        print("Failed to get response from Ollama")
    
    return None


if __name__ == "__main__":
    print(get_categories("Books", 10, "BookName", "ai_genre"))
