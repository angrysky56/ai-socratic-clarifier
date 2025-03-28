#!/usr/bin/env python3
"""
Debugging script for the AI-Socratic-Clarifier to troubleshoot integration issues.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add the root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_ollama_connectivity():
    """Check if Ollama is running and responsive."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama connection successful")
            print(f"Available models: {[m.get('name') for m in models]}")
            
            # Check if the model in ../../../../../../../../config.json is available
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../../../../config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                default_model = config.get("integrations", {}).get("ollama", {}).get("default_model")
                if default_model:
                    model_available = any(m.get("name") == default_model for m in models)
                    if model_available:
                        print(f"✅ Default model '{default_model}' is available in Ollama")
                    else:
                        print(f"❌ Default model '{default_model}' is NOT available in Ollama")
                        print("Consider updating ../../../../../../../../config.json to use one of the available models")
            
            return True
        else:
            print(f"❌ Ollama API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False

def check_sot_integration():
    """Check if the SoT integration is working."""
    try:
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        sot = SoTIntegration()
        
        if sot.available:
            print("✅ SoT integration is available")
            print(f"Available paradigms: {sot.avaliable_paradigms()}")
            
            # Test classification
            test_text = "Is 2 + 2 equal to 4?"
            paradigm = sot.classify_question(test_text)
            print(f"Test classification: '{test_text}' → {paradigm}")
            
            return True
        else:
            print("❌ SoT integration is not available (model failed to load)")
            return False
    except Exception as e:
        print(f"❌ Error with SoT integration: {e}")
        return False

def apply_direct_fixes():
    """Apply direct fixes to known issues."""
    # Fix 1: Update ../../../../../../../../config.json to ensure the correct model is used
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../../../../../config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get available models from Ollama
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                # Find a suitable model
                default_model = config.get("integrations", {}).get("ollama", {}).get("default_model")
                if default_model not in model_names and model_names:
                    # Update to an available model
                    config["integrations"]["ollama"]["default_model"] = model_names[0]
                    print(f"Updated default model from '{default_model}' to '{model_names[0]}'")
                    
                    # Write updated config
                    with open(config_path, 'w') as f:
                        json.dump(config, f, indent=4)
                    
                    print(f"✅ Updated ../../../../../../../../config.json with available model")
    except Exception as e:
        print(f"❌ Error updating config: {e}")
    
    # Fix 2: Create a direct patch for the app.py integration
    try:
        patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_interface", "direct_integration.py")
        with open(patch_path, 'w') as f:
            f.write("""\"\"\"
Direct integration patch for the AI-Socratic-Clarifier.
This file adds direct integration with Ollama and SoT.
\"\"\"

import requests
import json
import os
import sys
from pathlib import Path

# Add path for SoT integration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def direct_ollama_generate(prompt, model="deepseek-r1:7b", temperature=0.7, max_tokens=512):
    \"\"\"
    Generate text using Ollama directly.
    \"\"\"
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 200:
            return response.json().get("response", ""), response.json()
        else:
            return f"Error: {response.status_code} - {response.text}", {}
    except Exception as e:
        return f"Error: {str(e)}", {}

def direct_ollama_chat(messages, model="deepseek-r1:7b", temperature=0.7, max_tokens=512):
    \"\"\"
    Generate chat response using Ollama directly.
    \"\"\"
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", ""), response.json()
        else:
            return f"Error: {response.status_code} - {response.text}", {}
    except Exception as e:
        return f"Error: {str(e)}", {}

def generate_socratic_questions(text, issues, sot_paradigm=None):
    \"\"\"
    Generate Socratic questions using direct Ollama integration.
    \"\"\"
    # Create a system prompt for the LLM
    system_prompt = \"\"\"
    You are an expert at creating Socratic questions to help improve communication clarity and reduce bias.
    Based on the text and detected issues, generate thought-provoking questions that will help the author clarify their meaning, 
    consider potential biases, and strengthen their reasoning.
    
    Focus on questions that:
    - Ask for clarification of ambiguous terms
    - Challenge biased assumptions
    - Request evidence for unsupported claims
    - Identify logical inconsistencies
    - Encourage deeper reflection
    
    Your questions should be specific to the issues detected and should help improve the text.
    \"\"\"
    
    # Create context from the text and issues
    context = f"Text: \\"{text}\\"\\n\\nDetected issues:\\n"
    for i, issue in enumerate(issues):
        context += f"{i+1}. {issue.get('issue', 'Unknown issue')} - '{issue.get('term', '')}'\\n"
        context += f"   {issue.get('description', '')}\\n"
    
    # Add SoT format instructions if enabled
    if sot_paradigm:
        context += f"\\nGenerate questions using the {sot_paradigm} format. Begin with analyzing the issues, then present 3-5 questions.\\n"
    
    # Create messages for the chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    
    # Generate questions using direct Ollama integration
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json')
    model = "deepseek-r1:7b"  # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
        except:
            pass
    
    generated_text, _ = direct_ollama_chat(messages, model=model)
    
    # Parse the response to extract questions
    questions = []
    for line in generated_text.strip().split("\\n"):
        line = line.strip()
        if line and ("?" in line) and not line.startswith("#") and not line.startswith("<"):
            # Clean up numbering or bullet points
            clean_line = line
            if len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                clean_line = line[3:].strip()
            elif line.startswith('- '):
                clean_line = line[2:].strip()
            
            questions.append(clean_line)
    
    if not questions and sot_paradigm:
        # Fallback question if none were extracted
        questions = [
            "How would you define or quantify the terms in your statement?",
            "What evidence supports your assertion?",
            "Have you considered alternative perspectives to this view?"
        ]
    
    return questions

def direct_analyze_text(text, mode="standard", use_sot=True):
    \"\"\"
    Analyze text using direct Ollama integration and SoT.
    \"\"\"
    # Use Ollama to detect issues
    prompt = f\"\"\"
    Analyze the following text for issues related to clarity, ambiguity, bias, or logical problems:
    
    "{text}"
    
    Identify specific terms or phrases that might be:
    1. Vague or ambiguous
    2. Showing potential bias
    3. Making claims without evidence
    4. Using absolute language
    
    Format your response as JSON with the following structure:
    {{
        "issues": [
            {{
                "term": "specific term or phrase",
                "issue": "type of issue (e.g., vague_term, bias, unsupported_claim)",
                "description": "brief description of the issue",
                "confidence": 0.8  // number between 0 and 1
            }}
        ]
    }}
    
    If no issues are found, return an empty issues array.
    \"\"\"
    
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json')
    model = "deepseek-r1:7b"  # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
        except:
            pass
    
    # Generate issues using direct Ollama integration
    response, _ = direct_ollama_generate(prompt, model=model)
    
    # Extract JSON from response
    try:
        # Find JSON block in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            issues = data.get("issues", [])
        else:
            # Parse manually if no JSON block found
            issues = []
            lines = response.split('\\n')
            for line in lines:
                if ":" in line and ("vague" in line.lower() or "bias" in line.lower() or "ambig" in line.lower()):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        issues.append({
                            "term": parts[0].strip(),
                            "issue": "detected_issue",
                            "description": parts[1].strip(),
                            "confidence": 0.7
                        })
    except:
        # Fallback if JSON parsing fails
        issues = []
    
    # Determine SoT paradigm if enabled
    sot_paradigm = None
    reasoning = None
    
    if use_sot:
        try:
            from socratic_clarifier.integrations.sot_integration import SoTIntegration
            sot = SoTIntegration()
            
            if sot.available:
                # Classify the text
                sot_paradigm = sot.classify_question(text)
                
                # Generate reasoning
                if issues:
                    reasoning = sot.generate_reasoning(text, issues, paradigm=sot_paradigm)
        except:
            # Use a simpler fallback for reasoning
            if "math" in text.lower() or any(c.isdigit() for c in text):
                sot_paradigm = "chunked_symbolism"
            elif any(word in text.lower() for word in ["technical", "medicine", "legal", "expert"]):
                sot_paradigm = "expert_lexicons"
            else:
                sot_paradigm = "conceptual_chaining"
            
            # Generate simple reasoning
            if sot_paradigm == "conceptual_chaining":
                reasoning = "<think>\\n#statement → #analysis → #clarification_needed\\n</think>"
            elif sot_paradigm == "chunked_symbolism":
                reasoning = "<think>\\nclarity = 0.7\\nissues = 0\\nassessment = 'acceptable'\\n</think>"
            elif sot_paradigm == "expert_lexicons":
                reasoning = "<think>\\nstatement(x) → analysis(x) → clarity(x)\\n</think>"
    
    # Generate Socratic questions
    questions = generate_socratic_questions(text, issues, sot_paradigm) if issues else []
    
    # Build the result
    result = {
        "text": text,
        "issues": issues,
        "questions": questions,
        "reasoning": reasoning,
        "sot_paradigm": sot_paradigm,
        "confidence": sum(issue.get("confidence", 0) for issue in issues) / len(issues) if issues else 0.0,
        "sot_enabled": use_sot,
        "model": model,
        "provider": "ollama"
    }
    
    return result
""")
        print(f"✅ Created direct integration patch")
    except Exception as e:
        print(f"❌ Error creating patch: {e}")
    
    # Fix 3: Update app.py to use the direct integration
    try:
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_interface", "app.py")
        
        # Read the current app.py content
        with open(app_path, 'r') as f:
            app_content = f.read()
        
        # Add the import for direct integration if it doesn't exist
        if "import direct_integration" not in app_content:
            import_section = "from flask import Flask, render_template, request, jsonify"
            updated_import = f"{import_section}\nfrom web_interface import direct_integration"
            app_content = app_content.replace(import_section, updated_import)
        
        # Update the chat_message function to use direct integration
        if "@app.route('/chat', methods=['POST'])" in app_content:
            chat_section_start = app_content.find("@app.route('/chat', methods=['POST'])")
            chat_section_end = app_content.find("return jsonify(response)", chat_section_start)
            
            if chat_section_start > 0 and chat_section_end > chat_section_start:
                chat_section = app_content[chat_section_start:chat_section_end + len("return jsonify(response)")]
                
                updated_chat_section = """@app.route('/chat', methods=['POST'])
def chat_message():
    \"\"\"Process a chat message and return a response.\"\"\"
    try:
        # Get the data from the request
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        
        print(f"Received message: '{message}' with mode: {mode}, use_sot: {use_sot}")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(message, mode, use_sot)
        
        # Generate a response based on the analysis
        if result['issues'] and result['questions']:
            # Craft a response that includes one of the Socratic questions
            reply = f"I've analyzed your statement and have some thoughts to share. {result['questions'][0]}"
            
            # If there are more questions, include a followup
            if len(result['questions']) > 1:
                reply += f" I also wonder: {result['questions'][1]}"
        else:
            # Default response if no issues detected
            reply = "I've considered your statement. It seems clear and well-formed. Do you have any other thoughts you'd like to explore?"
        
        # Prepare the response data
        response = {
            'reply': reply,
            'text': message,
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'model': result['model'],
            'provider': result['provider']
        }
        
        return jsonify(response)"""
                
                app_content = app_content.replace(chat_section, updated_chat_section)
        
        # Update the analyze function to use direct integration
        if "@app.route('/analyze', methods=['POST'])" in app_content:
            analyze_section_start = app_content.find("@app.route('/analyze', methods=['POST'])")
            analyze_section_end = app_content.find("return jsonify(response)", analyze_section_start)
            
            if analyze_section_start > 0 and analyze_section_end > analyze_section_start:
                analyze_section = app_content[analyze_section_start:analyze_section_end + len("return jsonify(response)")]
                
                updated_analyze_section = """@app.route('/analyze', methods=['POST'])
def analyze():
    \"\"\"Analyze text and return results.\"\"\"
    try:
        # Get the data from the request
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        
        print(f"Analyzing text: '{text}' with mode: {mode}")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(text, mode)
        
        # Prepare the response
        response = {
            'text': result['text'],
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'provider': result['provider']
        }
        
        return jsonify(response)"""
                
                app_content = app_content.replace(analyze_section, updated_analyze_section)
        
        # Write the updated content back to app.py
        with open(app_path, 'w') as f:
            f.write(app_content)
        
        print(f"✅ Updated app.py to use direct integration")
    except Exception as e:
        print(f"❌ Error updating app.py: {e}")

def main():
    """Main function to run diagnostics and fixes."""
    print("=" * 50)
    print("AI-Socratic-Clarifier Diagnostics")
    print("=" * 50)
    
    # Check Ollama connectivity
    print("\nChecking Ollama connectivity...")
    ollama_ok = check_ollama_connectivity()
    
    # Check SoT integration
    print("\nChecking SoT integration...")
    sot_ok = check_sot_integration()
    
    # Apply fixes if needed
    if not (ollama_ok and sot_ok):
        print("\nApplying direct fixes...")
        apply_direct_fixes()
    
    print("\nDiagnostics complete. Restart the web interface to apply changes.")
    print("=" * 50)

if __name__ == "__main__":
    main()
