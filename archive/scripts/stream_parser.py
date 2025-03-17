#!/usr/bin/env python3
"""
Utility script to parse streaming responses from Ollama API correctly.
"""
import json
import requests
import os

def parse_streamed_json(response_text):
    """
    Parse streamed JSON responses from Ollama.
    
    Ollama can return multiple JSON objects separated by newlines in streaming mode.
    This function combines them properly to extract the full message content.
    
    Args:
        response_text: Raw response text from Ollama API
        
    Returns:
        Extracted content or raw text if parsing fails
    """
    # Save the raw response for debugging
    with open("/tmp/raw_streamed_response.txt", "w") as f:
        f.write(response_text)
    
    # Check if the response is empty
    if not response_text.strip():
        return "Empty response"
        
    try:
        # Try to split by newlines - the response may be a series of JSON objects
        json_strings = [line for line in response_text.split("\n") if line.strip()]
        
        if not json_strings:
            return "No valid JSON lines found"
        
        # For chat API responses
        accumulated_content = ""
        for json_str in json_strings:
            try:
                chunk = json.loads(json_str)
                if "message" in chunk and "content" in chunk["message"]:
                    accumulated_content += chunk["message"]["content"]
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                print(f"Skipping invalid JSON: {json_str[:50]}...")
        
        if accumulated_content:
            return accumulated_content
        
        # If chat API format didn't work, try the /generate format
        accumulated_content = ""
        for json_str in json_strings:
            try:
                chunk = json.loads(json_str)
                if "response" in chunk:
                    accumulated_content += chunk["response"]
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                pass
        
        if accumulated_content:
            return accumulated_content
        
        # If we still don't have content, try the last JSON object which might be complete
        try:
            last_chunk = json.loads(json_strings[-1])
            
            # For chat API
            if "message" in last_chunk and "content" in last_chunk["message"]:
                return last_chunk["message"]["content"]
                
            # For generate API
            if "response" in last_chunk:
                return last_chunk["response"]
        except:
            pass
            
        # If all else fails, return the raw response
        return response_text
        
    except Exception as e:
        print(f"Error parsing streamed response: {e}")
        return response_text

def test_streaming_parser():
    """Test the streaming parser with the Ollama API."""
    # Simple test to see if we can parse a streamed response
    model = "gemma3"
    prompt = "Analyze this text: 'Cheese is the best food.' List any issues with this statement."
    
    print(f"Testing with model: {model}")
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    # Try chat API
    try:
        print("Testing chat API...")
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False  # Explicitly disable streaming
            },
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        # Parse the response
        content = parse_streamed_json(response.text)
        
        print("\nParsed content:")
        print("-" * 40)
        print(content)
        
    except Exception as e:
        print(f"Error testing chat API: {e}")
    
    # Try generate API
    try:
        print("\nTesting generate API...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False  # Explicitly disable streaming
            },
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        # Parse the response
        content = parse_streamed_json(response.text)
        
        print("\nParsed content:")
        print("-" * 40)
        print(content)
        
    except Exception as e:
        print(f"Error testing generate API: {e}")

if __name__ == "__main__":
    test_streaming_parser()
