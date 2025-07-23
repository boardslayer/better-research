# PDF Highlight & Annotation Extractor

A comprehensive system for extracting highlighted text and annotations from PDF files, with intelligent grouping and multiple OCR engine support. Features advanced batch processing capabilities and organized output structure.

## 🌟 Features

- **Smart Extraction**: Detects yellow highlights and red marker annotations from PDFs
- **Intelligent Grouping**: Merges nearby regions into coherent extracts (reduces output by ~87%)
- **Multiple OCR Engines**: Switch between Tesseract (local) and Mathpix (API)
- **Batch Processing**: Process multiple PDFs simultaneously with organized outputs
- **Output Formats**: Generates both Markdown and HTML with embedded images
- **Configuration-Based**: Easy switching between OCR engines via config file
- **High Quality**: Mathpix optimized for academic documents with LaTeX support
- **Organized Structure**: Clean folder organization with separate inputs and outputs

## 📁 Project Structure

```txt
├── read/                          # Input folder - place your PDFs here
├── output/                        # Organized output directory
│   ├── images/                    # Extracted images (organized by PDF name)
│   ├── markdown/                  # Markdown results with embedded images
│   └── html/                      # HTML results for easy viewing
├── config.json                   # Main configuration file
├── batch_processor.py            # Batch processing for multiple PDFs
├── unified_ocr_processor.py      # Main OCR processor (supports both engines)
├── extracting_highlights_images.py # PDF extraction with intelligent grouping
├── convert_to_html.py            # Markdown to HTML converter
├── tune_extraction_params.py     # Parameter optimization tool
├── requirements.txt              # Python dependencies
├── BATCH_PROCESSING.md           # Batch processing documentation
├── MATHPIX_SETUP.md              # Mathpix setup guide
└── CONFIG_TEMPLATE.md            # Configuration templates
```

## ⚙️ Configuration

Edit `config.json` to customize the system:

```json
{
  "ocr_engine": "tesseract",        // "tesseract" or "mathpix"
  "mathpix": {
    "app_id": "",                   // Your Mathpix App ID
    "app_key": ""                   // Your Mathpix App Key
  },
  "tesseract": {
    "enabled": true,
    "language": "eng"               // Tesseract language
  },
  "extraction": {
    "extract_highlights": true,     // Extract yellow highlights
    "extract_handwriting": true     // Extract red handwriting/annotations
  },
  "folders": {
    "input": "read",                // Input folder for PDFs
    "output": "output",             // Main output folder
    "images": "output/images",      // Extracted images folder
    "markdown": "output/markdown",  // Markdown results folder
    "html": "output/html"           // HTML results folder
  },
  "output": {
    "generate_html": true,          // Generate HTML output
    "generate_markdown": true       // Generate Markdown output
  },
  "image_processing": {
    "max_size": 1024,
    "quality": 95
  }
}
```

### Extraction Control

The new `extraction` section allows you to selectively extract content:

- **Extract only highlights**: Set `extract_highlights: true` and `extract_handwriting: false`
- **Extract only handwriting**: Set `extract_highlights: false` and `extract_handwriting: true`  
- **Extract both** (default): Set both to `true`
- **Extract nothing**: Set both to `false` (not recommended)

## 🚀 Quick Start

### Option 1: Batch Processing (Recommended)

Process multiple PDFs with organized output:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your PDFs in the read folder
cp your_document.pdf read/
cp another_document.pdf read/

# 3. Run batch processing
python batch_processor.py
```

**Output Structure:**

- `output/images/{pdf_name}/` - Extracted images with extraction summaries
- `output/markdown/{pdf_name}_{engine}_results.md` - Markdown with text results
- `output/html/{pdf_name}_{engine}_results.html` - HTML for easy viewing

### Option 2: Single PDF Processing

For processing individual PDFs:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Extract images from PDF
python extracting_highlights_images.py

# 3. Run OCR processing
python unified_ocr_processor.py
```

## 🔍 OCR Engine Comparison

### Tesseract (Local)

