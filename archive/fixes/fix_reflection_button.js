/**
 * Fix for the "Analyze in Reflective Ecosystem" button in the multimodal interface
 * 
 * This script fixes the issue where large text content from PDFs breaks
 * the URL when passed as a parameter. It replaces the direct URL navigation
 * with a POST request that stores the text in the session.
 * 
 * Add this script to the multimodal.html template by adding:
 * <script src="/static/fix_reflection_button.js"></script>
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find the Analyze in Reflective Ecosystem button
    const analyzeTextButton = document.getElementById('analyzeTextButton');
    
    if (analyzeTextButton) {
        console.log('Found Analyze in Reflective Ecosystem button - applying fix');
        
        // Override the click event to use AJAX POST instead of direct URL
        analyzeTextButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Define extractedText if it's not already in scope
            // In the original code, this is a global variable defined in multimodal.html
            const extractedText = window.extractedText || document.getElementById('textOutput').textContent;
            
            if (!extractedText || extractedText.trim() === '') {
                console.error('No text available to analyze');
                return;
            }
            
            console.log('Sending text to reflection API via POST');
            
            // Create a form to submit the text via POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/reflection';
            form.style.display = 'none';
            
            // Add the text as a form field
            const textField = document.createElement('input');
            textField.type = 'hidden';
            textField.name = 'text';
            textField.value = extractedText;
            form.appendChild(textField);
            
            // Add form to document and submit
            document.body.appendChild(form);
            form.submit();
        });
    } else {
        console.warn('Analyze in Reflective Ecosystem button not found');
    }
});
