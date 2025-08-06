# better-research

A comprehensive research workflow tool that integrates Zotero, reMarkable, and OCR to streamline the process from paper discovery to annotated outputs. This tool helps extract annotations from PDFs to markdown files, with support for handwriting OCR and automated synchronization across your research tools.

This tool was mostly written by *Github Copilot* with minor corrections from me. So, I don't know what the license for it should be. You should read the more detailed [README](./docs/README.md) next.

```mermaid
sequenceDiagram
    participant User
    participant WorkflowOrchestrator
    participant ZoteroSync
    participant RemarkableSync
    participant BatchProcessor

    User->>WorkflowOrchestrator: Run workflow (full or steps)
    WorkflowOrchestrator->>ZoteroSync: Sync PDFs from Zotero
    ZoteroSync-->>WorkflowOrchestrator: PDFs downloaded to 'to-read'
    WorkflowOrchestrator->>RemarkableSync: Upload PDFs to reMarkable
    RemarkableSync-->>WorkflowOrchestrator: PDFs uploaded
    WorkflowOrchestrator->>RemarkableSync: Download annotated PDFs
    RemarkableSync-->>WorkflowOrchestrator: Annotated PDFs downloaded to 'read'
    WorkflowOrchestrator->>BatchProcessor: Process annotations (OCR, extract)
    BatchProcessor-->>WorkflowOrchestrator: Output markdown/HTML
    WorkflowOrchestrator-->>User: Print summary/results
```

## 🚀 New Features

- **Zotero Integration**: Automatically download tagged papers from your Zotero library
- **reMarkable Sync**: Bidirectional sync with reMarkable tablet for annotation
- **Workflow Orchestration**: Complete end-to-end automation from library to processed outputs
- **Batch Processing**: Process multiple papers efficiently

## 📋 Quick Start

1. **Setup**: Configure Zotero and reMarkable integration
2. **Tag**: Add `rm_to_sync` tag to papers in Zotero
3. **Run**: Execute the complete workflow
4. **Annotate**: Read and annotate on reMarkable
5. **Process**: Generate markdown and HTML outputs

```bash
# Complete workflow
python workflow_orchestrator.py --full

# Individual steps
python workflow_orchestrator.py --steps zotero upload download process
```

## 📚 Documentation

- [Workflow Guide](./docs/WORKFLOW_GUIDE.md) - Complete workflow overview
- [Zotero Setup](./docs/ZOTERO_SETUP.md) - Zotero integration configuration
- [reMarkable Setup](./docs/REMARKABLE_SETUP.md) - reMarkable sync setup
- [Batch Processing](./docs/BATCH_PROCESSING.md) - OCR and output generation
- [Configuration](./docs/CONFIG_TEMPLATE.md) - Configuration templates

## TO-DO

- [x] Integrate with Zotero
- [x] Integrate with Remarkable APIs
- [ ] Add support for different annotation workflows
- [ ] Implement citation extraction and linking
- [ ] Add web interface for workflow management
