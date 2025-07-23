#!/usr/bin/env python3
"""
PDF Highlight & Annotation Mathpix OCR Processor
=================================================

This script processes extracted images using Mathpix OCR API for high-quality text extraction,
especially optimized for academic documents and mathematical content.
"""

import os
import json
import base64
from pathlib import Path
from PIL import Image
import requests
import time
from typing import Dict, List, Tuple, Optional

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

def setup_mathpix_credentials(config: Dict):
    """
    Setup Mathpix API credentials from config file
    """
    mathpix_config = config.get('mathpix', {})
    app_id = mathpix_config.get('app_id', '').strip()
    app_key = mathpix_config.get('app_key', '').strip()
    
    # Check environment variables as fallback
    if not app_id:
        app_id = os.getenv('MATHPIX_APP_ID', '').strip()
    if not app_key:
        app_key = os.getenv('MATHPIX_APP_KEY', '').strip()
    
    if not app_id or not app_key:
        print("🔑 Mathpix API Credentials Required")
        print("=" * 50)
        print("Please add your credentials to config.json:")
        print('  "mathpix": {')
        print('    "app_id": "your_app_id_here",')
        print('    "app_key": "your_app_key_here"')
        print('  }')
        print("\nGet credentials from: https://mathpix.com/")
        raise ValueError("Mathpix credentials are required in config.json")
    
    return app_id, app_key

