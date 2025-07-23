#!/usr/bin/env python3
"""
Convert the markdown with images to HTML for better viewing.
Supports both Tesseract and Mathpix OCR results.
"""

import markdown
import os
import json
from typing import Dict, Optional

def load_config(config_file: str = "config.json") -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        # Return default config
        return {"ocr_engine": "tesseract"}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return {"ocr_engine": "tesseract"}

def convert_to_html(markdown_file: Optional[str] = None, html_file: Optional[str] = None):
    """
    Convert markdown file to HTML with proper image handling.
    Automatically detects OCR engine from config if files not specified.
    """
    
    # Load config to determine OCR engine if files not specified
    if markdown_file is None or html_file is None:
        config = load_config()
        ocr_engine = config.get('ocr_engine', 'tesseract').lower()
        
        if markdown_file is None:
            markdown_file = f"{ocr_engine}_ocr_results.md"
        if html_file is None:
            html_file = f"{ocr_engine}_ocr_results.html"
    
    if not os.path.exists(markdown_file):
        print(f"❌ Markdown file not found: {markdown_file}")
        return
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
    
    # Create a complete HTML document with CSS styling
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extracted Text from PDF Highlights and Annotations</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        
        h2 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        
        h3 {{
            color: #e74c3c;
            margin-top: 30px;
        }}
        
        h4 {{
            color: #8e44ad;
            margin-bottom: 10px;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ecf0f1;
            margin: 20px 0;
        }}
        
        strong {{
            color: #2980b9;
        }}
        
        em {{
            color: #7f8c8d;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #7f8c8d;
        }}
        
        .confidence {{
            background-color: #e8f5e8;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 10px;
        }}
        
        .stats {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }}
        
        .page-section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
        }}
        
        .highlight-section {{
            background-color: #fffbf0;
        }}
        
        .red-section {{
            background-color: #fdf2f2;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # Write HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ HTML version created: {html_file}")
    print(f"🌐 Open in browser to view images and formatted text")

if __name__ == "__main__":
    # Convert HTML for the configured OCR engine
    convert_to_html()
