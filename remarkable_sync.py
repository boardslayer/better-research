#!/usr/bin/env python3
"""
Remarkable Synchronization Module
=================================

This module handles synchronization with reMarkable tablet, specifically:
- Uploads PDFs from 'to-read' folder to reMarkable 'to-read' folder
- Downloads annotated PDFs from reMarkable 'read' folder to local 'read' folder
- Manages sync state and file organization


Requires rmapi to be installed and configured:
- Install: Download from https://github.com/juruen/rmapi/releases or use `go install github.com/juruen/rmapi@latest`
- Setup: Run `rmapi` to authenticate with your reMarkable account

"""

import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
import time

class RemarkableSync:
    """Handles reMarkable tablet synchronization"""
    
    def __init__(self, config: Dict):
        """
        Initialize Remarkable sync with configuration
        
        Args:
            config: Configuration dictionary containing Remarkable settings
        """
        self.config = config
        remarkable_config = config.get('remarkable', {})
        
        # Folder configuration
        folders = config.get('folders', {})
        self.to_read_folder = folders.get('to_read', 'to-read')
        self.read_folder = folders.get('input', 'read')  # This is where processed PDFs go
        
        # Remarkable folder names
        self.rm_to_read_folder = remarkable_config.get('to_read_folder', 'to-read')
        self.rm_read_folder = remarkable_config.get('read_folder', 'read')
        
        # Sync settings
        self.sync_uploads = remarkable_config.get('sync_uploads', True)
        self.sync_downloads = remarkable_config.get('sync_downloads', True)
        self.delete_after_upload = remarkable_config.get('delete_after_upload', False)
        self.delete_after_download = remarkable_config.get('delete_after_download', False)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure local directories exist
        Path(self.to_read_folder).mkdir(parents=True, exist_ok=True)
        Path(self.read_folder).mkdir(parents=True, exist_ok=True)
        
        # Check if rmapi is available
        if not self._check_rmapi():
            raise RuntimeError("rmapi is not available. Please install and configure rmapi.")
    
    def _check_rmapi(self) -> bool:
        """
        Check if rmapi is installed and can connect to reMarkable
        
        Returns:
            True if rmapi is available and connected
        """
        try:
            result = subprocess.run(['rmapi', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_rmapi_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        Run an rmapi command and return result
        
        Args:
            command: List of command arguments
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            self.logger.debug(f"Running rmapi command: {' '.join(command)}")
            result = subprocess.run(['rmapi'] + command, 
                                  capture_output=True, text=True, timeout=60)
            
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            if not success:
                self.logger.error(f"rmapi command failed: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("rmapi command timed out")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Error running rmapi command: {e}")
            return False, "", str(e)
    
    def _ensure_rm_folder_exists(self, folder_name: str) -> bool:
        """
        Ensure a folder exists on reMarkable
        
        Args:
            folder_name: Name of the folder to create
            
        Returns:
            True if folder exists or was created successfully
        """
        # Check if folder already exists
        success, stdout, _ = self._run_rmapi_command(['ls'])
        if success and folder_name in stdout:
            return True
        
        # Create the folder
        self.logger.info(f"Creating reMarkable folder: {folder_name}")
        success, _, _ = self._run_rmapi_command(['mkdir', folder_name])
        return success
    
    def _list_rm_folder_contents(self, folder_name: str) -> List[str]:
        """
        List contents of a reMarkable folder
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            List of file/folder names in the folder
        """
        success, stdout, _ = self._run_rmapi_command(['ls', folder_name])
        if not success:
            return []
        
        # Parse the output - rmapi ls returns lines with file info
        files = []
        for line in stdout.split('\\n'):
            if line.strip() and not line.startswith('total'):
                # Extract filename from ls output (format may vary)
                parts = line.strip().split()
                if parts:
                    filename = parts[-1]  # Last part is usually the filename
                    files.append(filename)
        
        return files
    
    def _get_local_pdf_files(self, folder_path: str) -> List[str]:
        """
        Get list of PDF files in a local folder
        
        Args:
            folder_path: Path to local folder
            
        Returns:
            List of PDF file paths
        """
        folder = Path(folder_path)
        if not folder.exists():
            return []
        
        return [str(f) for f in folder.glob('*.pdf')]
    
    def upload_to_read_files(self) -> int:
        """
        Upload PDF files from local to-read folder to reMarkable to-read folder
        
        Returns:
            Number of successfully uploaded files
        """
        if not self.sync_uploads:
            self.logger.info("Upload sync is disabled")
            return 0
        
        self.logger.info("🔄 Uploading files to reMarkable...")
        
        # Ensure reMarkable to-read folder exists
        if not self._ensure_rm_folder_exists(self.rm_to_read_folder):
            self.logger.error("Failed to create reMarkable to-read folder")
            return 0
        
        # Get local PDF files
        local_files = self._get_local_pdf_files(self.to_read_folder)
        
        if not local_files:
            self.logger.info("No PDF files found in to-read folder")
            return 0
        
        # Get existing files on reMarkable
        rm_files = self._list_rm_folder_contents(self.rm_to_read_folder)
        
        uploaded_count = 0
        
        for file_path in local_files:
            filename = Path(file_path).name
            
            # Skip if file already exists on reMarkable
            if filename in rm_files:
                self.logger.info(f"File already exists on reMarkable: {filename}")
                continue
            
            self.logger.info(f"Uploading: {filename}")
            
            # Upload the file
            success, _, stderr = self._run_rmapi_command([
                'put', file_path, self.rm_to_read_folder
            ])
            
            if success:
                self.logger.info(f"Successfully uploaded: {filename}")
                uploaded_count += 1
                
                # Optionally delete local file after upload
                if self.delete_after_upload:
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Deleted local file: {filename}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete local file {filename}: {e}")
            else:
                self.logger.error(f"Failed to upload {filename}: {stderr}")
            
            # Rate limiting
            time.sleep(1)
        
        self.logger.info(f"Upload complete. Uploaded {uploaded_count} files.")
        return uploaded_count
    
    def download_read_files(self) -> int:
        """
        Download annotated PDF files from reMarkable read folder to local read folder
        
        Returns:
            Number of successfully downloaded files
        """
        if not self.sync_downloads:
            self.logger.info("Download sync is disabled")
            return 0
        
        self.logger.info("🔄 Downloading annotated files from reMarkable...")
        
        # Get files from reMarkable read folder
        rm_files = self._list_rm_folder_contents(self.rm_read_folder)
        
        if not rm_files:
            self.logger.info("No files found in reMarkable read folder")
            return 0
        
        # Get existing local files
        local_files = [Path(f).name for f in self._get_local_pdf_files(self.read_folder)]
        
        downloaded_count = 0
        
        for filename in rm_files:
            # Skip if not a PDF or already exists locally
            if not filename.endswith('.pdf'):
                continue
            
            if filename in local_files:
                self.logger.info(f"File already exists locally: {filename}")
                continue
            
            self.logger.info(f"Downloading: {filename}")
            
            # Create temporary file for download
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Download the file
                success, _, stderr = self._run_rmapi_command([
                    'get', f"{self.rm_read_folder}/{filename}", temp_path
                ])
                
                if success:
                    # Move to final destination
                    final_path = Path(self.read_folder) / filename
                    shutil.move(temp_path, final_path)
                    
                    self.logger.info(f"Successfully downloaded: {filename}")
                    downloaded_count += 1
                    
                    # Optionally delete from reMarkable after download
                    if self.delete_after_download:
                        rm_success, _, _ = self._run_rmapi_command([
                            'rm', f"{self.rm_read_folder}/{filename}"
                        ])
                        if rm_success:
                            self.logger.info(f"Deleted from reMarkable: {filename}")
                        else:
                            self.logger.error(f"Failed to delete from reMarkable: {filename}")
                else:
                    self.logger.error(f"Failed to download {filename}: {stderr}")
                
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}")
            finally:
                # Clean up temp file if it still exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            # Rate limiting
            time.sleep(1)
        
        self.logger.info(f"Download complete. Downloaded {downloaded_count} files.")
        return downloaded_count
    
    def full_sync(self) -> Tuple[int, int]:
        """
        Perform full synchronization: upload to-read files and download read files
        
        Returns:
            Tuple of (uploaded_count, downloaded_count)
        """
        self.logger.info("🚀 Starting full reMarkable sync...")
        
        uploaded = self.upload_to_read_files()
        downloaded = self.download_read_files()
        
        self.logger.info(f"✅ Full sync complete! Uploaded: {uploaded}, Downloaded: {downloaded}")
        return uploaded, downloaded


def main():
    """CLI interface for Remarkable sync"""
    print("📱 reMarkable Synchronization")
    print("=" * 30)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    try:
        # Initialize sync
        sync = RemarkableSync(config)
        
        # Perform sync
        uploaded, downloaded = sync.full_sync()
        
        print("✅ Sync complete!")
        print(f"📤 Uploaded {uploaded} files to reMarkable")
        print(f"📥 Downloaded {downloaded} annotated files")
        
    except Exception as e:
        print("❌ Sync failed: {e}")
        print("💡 Make sure rmapi is installed and configured")


if __name__ == "__main__":
    main()
