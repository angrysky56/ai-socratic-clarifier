from setuptools import setup, find_packages

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
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    author="angrysky56",
    author_email="",
    description="An AI-assisted workflow for bias detection, language clarification, and Socratic questioning",
    keywords="nlp, bias-detection, socratic-questioning, sketch-of-thought",
    python_requires=">=3.10",
)
