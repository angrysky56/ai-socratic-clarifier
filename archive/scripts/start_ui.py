#!/usr/bin/env python3
"""
Starter script for the AI-Socratic-Clarifier web interface.
This ensures all necessary components are running before starting the web interface.
"""

import os
import sys
import time
import platform
import subprocess
import signal
import atexit
import json
from pathlib import Path

# Add the root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_ollama():
    """Check if Ollama is running and has the required models."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            print(f"Ollama is running with the following models:")
            for name in model_names:
                print(f"  - {name}")
            
            # Check for essential models from config
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                default_model = config.get("integrations", {}).get("ollama", {}).get("default_model")
                embedding_model = config.get("integrations", {}).get("ollama", {}).get("default_embedding_model")
                
                if default_model and default_model not in model_names:
                    print(f"Warning: Default model '{default_model}' not found in Ollama.")
                    print("Available models:", ", ".join(model_names))
                
                if embedding_model and embedding_model not in model_names:
                    print(f"Warning: Embedding model '{embedding_model}' not found in Ollama.")
                    print("Available models:", ", ".join(model_names))
            
            return True
        else:
            print(f"Ollama API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking Ollama: {e}")
        return False

def start_web_interface():
    """Start the Flask web interface."""
    try:
        print("Starting web interface...")
        web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_interface")
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=web_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True
        )
        
        print("Web interface starting. Please wait...")
        time.sleep(2)
        
        return process
    except Exception as e:
        print(f"Error starting web interface: {e}")
        return None

def cleanup_processes(processes):
    """Clean up child processes on exit."""
    for process in processes:
        if process and process.poll() is None:
            try:
                if platform.system() == 'Windows':
                    process.terminate()
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"Terminated process {process.pid}")
            except Exception as e:
                print(f"Error terminating process: {e}")

def main():
    """Main function to start all components."""
    processes = []
    
    # Register cleanup function
    atexit.register(cleanup_processes, processes)
    
    # Check if Ollama is running
    if not check_ollama():
        print("Warning: Ollama is not running or accessible. The clarifier will use fallback mechanisms.")
        choice = input("Do you want to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting...")
            return
    
    # Start web interface
    web_process = start_web_interface()
    if web_process:
        processes.append(web_process)
        
        # Print the URL
        print("\n" + "="*50)
        print("Web interface available at: http://localhost:5000")
        print("="*50 + "\n")
        
        # Monitor the web interface process
        try:
            while True:
                line = web_process.stdout.readline()
                if not line and web_process.poll() is not None:
                    break
                if line:
                    print(line.strip())
        except KeyboardInterrupt:
            print("\nStopping services...")
        finally:
            cleanup_processes(processes)
    else:
        print("Failed to start web interface.")
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
