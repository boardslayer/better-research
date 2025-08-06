#!/usr/bin/env python3
"""
Zotero Synchronization Module
============================

This module handles synchronization with Zotero library, specifically:
- Fetches items tagged with 'rm_to_sync'
- Downloads associated PDFs to the 'to-read' folder
- Manages sync state and removes tags after processing

"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from pyzotero import zotero
import time

class ZoteroSync:
    """Handles Zotero library synchronization"""
    
    def __init__(self, config: Dict):
        """
        Initialize Zotero sync with configuration
        
        Args:
            config: Configuration dictionary containing Zotero settings
        """
        self.config = config
        zotero_config = config.get('zotero', {})
        
        self.library_id = zotero_config.get('library_id')
        self.library_type = zotero_config.get('library_type', 'user')
        self.api_key = zotero_config.get('api_key')
        self.sync_tag = zotero_config.get('sync_tag', 'rm_to_sync')
        self.processed_tag = zotero_config.get('processed_tag', 'rm_processed')
        
        # Initialize folders
        folders = config.get('folders', {})
        self.to_read_folder = folders.get('to_read', 'to-read')
        
        if not all([self.library_id, self.api_key]):
            raise ValueError("Zotero library_id and api_key are required")
        
        # Initialize Zotero client
        self.zot = zotero.Zotero(self.library_id, self.library_type, self.api_key)
        
        # Setup logging
        # Setup logger (let application configure logging)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        Path(self.to_read_folder).mkdir(parents=True, exist_ok=True)
    
    def fetch_tagged_items(self) -> List[Dict]:
        """
        Fetch items from Zotero that are tagged with sync_tag
        
        Returns:
            List of Zotero items with the sync tag
        """
        try:
            self.logger.info(f"Fetching items tagged with '{self.sync_tag}'...")
            items = self.zot.items(tag=self.sync_tag)
            self.logger.info(f"Found {len(items)} items to sync")
            return items
        except Exception as e:
            self.logger.error(f"Error fetching tagged items: {e}")
            return []
    
    def get_item_attachments(self, item_key: str) -> List[Dict]:
        """
        Get attachments for a specific Zotero item
        
        Args:
            item_key: Zotero item key
            
        Returns:
            List of attachment items
        """
        try:
            attachments = self.zot.children(item_key)
            pdf_attachments = [
                att for att in attachments 
                if att['data'].get('contentType') == 'application/pdf'
            ]
            return pdf_attachments
        except Exception as e:
            self.logger.error(f"Error fetching attachments for item {item_key}: {e}")
            return []
    
    def download_attachment(self, attachment: Dict, item_title: str) -> Optional[str]:
        """
        Download a PDF attachment from Zotero
        
        Args:
            attachment: Zotero attachment item
            item_title: Title of the parent item (for filename)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            attachment_key = attachment['key']
            filename = attachment['data'].get('filename', f"{item_title}.pdf")
            
            # Sanitize filename
            filename = self._sanitize_filename(filename)
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            file_path = Path(self.to_read_folder) / filename
            
            # Check if file already exists
            if file_path.exists():
                self.logger.info(f"File already exists: {filename}")
                return str(file_path)
            
            self.logger.info(f"Downloading: {filename}")
            
            # Download the file
            file_content = self.zot.file(attachment_key)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            self.logger.info(f"Successfully downloaded: {filename}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error downloading attachment: {e}")
            return None
    
    def update_item_tags(self, item_key: str, remove_tag: Optional[str] = None, add_tag: Optional[str] = None):
        """
        Update tags for a Zotero item
        
        Args:
            item_key: Zotero item key
            remove_tag: Tag to remove
            add_tag: Tag to add
        """
        try:
            item = self.zot.item(item_key)
            tags = item['data'].get('tags', [])
            
            # Remove specified tag
            if remove_tag:
                tags = [tag for tag in tags if tag.get('tag') != remove_tag]
            
            # Add new tag
            if add_tag:
                if not any(tag.get('tag') == add_tag for tag in tags):
                    tags.append({'tag': add_tag})
            
            # Update the item
            item['data']['tags'] = tags
            self.zot.update_item(item)
            
            self.logger.info(f"Updated tags for item {item_key}")
            
        except Exception as e:
            self.logger.error(f"Error updating tags for item {item_key}: {e}")
    
    def sync_to_read_items(self) -> int:
        """
        Main sync function: fetch tagged items and download PDFs
        
        Returns:
            Number of successfully downloaded files
        """
        items = self.fetch_tagged_items()
        downloaded_count = 0
        
        for item in items:
            try:
                item_key = item['key']
                item_data = item['data']
                item_title = item_data.get('title', f'Item_{item_key}')
                
                self.logger.info(f"Processing item: {item_title}")
                
                # Get PDF attachments
                attachments = self.get_item_attachments(item_key)
                
                if not attachments:
                    self.logger.warning(f"No PDF attachments found for: {item_title}")
                    continue
                
                # Download each PDF attachment
                for attachment in attachments:
                    downloaded_file = self.download_attachment(attachment, item_title)
                    
                    if downloaded_file:
                        downloaded_count += 1
                
                # Update tags: remove sync tag, add processed tag
                self.update_item_tags(
                    item_key, 
                    remove_tag=self.sync_tag, 
                    add_tag=self.processed_tag
                )
                
                # Rate limiting to be nice to Zotero API
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing item {item.get('key', 'unknown')}: {e}")
                continue
        
        self.logger.info(f"Sync complete. Downloaded {downloaded_count} files.")
        return downloaded_count
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename.strip()


def main():
    """CLI interface for Zotero sync"""
    print("🔄 Zotero Synchronization")
    print("=" * 25)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Check if Zotero is configured
    if 'zotero' not in config:
        print("❌ Zotero configuration not found in config.json")
        print("💡 Please add your Zotero settings to the configuration file")
        return
    
    try:
        # Initialize sync
        sync = ZoteroSync(config)
        
        # Perform sync
        downloaded_count = sync.sync_to_read_items()
        
        print(f"\n✅ Sync complete!")
        print(f"📥 Downloaded {downloaded_count} new files to '{sync.to_read_folder}'")
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")


if __name__ == "__main__":
    main()
