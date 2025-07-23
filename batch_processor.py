#!/usr/bin/env python3
"""
Batch PDF Processor
==================

This script processes multiple PDF files from the 'read' folder, extracts highlights and annotations,
runs OCR, and organizes outputs into separate folders.

"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
import subprocess
import sys

def load_config(config_file: str = "config.json") -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        raise

def find_pdf_files(input_dir: str) -> List[str]:
    """Find all PDF files in the input directory"""
    pdf_files = []
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return []
    
    for file in input_path.glob("*.pdf"):
        pdf_files.append(str(file))
    
    return sorted(pdf_files)

def ensure_directories(config: Dict):
    """Ensure all required directories exist"""
    folders = config.get('folders', {})
    
    dirs_to_create = [
        folders.get('output', 'output'),
        folders.get('images', 'output/images'),
        folders.get('markdown', 'output/markdown'),
        folders.get('html', 'output/html')
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Ensured directory exists: {dir_path}")

def extract_pdf_images(pdf_path: str, config: Dict) -> str:
    """Extract images from a single PDF file"""
    pdf_name = Path(pdf_path).stem
    images_base_dir = config.get('folders', {}).get('images', 'output/images')
    output_dir = os.path.join(images_base_dir, pdf_name)
    
    print(f"🔍 Extracting from: {pdf_path}")
    print(f"📁 Output directory: {output_dir}")
    
    # Import and run the extraction function
    try:
        # Add current directory to path to import the extraction module
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from extracting_highlights_images import extract_highlights_and_red_annotations
        
        extracted_items = extract_highlights_and_red_annotations(pdf_path, output_dir, config)
        
        print(f"✅ Extracted {len(extracted_items)} items from {pdf_name}")
        return output_dir
        
    except Exception as e:
        print(f"❌ Error extracting from {pdf_path}: {e}")
        return ""

def run_ocr_on_images(images_dir: str, pdf_name: str, config: Dict):
    """Run OCR on extracted images and save results to organized folders"""
    if not os.path.exists(images_dir) or not os.listdir(images_dir):
        print(f"⚠️  No images found in {images_dir}")
        return
    
    ocr_engine = config.get('ocr_engine', 'tesseract').lower()
    
    # Import the unified OCR processor functions
    try:
        from unified_ocr_processor import process_images_with_ocr, generate_markdown, generate_html
        
        print(f"🔍 Running {ocr_engine.upper()} OCR on {pdf_name}...")
        
        # Process images with OCR
        results = process_images_with_ocr(images_dir, config)
        
        if not results:
            print(f"❌ No OCR results for {pdf_name}")
            return
        
        # Generate output files
        folders = config.get('folders', {})
        markdown_dir = folders.get('markdown', 'output/markdown')
        html_dir = folders.get('html', 'output/html')
        
        # Create output filenames
        markdown_file = os.path.join(markdown_dir, f"{pdf_name}_{ocr_engine}_results.md")
        html_file = os.path.join(html_dir, f"{pdf_name}_{ocr_engine}_results.html")
        
        # Generate outputs based on config
        output_config = config.get('output', {})
        
        if output_config.get('generate_markdown', True):
            generate_markdown(results, markdown_file, config)
            print(f"📝 Markdown saved: {markdown_file}")
        
        if output_config.get('generate_html', True):
            generate_html(markdown_file, html_file, config)
            print(f"🌐 HTML saved: {html_file}")
        
        # Print summary statistics
        successful = sum(1 for r in results if r['success'])
        success_rate = (successful / len(results)) * 100 if results else 0
        avg_confidence = sum(r['confidence'] for r in results if r['success']) / successful if successful > 0 else 0
        
        print(f"📊 {pdf_name} Results:")
        print(f"   • {len(results)} images processed")
        print(f"   • {successful} successful extractions")
        print(f"   • {success_rate:.1f}% success rate")
        print(f"   • {avg_confidence:.1%} average confidence")
        
    except Exception as e:
        print(f"❌ Error running OCR on {pdf_name}: {e}")

def process_all_pdfs(config: Dict):
    """Process all PDF files in the input directory"""
    folders = config.get('folders', {})
    input_dir = folders.get('input', 'read')
    
    # Find all PDF files
    pdf_files = find_pdf_files(input_dir)
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        print(f"💡 Place your PDF files in the '{input_dir}' folder and try again.")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files to process:")
    for pdf in pdf_files:
        print(f"   • {os.path.basename(pdf)}")
    
    print(f"\\n🚀 Starting batch processing with {config.get('ocr_engine', 'tesseract').upper()} OCR...")
    print("=" * 60)
    
    # Process each PDF
    total_images = 0
    total_successful = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = Path(pdf_path).stem
        
        print(f"\\n📄 Processing PDF {i}/{len(pdf_files)}: {pdf_name}")
        print("-" * 40)
        
        # Extract images
        images_dir = extract_pdf_images(pdf_path, config)
        
        if images_dir:
            # Run OCR and generate outputs
            run_ocr_on_images(images_dir, pdf_name, config)
            
            # Count images for summary
            image_count = len([f for f in os.listdir(images_dir) if f.endswith('.png')])
            total_images += image_count
        
        print("-" * 40)
    
    # Final summary
    print(f"\\n🎉 Batch processing complete!")
    print(f"📊 Summary:")
    print(f"   • {len(pdf_files)} PDFs processed")
    print(f"   • {total_images} total images extracted")
    print(f"   • OCR engine: {config.get('ocr_engine', 'tesseract').upper()}")
    
    folders = config.get('folders', {})
    print(f"\\n📁 Output locations:")
    print(f"   • Images: {folders.get('images', 'output/images')}")
    print(f"   • Markdown: {folders.get('markdown', 'output/markdown')}")
    print(f"   • HTML: {folders.get('html', 'output/html')}")

def main():
    """Main function for batch processing"""
    print("🚀 PDF Batch Processor")
    print("=" * 25)
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Ensure directories exist
    ensure_directories(config)
    
    # Process all PDFs
    process_all_pdfs(config)

if __name__ == "__main__":
    main()
