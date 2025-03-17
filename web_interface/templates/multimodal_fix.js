/**
 * This script adds a custom handler for the "Analyze in Reflective Ecosystem" button
 * to fix the issue with large URLs. The fix uses a POST request instead.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the analyze text button
    const analyzeTextButton = document.getElementById('analyzeTextButton');
    
    if (analyzeTextButton) {
        // Override the click event
        analyzeTextButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the extracted text
            if (!extractedText) {
                console.error("No text available to analyze");
                return;
            }
            
            // Create a fetch request to the new API endpoint
            fetch('/api/multimodal/analyze-reflective', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: extractedText
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.redirect) {
                    // Redirect to the reflection page
                    window.location.href = data.redirect;
                } else {
                    console.error("Error sending to reflection:", data.error);
                    alert("Error sending text to reflection: " + (data.error || "Unknown error"));
                }
            })
            .catch(error => {
                console.error("Error sending to reflection:", error);
                alert("Error sending text to reflection: " + error.message);
            });
        });
    } else {
        console.warn("Analyze text button not found");
    }
});
