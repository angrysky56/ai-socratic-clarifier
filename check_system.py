#!/usr/bin/env python3
"""
Check system setup for AI-Socratic-Clarifier.

This script checks the system setup to ensure everything is configured correctly.
"""

import os
import sys
import importlib
from loguru import logger

def check_imports():
    """Check if required modules can be imported."""
    required_modules = [
        "flask",
        "loguru",
        "requests",
        "PyPDF2",
        "socratic_clarifier",
        "enhanced_integration"
    ]
    
    results = {}
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            results[module] = True
        except ImportError:
            results[module] = False
    
    return results

def check_document_manager():
    """Check if document manager can be initialized."""
    try:
        from enhanced_integration.document_manager import get_document_manager
        manager = get_document_manager()
        return {
            "initialized": True,
            "storage_dir": manager.storage_dir,
            "doc_count": len(manager.get_all_documents())
        }
    except Exception as e:
        return {
            "initialized": False,
            "error": str(e)
        }

def check_multimodal():
    """Check if multimodal integration is available."""
    try:
        from socratic_clarifier.multimodal_integration import check_dependencies
        return {
            "available": True,
            "dependencies": check_dependencies()
        }
    except ImportError:
        try:
            from multimodal_integration import check_dependencies
            return {
                "available": True,
                "dependencies": check_dependencies()
            }
        except ImportError:
            return {
                "available": False,
                "error": "Multimodal integration not available"
            }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }

def check_enhanced_integration():
    """Check if enhanced integration can be initialized."""
    try:
        from enhanced_integration.integration import get_enhanced_enhancer
        enhancer = get_enhanced_enhancer()
        return {
            "initialized": enhancer.initialized
        }
    except Exception as e:
        return {
            "initialized": False,
            "error": str(e)
        }

def check_system():
    """Check the system setup."""
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version.major >= 3 and python_version.minor >= 8
    
    # Check imports
    import_results = check_imports()
    imports_ok = all(import_results.values())
    
    # Check document manager
    doc_manager = check_document_manager()
    doc_manager_ok = doc_manager.get("initialized", False)
    
    # Check multimodal
    multimodal = check_multimodal()
    multimodal_ok = multimodal.get("available", False)
    
    # Check enhanced integration
    enhanced = check_enhanced_integration()
    enhanced_ok = enhanced.get("initialized", False)
    
    # Overall status
    all_ok = python_ok and imports_ok and doc_manager_ok
    
    # Print results
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro} {'✅' if python_ok else '❌'}")
    logger.info(f"Imports: {'✅' if imports_ok else '❌'}")
    
    for module, ok in import_results.items():
        logger.info(f"  - {module}: {'✅' if ok else '❌'}")
    
    logger.info(f"Document manager: {'✅' if doc_manager_ok else '❌'}")
    if doc_manager_ok:
        logger.info(f"  - Storage directory: {doc_manager['storage_dir']}")
        logger.info(f"  - Document count: {doc_manager['doc_count']}")
    else:
        logger.error(f"  - Error: {doc_manager.get('error', 'Unknown error')}")
    
    logger.info(f"Multimodal integration: {'✅' if multimodal_ok else '❌'}")
    if multimodal_ok and "dependencies" in multimodal:
        for dep, ok in multimodal["dependencies"].items():
            logger.info(f"  - {dep}: {'✅' if ok else '❌'}")
    elif not multimodal_ok:
        logger.warning(f"  - Error: {multimodal.get('error', 'Unknown error')}")
    
    logger.info(f"Enhanced integration: {'✅' if enhanced_ok else '❌'}")
    if not enhanced_ok:
        logger.error(f"  - Error: {enhanced.get('error', 'Unknown error')}")
    
    logger.info(f"\nOverall status: {'✅ Ready to run' if all_ok else '❌ Issues found'}")
    
    return all_ok

if __name__ == "__main__":
    try:
        if check_system():
            logger.info("System check completed successfully")
            sys.exit(0)
        else:
            logger.warning("System check completed with issues")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking system: {e}")
        sys.exit(1)
