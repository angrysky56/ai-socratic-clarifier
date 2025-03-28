#!/usr/bin/env python3
"""
Simple direct test of Ollama API without any complex processing.
"""
import requests
import json
import os

def main():
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '../../../../../../../../config.json')
    model = "gemma3"  # Default
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
    except Exception as e:
        print(f"Error loading config: {e}")
    
    print(f"Using model: {model}")
    
    # Simple prompt
    prompt = "Analyze this text: 'Cheese is the best food.'\nList any issues with this statement."
    
    print("Calling Ollama chat API...")
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        # Save raw response
        with open("/tmp/simple_chat_response.txt", "wb") as f:
            f.write(response.content)
        
        print(f"Raw response saved to /tmp/simple_chat_response.txt")
        
        # Try to parse as JSON
        try:
            data = response.json()
            print("Successfully parsed response as JSON")
            print(f"Keys in response: {list(data.keys())}")
            
            # Extract content
            if "message" in data and "content" in data["message"]:
                print("\nContent from model:")
                print("-" * 40)
                print(data["message"]["content"])
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("\nFirst 500 characters of raw response:")
            print("-" * 40)
            print(response.text[:500])
    
    except Exception as e:
        print(f"Error calling Ollama API: {e}")

if __name__ == "__main__":
    main()
