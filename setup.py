from setuptools import setup, find_packages
import os
import subprocess
import sys

def install_sot():
    """Install Sketch-of-Thought package after the main package installation."""
    try:
        print("Installing Sketch-of-Thought (SoT)...")
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install_sot.py')
        if os.path.exists(script_path):
            subprocess.check_call([sys.executable, script_path])
            print("SoT installation completed successfully.")
            return True
        else:
            print(f"SoT installation script not found at {script_path}")
            return False
    except Exception as e:
        print(f"Error installing SoT: {e}")
        return False

# Custom install command that runs install_sot after the standard install
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        install.run(self)  # Run the standard install
        install_sot()      # Install SoT

# Custom develop command that runs install_sot after the standard develop
from setuptools.command.develop import develop

class CustomDevelop(develop):
    def run(self):
        develop.run(self)  # Run the standard develop
        install_sot()      # Install SoT

setup(
    name="socratic_clarifier",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "numpy>=1.20.0",
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "flask>=2.0.0",
        "requests>=2.25.0",
        "uvicorn>=0.15.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    cmdclass={
        'install': CustomInstall,
        'develop': CustomDevelop,
    },
    author="angrysky56",
    author_email="",
    description="An AI-assisted workflow for bias detection, language clarification, and Socratic questioning",
    keywords="nlp, bias-detection, socratic-questioning, sketch-of-thought",
    python_requires=">=3.10",
)
