# Configuration Template

Copy this to `config.json` and customize for your needs:

## For Tesseract (Local OCR)

```json
{
  "ocr_engine": "tesseract",
  "mathpix": {
    "app_id": "",
    "app_key": ""
  },
  "tesseract": {
    "enabled": true,
    "language": "eng"
  },
  "extraction": {
    "extract_highlights": true,
    "extract_handwriting": true
  },
  "folders": {
    "input": "read",
    "output": "output",
    "images": "output/images",
    "markdown": "output/markdown",
    "html": "output/html"
  },
  "output": {
    "generate_html": true,
    "generate_markdown": true
  },
  "image_processing": {
    "max_size": 1024,
    "quality": 95
  }
}
```

## For Mathpix (API OCR)

```json
{
  "ocr_engine": "mathpix",
  "mathpix": {
    "app_id": "your_mathpix_app_id_here",
    "app_key": "your_mathpix_app_key_here"
  },
  "tesseract": {
    "enabled": true,
    "language": "eng"
  },
  "extraction": {
    "extract_highlights": true,
    "extract_handwriting": true
  },
  "folders": {
    "input": "read",
    "output": "output",
    "images": "output/images",
    "markdown": "output/markdown",
    "html": "output/html"
  },
  "output": {
    "generate_html": true,
    "generate_markdown": true
  },
  "image_processing": {
    "max_size": 1024,
    "quality": 95
  }
}
```

## Configuration Options

- **ocr_engine**: `"tesseract"` or `"mathpix"`
- **mathpix.app_id**: Your Mathpix App ID from mathpix.com
- **mathpix.app_key**: Your Mathpix App Key from mathpix.com
- **tesseract.language**: Language code for Tesseract (e.g., "eng", "fra", "deu")
- **extraction.extract_highlights**: Extract yellow highlights (true/false)
- **extraction.extract_handwriting**: Extract red handwriting/annotations (true/false)
- **folders.input**: Input folder for PDF files
- **folders.output**: Main output folder
- **folders.images**: Folder for extracted images
- **folders.markdown**: Folder for markdown results
- **folders.html**: Folder for HTML results
- **output.generate_html**: Whether to generate HTML output
- **output.generate_markdown**: Whether to generate Markdown output
- **image_processing.max_size**: Maximum image dimension for processing
- **image_processing.quality**: Image quality for processing (1-100)

## Extraction Examples

**Extract only highlights (no red annotations):**

```json
{
  "extraction": {
    "extract_highlights": true,
    "extract_handwriting": false
  }
}
```

**Extract only handwriting (no yellow highlights):**

```json
{
  "extraction": {
    "extract_highlights": false,
    "extract_handwriting": true
  }
}
```

**Extract both (default):**

```json
{
  "extraction": {
    "extract_highlights": true,
    "extract_handwriting": true
  }
}
```

## Example Configuration Files

The workspace includes example configuration files:

- `config.json` - Default configuration (extracts both)
- `config_highlights_only.json` - Extract only yellow highlights
- `config_handwriting_only.json` - Extract only red handwriting

To use a specific configuration:

```bash
# Copy the desired config to use as main config
cp config_highlights_only.json config.json

# Or specify config file in your script
python batch_processor.py --config config_highlights_only.json
```
