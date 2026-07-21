# Best Practices: Document Processing Workflows

> Technique key: `document_processing` — Taking action on content within files (PDFs, Word docs, images)

## Workflow Design

Document processing workflows extract and act on content from files like PDFs, images, Word documents, and spreadsheets.

### Core Architecture Pattern
Trigger → Capture Binary → Extract Text → Parse/Transform → Route to Destination → Notify

### Common Flow Patterns

**Simple:** Gmail Trigger → Check file type → Extract from File → DataTable → Slack notification
**Complex with AI:** Webhook → File Type Check → OCR (if image) → AI Extract → Validate → CRM Update
**Batch:** Schedule Trigger → Fetch Files → Split In Batches → Sub-workflow → Merge Results → Bulk Update
**Multi-Source:** Multiple Triggers → Set common fields → Standardize → Process → Store

### Branching Strategy
Always branch early: File Type Branching (IF/Switch for PDF vs image vs spreadsheet), Provider Branching, Quality Branching.

## Binary Data Management

Documents are handled as binary data. Reference with `{{ $('Node Name').item.binary.property_name }}` or `{{ $binary.property_name }}`.

Many nodes (Code, Edit Fields, AI) drop binary data by default. Use parallel branches: one for processing, one to preserve the original file. Rejoin with Merge in pass-through mode. Alternative: enable "Include Other Input Fields" on Edit Fields.

File metadata: `{{ $json.documents[0].mimetype }}`, filename, size (from form trigger).

## Text Extraction Strategy

### CRITICAL: File Type Detection
ALWAYS check file type before using Extract from File. Use IF/Switch node to check file extension or MIME type first.

Extract from File operations: Extract from PDF, Extract from MS Excel, Extract from MS Word, Extract from CSV, Extract from HTML, Extract from RTF, Extract from Text File.

### Decision Tree
1. Check file type → Route to appropriate extraction
2. Scanned image/PDF → OCR (OCR.space, AWS Textract, Google Vision)
3. Structured invoice/receipt → Mindee or AI extraction
4. Text-based → Extract from File with correct operation

### Fallback Strategy
Check if text extraction returns empty → route to OCR → if OCR fails → manual review.

## AI-Powered Extraction

**Option 1 (Recommended):** Pass binary data to Document Loader (Data Source: "Binary") → Connect to AI Agent
**Option 2:** Extract raw text → Pass to AI Agent with structured prompt

**Document Classification Flow:** AI classification → Route to type-specific sub-workflow.

## Recommended Nodes

### Triggers
- **Gmail Trigger**: MUST set "Simplify" to FALSE and "Download Attachments" to TRUE. Use "Property Prefix Name" (e.g., "attachment_")
- **Email Read (IMAP)**: Enable "Download Attachments"
- **HTTP Webhook**: Enable "Raw Body" for binary data
- **Google Drive Trigger**: Monitor folders for new documents

### Text Extraction
- **Extract from File**: MUST check file type first. For multiple file types a Switch node MUST split to different extraction nodes
- **AWS Textract**: Advanced OCR with table/form detection
- **Mindee**: Specialized invoice/receipt parsing

### Data Processing
- **AI Agent**: Intelligent parsing with structured output tools
- **LLM Chain**: Document classification and data extraction
- **Document Loader**: Use "Binary" data source for AI processing
- **Structured Output Parser**: Ensure AI outputs match JSON schema
- **Simple Vector Store** (RECOMMENDED): No external dependencies, works out of the box

### Flow Control
- **Split In Batches**: Process 5-10 files at a time. Output 0 = done, Output 1 = loop
- **Merge**: Combine branches, use "Pass Through" for binary preservation. Waits for ALL branches
- **Edit Fields (Set)**: Better for combining independent/optional branches
- **Execute Workflow**: Delegate heavy processing to sub-workflow. Use `{{ $workflow.id }}` expression

### Data Destinations
DataTable, Google Sheets, Postgres, MySQL, MongoDB

### Utilities
- **IF/Switch**: Route by file type, extraction quality, classification
- **Code**: Custom validation and regex extraction
- **HTTP Request**: Call OCR APIs. NEVER set API keys directly — use credentials

## Common Pitfalls to Avoid

- **Binary Data Loss**: Use Merge node to reattach binary; or configure "Include Other Input Fields"
- **Incorrect OCR Fallback**: Always check if extraction result is empty
- **API Format Mismatches**: Check if API needs multipart/form-data vs Base64
- **Memory Overload**: Process sequentially or in small batches; delegate to sub-workflow
- **Duplicate Processing**: Configure email triggers to mark as read; implement deduplication