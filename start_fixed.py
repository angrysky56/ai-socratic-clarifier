#!/usr/bin/env python3
"""
Simplified startup script for AI-Socratic-Clarifier.
This avoids all MCP dependencies and uses direct Ollama integration.
"""

import os
import sys
import subprocess

def main():
    """
    Start the application with the right environment variables.
    """
    print("=" * 50)
    print("AI-Socratic-Clarifier - Fixed Startup")
    print("=" * 50)
    
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = os.path.join("web_interface", "app.py")
    env["FLASK_RUN_PORT"] = "5001"  # Use a different port to avoid conflicts
    
    # Set the working directory
    print(f"Starting web interface on port 5001...")
    
    # Build the command
    cmd = [sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
    
    # Start the process
    try:
        subprocess.run(cmd, cwd=base_dir, env=env)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
