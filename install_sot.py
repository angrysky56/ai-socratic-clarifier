"""
Helper script to install Sketch-of-Thought from GitHub.
"""

import os
import subprocess
import sys
import site
import importlib

def install_sot():
    """
    Clone and install the Sketch-of-Thought package.
    """
    print("Installing Sketch-of-Thought...")
    
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Git not found. Please install Git and try again.")
        return False
    
    # Create a temporary directory with a unique name
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="sot_", dir=os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Clone the repository
        print("Cloning Sketch-of-Thought repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/SimonAytes/SoT.git", os.path.join(tmp_dir, "SoT")],
            check=True
        )
        
        # Install the package
        print("Installing Sketch-of-Thought package...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", os.path.join(tmp_dir, "SoT")],
            check=True
        )
        
        # Force a reload of site packages to ensure the newly installed package is available
        importlib.reload(site)
        
        # Verify the installation
        try:
            importlib.import_module("sketch_of_thought")
            print("Sketch-of-Thought installed and verified successfully!")
            return True
        except ImportError:
            print("Warning: Sketch-of-Thought was installed but could not be imported.")
            print("You may need to restart your Python interpreter or adjust your PYTHONPATH.")
            print(f"The package was installed to: {os.path.join(tmp_dir, 'SoT')}")
            # Return True anyway as the installation did complete
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"Error installing Sketch-of-Thought: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = install_sot()
    sys.exit(0 if success else 1)
