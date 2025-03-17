# Debugging "Analyze in Reflective Ecosystem" Button Issue

This document explains the debugging process and the solution for the internal server error when clicking the "Analyze in Reflective Ecosystem" button in the multimodal interface.

## Problem Identified

When trying to use the "Analyze in Reflective Ecosystem" button after analyzing a PDF, an "internal server error" occurs. There are several issues that cause this:

1. The original URL parameter approach exceeded URL length limits when passing large text content
2. The updated form POST approach encounters a server-side error due to:
   - An incorrect URL route redirect (`url_for('reflection')` doesn't exist - should be `url_for('reflective.reflection_page')`)
   - Missing robust error handling in the route handler
   - Potential session configuration issues 

## Key Fixes Applied

The following fixes address the issues:

### 1. Fixed incorrect redirect URL in routes_reflective.py

```python
# Fixed:
return redirect(url_for('reflective.reflection_page'))

# Instead of:
return redirect(url_for('reflection'))
```

### 2. Added extensive error handling in routes_reflective.py

```python
@reflective_bp.route('/reflection', methods=['GET', 'POST'])
def reflection_page():
    try:
        # Handle request...
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in reflection_page: {e}\n{error_traceback}")
        return f"<h1>Error</h1><p>An error occurred: {e}</p><pre>{error_traceback}</pre>", 500
```

### 3. Added session debug route and better debugging

```python
@reflective_bp.route('/api/reflective/debug', methods=['GET'])
def debug_session():
    """Debug route to check session configuration."""
    try:
        # Test setting a value in session
        session['test_key'] = 'test_value'
        
        # Return session info
        return jsonify({
            'success': True,
            'session_working': True,
            'session_keys': list(session.keys()),
            'test_value': session.get('test_key')
        })
    except Exception as e:
        # Error handling...
```

### 4. Updated the templates to show debugging information

Modified both the multimodal.html and reflection.html templates to show more helpful error information and debug data.

## How to Apply the Fixes

You can apply the fixes in several ways:

1. **Automatic fix**: Run the fix_reflection_route.py script:
   ```bash
   python fix_reflection_route.py
   ```

2. **Manual fix**: Manually apply the changes to:
   - web_interface/routes_reflective.py
   - web_interface/templates/multimodal.html
   - web_interface/templates/reflection.html

3. **Restart the server**: After applying the fixes, restart the application:
   ```bash
   ./start_socratic.py
   ```

## Technical Details

### Session Storage

The fix leverages Flask's session to store the extracted text temporarily, which has several advantages:
- Not limited by URL length restrictions
- More secure than URL parameters
- Persists between requests

The internal server error occurred because the reflection route was inconsistently implemented between app.py and routes_reflective.py, resulting in incorrect URL generation.

### Testing the Fix

After applying the fixes, you can test if the session is working properly by accessing:
```
http://localhost:5000/api/reflective/debug
```

This should return a JSON response indicating if the session is working properly.
