#!/usr/bin/env python3
"""
Unified OCR Processor
====================

This script processes extracted images using either Tesseract (local) or Mathpix (API)
based on configuration settings and generates both markdown and HTML output.
"""

import os
import json
import base64
from pathlib import Path
from PIL import Image
import requests
import time
import markdown
from typing import Dict, List

# Import Tesseract if available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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

def setup_tesseract(config: Dict):
    """Setup Tesseract OCR based on configuration"""
    if not TESSERACT_AVAILABLE:
        raise ImportError("pytesseract not available")
    
    tesseract_config = config.get('tesseract', {})
    
    # Try to find Tesseract executable on macOS
    import platform
    if platform.system() == "Darwin":
        possible_paths = [
            "/opt/homebrew/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/opt/local/bin/tesseract"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        else:
            print("⚠️  Tesseract not found. Install with: brew install tesseract")
    
    return tesseract_config.get('language', 'eng')

def setup_mathpix_credentials(config: Dict):
    """Setup Mathpix API credentials from config file"""
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
        print("\\nGet credentials from: https://mathpix.com/")
        raise ValueError("Mathpix credentials are required in config.json")
    
    return app_id, app_key

def extract_text_with_tesseract(image_path: str, language: str) -> Dict:
    """Extract text using Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        return {
            'text': '',
            'confidence': 0,
            'success': False,
            'error': "pytesseract not available"
        }
    
    try:
        img = Image.open(image_path)
        
        # Simple OCR configuration
        text = pytesseract.image_to_string(img, lang=language)
        text = text.strip()
        
        # Get confidence data
        data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': text,
            'confidence': avg_confidence / 100,
            'success': bool(text and avg_confidence > 30),
            'error': None
        }
        
    except Exception as e:
        return {
            'text': '',
            'confidence': 0,
            'success': False,
            'error': f"Tesseract OCR failed: {str(e)}"
        }

def extract_text_with_mathpix(image_path: str, app_id: str, app_key: str) -> Dict:
    """Extract text using Mathpix OCR API"""
    try:
        # Encode image to base64
        with open(image_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare API request
        url = "https://api.mathpix.com/v3/text"
        headers = {
            "app_id": app_id,
            "app_key": app_key,
            "Content-type": "application/json"
        }
        
        data = {
            "src": f"data:image/jpeg;base64,{image_base64}",
            "formats": ["text", "latex_styled"],
            "data_options": {
                "include_asciimath": True,
                "include_latex": True,
                "include_tsv": False
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
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
        
    except Exception as e:
        return {
            'text': '',
            'latex': '',
            'confidence': 0,
            'success': False,
            'error': f"Mathpix OCR failed: {str(e)}"
        }

def process_images_with_ocr(images_dir: str, config: Dict) -> List[Dict]:
    """Process images with the configured OCR engine"""
    ocr_engine = config.get('ocr_engine', 'tesseract').lower()
    
    print(f"🔍 Using OCR Engine: {ocr_engine.upper()}")
    
    # Setup OCR engine
    if ocr_engine == 'mathpix':
        app_id, app_key = setup_mathpix_credentials(config)
        ocr_func = lambda img_path: extract_text_with_mathpix(img_path, app_id, app_key)
    elif ocr_engine == 'tesseract':
        language = setup_tesseract(config)
        ocr_func = lambda img_path: extract_text_with_tesseract(img_path, language)
    else:
        raise ValueError(f"Unknown OCR engine: {ocr_engine}")
    
    # Find image files
    images_dir_path = Path(images_dir)
    if not images_dir_path.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return []
    
    image_files = sorted([
        f for f in images_dir_path.glob('*.png') 
        if not f.name.endswith('_preprocessed.png')
    ])
    
    print(f"📁 Found {len(image_files)} images to process")
    
    results = []
    successful_extractions = 0
    total_confidence = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\\n 📸 Processing image {i}/{len(image_files)}: {image_path.name}")
        
        # Extract text
        result = ocr_func(str(image_path))
        
        if result['success']:
            print(f"✅ OCR successful (confidence: {result['confidence']:.1%})")
            successful_extractions += 1
            total_confidence += result['confidence']
        else:
            print(f"❌ OCR failed: {result['error']}")
        
        results.append({
            'image_file': image_path.name,
            'image_path': str(image_path),
            'ocr_engine': ocr_engine,
            **result
        })
        
        # Rate limiting for API calls
        if ocr_engine == 'mathpix':
            time.sleep(0.5)
    
    # Print statistics
    success_rate = (successful_extractions / len(image_files)) * 100 if image_files else 0
    avg_confidence = (total_confidence / successful_extractions) if successful_extractions > 0 else 0
    
    print(f"\\n 📊  Processing Statistics:")
    print(f"   • OCR Engine: {ocr_engine.upper()}")
    print(f"   • Total images: {len(image_files)}")
    print(f"   • Successful extractions: {successful_extractions}")
    print(f"   • Success rate: {success_rate:.1f}%")
    print(f"   • Average confidence: {avg_confidence:.1%}")
    
    return results

def generate_markdown(results: List[Dict], output_file: str, config: Dict):
    """Generate markdown file with OCR results"""
    ocr_engine = config.get('ocr_engine', 'tesseract').upper()
    
    # Calculate relative path from markdown file to images
    output_dir = os.path.dirname(output_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# PDF Highlights & Annotations - {ocr_engine} OCR Results\n\n")
        f.write(f"*Generated using {ocr_engine} OCR engine*\n\n")
        
        # Statistics
        total_images = len(results)
        successful = sum(1 for r in results if r['success'])
        success_rate = (successful / total_images) * 100 if total_images > 0 else 0
        avg_confidence = sum(r['confidence'] for r in results if r['success']) / successful if successful > 0 else 0
        
        f.write("## Processing Statistics\n\n")
        f.write(f"- **OCR Engine**: {ocr_engine}\n")
        f.write(f"- **Total Images Processed**: {total_images}\n")
        f.write(f"- **Successful Extractions**: {successful}\n")
        f.write(f"- **Success Rate**: {success_rate:.1f}%\n")
        f.write(f"- **Average Confidence**: {avg_confidence:.1%}\n\n")
        f.write("---\n\n")
        
        # Results for each image
        for i, result in enumerate(results, 1):
            f.write(f"## Extract {i}: {result['image_file']}\n\n")
            
            # Calculate relative path from markdown file to image
            try:
                image_path = result['image_path']
                if os.path.isabs(image_path):
                    # Convert absolute path to relative path from markdown file
                    rel_path = os.path.relpath(image_path, output_dir)
                else:
                    # For relative paths, calculate relative to markdown output directory
                    rel_path = os.path.relpath(image_path, output_dir)
                f.write(f"![Extract {i}]({rel_path})\n\n")
            except Exception as e:
                # Fallback to original path if relative path calculation fails
                print(f"⚠️  Path calculation failed for {result['image_path']}: {e}")
                f.write(f"![Extract {i}]({result['image_path']})\n\n")
            
            if result['success']:
                f.write(f"**Confidence**: {result['confidence']:.1%}\n\n")
                
                if result['text']:
                    f.write("### Extracted Text\n\n")
                    f.write(f"{result['text']}\n\n")
                
                # Add LaTeX if available (Mathpix)
                if 'latex' in result and result['latex'] and result['latex'] != result['text']:
                    f.write("### LaTeX Format\n\n")
                    f.write("```latex\n")
                    f.write(f"{result['latex']}\n")
                    f.write("```\n\n")
                
                if not result['text']:
                    f.write("*No text content extracted from this image*\n\n")
            else:
                f.write(f"**Error**: {result.get('error', 'Unknown error')}\n\n")
            
            f.write("---\n\n")
    
    print(f"📝 Markdown file generated: {output_file}")

def generate_html(markdown_file: str, html_file: str, config: Dict):
    """Generate HTML file from markdown"""
    if not os.path.exists(markdown_file):
        print(f"❌ Markdown file not found: {markdown_file}")
        return
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
    
    ocr_engine = config.get('ocr_engine', 'tesseract').upper()
    
    # Create complete HTML document with improved styling
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Highlights & Annotations - {ocr_engine} OCR Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #fafafa;
        }}
        
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transition: transform 0.2s ease-in-out;
        }}
        
        img:hover {{
            transform: scale(1.02);
            border-color: #3498db;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        h3 {{
            color: #e74c3c;
            margin-top: 25px;
            font-size: 1.1em;
        }}
        
        strong {{
            color: #2980b9;
            font-weight: 600;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
            border: 1px solid #e9ecef;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #e9ecef;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
        }}
        
        .ocr-badge {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .confidence {{
            background-color: #e8f5e8;
            color: #155724;
            padding: 6px 12px;
            border-radius: 15px;
            display: inline-block;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        
        .stats {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 25px 0;
            border-left: 4px solid #17a2b8;
        }}
        
        .stats ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .stats li {{
            margin-bottom: 8px;
        }}
        
        .extract-section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            background-color: #fdfdfd;
        }}
        
        .error-message {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #dc3545;
            margin: 10px 0;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #e9ecef;
            margin: 30px 0;
        }}
        
        .text-content {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #6c757d;
            margin: 15px 0;
            font-family: Georgia, serif;
            line-height: 1.7;
        }}
        
        .latex-content {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #ffc107;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="ocr-badge">OCR Engine: {ocr_engine}</div>
        {html_content}
    </div>
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"🌐 HTML file generated: {html_file}")

def main():
    """Main function to process images with unified OCR"""
    config = load_config()
    
    images_dir = "extracted_content_grouped"
    ocr_engine = config.get('ocr_engine', 'tesseract').lower()
    
    # Generate output filenames based on OCR engine
    markdown_file = f"{ocr_engine}_ocr_results.md"
    html_file = f"{ocr_engine}_ocr_results.html"
    
    print("🚀 Unified OCR Processor")
    print("=" * 25)
    
    # Process images
    results = process_images_with_ocr(images_dir, config)
    
    if not results:
        print("❌ No results to process")
        return
    
    # Generate outputs based on config
    output_config = config.get('output', {})
    
    if output_config.get('generate_markdown', True):
        generate_markdown(results, markdown_file, config)
    
    if output_config.get('generate_html', True):
        generate_html(markdown_file, html_file, config)

if __name__ == "__main__":
    main()
