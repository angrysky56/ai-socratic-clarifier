#!/usr/bin/env python3
"""
Improved Multimodal Module for the AI-Socratic-Clarifier

This script adds:
1. UI controls for max number of questions
2. Improved question generation through proper SRE (Socratic Reasoning Engine) usage
3. Better error handling and direct use of SRE in the tab
"""

import os
import sys
import shutil
import json

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = file_path + ".bak"
    if os.path.exists(file_path):
        print(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path

def modify_multimodal_template():
    """Modify the multimodal.html template to add max questions control."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "templates", "multimodal.html")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add max questions control after the mode toggle
        if '<div class="mode-toggle">' in content and 'maxQuestionsSlider' not in content:
            # Find mode toggle section
            mode_toggle_section = content.find('<div class="mode-toggle">')
            socratic_mode_end = content.find('</div>', mode_toggle_section)
            socratic_mode_section_end = content.find('</div>', socratic_mode_end + 1)
            
            # Add max questions control
            max_questions_control = """
                            <div class="mt-3" id="socraticOptions" style="display:none;">
                                <label for="maxQuestionsSlider" class="form-label">Maximum Questions: <span id="maxQuestionsValue">5</span></label>
                                <input type="range" class="form-range" min="1" max="10" step="1" value="5" id="maxQuestionsSlider">
                                
                                <div class="form-check mt-2">
                                    <input class="form-check-input" type="checkbox" id="useSreCheckbox" checked>
                                    <label class="form-check-label" for="useSreCheckbox">
                                        Use Socratic Reasoning Engine for improved questions
                                    </label>
                                </div>
                            </div>
"""
            # Insert after the mode toggle
            new_content = content[:socratic_mode_section_end + 1] + max_questions_control + content[socratic_mode_section_end + 1:]
            
            # Add JavaScript to show/hide socratic options based on selected mode
            if "function handleFileSelect()" in new_content:
                # Find where to insert event listeners for mode selection
                process_button_listener_start = new_content.find("// Process button click")
                
                mode_listeners = """
            // Toggle socratic options based on selected mode
            document.querySelectorAll('input[name="analysisMode"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    const socraticOptions = document.getElementById('socraticOptions');
                    if (this.value === 'socratic') {
                        socraticOptions.style.display = 'block';
                    } else {
                        socraticOptions.style.display = 'none';
                    }
                });
            });
            
"""
                new_content = new_content[:process_button_listener_start] + mode_listeners + new_content[process_button_listener_start:]
            
            # Update the FormData to include the max questions and SRE options
            form_data_section = new_content.find("// Create FormData")
            form_data_end = new_content.find("// Send to server", form_data_section)
            
            updated_form_data = """                // Create FormData
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('mode', mode);
                
                // Add socratic options if applicable
                if (mode === 'socratic') {
                    const maxQuestions = document.getElementById('maxQuestionsSlider').value;
                    const useSre = document.getElementById('useSreCheckbox').checked;
                    
                    formData.append('max_questions', maxQuestions);
                    formData.append('use_sre', useSre ? '1' : '0');
                    
                    logToDebug(`Socratic options: maxQuestions=${maxQuestions}, useSre=${useSre}`);
                }
                
"""
            
            new_content = new_content[:form_data_section] + updated_form_data + new_content[form_data_end:]
            
            # Add event listener for the slider
            if "// Toggle debug mode" in new_content:
                debug_toggle_section = new_content.find("// Toggle debug mode")
                
                slider_listener = """            // Max questions slider
            const maxQuestionsSlider = document.getElementById('maxQuestionsSlider');
            const maxQuestionsValue = document.getElementById('maxQuestionsValue');
            
            if (maxQuestionsSlider && maxQuestionsValue) {
                maxQuestionsSlider.addEventListener('input', function() {
                    maxQuestionsValue.textContent = this.value;
                });
            }
            
