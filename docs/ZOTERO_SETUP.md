# Zotero Configuration Template

To set up Zotero integration, you need to configure the following settings in your `config.json`:

## 1. Get Your Zotero Credentials

### Library ID

1. Go to [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys)
2. Your User ID is shown at the top of the page
3. For group libraries, use the group ID instead

### API Key

1. Go to [https://www.zotero.org/settings/keys](https://www.zotero.org/settings/keys)
2. Click "Create new private key"
3. Give it a descriptive name like "reMarkable Sync"
4. Select the permissions you need:
   - **Read Library**: Required to fetch items
   - **Write Library**: Required to update tags
5. Copy the generated key

## 2. Configuration

Add this to your `config.json`:

```json
{
  "zotero": {
    "library_id": "YOUR_USER_ID_HERE",
    "library_type": "user",
    "api_key": "YOUR_API_KEY_HERE",
    "sync_tag": "rm_to_sync",
    "processed_tag": "rm_processed"
  }
}
```

> **⚠️ SECURITY WARNING**: Never commit your `config.json` file with real API keys and user IDs to version control!
>
> **Recommended security practices:**
>
> - Add `config.json` to your `.gitignore` file
> - Use environment variables for sensitive credentials
> - Consider using a `config.sample.json` template for sharing
> - Use secret management tools in production environments
>
> **Quick fix:** Add this line to your `.gitignore`:
>
> ```
> config.json
> ```

### Configuration Options

- **library_id**: Your Zotero user ID or group ID
- **library_type**: Either "user" or "group"
- **api_key**: Your Zotero API key
- **sync_tag**: Tag used to mark items for sync (default: "rm_to_sync")
- **processed_tag**: Tag added after successful sync (default: "rm_processed")

## 3. Usage Workflow

### Step 1: Tag Items in Zotero

1. In your Zotero library, find papers you want to read
2. Add the tag `rm_to_sync` to those items
3. Make sure the items have PDF attachments

### Step 2: Run Sync

```bash
python zotero_sync.py
```

Or use the workflow orchestrator:

```bash
python workflow_orchestrator.py --steps zotero
```

### Step 3: Automatic Processing

- PDFs are downloaded to the `to-read` folder
- Original tag (`rm_to_sync`) is removed
- New tag (`rm_processed`) is added
- Files are ready for upload to reMarkable

## 4. Troubleshooting

### Authentication Issues

- Verify your User ID and API key are correct
- Check that your API key has the necessary permissions
- Test with a simple call: `python -c "from pyzotero import zotero; z = zotero.Zotero('YOUR_ID', 'user', 'YOUR_KEY'); print(len(z.items()))"`

### No Items Found

- Make sure items have the correct tag (`rm_to_sync`)
- Check that items have PDF attachments
- Verify the library type (user vs group)

### Download Failures

- Check your internet connection
- Verify PDF attachments exist and are accessible
- Check file permissions in the target folder

## 5. Advanced Configuration

### Custom Folder Structure

```json
{
  "folders": {
    "to_read": "custom-to-read-folder"
  }
}
```

### Rate Limiting

The sync includes automatic rate limiting to be respectful of Zotero's API. If you experience issues, you can adjust the delays in the code.

### Multiple Libraries

To sync from multiple libraries, you can create multiple configuration files and run the sync separately for each.
