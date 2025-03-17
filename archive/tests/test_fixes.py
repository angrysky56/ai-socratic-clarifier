#!/usr/bin/env python3
"""
Test script for the AI-Socratic-Clarifier fixes.

This script checks if the fixes have been applied correctly by:
1. Testing if the max_questions parameter is handled properly
2. Checking if the fixed routes files exist
3. Testing if the improved UI template exists
"""

import os
import sys
import importlib.util

def test_max_questions_fix():
    """Test if the max_questions parameter is handled properly in direct_integration.py."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        direct_integration_path = os.path.join(base_dir, "web_interface", "direct_integration.py")
        
        if not os.path.exists(direct_integration_path):
            print("❌ direct_integration.py not found!")
            return False
        
        # Read the file content to check for max_questions parameter
        with open(direct_integration_path, "r") as f:
            content = f.read()
        
        if "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5)" in content:
            print("✅ max_questions parameter found in direct_analyze_text function")
            return True
        else:
            print("❌ max_questions parameter not found in direct_analyze_text function")
            return False
    except Exception as e:
        print(f"❌ Error testing max_questions fix: {e}")
        return False

def test_fixed_routes():
    """Test if the fixed routes files exist."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fixed_multimodal_path = os.path.join(base_dir, "web_interface", "fixed_routes_multimodal.py")
        fixed_reflective_path = os.path.join(base_dir, "web_interface", "fixed_routes_reflective.py")
        
        result = True
        if os.path.exists(fixed_multimodal_path):
            print("✅ fixed_routes_multimodal.py exists")
        else:
            print("❌ fixed_routes_multimodal.py not found")
            result = False
        
        if os.path.exists(fixed_reflective_path):
            print("✅ fixed_routes_reflective.py exists")
        else:
            print("❌ fixed_routes_reflective.py not found")
            result = False
        
        return result
    except Exception as e:
        print(f"❌ Error testing fixed routes: {e}")
        return False

def test_improved_ui():
    """Test if the improved UI template exists."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        improved_template_path = os.path.join(base_dir, "web_interface", "templates", "multimodal_improved.html")
        
        if os.path.exists(improved_template_path):
            print("✅ multimodal_improved.html exists")
            return True
        else:
            print("❌ multimodal_improved.html not found")
            return False
    except Exception as e:
        print(f"❌ Error testing improved UI: {e}")
        return False

def test_app_integration():
    """Test if the app.py file has been updated with the new routes."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, "web_interface", "app.py")
        
        if not os.path.exists(app_path):
            print("❌ app.py not found!")
            return False
        
        # Read the file content to check for blueprint registration
        with open(app_path, "r") as f:
            content = f.read()
        
        result = True
        if "from web_interface.fixed_routes_multimodal import improved_multimodal_bp" in content:
            print("✅ improved_multimodal_bp import found in app.py")
        else:
            print("❌ improved_multimodal_bp import not found in app.py")
            result = False
        
        if "from web_interface.fixed_routes_reflective import fixed_reflective_bp" in content:
            print("✅ fixed_reflective_bp import found in app.py")
        else:
            print("❌ fixed_reflective_bp import not found in app.py")
            result = False
        
        if "app.register_blueprint(improved_multimodal_bp)" in content:
            print("✅ improved_multimodal_bp registration found in app.py")
        else:
            print("❌ improved_multimodal_bp registration not found in app.py")
            result = False
        
        if "app.register_blueprint(fixed_reflective_bp)" in content:
            print("✅ fixed_reflective_bp registration found in app.py")
        else:
            print("❌ fixed_reflective_bp registration not found in app.py")
            result = False
        
        return result
    except Exception as e:
        print(f"❌ Error testing app integration: {e}")
        return False

def main():
    """Run all tests."""
    print("\n=== Testing AI-Socratic-Clarifier Fixes ===\n")
    
    print("Testing max_questions fix...")
    max_questions_result = test_max_questions_fix()
    print()
    
    print("Testing fixed routes...")
    fixed_routes_result = test_fixed_routes()
    print()
    
    print("Testing improved UI...")
    improved_ui_result = test_improved_ui()
    print()
    
    print("Testing app integration...")
    app_integration_result = test_app_integration()
    print()
    
    # Summary
    print("\n=== Summary ===\n")
    print(f"max_questions fix: {'✅ PASS' if max_questions_result else '❌ FAIL'}")
    print(f"Fixed routes: {'✅ PASS' if fixed_routes_result else '❌ FAIL'}")
    print(f"Improved UI: {'✅ PASS' if improved_ui_result else '❌ FAIL'}")
    print(f"App integration: {'✅ PASS' if app_integration_result else '❌ FAIL'}")
    
    all_passed = max_questions_result and fixed_routes_result and improved_ui_result and app_integration_result
    print(f"\nOverall: {'✅ All fixes applied successfully!' if all_passed else '❌ Some fixes are missing or incorrect'}")
    
    if all_passed:
        print("\nYou can now run the application with:")
        print("  python -m web_interface.app")
        print("\nThen access the following URLs:")
        print("  - Original UI (with fixes): http://localhost:5000/multimodal")
        print("  - Improved UI: http://localhost:5000/improved_multimodal")
        print("  - Reflective analysis: http://localhost:5000/reflection")
        print("  - Improved reflective analysis: http://localhost:5000/reflection_improved")
    else:
        print("\nPlease run the fix scripts to apply all fixes:")
        print("  python fix_max_questions.py")
        print("  python fix_reflection_button.py")
        print("  python improved_multimodal_ui.py")
        print("\nOr run them all at once:")
        print("  python apply_all_fixes.py")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
