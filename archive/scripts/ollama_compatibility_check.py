#!/usr/bin/env python3
"""
Simple script to check Ollama API compatibility.
This helps identify which API endpoints are available and functional.
"""

import os
import sys
import json
import requests
import time

def load_config():
    """Load configuration from the config file."""
    config_path = os.path.join(os.path.dirname(__file__), '../../../../../../../../config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Configuration file not found at {config_path}")
            return {}
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def check_ollama_version():
    """Check Ollama version and capabilities."""
    config = load_config()
    base_url = config.get("integrations", {}).get("ollama", {}).get("base_url", "http://localhost:11434/api")
    
    if not base_url.endswith("/api"):
        base_url += "/api"
    
    base_url_without_api = base_url.replace("/api", "")
    
    print(f"Checking Ollama compatibility at: {base_url}")
    print("-" * 60)
    
    # Define endpoints to check
    endpoints = [
        {"name": "List Models", "url": f"{base_url}/tags", "method": "GET", "data": None},
        {"name": "Health Check", "url": f"{base_url_without_api}/", "method": "GET", "data": None},
        {"name": "Generate Test", "url": f"{base_url}/generate", "method": "POST", 
         "data": {"model": "gemma3", "prompt": "Say hello", "max_tokens": 10}},
        {"name": "Chat API Test", "url": f"{base_url}/chat", "method": "POST",
         "data": {"model": "gemma3", "messages": [{"role": "user", "content": "Say hello"}]}},
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint['name']}...")
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=5)
            else:  # POST
                response = requests.post(endpoint['url'], json=endpoint['data'], timeout=10)
            
            status = response.status_code
            supported = status < 400  # Consider 4xx and 5xx as errors
            
            if supported:
                print(f"  ✅ Success: Status code {status}")
                try:
                    response_json = response.json()
                    print(f"  Response contains {len(response_json)} keys: {', '.join(response_json.keys())}")
                    
                    # Special case for models listing
                    if endpoint["name"] == "List Models" and "models" in response_json:
                        models = response_json.get("models", [])
                        if models:
                            print(f"  Available models: {', '.join(model['name'] for model in models[:5])}")
                            if len(models) > 5:
                                print(f"  ...and {len(models) - 5} more")
                except:
                    print("  Could not parse response as JSON")
            else:
                print(f"  ❌ Failed: Status code {status}")
                print(f"  Response: {response.text[:100]}...")
            
            results[endpoint['name']] = {
                "supported": supported,
                "status": status,
                "response_snippet": response.text[:100] if not supported else ""
            }
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results[endpoint['name']] = {
                "supported": False,
                "error": str(e)
            }
    
    print("\nSummary:")
    print("-" * 60)
    for name, result in results.items():
        if result.get("supported", False):
            print(f"✅ {name}: Supported")
        else:
            print(f"❌ {name}: Not supported - {result.get('error', f'Status {result.get('status', 'unknown')}')}")
    
    # Recommend the best API to use
    print("\nRecommendation:")
    print("-" * 60)
    if results.get("Chat API Test", {}).get("supported", False):
        print("✅ Use the Chat API for best results")
    elif results.get("Generate Test", {}).get("supported", False):
        print("✅ Use the Generate API (Chat API not available)")
    else:
        print("❌ No working API endpoints found - check your Ollama installation")
    
    # Return working APIs
    return {
        "chat_supported": results.get("Chat API Test", {}).get("supported", False),
        "generate_supported": results.get("Generate Test", {}).get("supported", False),
        "models": results.get("List Models", {}).get("supported", False)
    }

if __name__ == "__main__":
    check_ollama_version()
