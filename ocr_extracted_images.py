#!/usr/bin/env python3
"""
OCR script to extract text from highlighted and annotated images.
Uses Tesseract OCR for local text recognition.
"""

import os
import json
import re
from PIL import Image
import pytesseract
from datetime import datetime
from typing import Dict

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

def setup_tesseract():
    """
    Setup Tesseract OCR path for different operating systems.
    """
    import platform
    
    system = platform.system()
    if system == "Darwin":  # macOS
        # Common Tesseract paths on macOS (installed via Homebrew)
        possible_paths = [
            "/opt/homebrew/bin/tesseract",  # Apple Silicon
            "/usr/local/bin/tesseract",     # Intel Mac
            "/opt/local/bin/tesseract"      # MacPorts
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        
        print("⚠️  Tesseract not found. Install with: brew install tesseract")
        return False
    
    elif system == "Linux":
        # Tesseract is usually in PATH on Linux
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            print("⚠️  Tesseract not found. Install with: sudo apt-get install tesseract-ocr")
            return False
    
    elif system == "Windows":
        # Common Windows installation path
        windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(windows_path):
            pytesseract.pytesseract.tesseract_cmd = windows_path
            return True
        else:
            print("⚠️  Tesseract not found. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    
    return False

def preprocess_image_for_ocr(image_path):
    """
    Preprocess image to improve OCR accuracy.
    """
    try:
        from PIL import ImageEnhance, ImageFilter
        
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Scale up image for better OCR (2x)
        width, height = image.size
        image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        
        return image
    
    except Exception as e:
        print(f"⚠️  Could not preprocess {image_path}: {e}")
        return Image.open(image_path)

def extract_text_from_image(image_path, confidence_threshold=30):
    """
    Extract text from an image using OCR.
    
    Args:
        image_path (str): Path to the image file
        confidence_threshold (int): Minimum confidence for text recognition
    
    Returns:
        tuple: (extracted_text, confidence_score)
    """
    try:
        # Preprocess image
        image = preprocess_image_for_ocr(image_path)
        
        # OCR configuration for better accuracy
        custom_config = r'--oem 3 --psm 6'
        
        # Extract text with confidence scores
        data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
        
        # Filter by confidence and combine text
        text_parts = []
        confidences = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > confidence_threshold:
                text = data['text'][i].strip()
                if text:
                    text_parts.append(text)
                    confidences.append(int(data['conf'][i]))
        
        # Combine text parts
        extracted_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Clean up text
        extracted_text = clean_extracted_text(extracted_text)
        
        return extracted_text, avg_confidence
    
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return "", 0

def clean_extracted_text(text):
    """
    Clean and format extracted text.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR mistakes
    text = text.replace('|', 'I')  # Common pipe/I confusion
    text = text.replace('0', 'O', text.count('0') // 3)  # Some zero/O fixes (conservative)
    
    # Capitalize first letter of sentences
    sentences = text.split('. ')
    sentences = [s.capitalize() if s else s for s in sentences]
    text = '. '.join(sentences)
    
    return text.strip()

def process_extracted_images(images_dir="extracted_content_grouped", output_file="extracted_text.md"):
    """
    Process all extracted images and create a markdown file with OCR results.
    """
    
    if not os.path.exists(images_dir):
        print(f"❌ Directory not found: {images_dir}")
        return
    
    # Load extraction summary
    summary_file = os.path.join(images_dir, "extraction_summary.json")
    if not os.path.exists(summary_file):
        print(f"❌ Summary file not found: {summary_file}")
        return
    
    with open(summary_file, 'r') as f:
        extraction_data = json.load(f)
    
    # Group by page
    pages = {}
    for item in extraction_data:
        page = item['page']
        if page not in pages:
            pages[page] = {'yellow': [], 'red': []}
        
        if 'yellow' in item['type']:
            pages[page]['yellow'].append(item)
        else:
            pages[page]['red'].append(item)
    
    # Process images and create markdown
    markdown_content = generate_markdown_header()
    
    total_processed = 0
    successful_extractions = 0
    
    for page_num in sorted(pages.keys()):
        print("\n📄 Processing Page {page_num}...")
        
        page_data = pages[page_num]
        page_content = "\n## Page {page_num}\n\n"
        
        # Process yellow highlights
        if page_data['yellow']:
            page_content += "### 📝 Highlighted Content\n\n"
            
            for item in page_data['yellow']:
                image_path = os.path.join(images_dir, item['filename'])
                
                if os.path.exists(image_path):
                    print(f"  🔍 OCR on {item['filename']}...")
                    text, confidence = extract_text_from_image(image_path)
                    total_processed += 1
                    
                    if text and confidence > 30:
                        successful_extractions += 1
                        individual_count = item.get('individual_regions', 1)
                        regions_note = f" *(merged from {individual_count} regions)*" if individual_count > 1 else ""
                        
                        page_content += f"#### Highlight Group {item['filename'].split('_')[-1].split('.')[0]}{regions_note}\n\n"
                        page_content += f"![{item['filename']}]({images_dir}/{item['filename']})\n\n"
                        page_content += f"**Confidence:** {confidence:.1f}%\n\n"
                        page_content += f"{text}\n\n"
                        page_content += "---\n\n"
                    else:
                        page_content += f"#### Highlight Group {item['filename'].split('_')[-1].split('.')[0]}\n\n"
                        page_content += f"![{item['filename']}]({images_dir}/{item['filename']})\n\n"
                        page_content += "*OCR could not extract readable text from this image.*\n\n"
                        page_content += "---\n\n"
        
        # Process red marks
        if page_data['red']:
            page_content += "### 🔴 Red Annotations\n\n"
            
            for item in page_data['red']:
                image_path = os.path.join(images_dir, item['filename'])
                
                if os.path.exists(image_path):
                    print(f"  🔍 OCR on {item['filename']}...")
                    text, confidence = extract_text_from_image(image_path)
                    total_processed += 1
                    
                    if text and confidence > 30:
                        successful_extractions += 1
                        individual_count = item.get('individual_regions', 1)
                        regions_note = f" *(merged from {individual_count} regions)*" if individual_count > 1 else ""
                        
                        page_content += f"#### Red Annotation {item['filename'].split('_')[-1].split('.')[0]}{regions_note}\n\n"
                        page_content += f"![{item['filename']}]({images_dir}/{item['filename']})\n\n"
                        page_content += f"**Confidence:** {confidence:.1f}%\n\n"
                        page_content += f"{text}\n\n"
                        page_content += "---\n\n"
                    else:
                        page_content += f"#### Red Annotation {item['filename'].split('_')[-1].split('.')[0]}\n\n"
                        page_content += f"![{item['filename']}]({images_dir}/{item['filename']})\n\n"
                        page_content += "*OCR could not extract readable text from this image.*\n\n"
                        page_content += "---\n\n"
        
        markdown_content += page_content
    
    # Add summary
    markdown_content += generate_markdown_footer(total_processed, successful_extractions)
    
    # Save markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✅ OCR processing complete!")
    print(f"📊 Results:")
    print(f"  - Total images processed: {total_processed}")
    print(f"  - Successful text extractions: {successful_extractions}")
    print(f"  - Success rate: {(successful_extractions/total_processed*100):.1f}%" if total_processed > 0 else "  - Success rate: 0%")
    print(f"📄 Markdown saved to: {output_file}")

def generate_markdown_header():
    """Generate markdown file header."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""# Extracted Text from PDF Highlights and Annotations

**Generated on:** {timestamp}  
**Source:** PDF highlight and annotation extraction with OCR

This document contains text extracted from highlighted content and red annotations using Optical Character Recognition (OCR). Each section includes the source image followed by the extracted text and confidence score.

---

"""

def generate_markdown_footer(total_processed, successful_extractions):
    """Generate markdown file footer with statistics."""
    
    success_rate = (successful_extractions/total_processed*100) if total_processed > 0 else 0
    
    return f"""
---

## OCR Processing Statistics

- **Total images processed:** {total_processed}
- **Successful text extractions:** {successful_extractions}
- **Success rate:** {success_rate:.1f}%
- **OCR Engine:** Tesseract
- **Processing date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### Notes

- Text extraction confidence scores indicate OCR reliability
- Low-confidence extractions were filtered out to maintain quality
- Images with merged regions show the number of original fragments combined
- Some annotations may be drawings or symbols that don't contain readable text

---

*Generated by PDF Highlight & Annotation Image Extractor with OCR*
"""

def check_tesseract_installation():
    """Check if Tesseract is properly installed."""
    
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR found: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        print("\n📥 Installation instructions:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def main():
    """Main function to run OCR on extracted images."""
    
    print("🔍 PDF Highlight & Annotation OCR Processor")
    print("=" * 50)
    
    # Check Tesseract installation
    if not setup_tesseract():
        return
    
    if not check_tesseract_installation():
        return
    
    # Check for extracted images
    images_dir = "extracted_content_grouped"
    if not os.path.exists(images_dir):
        print(f"❌ No extracted images found in {images_dir}/")
        print("   Run extracting_highlights_images.py first to extract images from PDF")
        return
    
    # Count available images
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    print(f"📁 Found {len(image_files)} images to process")
    
    if len(image_files) == 0:
        print("❌ No PNG images found in the directory")
        return
    
    # Run OCR processing
    output_file = "extracted_text.md"
    process_extracted_images(images_dir, output_file)

if __name__ == "__main__":
    main()
