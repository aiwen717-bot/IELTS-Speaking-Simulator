"""
Test script to verify Qwen API connectivity and key validity.
"""
import requests
import json

def test_qwen_api():
    # Read API key from config
    try:
        with open('llm_module/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get('qwen_api_key', '')
        print(f"API Key (first 10 chars): {api_key[:10]}...")
        
        if not api_key:
            print("Error: No API key found in config")
            return False
        
        # Test API call
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "qwen-max",
            "input": {
                "prompt": "Hello, this is a test message."
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        print("Testing API call...")
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("✓ API call successful!")
            return True
        else:
            print("✗ API call failed!")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_alternative_api_format():
    """Test with alternative API format that might be correct for Qwen."""
    try:
        with open('llm_module/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get('qwen_api_key', '')
        
        # Try different header format
        headers = {
            "Content-Type": "application/json",
            "X-DashScope-SSE": "disable",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Try different payload format
        payload = {
            "model": "qwen-max",
            "input": {
                "messages": [
                    {
                        "role": "user", 
                        "content": "Hello, this is a test message."
                    }
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100,
                "result_format": "message"
            }
        }
        
        print("\nTesting alternative API format...")
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("✓ Alternative API format successful!")
            return True
        else:
            print("✗ Alternative API format failed!")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Qwen API connectivity...")
    print("=" * 50)
    
    success1 = test_qwen_api()
    success2 = test_alternative_api_format()
    
    if not success1 and not success2:
        print("\n" + "=" * 50)
        print("Both API formats failed. Possible issues:")
        print("1. Invalid API key")
        print("2. Incorrect API endpoint")
        print("3. Network connectivity issues")
        print("4. API service temporarily unavailable")
        print("\nPlease check your Qwen API key and try again.")
    else:
        print("\n✓ At least one API format worked!")
