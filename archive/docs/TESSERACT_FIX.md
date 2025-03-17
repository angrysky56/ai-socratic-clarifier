# Fixing the TESSERACT_AVAILABLE Error

## Issue

The error `Error processing document: cannot access local variable 'TESSERACT_AVAILABLE' where it is not associated with a value` occurs in the multimodal integration module. This is a Python variable scope issue where the `TESSERACT_AVAILABLE` variable is being modified within the `check_dependencies()` function but is not properly declared as global.

## The Fix

The fix involves two main changes to the `multimodal_integration.py` file:

1. Define the global variables at the module level with default values:
   ```python
   # Define default globals
   TESSERACT_AVAILABLE = False
   PDF_SUPPORT = False
   CV2_AVAILABLE = False
   ```

2. Properly declare the variables as global within the `check_dependencies()` function:
   ```python
   def check_dependencies():
       global TESSERACT_AVAILABLE, PDF_SUPPORT, CV2_AVAILABLE
       global pytesseract, Image, pdf2image, cv2
       # Rest of the function...
   ```

## How to Apply the Fix

We've provided a simple script to apply this fix automatically:

```bash
./fix_tesseract_issue.py
```

This script will:
1. Back up your original `multimodal_integration.py` file
2. Apply the necessary changes to fix the variable scope issue
3. Check if Tesseract OCR is installed on your system

After running this fix, you can continue to use the application normally with `./start_socratic.py`.

## Additional Dependencies

For full PDF and image processing capabilities, you need:

1. **Tesseract OCR**:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`
   - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

2. **Poppler** (for PDF processing):
   - Ubuntu/Debian: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`
   - Windows: Download from [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/)

The application will work without these dependencies, but PDF and image processing capabilities will be limited.