- ✅ **Free and local** - No API costs or internet required
- ✅ **Privacy** - All processing done locally
- ✅ **Fast setup** - Just install via package manager
- ❌ **Lower accuracy** - Especially on academic documents
- ❌ **No LaTeX** - Plain text output only

**Best for**: Simple documents, privacy-sensitive content, cost-conscious users

### Mathpix (API-based)

- ✅ **High accuracy** - Optimized for academic content (~95%+ accuracy)
- ✅ **LaTeX support** - Extracts mathematical expressions
- ✅ **Smart formatting** - Better handling of tables and complex layouts
- ✅ **No local setup** - Works immediately with API keys
- ❌ **Paid service** - API costs apply
- ❌ **Internet required** - Must be online to process

**Best for**: Academic papers, mathematical content, professional documents

## 📊 Recent Performance Results

**Current System Performance:**

- **Mathpix Engine**: 100% success rate on test documents with 73.8% average confidence
- **Tesseract Engine**: 73.1% success rate with 80.4% average confidence
- **Processing Efficiency**: Reduced from 211 individual regions to 26 grouped images (87.7% reduction)
- **LaTeX Support**: Mathpix provides mathematical notation extraction with LaTeX formatting

**Test Results Example** (Coldwell22.pdf):

- **Total Images Processed**: 26 grouped extractions
- **Mathpix**: 26/26 successful extractions (100.0% success)
- **Content Types**: Academic paper with mathematical formulas, tables, and technical content
- **Output Quality**: High-quality text extraction with preserved formatting

## 🔧 Advanced Usage

### Batch Processing Multiple PDFs

For processing multiple documents efficiently, see the detailed [Batch Processing Guide](BATCH_PROCESSING.md):

```bash
python batch_processor.py
```

### Switching OCR Engines

Edit `config.json` and change the `ocr_engine` value:

```json
{
  "ocr_engine": "mathpix"  // or "tesseract"
}
```

### Mathpix Setup

For high-quality academic document processing, see the [Mathpix Setup Guide](MATHPIX_SETUP.md):

1. Sign up at [mathpix.com](https://mathpix.com/)
2. Get your API credentials
3. Add them to `config.json`:

```json
{
  "mathpix": {
    "app_id": "your_app_id_here",
    "app_key": "your_app_key_here"
  }
}
```

### Parameter Tuning

Optimize extraction parameters for your specific documents:

```bash
python tune_extraction_params.py
```

### Selective Content Extraction

Control what types of content to extract by editing the `extraction` section in `config.json`:

**Extract only yellow highlights:**

```json
{
  "extraction": {
    "extract_highlights": true,
    "extract_handwriting": false
  }
}
```

**Extract only red handwriting/annotations:**

```json
{
  "extraction": {
    "extract_highlights": false,
    "extract_handwriting": true
  }
}
```

This is useful when:

- You only want to extract specific types of annotations
- Processing time needs to be reduced
- Your document only contains one type of annotation
- You want to analyze highlights vs handwritten notes separately

### Custom HTML Styling

The `convert_to_html.py` script includes built-in CSS styling. Modify the template to customize appearance.

## 📋 Processing Workflow

1. **PDF Analysis**: Scans PDF for yellow highlights and red annotations
2. **Color Detection**: Uses HSV color space for accurate color matching
3. **Region Extraction**: Crops image regions around detected annotations
4. **Intelligent Grouping**: Merges nearby regions using proximity algorithms (reduces output by ~87%)
5. **OCR Processing**: Extracts text using selected engine (Tesseract or Mathpix)
6. **Output Generation**: Creates formatted Markdown and HTML files with embedded images
7. **Organization**: Saves results in structured output folders for easy access

## 📂 Output Examples

### File Structure After Processing

```txt
output/
├── images/
│   └── document_name/
│       ├── extraction_summary.json    # Metadata about extractions
│       ├── page_1_yellow_highlight_group_1.png
│       ├── page_1_red_mark_group_2.png
│       └── ...
├── markdown/
│   ├── document_name_mathpix_results.md
│   └── document_name_tesseract_results.md
└── html/
    ├── document_name_mathpix_results.html
    └── document_name_tesseract_results.html
```

### Markdown Output Sample

```markdown
# PDF Highlights & Annotations - MATHPIX OCR Results

*Generated using MATHPIX OCR engine*

## Processing Statistics
- **Total Images Processed**: 26
- **Successful Extractions**: 26 
- **Success Rate**: 100.0%
- **Average Confidence**: 73.8%

## Extract 1: page_1_yellow_highlight_group_1.png
![Extract 1](output/images/document/page_1_yellow_highlight_group_1.png)

**Confidence**: 99.6%

### Extracted Text
To evaluate the latency and accuracy of these models...

### LaTeX Format

```latex
\text{Mathematical expressions preserved}
```

### HTML Output Features

- Clean, responsive design
- Embedded images with proper paths
- OCR engine identification badges
- Confidence indicators for each extraction
- Professional CSS styling
- Easy navigation between extracts

## 🛠️ Troubleshooting

### Tesseract Issues

- **Install Tesseract**: `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Ubuntu)
- **Check path**: Script auto-detects common installation paths
- **Language packs**: Install additional languages if needed: `brew install tesseract-lang`

