#!/usr/bin/env python3
"""
AI-Socratic-Clarifier - Simple Startup Script

This script starts the AI-Socratic-Clarifier web UI with all necessary components.
It performs basic checks to ensure Ollama is running and provides a clean interface
for launching the application.
"""

import os
import sys
import json
import time
import requests
import subprocess
import traceback
from pathlib import Path

def print_banner():
    """Display a nice banner at startup."""
    banner = """
    ╔═════════════════════════════════════════════════════╗
    ║             AI-Socratic-Clarifier                   ║
    ╚═════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Check if the environment is properly set up."""
    # Check if we're in the right directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {base_dir}")
    
    # Check if venv is active
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("Warning: Virtual environment is not active.")
        venv_path = os.path.join(base_dir, "venv")
        
        if os.path.exists(venv_path):
            print(f"A virtual environment exists at {venv_path}")
            print("You may want to activate it with:")
            
            if os.name == 'nt':  # Windows
                print(f"    {venv_path}\\Scripts\\activate")
            else:  # Linux/Mac
                print(f"    source {venv_path}/bin/activate")
        else:
            print("No virtual environment found. You might want to create one with:")
            print("    python -m venv venv")
    else:
        print(f"Virtual environment active: {sys.prefix}")
    
    # Check if ../../../../../../../../config.json exists
    config_path = os.path.join(base_dir, "../../../../../../../../config.json")
    if not os.path.exists(config_path):
        print("Warning: ../../../../../../../../config.json not found. Creating default configuration...")
        
        default_config = {
            "integrations": {
                "ollama": {
                    "enabled": True,
                    "base_url": "http://localhost:11434/api",
                    "api_key": None,
                    "default_model": "gemma3",
                    "default_embedding_model": "nomic-embed-text:latest",
                    "timeout": 60
                }
            },
            "settings": {
                "prefer_provider": "auto",
                "use_llm_questions": True,
                "use_llm_reasoning": True,
                "use_sot": True,
                "use_multimodal": True
            }
        }
        
        # Save the default config
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print("Created default configuration file.")
        except Exception as e:
            print(f"Error creating default configuration: {e}")
    else:
        print("Config file found.")

def check_ollama():
    """Check if Ollama is running and has the required models."""
    print("\nChecking Ollama...")
    try:
        # Load the config to get the model name
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../../../../config.json")
        model_name = "gemma3"  # Default fallback
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                model_name = config.get("integrations", {}).get("ollama", {}).get("default_model", model_name)
        
        # Check if Ollama API is responsive
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            print(f"✅ Ollama is running with {len(model_names)} models")
            
            # Check if our configured model is available
            if model_name in model_names:
                print(f"✅ Required model '{model_name}' is available")
            else:
                print(f"⚠️ Warning: Configured model '{model_name}' not found!")
                print(f"Available models: {', '.join(model_names[:5])}" + 
                      ("..." if len(model_names) > 5 else ""))
                
                if model_names:
                    # Ask if user wants to update the config
                    print("\nWould you like to update the configuration to use an available model?")
                    for i, name in enumerate(model_names[:5]):
                        print(f"{i+1}. {name}")
                    
                    choice = input("Enter number (or any other key to skip): ")
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(model_names[:5]):
                            # Update the config
                            config["integrations"]["ollama"]["default_model"] = model_names[idx]
                            with open(config_path, 'w') as f:
                                json.dump(config, f, indent=4)
                            print(f"✅ Updated configuration to use '{model_names[idx]}'")
                    except:
                        print("Continuing with current configuration...")
            
            return True
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running or not accessible at http://localhost:11434")
        print("   Please make sure Ollama is installed and running.")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def start_web_interface():
    """Start the Flask web interface."""
    # Build the command
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = os.path.join("web_interface", "app.py")
    
    # If we're in a virtual environment, use its Python
    if sys.prefix != sys.base_prefix:
        python_exec = os.path.join(sys.prefix, "bin", "python")
        if os.name == 'nt':  # Windows
            python_exec = os.path.join(sys.prefix, "Scripts", "python.exe")
    else:
        python_exec = sys.executable
    
    # Check if the flask module is available
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask is not installed. Attempting to install...")
        try:
            subprocess.run([python_exec, "-m", "pip", "install", "flask"], check=True)
            print("✅ Flask installed successfully")
        except Exception as e:
            print(f"❌ Error installing Flask: {e}")
            return False
    
    print("\n🚀 Starting web interface...")
    try:
        cmd = [python_exec, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
        
        process = subprocess.Popen(
            cmd,
            cwd=base_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for a moment to see if the server starts
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is not None:
            print("❌ Failed to start web interface")
            stdout, stderr = process.communicate()
            print("Output:")
            print(stdout)
            print("Error:")
            print(stderr)
            return False
        
        print("✅ Web server started successfully")
        print("\n" + "="*50)
        print("🌐 Web interface available at: http://localhost:5000")
        print("🔍 Chat interface at: http://localhost:5000/chat")
        print("🧠 Reflection interface at: http://localhost:5000/reflection")
        print("="*50 + "\n")
        
        # Monitor the process output
        try:
            while True:
                # Check stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    print(stdout_line.strip())
                
                # Check stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    print(f"ERROR: {stderr_line.strip()}")
                
                # If both are empty and process has ended, break
                if not stdout_line and not stderr_line and process.poll() is not None:
                    break
                
                # Small delay to reduce CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print_banner()
    
    # Check environment
    check_environment()
    
    # Check if Ollama is running
    ollama_running = check_ollama()
    if not ollama_running:
        print("\n⚠️ Warning: Ollama is not running or not properly configured.")
        choice = input("Do you want to continue anyway? (y/n): ")
        if choice.lower() != 'y':
            print("👋 Exiting...")
            return
    
    # Start the web interface
    started = start_web_interface()
    
    if not started:
        print("\n❌ Failed to start the web interface.")
        print("Please check the error messages above for more information.")
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
