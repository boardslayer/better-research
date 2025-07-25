#!/usr/bin/env python3
"""
Setup and Installation Helper
============================

This script helps set up the better-research environment with all dependencies
and initial configuration.

"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("🔬 better-research Setup")
    print("=" * 30)
    print("Setting up your research workflow environment...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_rmapi():
    """Check if rmapi is available"""
    print("🔍 Checking for rmapi...")
    try:
        result = subprocess.run(["rmapi", "version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ rmapi is installed and available")
            return True
        else:
            print("⚠️ rmapi is installed but may not be configured")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ rmapi not found")
        print("💡 Install with: pip install rmapi")
        print("💡 Then run: rmapi (for first-time setup)")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    dirs = ["to-read", "read", "output", "output/images", "output/markdown", "output/html"]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_name}/")
    
    print("✅ Directories created")

def create_sample_config():
    """Create a sample configuration file"""
    print("⚙️ Creating sample configuration...")
    
    sample_config = {
        "ocr_engine": "tesseract",
        "mathpix": {
            "app_id": "YOUR_MATHPIX_APP_ID",
            "app_key": "YOUR_MATHPIX_APP_KEY"
        },
        "tesseract": {
            "enabled": True,
            "language": "eng"
        },
        "extraction": {
            "extract_highlights": True,
            "extract_handwriting": True
        },
        "folders": {
            "to_read": "to-read",
            "input": "read",
            "output": "output",
            "images": "output/images",
            "markdown": "output/markdown",
            "html": "output/html"
        },
        "output": {
            "generate_html": True,
            "generate_markdown": True
        },
        "image_processing": {
            "max_size": 1024,
            "quality": 95
        },
        "zotero": {
            "library_id": "YOUR_LIBRARY_ID",
            "library_type": "user",
            "api_key": "YOUR_API_KEY",
            "sync_tag": "rm_to_sync",
            "processed_tag": "rm_processed"
        },
        "remarkable": {
            "enabled": True,
            "to_read_folder": "to-read",
            "read_folder": "read",
            "sync_uploads": True,
            "sync_downloads": True,
            "delete_after_upload": False,
            "delete_after_download": False
        },
        "logging": {
            "level": "INFO"
        }
    }
    
    # Check if config already exists
    if Path("config.json").exists():
        print("⚠️ config.json already exists - creating config.sample.json")
        config_file = "config.sample.json"
    else:
        config_file = "config.json"
    
    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"✅ Configuration created: {config_file}")
    return config_file

def print_next_steps(config_file):
    """Print next steps for user"""
    print()
    print("🎉 Setup Complete!")
    print("=" * 20)
    print()
    print("📋 Next Steps:")
    print()
    print("1. Configure your integrations:")
    print(f"   • Edit {config_file}")
    print("   • Add your Zotero API credentials")
    print("   • Add your Mathpix credentials (if using)")
    print()
    print("2. Set up reMarkable sync:")
    print("   • Run: rmapi (for first-time authentication)")
    print("   • Test: rmapi ls")
    print()
    print("3. Test the workflow:")
    print("   • Tag some papers in Zotero with 'rm_to_sync'")
    print("   • Run: python workflow_orchestrator.py --full")
    print()
    print("📚 Documentation:")
    print("   • docs/WORKFLOW_GUIDE.md - Complete workflow guide")
    print("   • docs/ZOTERO_SETUP.md - Zotero configuration")
    print("   • docs/REMARKABLE_SETUP.md - reMarkable setup")
    print()
    print("🚀 Quick commands:")
    print("   python workflow_orchestrator.py --full")
    print("   python workflow_orchestrator.py --steps zotero")
    print("   python batch_processor.py")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    print()
    
    # Install requirements
    if not install_requirements():
        return 1
    
    print()
    
    # Check rmapi
    check_rmapi()
    
    print()
    
    # Create directories
    create_directories()
    
    print()
    
    # Create config
    config_file = create_sample_config()
    
    # Print next steps
    print_next_steps(config_file)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