"""
                new_content = new_content[:debug_toggle_section] + slider_listener + new_content[debug_toggle_section:]
            
            # Write the modified content
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Added max questions control to {file_path}")
            return True
            
        else:
            if 'maxQuestionsSlider' in content:
                print(f"ℹ️ Max questions control already exists in {file_path}")
            else:
                print(f"❌ Could not find mode toggle section in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error modifying {file_path}: {e}")
        # Restore from backup
        backup_path = file_path + ".bak"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
        return False

def modify_routes_multimodal():
    """Modify routes_multimodal.py to use SRE and respect max questions."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "routes_multimodal.py")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add max_questions and use_sre to the process_document function
        if "def process_document():" in content:
            # Look for the socratic mode section
            socratic_mode_section = content.find("elif mode == 'socratic':")
            socratic_mode_end = content.find("# Invalid mode", socratic_mode_section)
            
            # Get the socratic mode section
            socratic_mode_content = content[socratic_mode_section:socratic_mode_end]
            
            # Check if we need to modify it
            if "max_questions" not in socratic_mode_content:
                # Get max questions and SRE parameters
                new_socratic_section = """        elif mode == 'socratic':
            # Socratic analysis mode - first extract text, then analyze
            # Get socratic options from request
            max_questions = int(request.form.get('max_questions', '5'))
            use_sre = request.form.get('use_sre', '1') == '1'
            
            logger.info(f"Socratic analysis with max_questions={max_questions}, use_sre={use_sre}")
            
            result = process_file(file_path, use_multimodal=(mode=='multimodal'))
            
            if not result.get('success', False):
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error extracting text')
                })
            
            # Get the text from OCR or multimodal analysis
            text = result.get('text', '') or result.get('content', '')
            
            if not text.strip():
                return jsonify({
                    'success': False,
                    'error': 'No text could be extracted from the document'
                })
            
            # Analyze the extracted text with Socratic analysis
            try:
                # Pass max_questions and use_sre to direct_analyze_text
                analysis_result = direct_integration.direct_analyze_text(
                    text, 
                    'reflective' if use_sre else 'standard', 
                    use_sre,
                    max_questions=max_questions
                )
                
                return jsonify({
                    'success': True,
                    'text': text,
                    'method': result.get('method', 'ocr+socratic'),
                    'issues': analysis_result.get('issues', []),
                    'questions': analysis_result.get('questions', []),
                    'reasoning': analysis_result.get('reasoning'),
                    'sre_used': use_sre
                })
            except Exception as e:
                logger.error(f"Error in Socratic analysis: {e}")
                return jsonify({
                    'success': False,
                    'text': text,  # Still return the text even if analysis failed
                    'error': f"Error during Socratic analysis: {str(e)}"
                })"""
                
                # Replace the socratic mode section
                new_content = content[:socratic_mode_section] + new_socratic_section + content[socratic_mode_end:]
                
                # Write the modified content
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                print(f"✅ Updated routes_multimodal.py to use SRE and respect max questions")
                return True
            else:
                print(f"ℹ️ routes_multimodal.py already has max_questions support")
                return False
        else:
            print(f"❌ Could not find process_document function in {file_path}")
            return False
        
    except Exception as e:
        print(f"❌ Error modifying {file_path}: {e}")
        # Restore from backup
        backup_path = file_path + ".bak"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
        return False

