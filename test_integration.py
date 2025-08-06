#!/usr/bin/env python3
"""
Integration Tests
================

Test suite for the better-research workflow components.

"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestZoteroSync(unittest.TestCase):
    """Test Zotero synchronization"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'zotero': {
                'library_id': 'test_library',
                'library_type': 'user',
                'api_key': 'test_key',
                'sync_tag': 'test_sync',
                'processed_tag': 'test_processed'
            },
            'folders': {
                'to_read': 'test-to-read'
            }
        }
    
    @patch('zotero_sync.zotero.Zotero')
    def test_zotero_initialization(self, mock_zotero):
        """Test Zotero client initialization"""
        from zotero_sync import ZoteroSync
        
        sync = ZoteroSync(self.test_config)
        
        mock_zotero.assert_called_once_with(
            'test_library', 'user', 'test_key'
        )
        self.assertEqual(sync.sync_tag, 'test_sync')
        self.assertEqual(sync.processed_tag, 'test_processed')
    
    @patch('zotero_sync.zotero.Zotero')
    def test_fetch_tagged_items(self, mock_zotero):
        """Test fetching items with specific tag"""
        from zotero_sync import ZoteroSync
        
        # Mock Zotero client
        mock_client = Mock()
        mock_client.items.return_value = [
            {'key': 'item1', 'data': {'title': 'Test Paper 1'}},
            {'key': 'item2', 'data': {'title': 'Test Paper 2'}}
        ]
        mock_zotero.return_value = mock_client
        
        sync = ZoteroSync(self.test_config)
        items = sync.fetch_tagged_items()
        
        self.assertEqual(len(items), 2)
        mock_client.items.assert_called_once_with(tag='test_sync')


class TestRemarkableSync(unittest.TestCase):
    """Test reMarkable synchronization"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'remarkable': {
                'enabled': True,
                'to_read_folder': 'test-to-read',
                'read_folder': 'test-read'
            },
            'folders': {
                'to_read': 'test-to-read',
                'input': 'test-read'
            }
        }
    
    @patch('remarkable_sync.subprocess.run')
    def test_rmapi_check(self, mock_run):
        """Test rmapi availability check"""
        from remarkable_sync import RemarkableSync
        
        # Mock successful rmapi version check
        mock_run.return_value.returncode = 0
        
        sync = RemarkableSync(self.test_config)
        self.assertTrue(sync._check_rmapi())
        
        mock_run.assert_called_with(
            ['rmapi', 'version'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
    
    @patch('remarkable_sync.subprocess.run')
    def test_rmapi_command(self, mock_run):
        """Test running rmapi commands"""
        from remarkable_sync import RemarkableSync
        
        # Mock rmapi command success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test output"
        mock_run.return_value.stderr = ""
        
        sync = RemarkableSync(self.test_config)
        success, stdout, stderr = sync._run_rmapi_command(['ls'])
        
        self.assertTrue(success)
        self.assertEqual(stdout, "test output")


class TestWorkflowOrchestrator(unittest.TestCase):
    """Test workflow orchestration"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'folders': {
                'to_read': 'test-to-read',
                'input': 'test-read',
                'output': 'test-output'
            },
            'zotero': {
                'library_id': 'test_lib',
                'api_key': 'test_key'
            },
            'remarkable': {
                'enabled': True
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def test_config_loading(self):
        """Test configuration loading"""
        from workflow_orchestrator import WorkflowOrchestrator
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            config_file = f.name
        
        try:
            orchestrator = WorkflowOrchestrator(config_file)
            self.assertEqual(orchestrator.config['folders']['to_read'], 'test-to-read')
        finally:
            os.unlink(config_file)
    
    @patch('workflow_orchestrator.ZoteroSync')
    @patch('workflow_orchestrator.RemarkableSync')
    def test_component_initialization(self, mock_rm_sync, mock_zot_sync):
        """Test initialization of sync components"""
        from workflow_orchestrator import WorkflowOrchestrator
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            config_file = f.name
        
        try:
            orchestrator = WorkflowOrchestrator(config_file)
            
            # Should initialize both components
            mock_zot_sync.assert_called_once()
            mock_rm_sync.assert_called_once()
        finally:
            os.unlink(config_file)


class TestBatchProcessor(unittest.TestCase):
    """Test batch processing functionality"""
    
    def test_config_loading(self):
        """Test configuration loading in batch processor"""
        from batch_processor import load_config
        
        test_config = {
            'ocr_engine': 'tesseract',
            'folders': {
                'input': 'test-read'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            config = load_config(config_file)
            self.assertEqual(config['ocr_engine'], 'tesseract')
        finally:
            os.unlink(config_file)
    
    def test_pdf_file_finding(self):
        """Test finding PDF files in directory"""
        from batch_processor import find_pdf_files
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test PDF files
            pdf1 = Path(temp_dir) / "test1.pdf"
            pdf2 = Path(temp_dir) / "test2.pdf"
            txt_file = Path(temp_dir) / "test.txt"
            
            pdf1.touch()
            pdf2.touch()
            txt_file.touch()
            
            pdf_files = find_pdf_files(temp_dir)
            
            self.assertEqual(len(pdf_files), 2)
            self.assertTrue(any("test1.pdf" in f for f in pdf_files))
            self.assertTrue(any("test2.pdf" in f for f in pdf_files))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def test_folder_structure_creation(self):
        """Test that all necessary folders are created"""
        from batch_processor import ensure_directories
        
        test_config = {
            'folders': {
                'to_read': 'test-to-read',
                'input': 'test-read',
                'output': 'test-output',
                'images': 'test-output/images',
                'markdown': 'test-output/markdown',
                'html': 'test-output/html'
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                ensure_directories(test_config)
                
                # Check that all folders exist
                self.assertTrue(Path('test-to-read').exists())
                self.assertTrue(Path('test-read').exists())
                self.assertTrue(Path('test-output').exists())
                self.assertTrue(Path('test-output/images').exists())
                self.assertTrue(Path('test-output/markdown').exists())
                self.assertTrue(Path('test-output/html').exists())
            finally:
                os.chdir(old_cwd)


def run_tests():
    """Run all tests"""
    print("🧪 Running better-research Test Suite")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestZoteroSync,
        TestRemarkableSync, 
        TestWorkflowOrchestrator,
        TestBatchProcessor,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 40)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
