"""
Simple FastAPI server for the AI-Socratic-Clarifier.
This demonstrates how to create an API service for the clarifier.
"""

import sys
import os
from typing import List, Optional

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from socratic_clarifier import SocraticClarifier

# Initialize the clarifier
clarifier = SocraticClarifier()

# Define request/response models
class AnalyzeRequest(BaseModel):
    text: str
    mode: Optional[str] = "standard"

class Issue(BaseModel):
    term: str
    issue: str
    description: str
    confidence: float
    span: tuple

class AnalyzeResponse(BaseModel):
    text: str
    issues: List[Issue]
    questions: List[str]
    reasoning: Optional[str] = None
    sot_paradigm: Optional[str] = None
    confidence: float

# Initialize FastAPI
app = FastAPI(
    title="AI-Socratic-Clarifier API",
    description="API for detecting issues and generating Socratic questions",
    version="0.1.0"
)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for issues and generate Socratic questions.
    """
    try:
        # Set the mode based on the request
        clarifier.set_mode(request.mode)
        
        # Analyze the text
        result = clarifier.analyze(request.text)
        
        # Convert to response model
        return AnalyzeResponse(
            text=result.text,
            issues=[Issue(**issue) for issue in result.issues],
            questions=result.questions,
            reasoning=result.reasoning,
            sot_paradigm=result.sot_paradigm,
            confidence=result.confidence
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/modes")
async def get_modes():
    """
    Get a list of available operating modes.
    """
    return {"modes": clarifier.available_modes()}

@app.get("/")
async def root():
    """
    Root endpoint with basic info.
    """
    return {
        "name": "AI-Socratic-Clarifier API",
        "version": "0.1.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This info"},
            {"path": "/analyze", "method": "POST", "description": "Analyze text"},
            {"path": "/modes", "method": "GET", "description": "Get available modes"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
