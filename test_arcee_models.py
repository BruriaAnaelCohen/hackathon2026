"""
Test script to check available Arcee AI models
"""

import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ARCEE_API_KEY")

def get_available_models():
    """Fetch available models from Arcee AI"""
    try:
        req = urllib.request.Request(
            "https://api.arcee.ai/v1/models",
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            print("=" * 60)
            print("Available Arcee AI Models:")
            print("=" * 60)
            
            if 'data' in data and len(data['data']) > 0:
                for model in data['data']:
                    model_id = model.get('id', 'Unknown')
                    print(f"  - {model_id}")
                return data['data'][0]['id']
            else:
                print("No models found in response")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_chat_completion(model_name):
    """Test chat completion with a specific model"""
    print(f"\nTesting chat completion with model: {model_name}")
    print("-" * 60)
    
    try:
        url = "https://api.arcee.ai/v1/chat/completions"
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Say 'Hello, Arcee AI is working!' in exactly 5 words"}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        data_json = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content']
                print(f"✅ Success! Response: {response_text}")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Arcee AI Connection\n")
    
    # Get available models
    first_model = get_available_models()
    
    if first_model:
        # Test the first available model
        test_chat_completion(first_model)
    else:
        # Try fallback models
        fallback_models = ["trinity-mini", "arcee-ai/modal", "modal"]
        print("\nTrying fallback models...")
        
        for model in fallback_models:
            success = test_chat_completion(model)
            if success:
                print(f"\n✅ Working model found: {model}")
                break
        else:
            print("\n❌ None of the fallback models worked")
