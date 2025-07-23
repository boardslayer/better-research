# PDF Batch Processing System

## 🏗️ New Folder Structure

```
├── read/                           # Input folder - place your PDFs here
├── output/                         # Output folder (organized by type)
│   ├── images/                     # Extracted images (organized by PDF name)
│   │   └── {pdf_name}/            # Individual PDF image folders
│   ├── markdown/                   # Markdown results
│   │   └── {pdf_name}_{engine}_results.md
│   └── html/                      # HTML results  
│       └── {pdf_name}_{engine}_results.html
├── config.json                    # Configuration file
└── batch_processor.py             # Main batch processing script
```

## 🚀 Quick Start

### 1. Place PDFs in the read folder

```bash
# Copy your PDFs to the read folder
cp your_document.pdf read/
cp another_document.pdf read/
```

### 2. Configure OCR engine (optional)

Edit `config.json` to choose between `tesseract` (local) or `mathpix` (API):

```json
{
  "ocr_engine": "mathpix"  // or "tesseract"
}
```

### 3. Run batch processing

```bash
python batch_processor.py
```

## 📊 Results

The system will process each PDF and generate:

- **Images**: `output/images/{pdf_name}/` - Extracted highlight and annotation images
- **Markdown**: `output/markdown/{pdf_name}_{engine}_results.md` - Text results with embedded images
- **HTML**: `output/html/{pdf_name}_{engine}_results.html` - Formatted viewing version

## 🎯 Features

### ✅ Multiple File Processing

- Automatically finds all PDF files in the `read/` folder
- Processes each PDF independently
- Generates separate output files for each document

### ✅ Organized Output Structure

- Images organized by PDF name
- Separate folders for markdown and HTML
- Clear naming convention: `{pdf_name}_{ocr_engine}_results.{ext}`

### ✅ Relative Path Handling

- Markdown files use relative paths to images
- HTML files display images correctly
- Works properly when moving folders

### ✅ Comprehensive Statistics

- Per-PDF processing statistics
- Overall batch processing summary
- OCR confidence scores and success rates

## 📈 Example Results

**Mathpix OCR Performance** (recent test):

- **100% success rate** - All 26 images processed successfully
- **73.8% average confidence** - High-quality text extraction
- **LaTeX support** - Mathematical content preserved
- **Academic optimization** - Designed for research papers

**Folder Structure After Processing**:

```
output/
├── images/
│   ├── Coldwell22/
│   │   ├── page_1_yellow_highlight_group_1.png
│   │   ├── page_1_red_mark_group_2.png
│   │   └── ... (24 more images)
│   └── AnotherDocument/
│       └── ... (extracted images)
├── markdown/
│   ├── Coldwell22_mathpix_results.md
│   └── AnotherDocument_mathpix_results.md
└── html/
    ├── Coldwell22_mathpix_results.html
    └── AnotherDocument_mathpix_results.html
```

## ⚙️ Configuration Options

```json
{
  "ocr_engine": "mathpix",           // "tesseract" or "mathpix"
  "folders": {
    "input": "read",                 // Input PDF folder
    "output": "output",              // Base output folder  
    "images": "output/images",       // Image extraction folder
    "markdown": "output/markdown",   // Markdown results folder
    "html": "output/html"           // HTML results folder
  },
  "output": {
    "generate_html": true,           // Generate HTML files
    "generate_markdown": true        // Generate Markdown files
  }
}
```

## 🔄 Legacy Compatibility

The old single-file processing scripts still work:

- `unified_ocr_processor.py` - Process single image folder
- `extracting_highlights_images.py` - Extract from single PDF
- `convert_to_html.py` - Convert single markdown to HTML

## 💡 Tips

1. **Use Mathpix for academic papers** - Superior accuracy on research documents
2. **Check image quality** - View extracted images in `output/images/{pdf_name}/`
3. **Batch process overnight** - Large document sets with API rate limiting
4. **Organize by project** - Use separate folders for different document sets

## 🚨 Troubleshooting

### No PDFs Found

- Ensure PDF files are in the `read/` folder
- Check file extensions are `.pdf` (case-sensitive)

### OCR Failures  

- **Mathpix**: Check API credentials and internet connection
- **Tesseract**: Ensure Tesseract is installed (`brew install tesseract`)

### Image Path Issues

- Markdown uses relative paths from markdown file to images
- Move entire `output/` folder as a unit to preserve relationships

## 📞 Support

The batch processor automatically handles:

- ✅ Multiple input files
- ✅ Organized output folders  
- ✅ Relative path generation
- ✅ Error handling per file
- ✅ Comprehensive logging
- ✅ Statistics reporting
