"""
Web interface for the AI-Socratic-Clarifier.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from socratic_clarifier import SocraticClarifier

app = Flask(__name__)
app.config['SECRET_KEY'] = 'socratic-clarifier-key'

# Initialize the clarifier
clarifier = SocraticClarifier()

@app.route('/', methods=['GET'])
def index():
    """Render the main page."""
    return render_template('index.html', modes=clarifier.available_modes())

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text and return results."""
    try:
        # Get the data from the request
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        
        # Set the mode and analyze
        clarifier.set_mode(mode)
        result = clarifier.analyze(text)
        
        # Prepare the response
        response = {
            'text': result.text,
            'issues': [
                {
                    'term': issue.get('term', ''),
                    'issue': issue.get('issue', ''),
                    'description': issue.get('description', ''),
                    'confidence': issue.get('confidence', 0)
                }
                for issue in result.issues
            ],
            'questions': result.questions,
            'reasoning': result.reasoning,
            'sot_paradigm': result.sot_paradigm,
            'confidence': result.confidence
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Record feedback on question effectiveness."""
    try:
        # Get the feedback data
        data = request.get_json()
        question = data.get('question', '')
        helpful = data.get('helpful', False)
        issue_type = data.get('issue_type', '')
        
        # In a real implementation, this would store feedback in a database
        # For this example, we'll just print it
        print(f"Feedback received: Question '{question}' was {'helpful' if helpful else 'not helpful'}")
        print(f"Issue type: {issue_type}")
        
        # Log the feedback (in a real app, save to database)
        feedback_dir = Path(__file__).parent / 'feedback'
        feedback_dir.mkdir(exist_ok=True)
        
        with open(feedback_dir / 'feedback_log.txt', 'a') as f:
            f.write(f"Question: {question}\n")
            f.write(f"Helpful: {helpful}\n")
            f.write(f"Issue Type: {issue_type}\n")
            f.write("-" * 50 + "\n")
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create the templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create the feedback directory if it doesn't exist
    feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)
    
    app.run(debug=True, port=5000)
