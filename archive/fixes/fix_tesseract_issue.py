#!/usr/bin/env python3
"""
Fix for the TESSERACT_AVAILABLE variable scope issue in multimodal_integration.py
"""

import os
import sys
import subprocess
import shutil

# Check if Tesseract is installed
def check_tesseract():
    try:
        result = subprocess.run(["tesseract", "--version"], 
                               capture_output=True, 
                               text=True)
        if result.returncode == 0:
            version = result.stdout.splitlines()[0] if result.stdout else "Unknown version"
            print(f"✅ Tesseract OCR is installed: {version}")
            return True
        else:
            print("❌ Tesseract OCR is not properly installed")
            print_install_instructions()
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR is not installed")
        print_install_instructions()
        return False

def print_install_instructions():
    print("\nTo install Tesseract OCR:")
    print("- Ubuntu/Debian: sudo apt-get install tesseract-ocr")
    print("- macOS: brew install tesseract")
    print("- Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki")
    print("\nThe application can run without Tesseract, but PDF and image text extraction will be limited.\n")

def fix_multimodal_integration():
    """
    Fix the TESSERACT_AVAILABLE variable scope issue in multimodal_integration.py
    """
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    multimodal_file = os.path.join(base_dir, "multimodal_integration.py")
    backup_file = os.path.join(base_dir, "multimodal_integration.py.bak")
    
    # Backup the original file
    if os.path.exists(multimodal_file):
        print(f"Creating backup of multimodal_integration.py to {backup_file}")
        shutil.copy2(multimodal_file, backup_file)
    
    # Apply the fix
    with open(multimodal_file, 'r') as f:
        content = f.read()
    
    # Check if we need to fix the global scope issue
    if "global TESSERACT_AVAILABLE" not in content:
        print("Fixing TESSERACT_AVAILABLE variable scope issue...")
        
        # Add global declaration in the check_dependencies function
        fixed_content = content.replace(
            "def check_dependencies():",
            "def check_dependencies():\n    global TESSERACT_AVAILABLE, PDF_SUPPORT, CV2_AVAILABLE\n    global pytesseract, Image, pdf2image, cv2"
        )
        
        # Fix the variable declaration at the top
        fixed_content = fixed_content.replace(
            "# Optional imports - will be checked and installed if needed",
            "# Define default globals\nTESSERACT_AVAILABLE = False\nPDF_SUPPORT = False\nCV2_AVAILABLE = False\n\n# Optional imports - will be checked and installed if needed"
        )
        
        # Save the fixed file
        with open(multimodal_file, 'w') as f:
            f.write(fixed_content)
            
        print("✅ Applied fix to multimodal_integration.py")
    else:
        print("TESSERACT_AVAILABLE variable scope issue already fixed")
    
    return True

def main():
    """Main function"""
    print("\n=== Fixing TESSERACT_AVAILABLE variable scope issue ===\n")
    
    # Apply the fix
    fixed = fix_multimodal_integration()
    
    # Check if Tesseract is installed
    has_tesseract = check_tesseract()
    
    print("\n=== Fix applied successfully ===")
    print("\nYou can now run the application using:")
    print("./start_socratic.py")
    
    if not has_tesseract:
        print("\nNote: Tesseract OCR is not installed. PDF and image processing will be limited.")
        print("Consider installing Tesseract OCR using the instructions above.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
