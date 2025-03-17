"""
Setup script for the AI-Socratic-Clarifier package.
"""

from setuptools import setup, find_packages

setup(
    name="socratic_clarifier",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "ollama>=0.1.0",
        "loguru>=0.6.0",
        "pillow>=8.0.0",
        "pytesseract>=0.3.8",
        "transformers>=4.20.0",
        "pdf2image>=1.16.0",
        "werkzeug>=2.0.0",
        "requests>=2.25.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
        "rag": [
            "faiss-cpu",
            "sentence-transformers",
        ],
    },
    entry_points={
        "console_scripts": [
            "socratic-clarifier=socratic_clarifier.cli:main",
        ],
    },
    author="AngrySkySix",
    author_email="angrysky56@github.com",
    description="A tool for analyzing statements through a Socratic lens",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/angrysky56/ai-socratic-clarifier",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
