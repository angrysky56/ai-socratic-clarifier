#!/usr/bin/env python3
"""
Start script for the AI-Socratic-Clarifier with direct model integration.
This ensures everything is properly connected and working.
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
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../../../../config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                default_model = config.get("integrations", {}).get("ollama", {}).get("default_model")
                embedding_model = config.get("integrations", {}).get("ollama", {}).get("default_embedding_model")
                
                if default_model and default_model not in model_names:
                    print(f"Warning: Default model '{default_model}' not found in Ollama.")
                    print("Available models:", ", ".join(model_names))
                    
                    # Try to update config with an available model
                    if model_names:
                        config["integrations"]["ollama"]["default_model"] = model_names[0]
                        with open(config_path, 'w') as f:
                            json.dump(config, f, indent=4)
                        print(f"Updated config to use '{model_names[0]}' as default model.")
                
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

def ensure_direct_integration():
    """Ensure the direct integration file exists."""
    direct_integration_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_interface", "direct_integration.py")
    
    if not os.path.exists(direct_integration_path):
        print("Direct integration file not found. Running diagnostics...")
        
        # Run the diagnostics script which will create the necessary files
        diagnostics_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debugging.py")
        subprocess.run([sys.executable, diagnostics_path], check=True)
        
        # Verify the file was created
        if os.path.exists(direct_integration_path):
            print("Direct integration file created successfully.")
            return True
        else:
            print("Failed to create direct integration file.")
            return False
    
    return True

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
        print("Warning: Ollama is not running or accessible. The clarifier will not function properly.")
        choice = input("Do you want to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting...")
            return
    
    # Ensure direct integration
    if not ensure_direct_integration():
        print("Warning: Direct integration setup failed. The web interface may not function properly.")
        choice = input("Do you want to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting...")
            return
    
    # Test SoT integration
    try:
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        sot = SoTIntegration()
        if sot.available:
            print("SoT integration is available and working.")
        else:
            print("SoT integration loaded but not available. Will use fallback mechanisms.")
    except ImportError:
        print("SoT integration could not be imported. Will use fallback mechanisms.")
    
    # Start web interface
    web_process = start_web_interface()
    if web_process:
        processes.append(web_process)
        
        # Print the URL
        print("\n" + "="*50)
        print("Web interface available at: http://localhost:5000")
        print("Chat interface at: http://localhost:5000/chat")
        print("Reflection interface at: http://localhost:5000/reflection")
        print("="*50 + "\n")
        
        # Monitor the web interface process
        try:
            while True:
                line = web_process.stdout.readline()
                if not line and web_process.poll() is not None:
                    break
                if line:
                    print(line.strip())
                
                # Check for errors
                error = web_process.stderr.readline()
                if error:
                    print(f"ERROR: {error.strip()}")
        except KeyboardInterrupt:
            print("\nStopping services...")
        finally:
            cleanup_processes(processes)
    else:
        print("Failed to start web interface.")
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