def modify_direct_integration():
    """Modify direct_integration.py to pass max_questions to analyze_text."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "direct_integration.py")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update the direct_analyze_text function to accept max_questions
        if "def direct_analyze_text(" in content:
            # Find the function definition
            function_start = content.find("def direct_analyze_text(")
            function_end = content.find(")", function_start) + 1
            
            # Check current parameters
            current_params = content[function_start:function_end]
            
            if "max_questions" not in current_params:
                # Update the function signature
                new_signature = current_params.replace("use_sot=True", "use_sot=True, max_questions=None")
                
                # Replace the signature
                new_content = content[:function_start] + new_signature + content[function_end:]
                
                # Find where clarifier.analyze is called
                analyze_call = new_content.find("result = clarifier.analyze(")
                next_line_after_call = new_content.find("\n", analyze_call)
                
                # Find the end of the call, which may span multiple lines
                call_end = -1
                depth = 0
                for i in range(analyze_call, len(new_content)):
                    if new_content[i] == '(':
                        depth += 1
                    elif new_content[i] == ')':
                        depth -= 1
                        if depth == 0:
                            call_end = i + 1
                            break
                
                if call_end > 0:
                    # Extract the current call
                    current_call = new_content[analyze_call:call_end]
                    
                    # Check if we already have max_questions
                    if "max_questions" not in current_call:
                        # Insert max_questions
                        if current_call.endswith(")"):
                            # Add before the final parenthesis
                            new_call = current_call[:-1]
                            
                            # Check if we need to add a comma
                            if not new_call.rstrip().endswith(","):
                                new_call += ","
                            
                            new_call += "\n        max_questions=max_questions)"
                            
                            # Replace the call
                            new_content = new_content[:analyze_call] + new_call + new_content[call_end:]
                            
                            # Find where mode is set
                            mode_section = new_content.find("mode = mode.lower()")
                            if mode_section > 0:
                                next_line_after_mode = new_content.find("\n", mode_section)
                                
                                # Add code to set max_questions in the mode dict
                                max_questions_code = """
    # Set max_questions in the mode dict if provided
    if max_questions is not None:
        mode_config = clarifier.mode_manager.get_mode(mode)
        mode_config['question_limit'] = max_questions"""
                                
                                # Insert after the mode line
                                new_content = new_content[:next_line_after_mode] + max_questions_code + new_content[next_line_after_mode:]
                            
                            # Write the modified content
                            with open(file_path, 'w') as f:
                                f.write(new_content)
                            
                            print(f"✅ Updated direct_integration.py to support max_questions")
                            return True
                    else:
                        print(f"ℹ️ direct_integration.py already has max_questions support")
                        return False
                else:
                    print(f"❌ Could not find analyze call in {file_path}")
                    return False
            else:
                print(f"ℹ️ direct_integration.py already has max_questions parameter")
                return False
        else:
            print(f"❌ Could not find direct_analyze_text function in {file_path}")
            return False
        
    except Exception as e:
        print(f"❌ Error modifying {file_path}: {e}")
        # Restore from backup
        backup_path = file_path + ".bak"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
        return False

def improve_question_quality():
    """Improve the quality of generated questions by enhancing question templates."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "socratic_clarifier", "generators", "question_generator.py")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if we need to improve the templates
        if "# High-quality question templates" not in content:
            # Add improved templates
            improved_templates = """        # High-quality question templates
        self.improved_templates = {
            "vague_term": [
                "Could you elaborate on what specific criteria define '{term}' in this context?",
                "What measurable indicators would help quantify or evaluate '{term}'?",
                "How would experts in this field operationalize the concept of '{term}'?",
                "What precise boundaries or thresholds distinguish '{term}' from related concepts?"
            ],
            "unclear_reference": [
                "Which specific entity or concept does '{term}' refer to in this context?",
                "Could you clarify the exact antecedent of '{term}' for precision?",
                "How would you disambiguate the reference '{term}' to avoid multiple interpretations?",
                "What explicit identification would make the reference '{term}' unambiguous?"
            ],
            "gender_bias": [
                "How might this statement read if we applied it equally across all genders?",
                "What underlying assumptions about gender roles are embedded in this phrasing?",
                "In what ways might this formulation inadvertently reinforce gender stereotypes?",
                "How could this be rephrased to maintain its core meaning while being gender-inclusive?"
            ],
            "stereotype": [
                "What specific evidence supports this generalization beyond anecdotal observation?",
                "How might individual variation within this group contradict this characterization?",
                "What contextual factors might better explain these observed patterns than group identity?",
                "How could this observation be reformulated to acknowledge the diversity within this group?"
            ],
            "non_inclusive": [
                "How might this terminology affect readers from different backgrounds or identities?",
                "What historical context makes this term potentially exclusionary for certain groups?",
                "What more universally accessible language could convey the same concept?",
                "How would you reframe this point using terminology that acknowledges diverse perspectives?"
            ],
            "absolute_statement": [
                "Under what specific conditions or circumstances might exceptions to this statement exist?",
                "What degree of certainty would be appropriate to assign to this claim based on available evidence?",
                "How might this statement be qualified to acknowledge potential limitations or exceptions?",
                "What evidence would be required to justify the absolute nature of this claim?"
            ],
            "unsupported_claim": [
                "What empirical evidence would strengthen the foundation of this assertion?",
                "How might this claim be revised to reflect the current state of evidence?",
                "What methodologies could be employed to test the validity of this claim?",
                "What specific sources or data points would need to be cited to substantiate this position?"
            ],
            "normative_statement": [
                "What underlying values or principles inform this normative judgment?",
                "How might this evaluation differ based on alternative ethical frameworks?",
                "How could this normative claim be distinguished from an empirical observation?",
                "What criteria are being applied to make this value judgment?"
            ]
        }"""
            
            # Add the improved templates before the SoT structures
            sot_structures_section = content.find("# SoT paradigm-specific question structures")
            
            new_content = content[:sot_structures_section] + improved_templates + "\n        \n        " + content[sot_structures_section:]
            
            # Update the generate method to use the improved templates
            generate_method = new_content.find("def generate(self, text: str, issues: List[Dict[str, Any]],")
            if generate_method > 0:
                # Find where the templates are selected
                templates_selection = new_content.find("# Get templates for this issue type", generate_method)
                
                if templates_selection > 0:
                    templates_if_section_end = new_content.find("if issue_type in self.templates:", templates_selection)
                    templates_if_block_end = new_content.find("else:", templates_if_section_end)
                    
                    if templates_if_section_end > 0 and templates_if_block_end > 0:
                        # Create improved code for template selection
                        improved_template_code = """                # Get templates for this issue type
                if issue_type in self.improved_templates and mode.get("question_style", "neutral") == "precise":
                    # Use high-quality templates for precise question style
                    templates = self.improved_templates[issue_type]
                elif issue_type in self.templates:
                    # Use standard templates
                    templates = self.templates[issue_type]"""
                        
                        # Replace the template selection code
                        new_content = new_content[:templates_selection] + improved_template_code + new_content[templates_if_block_end:]
                        
                        # Write the modified content
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        
                        print(f"✅ Improved question templates in {file_path}")
                        return True
            
            print(f"❌ Could not update templates in {file_path}")
            return False
        else:
            print(f"ℹ️ Question templates already improved in {file_path}")
            return False
        
    except Exception as e:
        print(f"❌ Error modifying {file_path}: {e}")
        # Restore from backup
        backup_path = file_path + ".bak"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
        return False

def main():
    """Main function to apply all improvements."""
    print("\n=== Improving Multimodal Analysis ===\n")
    
    # 1. Add max questions control to the UI
    ui_updated = modify_multimodal_template()
    
    # 2. Update routes to respect max_questions and use SRE
    routes_updated = modify_routes_multimodal()
    
    # 3. Update direct_integration to support max_questions
    integration_updated = modify_direct_integration()
    
    # 4. Improve question quality
    questions_improved = improve_question_quality()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"✓ Added max questions UI control: {'Yes' if ui_updated else 'No'}")
    print(f"✓ Updated routes for SRE: {'Yes' if routes_updated else 'No'}")
    print(f"✓ Updated integration for max questions: {'Yes' if integration_updated else 'No'}")
    print(f"✓ Improved question quality: {'Yes' if questions_improved else 'No'}")
    
    # Instructions
    print("\n=== Instructions ===")
    print("1. Restart the server: ./start_socratic.py")
    print("2. Go to the multimodal interface")
    print("3. Upload a PDF or image")
    print("4. Select 'Socratic Analysis' mode")
    print("5. Adjust the 'Maximum Questions' slider to your preferred number")
    print("6. Make sure 'Use Socratic Reasoning Engine' is checked")
    print("7. Process the document")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
