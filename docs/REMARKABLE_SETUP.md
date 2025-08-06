# reMarkable Setup Guide

This guide covers setting up reMarkable integration for the better-research workflow.

## Prerequisites

### 1. Install rmapi

[rmapi](https://github.com/ddvk/rmapi) is the command-line tool for interacting with reMarkable tablets.

On MacOS, you can use the following:

```bash
brew install io41/tap/rmapi
```

#### Installation Options

**Option A: Using pip (recommended)**

```bash
pip install rmapi
```

**Option B: Using binary releases**

1. Download from <https://github.com/juruen/rmapi/releases>
2. Extract and add to your PATH

### 2. Set up rmapi authentication

#### First-time setup

```bash
rmapi
```

This will prompt you to:

1. Go to <https://my.remarkable.com/connect/desktop>
2. Enter the one-time code shown
3. Complete the device registration

#### Verify connection

```bash
rmapi ls
```

You should see your reMarkable folder structure.

## Configuration

Add reMarkable settings to your `config.json`:

```json
{
  "remarkable": {
    "enabled": true,
    "to_read_folder": "to-read",
    "read_folder": "read",
    "sync_uploads": true,
    "sync_downloads": true,
    "delete_after_upload": false,
    "delete_after_download": false
  }
}
```

### Configuration Options

- **enabled**: Enable/disable reMarkable sync
- **to_read_folder**: Folder name on reMarkable for new papers
- **read_folder**: Folder name on reMarkable for annotated papers
- **sync_uploads**: Upload files from local to-read folder
- **sync_downloads**: Download annotated files from reMarkable
- **delete_after_upload**: Remove local files after upload (not recommended)
- **delete_after_download**: Remove files from reMarkable after download

## Folder Structure Setup

### On reMarkable

The sync expects this folder structure on your reMarkable:

```text
/ (root)
├── to-read/          # New papers to read and annotate
└── read/             # Finished papers with annotations
```

These folders will be created automatically if they don't exist.

### Local Structure

```text
better-research/
├── to-read/          # PDFs ready to upload to reMarkable
├── read/             # Annotated PDFs downloaded from reMarkable
└── output/           # Generated markdown and HTML files
```

## Usage Workflow

### 1. Upload Phase

```bash
python remarkable_sync.py
```

Or using the orchestrator:

```bash
python workflow_orchestrator.py --steps upload
```

This will:

- Upload all PDFs from `to-read/` to reMarkable `to-read/` folder
- Skip files that already exist on reMarkable

### 2. Reading and Annotation

On your reMarkable:

1. Open papers from the `to-read` folder
2. Add highlights, notes, and annotations
3. When finished, move papers to the `read` folder

### 3. Download Phase

```bash
python workflow_orchestrator.py --steps download
```

This will:

- Download annotated PDFs from reMarkable `read/` folder
- Save them to local `read/` folder
- Skip files that already exist locally

### 4. Process Annotations

```bash
python workflow_orchestrator.py --steps process
```

This runs OCR on the annotations and generates output files.

## Troubleshooting

### Connection Issues

**Problem**: rmapi commands fail with authentication errors

**Solutions**:

- Re-run `rmapi` to re-authenticate
- Check your internet connection
- Verify your reMarkable is connected to WiFi

**Problem**: "rmapi not found" error

**Solutions**:

- Install rmapi: `pip install rmapi`
- Check that rmapi is in your PATH: `which rmapi`

### Sync Issues

**Problem**: Files not uploading

**Solutions**:

- Check file permissions in `to-read/` folder
- Verify PDF files are valid
- Check reMarkable storage space

**Problem**: Files not downloading

**Solutions**:

- Check that files exist in reMarkable `read/` folder
- Verify local `read/` folder permissions
- Check available disk space

### Performance Tips

**Large file uploads**:

- rmapi may be slow for large files
- Consider using WiFi instead of cellular on reMarkable
- Upload during off-peak hours for better performance

**Batch operations**:

- The sync includes rate limiting to avoid overwhelming the API
- For many files, consider running overnight

## Advanced Usage

### Manual Operations

#### List reMarkable folders

```bash
rmapi ls
```

#### Upload single file

```bash
rmapi put file.pdf to-read/file.pdf
```

#### Download single file  

```bash
rmapi get read/file.pdf local-file.pdf
```

#### Create folders

```bash
rmapi mkdir new-folder
```

### Custom rmapi Configuration

You can customize rmapi behavior by editing `~/.rmapi/rmapi.conf`:

```json
{
  "auth": "...",
  "sync": {
    "enabled": true,
    "interval": 300
  }
}
```

### Alternative Tools

If rmapi doesn't work for your setup, consider:

- **rmapy**: Python library for reMarkable API
- **remarkable-cli**: Alternative command-line tool
- **rmfuse**: Mount reMarkable as filesystem

## Security Notes

- rmapi stores authentication tokens locally
- Keep your authentication tokens secure
- Re-authenticate periodically for security
- Don't share configuration files containing tokens

## Limitations

- rmapi requires reMarkable cloud sync to be enabled
- Some reMarkable features may not be supported
- Sync speed depends on internet connection
- File organization must match expected folder structure