### Mathpix Issues

- **API limits**: Check your plan limits at [mathpix.com](https://mathpix.com/)
- **Credentials**: Ensure API keys are correctly set in `config.json`
- **Network**: Verify internet connection for API calls
- **Rate limiting**: Mathpix has rate limits; batch processing handles this automatically

### No Text Extracted

- **Image quality**: Check if extracted images are clear and readable
- **Color detection**: Verify highlights/annotations are in correct colors (yellow/red)
- **OCR confidence**: Low confidence may indicate poor image quality
- **PDF resolution**: Higher resolution PDFs generally produce better results

## 📈 Performance Tips

1. **Use Mathpix for academic content** - Significantly better accuracy on papers with mathematical content
2. **Adjust extraction parameters** - Use `tune_extraction_params.py` for optimization
3. **Batch processing** - Use `batch_processor.py` for multiple PDFs
4. **Check extraction summaries** - Review `extraction_summary.json` files for processing details
5. **Optimize image quality** - Ensure PDFs are high resolution for better OCR results

## 🔄 Available Tools

### Core Processing Scripts

- `batch_processor.py` - **Recommended**: Process multiple PDFs with organized output
- `unified_ocr_processor.py` - Main OCR processor supporting both engines
- `extracting_highlights_images.py` - PDF extraction with intelligent grouping
- `convert_to_html.py` - Convert markdown results to HTML format

### Specialized Tools

- `tune_extraction_params.py` - Parameter optimization tool

### Documentation

- `BATCH_PROCESSING.md` - Detailed batch processing guide
- `MATHPIX_SETUP.md` - Complete Mathpix setup instructions
- `CONFIG_TEMPLATE.md` - Configuration file templates

## 📋 Requirements

### Dependencies

All required packages are listed in `requirements.txt`:

- **PyMuPDF** (>=1.23.0) - PDF processing and manipulation
- **matplotlib** (>=3.8.0) - Image processing and visualization
- **numpy** (>=1.24.0) - Numerical computations
- **opencv-python** (>=4.8.0) - Computer vision and image processing
- **Pillow** (>=10.0.0) - Image manipulation
- **pytesseract** (>=0.3.10) - Tesseract OCR interface
- **markdown** (>=3.4.0) - Markdown processing

### System Requirements

- **Python 3.8+**
- **Tesseract OCR** (for local processing)
- **Internet connection** (for Mathpix API)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Issues**: Found a bug or have a feature request? Open an issue
2. **Submit Pull Requests**: Improvements to code, documentation, or new features
3. **Share Results**: Test the system with different types of documents and share feedback
4. **Documentation**: Help improve guides and examples

### Development Setup

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📜 License

This project is open source and available under the MIT License.

---

## 🔗 Quick Links

- [Batch Processing Guide](BATCH_PROCESSING.md) - Process multiple PDFs efficiently
- [Mathpix Setup Guide](MATHPIX_SETUP.md) - Get started with high-quality OCR
- [Configuration Template](CONFIG_TEMPLATE.md) - Configuration examples and options

**Last Updated**: July 2025
