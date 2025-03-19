#!/usr/bin/env python3
"""
Test file for advanced_rag_fix.py.
This script tests the individual functions of the advanced_rag_fix.py to ensure they work correctly.
"""

import os
import sys
import unittest
from unittest import mock

# Add parent directory to path so we can import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import functions to test
from advanced_rag_fix import (
    backup_file,
    update_config_for_advanced_rag,
    fix_direct_integration,
    enhance_document_rag_routes,
    update_multimodal_integration,
    create_advanced_rag_readme
)

class TestAdvancedRagFix(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for test files
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_rag_fix_temp')
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        # Clean up temp files if they exist
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
    
    def test_backup_file(self):
        """Test that backup_file creates a backup correctly."""
        # Create a test file
        test_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('Test content')
        
        # Mock the function to use our test directory
        with mock.patch('advanced_rag_fix.backup_file', return_value=f"{test_file}.advanced_rag_bak"):
            # Call the function
            backup_path = backup_file(test_file)
            
            # Check that backup was created
            self.assertEqual(backup_path, f"{test_file}.advanced_rag_bak")
            self.assertTrue(os.path.exists(backup_path))
    
    def test_create_advanced_rag_readme(self):
        """Test that the README is created correctly."""
        # Mock the open function to write to our test directory
        readme_path = os.path.join(self.test_dir, 'ADVANCED_RAG_README.md')
        
        # Use a context manager to patch open
        with mock.patch('builtins.open', mock.mock_open()) as mocked_open:
            with mock.patch('advanced_rag_fix.os.path.join', return_value=readme_path):
                result = create_advanced_rag_readme()
                
                # Check that the function returned success
                self.assertTrue(result)
                
                # Check that open was called with the right path
                mocked_open.assert_called_once_with(readme_path, 'w')
                
                # Check that write was called (content is long, so just check a substring)
                handle = mocked_open()
                handle.write.assert_called_once()
                self.assertIn("Advanced RAG Integration", handle.write.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
