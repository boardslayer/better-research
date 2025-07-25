# Workflow Orchestrator Guide

The Workflow Orchestrator provides a unified interface to manage the complete research workflow from Zotero to processed annotations.

## Overview

The orchestrator manages four key steps:

1. **Zotero Sync** - Download tagged PDFs from Zotero library
2. **reMarkable Upload** - Upload PDFs to reMarkable for annotation
3. **reMarkable Download** - Download annotated PDFs back
4. **Batch Processing** - Extract annotations and generate outputs

## Quick Start

### Complete Workflow
```bash
python workflow_orchestrator.py --full
```

### Specific Steps
```bash
# Run only Zotero sync
python workflow_orchestrator.py --steps zotero

# Upload to reMarkable and download annotated files
python workflow_orchestrator.py --steps upload download

# Process annotations only
python workflow_orchestrator.py --steps process
```

## Step-by-Step Guide

### Step 1: Initial Setup

1. **Configure Zotero** (see [ZOTERO_SETUP.md](./ZOTERO_SETUP.md))
   - Get API credentials
   - Add to config.json

2. **Configure reMarkable** (see [REMARKABLE_SETUP.md](./REMARKABLE_SETUP.md))
   - Install and setup rmapi
   - Test connection

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Tag Papers in Zotero

1. Open your Zotero library
2. Find papers you want to read
3. Add the tag `rm_to_sync` to those items
4. Ensure papers have PDF attachments

### Step 3: Run the Workflow

#### Option A: Complete Automated Workflow
```bash
python workflow_orchestrator.py --full
```

This runs all four steps automatically.

#### Option B: Manual Step-by-Step

```bash
# 1. Download from Zotero
python workflow_orchestrator.py --steps zotero

# 2. Upload to reMarkable
python workflow_orchestrator.py --steps upload

# 3. Read and annotate on reMarkable
# (Move annotated papers to 'read' folder when done)

# 4. Download annotated papers
python workflow_orchestrator.py --steps download

# 5. Process annotations
python workflow_orchestrator.py --steps process
```

## Configuration

### Complete Configuration Example

```json
{
  "ocr_engine": "mathpix",
  "folders": {
    "to_read": "to-read",
    "input": "read", 
    "output": "output",
    "images": "output/images",
    "markdown": "output/markdown",
    "html": "output/html"
  },
  "zotero": {
    "library_id": "12345678",
    "library_type": "user",
    "api_key": "your_api_key_here",
    "sync_tag": "rm_to_sync",
    "processed_tag": "rm_processed"
  },
  "remarkable": {
    "enabled": true,
    "to_read_folder": "to-read",
    "read_folder": "read",
    "sync_uploads": true,
    "sync_downloads": true,
    "delete_after_upload": false,
    "delete_after_download": false
  },
  "logging": {
    "level": "INFO"
  }
}
```

### Minimal Configuration

If you only want to use some features:

```json
{
  "folders": {
    "input": "read",
    "output": "output"
  },
  "zotero": {
    "library_id": "12345678",
    "api_key": "your_api_key_here"
  }
}
```

## Command Line Options

```bash
python workflow_orchestrator.py [OPTIONS]

Options:
  -c, --config PATH     Configuration file (default: config.json)
  -f, --full           Run complete workflow
  -s, --steps STEPS    Run specific steps
  
Steps:
  zotero               Download PDFs from Zotero
  upload               Upload PDFs to reMarkable  
  download             Download annotated PDFs
  process              Extract annotations and generate outputs
```

## Folder Structure

```
better-research/
├── to-read/                    # PDFs ready for reMarkable
├── read/                       # Annotated PDFs from reMarkable
├── output/                     # Generated content
│   ├── images/                 # Extracted annotation images
│   ├── markdown/               # Markdown files with OCR text
│   └── html/                   # HTML versions for viewing
├── config.json                 # Configuration file
└── workflow_orchestrator.py    # Main workflow script
```

## Output Examples

### Console Output
```
🔬 Research Workflow Orchestrator
========================================
🚀 Starting complete research workflow...
🔄 Step 1: Syncing from Zotero...
✅ Zotero sync complete: 3 files downloaded
📤 Step 2: Uploading to reMarkable...
✅ reMarkable upload complete: 3 files uploaded
📥 Step 3: Downloading annotated files from reMarkable...
✅ reMarkable download complete: 2 files downloaded
🔧 Step 4: Processing annotations...
✅ Batch processing complete

==================================================
📊 WORKFLOW SUMMARY
==================================================
🔄 Zotero Downloads:      3
📤 reMarkable Uploads:    3
📥 reMarkable Downloads:  2
🔧 Batch Processing:      ✅ Success
==================================================
📁 Folders:
   • To-Read: to-read
   • Read:    read  
   • Output:  output
==================================================
```

### Generated Files

For each processed PDF, you get:

```
output/
├── images/
│   └── paper_name/
│       ├── page_1_highlight_1.png
│       ├── page_2_annotation_1.png
│       └── ...
├── markdown/
│   └── paper_name_mathpix_results.md
└── html/
    └── paper_name_mathpix_results.html
```

## Troubleshooting

### Common Issues

**"No files downloaded from Zotero"**
- Check Zotero API credentials
- Verify items have `rm_to_sync` tag
- Ensure items have PDF attachments

**"reMarkable sync failed"**
- Check rmapi installation: `rmapi --help`
- Verify authentication: `rmapi ls`
- Check internet connection

**"Batch processing failed"**
- Check OCR engine configuration
- Verify PDFs are in `read/` folder
- Check file permissions

### Debug Mode

Enable detailed logging:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Test Individual Components

```bash
# Test Zotero only
python zotero_sync.py

# Test reMarkable only  
python remarkable_sync.py

# Test OCR processing only
python batch_processor.py
```

## Advanced Usage

### Custom Workflows

Create custom scripts combining steps:

```python
from workflow_orchestrator import WorkflowOrchestrator

# Initialize
orchestrator = WorkflowOrchestrator('my_config.json')

# Custom workflow
orchestrator.step1_zotero_sync()
# ... do something custom ...
orchestrator.step4_batch_processing()
```

### Scheduled Automation

Set up automated syncing with cron:

```bash
# Daily Zotero sync at 9 AM
0 9 * * * cd /path/to/better-research && python workflow_orchestrator.py --steps zotero upload

# Weekly processing on Sundays at 6 PM  
0 18 * * 0 cd /path/to/better-research && python workflow_orchestrator.py --steps download process
```

### Multiple Configurations

Use different configs for different projects:

```bash
python workflow_orchestrator.py --config research_project_1.json --full
python workflow_orchestrator.py --config research_project_2.json --steps process
```

## Performance Tips

- **Large libraries**: Use Zotero collections and tags strategically
- **Many files**: Run upload/download during off-peak hours
- **OCR processing**: Mathpix is faster but costs money; Tesseract is free but slower
- **Storage**: Monitor reMarkable storage space for large PDF collections

## Integration Tips

- **Zotero Collections**: Use collections to organize papers by project
- **reMarkable Folders**: Create project-specific folders beyond to-read/read
- **Output Organization**: Use different output folders for different projects
- **Backup**: Regularly backup your configuration and output folders
