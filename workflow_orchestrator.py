#!/usr/bin/env python3
"""
Research Workflow Orchestrator
=============================

This module orchestrates the complete research workflow:
1. Sync from Zotero (download tagged PDFs to to-read folder)
2. Upload to reMarkable (sync to-read folder)
3. Download from reMarkable (sync annotated PDFs to read folder)
4. Process annotations (batch OCR and generate markdown/HTML)

This provides a complete end-to-end solution for managing research papers
from library to annotated output.

"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys
import time

# Import our sync modules
try:
    from zotero_sync import ZoteroSync
    from remarkable_sync import RemarkableSync
    from batch_processor import load_config, ensure_directories, process_all_pdfs
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all required modules are available")
    sys.exit(1)

class WorkflowOrchestrator:
    """Orchestrates the complete research workflow"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the workflow orchestrator
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
        # Setup logging
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize sync components
        self.zotero_sync = None
        self.remarkable_sync = None
        
        self._initialize_components()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _initialize_components(self):
        """Initialize sync components based on configuration"""
        # Initialize Zotero sync if configured
        if 'zotero' in self.config:
            try:
                self.zotero_sync = ZoteroSync(self.config)
                self.logger.info("✅ Zotero sync initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Zotero sync initialization failed: {e}")
        
        # Initialize Remarkable sync if configured
        if 'remarkable' in self.config or self.config.get('remarkable', {}).get('enabled', True):
            try:
                self.remarkable_sync = RemarkableSync(self.config)
                self.logger.info("✅ reMarkable sync initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ reMarkable sync initialization failed: {e}")
    
    def step1_zotero_sync(self) -> int:
        """
        Step 1: Sync from Zotero library
        
        Returns:
            Number of files downloaded from Zotero
        """
        self.logger.info("🔄 Step 1: Syncing from Zotero...")
        
        if not self.zotero_sync:
            self.logger.warning("⚠️ Zotero sync not available - skipping")
            return 0
        
        try:
            downloaded = self.zotero_sync.sync_to_read_items()
            self.logger.info(f"✅ Zotero sync complete: {downloaded} files downloaded")
            return downloaded
        except Exception as e:
            self.logger.error(f"❌ Zotero sync failed: {e}")
            return 0
    
    def step2_remarkable_upload(self) -> int:
        """
        Step 2: Upload to reMarkable
        
        Returns:
            Number of files uploaded to reMarkable
        """
        self.logger.info("📤 Step 2: Uploading to reMarkable...")
        
        if not self.remarkable_sync:
            self.logger.warning("⚠️ reMarkable sync not available - skipping")
            return 0
        
        try:
            uploaded = self.remarkable_sync.upload_to_read_files()
            self.logger.info(f"✅ reMarkable upload complete: {uploaded} files uploaded")
            return uploaded
        except Exception as e:
            self.logger.error(f"❌ reMarkable upload failed: {e}")
            return 0
    
    def step3_remarkable_download(self) -> int:
        """
        Step 3: Download annotated files from reMarkable
        
        Returns:
            Number of annotated files downloaded
        """
        self.logger.info("📥 Step 3: Downloading annotated files from reMarkable...")
        
        if not self.remarkable_sync:
            self.logger.warning("⚠️ reMarkable sync not available - skipping")
            return 0
        
        try:
            downloaded = self.remarkable_sync.download_read_files()
            self.logger.info(f"✅ reMarkable download complete: {downloaded} files downloaded")
            return downloaded
        except Exception as e:
            self.logger.error(f"❌ reMarkable download failed: {e}")
            return 0
    
    def step4_batch_processing(self) -> bool:
        """
        Step 4: Process annotations with OCR and generate outputs
        
        Returns:
            True if batch processing succeeded
        """
        self.logger.info("🔧 Step 4: Processing annotations...")
        
        try:
            # Ensure directories exist
            ensure_directories(self.config)
            
            # Run batch processing
            process_all_pdfs(self.config)
            
            self.logger.info("✅ Batch processing complete")
            return True
        except Exception as e:
            self.logger.error(f"❌ Batch processing failed: {e}")
            return False
    
    def run_full_workflow(self) -> Dict[str, int]:
        """
        Run the complete workflow from start to finish
        
        Returns:
            Dictionary with step results
        """
        self.logger.info("🚀 Starting complete research workflow...")
        
        results = {
            'zotero_downloads': 0,
            'remarkable_uploads': 0, 
            'remarkable_downloads': 0,
            'batch_processing': False
        }
        
        # Step 1: Zotero sync
        results['zotero_downloads'] = self.step1_zotero_sync()
        
        # Wait a bit between steps
        time.sleep(2)
        
        # Step 2: Upload to reMarkable
        results['remarkable_uploads'] = self.step2_remarkable_upload()
        
        # Step 3: Download from reMarkable (may not have new files immediately)
        results['remarkable_downloads'] = self.step3_remarkable_download()
        
        # Step 4: Process annotations
        results['batch_processing'] = self.step4_batch_processing()
        
        # Print summary
        self._print_workflow_summary(results)
        
        return results
    
    def run_partial_workflow(self, steps: list) -> Dict[str, int]:
        """
        Run specific steps of the workflow
        
        Args:
            steps: List of step names to run
        
        Returns:
            Dictionary with step results
        """
        self.logger.info(f"🔄 Running partial workflow: {', '.join(steps)}")
        
        results = {
            'zotero_downloads': 0,
            'remarkable_uploads': 0,
            'remarkable_downloads': 0,
            'batch_processing': False
        }
        
        if 'zotero' in steps:
            results['zotero_downloads'] = self.step1_zotero_sync()
            time.sleep(1)
        
        if 'upload' in steps:
            results['remarkable_uploads'] = self.step2_remarkable_upload()
            time.sleep(1)
        
        if 'download' in steps:
            results['remarkable_downloads'] = self.step3_remarkable_download()
            time.sleep(1)
        
        if 'process' in steps:
            results['batch_processing'] = self.step4_batch_processing()
        
        self._print_workflow_summary(results)
        return results
    
    def _print_workflow_summary(self, results: Dict):
        """Print a summary of workflow results"""
        print("\\n" + "="*50)
        print("📊 WORKFLOW SUMMARY")
        print("="*50)
        print(f"🔄 Zotero Downloads:      {results['zotero_downloads']}")
        print(f"📤 reMarkable Uploads:    {results['remarkable_uploads']}")
        print(f"📥 reMarkable Downloads:  {results['remarkable_downloads']}")
        print(f"🔧 Batch Processing:      {'✅ Success' if results['batch_processing'] else '❌ Failed'}")
        print("="*50)
        
        # Get folder info for reference
        folders = self.config.get('folders', {})
        print(f"📁 Folders:")
        print(f"   • To-Read: {folders.get('to_read', 'to-read')}")
        print(f"   • Read:    {folders.get('input', 'read')}")
        print(f"   • Output:  {folders.get('output', 'output')}")
        print("="*50)


def main():
    """CLI interface for the workflow orchestrator"""
    parser = argparse.ArgumentParser(
        description="Research Workflow Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --full                    # Run complete workflow
  %(prog)s --steps zotero upload     # Run only Zotero sync and upload
  %(prog)s --steps download process  # Run only download and processing
  %(prog)s --config my_config.json   # Use custom config file
        """
    )
    
    parser.add_argument('--config', '-c', 
                       default='config.json',
                       help='Configuration file path (default: config.json)')
    
    parser.add_argument('--full', '-f',
                       action='store_true',
                       help='Run the complete workflow')
    
    parser.add_argument('--steps', '-s',
                       nargs='+',
                       choices=['zotero', 'upload', 'download', 'process'],
                       help='Run specific workflow steps')
    
    args = parser.parse_args()
    
    # Print header
    print("🔬 Research Workflow Orchestrator")
    print("=" * 40)
    
    try:
        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(args.config)
        
        # Run workflow
        if args.full:
            orchestrator.run_full_workflow()
        elif args.steps:
            orchestrator.run_partial_workflow(args.steps)
        else:
            print("❌ Please specify --full or --steps")
            parser.print_help()
            return 1
        
        print("\\n✅ Workflow completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
