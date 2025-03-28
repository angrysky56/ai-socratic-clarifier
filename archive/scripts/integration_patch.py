#!/usr/bin/env python3
"""
Integration patch for the fixed analyzer.
This script creates a backup of the original direct_integration.py file and patches
it to use the new robust analyzer approach.
"""
import os
import sys
import shutil
import re
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTEGRATION_PATH = os.path.join(BASE_DIR, 'web_interface', 'direct_integration.py')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
FIXED_ANALYZER_PATH = os.path.join(BASE_DIR, 'fixed_json_analyzer.py')

def create_backup():
    """Create a backup of the direct_integration.py file."""
    if not os.path.exists(INTEGRATION_PATH):
        print(f"Error: {INTEGRATION_PATH} not found")
        return False
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Create a backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"direct_integration_{timestamp}.py")
    
    try:
        shutil.copy2(INTEGRATION_PATH, backup_path)
        print(f"Backup created at {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def extract_functions_from_file(file_path):
    """Extract functions from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find imports
    import_pattern = r'^import\s+.*$|^from\s+.*$'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    # Find function definitions
    func_pattern = r'^def\s+([a-zA-Z0-9_]+)\s*\(.*?\):\s*(?:""".*?""")?\s*(.*?)(?=^def|\Z)'
    functions = re.findall(func_pattern, content, re.MULTILINE | re.DOTALL)
    
    return imports, functions

def integrate_fixed_analyzer():
    """Integrate the fixed analyzer into direct_integration.py."""
    if not os.path.exists(FIXED_ANALYZER_PATH):
        print(f"Error: {FIXED_ANALYZER_PATH} not found")
        return False
    
    if not create_backup():
        print("Aborting due to backup failure")
        return False
    
    # Extract functions from fixed analyzer
    analyzer_imports, analyzer_functions = extract_functions_from_file(FIXED_ANALYZER_PATH)
    
    # Read the current integration file
    with open(INTEGRATION_PATH, 'r') as f:
        integration_content = f.read()
    
    # Find the direct_analyze_text function
    analyze_pattern = r'def\s+direct_analyze_text\s*\(.*?\):\s*""".*?""".*?(?=def|\Z)'
    analyze_match = re.search(analyze_pattern, integration_content, re.DOTALL)
    
    if not analyze_match:
        print("Error: Could not find direct_analyze_text function")
        return False
    
    # Find the function that implements the new analyzer
    new_analyze_func = None
    for func_name, func_body in analyzer_functions:
        if func_name == 'analyze_text':
            new_analyze_func = func_body
            break
    
    if not new_analyze_func:
        print("Error: Could not find analyze_text function in fixed analyzer")
        return False
    
    # Create the new function
    new_direct_analyze = f"""def direct_analyze_text(text, mode="standard", use_sot=True):
    \"\"\"
    Analyze text using direct Ollama integration and SoT.
    \"\"\"
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json')
    model = "gemma3"  # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
        except:
            pass
    
    print(f"Analyzing text with model: {model}")
    
    # Create prompt and call model - use a robust approach that doesn't rely on JSON
    prompt = create_analysis_prompt(text)
    response, _ = direct_ollama_generate(prompt, model=model, temperature=0.3, max_tokens=800)
    
    # Extract issues using pattern matching instead of JSON
    issues = extract_issues_from_text(response)
    
    # Generate simple questions
    questions = generate_questions(issues, text)
    
    # Determine SoT paradigm if enabled
    sot_paradigm = None
    reasoning = None
    
    if use_sot and issues:  # Only try to use SoT if we actually found issues
        try:
            from socratic_clarifier.integrations.sot_integration import SoTIntegration
            sot = SoTIntegration()
            
            if sot.available:
                # Classify the text
                sot_paradigm = sot.classify_question(text)
                
                # Generate reasoning
                reasoning = sot.generate_reasoning(text, issues, paradigm=sot_paradigm)
                print(f"Generated SoT reasoning with paradigm '{sot_paradigm}'")
        except Exception as e:
            print(f"Error using SoT integration: {e}")
            # No fallback - if it doesn't work, we don't want artificial reasoning
    
    # Build the result
    result = {
        "text": text,
        "issues": issues,
        "questions": questions,
        "reasoning": reasoning,
        "sot_paradigm": sot_paradigm,
        "confidence": sum(issue.get("confidence", 0) for issue in issues) / max(1, len(issues)) if issues else 0.0,
        "sot_enabled": use_sot,
        "model": model,
        "provider": "ollama",
        "reflective_ecosystem_used": REFLECTIVE_ECOSYSTEM_AVAILABLE
    }
    
    return result
"""
    
    # Replace the old function with the new one
    new_integration_content = re.sub(analyze_pattern, new_direct_analyze, integration_content, flags=re.DOTALL)
    
    # Add the helper functions from the fixed analyzer
    helper_funcs = []
    for func_name, func_body in analyzer_functions:
        if func_name in ['create_analysis_prompt', 'extract_issues_from_text', 'generate_questions']:
            helper_funcs.append(f"def {func_name}{func_body}")
    
    # Add the helpers before the direct_analyze_text function
    helper_block = '\n\n'.join(helper_funcs)
    direct_analyze_pos = new_integration_content.find('def direct_analyze_text')
    new_integration_content = (
        new_integration_content[:direct_analyze_pos] + 
        helper_block + 
        '\n\n\n' + 
        new_integration_content[direct_analyze_pos:]
    )
    
    # Write the updated file
    with open(INTEGRATION_PATH, 'w') as f:
        f.write(new_integration_content)
    
    print(f"Successfully patched {INTEGRATION_PATH}")
    return True

if __name__ == "__main__":
    if integrate_fixed_analyzer():
        print("\nIntegration successful!")
        print("You can now restart the application to use the new analyzer.")
    else:
        print("\nIntegration failed. Check the error messages above.")
