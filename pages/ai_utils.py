"""
AI utility functions for AI Enrichment Tool
"""

import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv()


def get_categories_list(subject, limit=10, column_name="Value", dest_column_name="ai_category"):
    """
    Generate a prompt for categorizing column values using AI.
    
    Args:
        subject: The subject/domain (e.g., "Books", "Employees")
        limit: Number of categories to generate
        column_name: Source column name (e.g., "BookName", "JobTitle")
        dest_column_name: Destination column name (e.g., "ai_genre", "ai_category")
    
    Returns:
        List of categories
    """
    prompt = f"""
You are generating classification categories for a database column.

Subject domain: {subject}
Source column name: {column_name}
Destination column name: {dest_column_name}

Generate {limit} distinct categories that could classify values in this column.

Rules:
- Categories must be generic types, themes, or domains
- Each category should be 1-3 words
- All categories must be unique

Output format (ONLY):
['cat1','cat2',...,cat{limit}]
"""
    return call_ollama(prompt)


def call_ollama(prompt, model_name="llama3", base_url="http://localhost:11434"):
    """Call Ollama API"""
    try:
        url = f"{base_url}/api/generate"
        data = json.dumps({
            "model": model_name,
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
            response_text = result.get("response", "").strip()
            
            # Parse the response to get categories list
            if response_text and '[' in response_text:
                try:
                    # Try to extract list from response
                    start = response_text.find('[')
                    end = response_text.find(']') + 1
                    list_str = response_text[start:end]
                    # Parse the list
                    categories = [c.strip().strip("'\"") for c in list_str[1:-1].split(',')]
                    return categories
                except:
                    return [response_text]
            return [response_text]
            
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None


def generate_categories_ai(subject, limit=10, column_name="Value", dest_column_name="ai_category"):
    """
    Generate categories using AI based on column metadata.
    
    This function creates categories WITHOUT looking at actual data values.
    It uses only the subject, column name, and description to infer appropriate categories.
    """
    return get_categories_list(subject, limit, column_name, dest_column_name)


def call_arcee_api(prompt, model_name="trinity-mini"):
    """Call Arcee AI API"""
    try:
        api_key = os.getenv("ARCEE_API_KEY")
        if not api_key:
            return None
            
        url = "https://api.arcee.ai/v1/chat/completions"
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        data_json = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            return None
            
    except Exception as e:
        print(f"Error calling Arcee API: {e}")
        return None