def encode_image_to_base64(image_path: str) -> str:
    """Convert image to base64 string for Mathpix API"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_with_mathpix(image_path: str, app_id: str, app_key: str) -> Dict:
    """
    Extract text from image using Mathpix OCR API
    
    Args:
        image_path: Path to the image file
        app_id: Mathpix App ID
        app_key: Mathpix App Key
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        # Encode image to base64
        image_base64 = encode_image_to_base64(image_path)
        
        # Prepare API request
        url = "https://api.mathpix.com/v3/text"
        headers = {
            "app_id": app_id,
            "app_key": app_key,
            "Content-type": "application/json"
        }
        
        # Configure OCR options for academic documents
        data = {
            "src": f"data:image/jpeg;base64,{image_base64}",
            "formats": ["text", "latex_styled"],  # Get both plain text and LaTeX
            "data_options": {
                "include_asciimath": True,
                "include_latex": True,
                "include_tsv": False
            }
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract relevant information
        text_content = result.get('text', '')
        latex_content = result.get('latex_styled', '')
        confidence = result.get('confidence', 0)
        
        return {
            'text': text_content,
            'latex': latex_content,
            'confidence': confidence,
            'success': True,
            'error': None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'text': '',
            'latex': '',
            'confidence': 0,
            'success': False,
            'error': f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            'text': '',
            'latex': '',
            'confidence': 0,
            'success': False,
            'error': f"Processing failed: {str(e)}"
        }

def preprocess_image_for_mathpix(image_path: str) -> str:
    """
    Preprocess image for better Mathpix OCR results
    
    Args:
        image_path: Path to input image
        
    Returns:
        Path to preprocessed image
    """
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image is too large (Mathpix has size limits)
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save preprocessed image
        preprocessed_path = image_path.replace('.png', '_preprocessed.png')
        img.save(preprocessed_path, 'PNG', quality=95)
        
        return preprocessed_path
        
    except Exception as e:
        print(f"⚠️  Preprocessing failed for {image_path}: {e}")
        return image_path  # Return original if preprocessing fails

def process_extracted_images_mathpix(images_dir: str, output_file: str, config: Dict):
    """
    Process all extracted images using Mathpix OCR and generate markdown
    
    Args:
        images_dir: Directory containing extracted images
        output_file: Output markdown file path
        config: Configuration dictionary
    """
    print("🚀 PDF Highlight & Annotation Mathpix OCR Processor")
    print("=" * 55)
    
    # Setup Mathpix credentials
    try:
        app_id, app_key = setup_mathpix_credentials(config)
    except Exception as e:
        print(f"❌ Failed to setup Mathpix credentials: {e}")
        return
    
    # Find all image files
    images_dir_path = Path(images_dir)
    if not images_dir_path.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return
    
    image_files = sorted([
        f for f in images_dir_path.glob('*.png') 
        if not f.name.endswith('_preprocessed.png')
    ])
    
    if not image_files:
        print(f"❌ No PNG images found in {images_dir}")
        return
    
    print(f"📁 Found {len(image_files)} images to process with Mathpix OCR")
    
    # Process each image
    results = []
    successful_extractions = 0
    total_confidence = 0
    
    for i, image_path in enumerate(image_files, 1):
        print("\n 📸 Processing image {i}/{len(image_files)}: {image_path.name}")
        
        # Preprocess image for better OCR
        preprocessed_path = preprocess_image_for_mathpix(str(image_path))
        
        # Extract text using Mathpix
        result = extract_text_with_mathpix(preprocessed_path, app_id, app_key)
        
        if result['success']:
            print(f"✅ OCR successful (confidence: {result['confidence']:.1%})")
            successful_extractions += 1
            total_confidence += result['confidence']
            
            # Clean up extracted text
            text = result['text'].strip()
            latex = result['latex'].strip()
            
            results.append({
                'image_file': image_path.name,
                'image_path': str(image_path),
                'text': text,
                'latex': latex,
                'confidence': result['confidence'],
                'success': True
            })
        else:
            print(f"❌ OCR failed: {result['error']}")
            results.append({
                'image_file': image_path.name,
                'image_path': str(image_path),
                'text': '',
                'latex': '',
                'confidence': 0,
                'success': False,
                'error': result['error']
            })
        
        # Clean up preprocessed file if it's different from original
        if preprocessed_path != str(image_path) and os.path.exists(preprocessed_path):
            os.remove(preprocessed_path)
        
        # Add small delay to respect API rate limits
        time.sleep(0.5)
    
    # Generate statistics
    success_rate = (successful_extractions / len(image_files)) * 100 if image_files else 0
    avg_confidence = (total_confidence / successful_extractions) if successful_extractions > 0 else 0
    
    print("\n 📊  Processing Statistics:")
    print(f"   • Total images: {len(image_files)}")
    print(f"   • Successful extractions: {successful_extractions}")
    print(f"   • Success rate: {success_rate:.1f}%")
    print(f"   • Average confidence: {avg_confidence:.1%}")
    
    # Generate markdown output
    generate_mathpix_markdown(results, output_file, {
        'total_images': len(image_files),
        'successful_extractions': successful_extractions,
        'success_rate': success_rate,
        'avg_confidence': avg_confidence
    })

def generate_mathpix_markdown(results: List[Dict], output_file: str, stats: Dict):
    """Generate markdown file with Mathpix OCR results and embedded images"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# PDF Highlights & Annotations - Mathpix OCR Results\n\n")
        f.write("*Generated using high-quality Mathpix OCR for academic documents*\n\n")
        
        # Write statistics
        f.write("## Processing Statistics\n\n")
        f.write(f"- **Total Images Processed**: {stats['total_images']}\n")
        f.write(f"- **Successful Extractions**: {stats['successful_extractions']}\n")
        f.write(f"- **Success Rate**: {stats['success_rate']:.1f}%\n")
        f.write(f"- **Average Confidence**: {stats['avg_confidence']:.1%}\n\n")
        
        f.write("---\n\n")
        
        # Write results for each image
        for i, result in enumerate(results, 1):
            f.write(f"## Extract {i}: {result['image_file']}\n\n")
            
            # Embed the image
            f.write(f"![Extract {i}]({result['image_path']})\n\n")
            
            if result['success']:
                # Write confidence score
                f.write(f"**Confidence**: {result['confidence']:.1%}\n\n")
                
                # Write extracted text
                if result['text']:
                    f.write("### Extracted Text\n\n")
                    f.write(f"{result['text']}\n\n")
                
                # Write LaTeX if available and different from text
                if result['latex'] and result['latex'] != result['text']:
                    f.write("### LaTeX Format\n\n")
                    f.write("```latex\n")
                    f.write(f"{result['latex']}\n")
                    f.write("```\n\n")
                
                if not result['text'] and not result['latex']:
                    f.write("*No text content extracted from this image*\n\n")
            else:
                f.write(f"**Error**: {result.get('error', 'Unknown error')}\n\n")
            
            f.write("---\n\n")
    
    print(f"📝 Markdown file generated: {output_file}")

def main():
    """Main function to process extracted images with Mathpix OCR"""
    config = load_config()
    images_dir = "extracted_content_grouped"
    output_file = "mathpix_ocr_results.md"
    
    process_extracted_images_mathpix(images_dir, output_file, config)

if __name__ == "__main__":
    main()
