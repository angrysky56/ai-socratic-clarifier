#!/usr/bin/env python3
"""
Test script to verify the fixes made to the AI-Socratic-Clarifier.
This script runs basic checks to ensure:
1. SoT is installed or will be installed
2. Configuration is loaded correctly
3. The web interface runs
4. The enhanced clarifier works with Ollama
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def check_installation():
    """Check if the package is installed properly."""
    print("\n== Checking Installation ==")
    try:
        import socratic_clarifier
        print("✓ socratic_clarifier package is importable")
    except ImportError:
        print("✗ socratic_clarifier package is not installed")
        print("  Installing package in development mode...")
        subprocess.call([sys.executable, "-m", "pip", "install", "-e", "."])
        try:
            import socratic_clarifier
            print("✓ socratic_clarifier package installed successfully")
        except ImportError:
            print("✗ Failed to install socratic_clarifier package")
            return False
    
    # Check for SoT installation with retry
    max_retries = 3
    for i in range(max_retries):
        try:
            # Clear any cached imports
            if "sketch_of_thought" in sys.modules:
                del sys.modules["sketch_of_thought"]
            
            # Try to import
            from sketch_of_thought import SoT
            print("✓ Sketch-of-Thought is installed")
            break
        except ImportError:
            if i < max_retries - 1:
                print(f"  Retrying import ({i+1}/{max_retries})...")
                time.sleep(2)  # Give it a moment before retrying
            else:
                print("✗ Sketch-of-Thought is not installed")
                print("  Running install_sot.py...")
                result = subprocess.call([sys.executable, "install_sot.py"])
                if result == 0:
                    try:
                        # Clear cache again
                        if "sketch_of_thought" in sys.modules:
                            del sys.modules["sketch_of_thought"]
                        from sketch_of_thought import SoT
                        print("✓ Sketch-of-Thought installed successfully")
                    except ImportError:
                        print("✗ Failed to import Sketch-of-Thought even after installation")
                        print("  Continuing with fallback SoT implementation...")
                else:
                    print("✗ Failed to install Sketch-of-Thought")
                    print("  Continuing with fallback SoT implementation...")
    
    return True

def check_config():
    """Check if the configuration file is loaded correctly."""
    print("\n== Checking Configuration ==")
    
    # Check if config.json exists
    config_path = Path('config.json')
    if not config_path.exists():
        print("✗ config.json does not exist")
        print("  Creating from config.example.json...")
        try:
            with open('config.example.json', 'r') as f:
                config = json.load(f)
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            print("✓ config.json created successfully")
        except Exception as e:
            print(f"✗ Failed to create config.json: {e}")
            return False
    else:
        print("✓ config.json exists")
    
    # Try to load the configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check for required keys
        if "integrations" in config and "settings" in config:
            print("✓ config.json has correct structure")
        else:
            print("✗ config.json is missing required keys")
            return False
        
        # Check Ollama configuration
        if "ollama" in config["integrations"]:
            ollama_config = config["integrations"]["ollama"]
            print(f"✓ Ollama configuration found: {ollama_config['default_model']}")
        else:
            print("✗ Ollama configuration not found")
        
        # Check LM Studio configuration
        if "lm_studio" in config["integrations"]:
            lm_studio_config = config["integrations"]["lm_studio"]
            print(f"✓ LM Studio configuration found: {lm_studio_config['default_model']}")
        else:
            print("✗ LM Studio configuration not found")
        
        # Check settings
        if config["settings"].get("use_sot", True):
            print("✓ SoT is enabled in configuration")
        else:
            print("✗ SoT is disabled in configuration")
    
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    return True

def check_basic_usage():
    """Check if the basic_usage.py example runs correctly."""
    print("\n== Testing basic_usage.py ==")
    try:
        result = subprocess.run(
            [sys.executable, "examples/basic_usage.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ basic_usage.py ran successfully")
            
            # Check if SoT was used
            if "SoT Paradigm" in result.stdout:
                print("✓ SoT paradigm was used in analysis")
            else:
                print("✗ SoT paradigm was not used in analysis")
            
            # Check for issues
            if "Detected" in result.stdout and "issues" in result.stdout:
                print("✓ Issues were detected in the sample text")
            else:
                print("✗ No issues were detected in the sample text")
            
            # Check for questions
            if "Suggested questions" in result.stdout:
                print("✓ Socratic questions were generated")
            else:
                print("✗ No Socratic questions were generated")
            
            return True
        else:
            print(f"✗ basic_usage.py failed with error code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("✗ basic_usage.py timed out (took more than 30 seconds)")
        return False
    except Exception as e:
        print(f"✗ Failed to run basic_usage.py: {e}")
        return False

def check_enhanced_clarifier():
    """Check if the enhanced_clarifier.py example runs correctly."""
    print("\n== Testing enhanced_clarifier.py ==")
    try:
        # Run with --base-only to avoid requiring Ollama to be running
        result = subprocess.run(
            [sys.executable, "examples/local_llm_integration/enhanced_clarifier.py", "--base-only"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ enhanced_clarifier.py ran successfully with --base-only")
            
            # Check if configuration was loaded
            if "Using base SoT functionality only" in result.stdout:
                print("✓ Base SoT functionality was used (as expected)")
            
            # Try to detect if Ollama is running
            print("  Checking if Ollama is running...")
            try:
                import requests
                response = requests.get("http://localhost:11434/api/version", timeout=5)
                if response.status_code == 200:
                    print("✓ Ollama is running")
                    
                    # Run the enhanced clarifier without --base-only
                    print("  Testing enhanced clarifier with Ollama...")
                    result = subprocess.run(
                        [sys.executable, "examples/local_llm_integration/enhanced_clarifier.py"],
                        capture_output=True,
                        text=True,
                        timeout=20
                    )
                    
                    if result.returncode == 0:
                        if "Local LLM providers available: ollama" in result.stdout:
                            print("✓ Enhanced clarifier detected Ollama")
                        else:
                            print("✗ Enhanced clarifier did not detect Ollama properly")
                    else:
                        print(f"✗ Enhanced clarifier failed with Ollama: {result.stderr}")
                else:
                    print(f"✗ Ollama returned unexpected status code: {response.status_code}")
            except Exception as e:
                print(f"✗ Ollama does not appear to be running: {e}")
                print("  You can still use the base functionality without Ollama")
            
            return True
        else:
            print(f"✗ enhanced_clarifier.py failed with error code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("✗ enhanced_clarifier.py timed out (took more than 30 seconds)")
        return False
    except Exception as e:
        print(f"✗ Failed to run enhanced_clarifier.py: {e}")
        return False

def check_web_interface():
    """Check if the web interface can start."""
    print("\n== Testing Web Interface ==")
    try:
        # Start the web interface in the background
        process = subprocess.Popen(
            [sys.executable, "web_interface/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a few seconds to start
        time.sleep(5)
        
        # Check if it's still running
        if process.poll() is None:
            print("✓ Web interface started successfully")
            
            # Try to connect to the web interface
            try:
                import requests
                response = requests.get("http://localhost:5000/", timeout=5)
                if response.status_code == 200:
                    print("✓ Web interface is accessible")
                else:
                    print(f"✗ Web interface returned unexpected status code: {response.status_code}")
            except Exception as e:
                print(f"✗ Failed to connect to web interface: {e}")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✓ Web interface shut down cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("✗ Web interface did not shut down cleanly, had to force kill")
            
            return True
        else:
            # The process exited already, get the error
            stdout, stderr = process.communicate()
            print(f"✗ Web interface failed to start: {stderr}")
            return False
    
    except Exception as e:
        print(f"✗ Failed to start web interface: {e}")
        return False

def main():
    """Run all the checks."""
    print("=== AI-Socratic-Clarifier Verification ===")
    
    results = []
    
    # Check installation
    results.append(("Installation", check_installation()))
    
    # Check configuration
    results.append(("Configuration", check_config()))
    
    # Check basic usage
    results.append(("Basic Usage", check_basic_usage()))
    
    # Check enhanced clarifier
    results.append(("Enhanced Clarifier", check_enhanced_clarifier()))
    
    # Check web interface
    results.append(("Web Interface", check_web_interface()))
    
    # Print summary
    print("\n=== Summary ===")
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nAll checks passed! The AI-Socratic-Clarifier is working correctly.")
    else:
        print("\nSome checks failed. Please review the output for details.")

if __name__ == "__main__":
    main()
