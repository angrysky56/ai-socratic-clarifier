import random
import requests
from socratic_clarifier import SocraticClarifier

class ReflectiveWrapper:
    """
    A wrapper to integrate Symbiotic Reflective Ecosystem (SRE) with AI-Socratic-Clarifier.
    This module dynamically adjusts bias detection, questioning depth, and reasoning coherence
    using resonance-based feedback loops, with web API integration for live interactions.
    """
    
    def __init__(self, clarifier: SocraticClarifier, api_url="http://localhost:8000/analyze"):
        self.clarifier = clarifier
        self.api_url = api_url  # Web API endpoint for live interaction
        self.global_resonance = 1.0  # Initial resonance level for coherence tracking
        self.feedback_sensitivity = 0.5  # Adjusts adaptively based on detected issues
        self.multimodal_enabled = True  # Enable multimodal analysis
    
    def analyze(self, text: str, image_path=None, mode="standard"):
        """
        Enhanced analysis method incorporating resonance-based adjustments and optional multimodal input.
        """
        result = self.clarifier.analyze(text)
        
        if self.multimodal_enabled and image_path:
            multimodal_result = self._analyze_multimodal(text, image_path)
            result.questions.extend(multimodal_result.questions)
        
        self._apply_resonance_modulation(result)
        return result
    
    def analyze_with_api(self, text: str, mode="standard"):
        """
        Sends a request to the web API for live analysis and integrates resonance-based reasoning.
        """
        try:
            response = requests.post(self.api_url, json={"text": text, "mode": mode})
            if response.status_code == 200:
                result = response.json()
                self._apply_resonance_modulation(result)
                return result
            else:
                print(f"Error: API request failed with status {response.status_code}")
                return None
        except Exception as e:
            print(f"Error connecting to API: {e}")
            return None
    
    def _apply_resonance_modulation(self, result):
        """
        Adjust questioning depth and bias detection thresholds based on coherence resonance.
        """
        issue_resonance = [issue['confidence'] for issue in result.get('issues', [])]
        avg_resonance = sum(issue_resonance) / len(issue_resonance) if issue_resonance else 1.0
        
        stability = abs(avg_resonance - self.global_resonance)
        self.feedback_sensitivity = 0.3 if stability > 0.1 else 0.7
        
        for i, question in enumerate(result.get('questions', [])):
            weight = random.uniform(0.5, 1.5)  # Introduce variability in questioning strength
            if stability > 0.15:
                result['questions'][i] = f"(Deeper Inquiry) {question}"
            elif stability < 0.05:
                result['questions'][i] = f"(Surface Inquiry) {question}"
        
        self.global_resonance = avg_resonance
    
    def _analyze_multimodal(self, text, image_path):
        """
        Placeholder function for multimodal analysis.
        Future implementation should use image-text coherence verification.
        """
        print(f"Processing image at {image_path} for contextual coherence...")
        multimodal_questions = [
            "How does the visual information support or contradict the statement?",
            "Are there any biases present in the image that reflect on the text?"
        ]
        return type("MultimodalResult", (object,), {"questions": multimodal_questions})()
    
    def feedback_loop(self, user_feedback: dict):
        """
        Adjust system behavior based on user feedback on question effectiveness.
        """
        helpful = user_feedback.get('helpful', False)
        if not helpful:
            self.global_resonance *= 0.9  # Reduce resonance if feedback suggests low accuracy
        else:
            self.global_resonance = min(1.0, self.global_resonance * 1.1)
        
        print(f"Updated Global Resonance: {self.global_resonance}")

# Usage Example
if __name__ == "__main__":
    clarifier = SocraticClarifier(mode="academic")
    reflective_clarifier = ReflectiveWrapper(clarifier)
    
    text = "Men are better leaders than women."
    image_path = "example_chart.png"
    result = reflective_clarifier.analyze_with_api(text)
    if result:
        print(result['questions'])
