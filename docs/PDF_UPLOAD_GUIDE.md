# 📤 PDF Upload Feature Documentation

## Overview

The PDF Upload feature allows you to add your own research papers directly from your file system to the Research Assistant. This is particularly useful for:

- 🔒 **Private or unpublished papers** that aren't available in public databases
- 📚 **Papers you already have** saved on your computer
- 💼 **Internal company research** documents
- 📖 **Subscription-only papers** from journals you have access to

## Features

### Intelligent PDF Parsing

The system automatically extracts:
- **Title**: From the first page of the PDF
- **Authors**: Names and affiliations
- **Abstract**: Full abstract text
- **Publication Year**: When available
- **Keywords**: Research keywords and topics
- **Full Text**: Complete paper content for embedding
- **Paper Type**: Automatically classified (Journal/Conference/Review)

### Seamless Integration

Uploaded papers are:
- ✅ Added to the FAISS vector database
- ✅ Available in semantic similarity searches
- ✅ Included in literature review generation
- ✅ Displayed alongside searched papers
- ✅ Given high relevance scores (0.85) by default

## How to Use

### Step 1: Access Upload Interface

1. Launch the application: `python main.py`
2. Open your browser to `http://localhost:7860`
3. At the top of the page, click **"📤 Upload Your Own Papers"** accordion

### Step 2: Select PDF Files

1. Click **"📁 Select PDF Files"** button
2. Choose one or multiple PDF files from your computer
3. Supported format: `.pdf` only

### Step 3: Upload & Parse

1. Click **"📤 Upload & Parse Papers"** button
2. Wait for the system to:
   - Parse each PDF file
   - Extract metadata automatically
   - Add papers to the vector database
3. Review the success message showing:
   - Number of papers uploaded
   - Title and authors for each paper
   - Confirmation of database storage

### Step 4: Use Uploaded Papers

Once uploaded, your papers are available for:

- **Search Results**: Combined with database searches
- **Similarity Search**: Find related papers using FAISS
- **Literature Reviews**: Included in generated reviews
- **Query Augmentation**: Can be selected for iterative search

## Technical Details

### PDF Parsing Algorithm

```python
# Extraction Process
1. Open PDF with PyMuPDF (fitz)
2. Extract text from first 3 pages (for metadata)
3. Extract full text (for embedding)
4. Pattern matching for:
   - Title (first substantial line)
   - Authors (name patterns)
   - Abstract (section markers)
   - Year (date patterns)
   - Keywords (keyword sections)
5. Classify paper type
6. Create paper data object
```

### Data Structure

Uploaded papers are stored with:

```python
{
    'paper_id': 'uploaded_XXXXXXXX',
    'title': 'Extracted Title',
    'authors': ['Author 1', 'Author 2'],
    'abstract': 'Full abstract text...',
    'publication_date': 'YYYY',
    'journal': 'User Uploaded Paper',
    'citation_count': 0,
    'relevance_score': 0.85,  # High by default
    'confidence_score': 0.9,
    'url': 'file:///path/to/pdf',
    'doi': None,
    'keywords': ['keyword1', 'keyword2'],
    'categories': ['User Upload'],
    'source': 'user_upload',
    'paper_type': 'journal/conference/review',
    'full_text': 'First 10k characters...'
}
```

### FAISS Integration

- Papers are embedded using Google's `text-embedding-004` model
- Embedding text includes: title + abstract + keywords + full text excerpt
- Stored with session ID: `{session_id}_uploads`
- Available for similarity search immediately after upload

## Best Practices

### 1. PDF Quality

✅ **Good PDFs:**
- Text-based (not scanned images)
- Clear structure with abstract and sections
- Standard research paper format
- Reasonable file size (< 50 MB)

❌ **Problematic PDFs:**
- Image-only scans (no extractable text)
- Heavily encrypted or protected
- Non-standard layouts
- Very large files (> 100 MB)

### 2. Batch Uploads

- Upload multiple papers at once for efficiency
- Recommended: 5-10 papers per batch
- Monitor the parsing progress in the status message

### 3. Organization

- Upload papers before starting your research queries
- Use descriptive filenames (they're used as fallback titles)
- Group related papers in single upload sessions

## Troubleshooting

### "Failed to parse PDF"

**Possible causes:**
- PDF is image-based (scanned document)
- File is corrupted
- File is encrypted or protected

**Solutions:**
- Try using OCR software to create text-based PDF
- Verify file integrity
- Remove password protection

### "No abstract available"

**Cause:**
- Abstract section not detected in standard format

**Impact:**
- Paper still added to database
- Uses first paragraph as fallback
- May have slightly lower search relevance

### Upload button not working

**Solutions:**
1. Ensure PDFs are selected (check file picker)
2. Wait for pipeline initialization
3. Check browser console for errors
4. Refresh the page and try again

## Limitations

1. **Text Extraction Only**: Cannot process image-only PDFs
2. **Metadata Accuracy**: Depends on PDF structure and formatting
3. **File Size**: Very large PDFs may take longer to process
4. **Language**: Best results with English-language papers

## Privacy & Security

- ✅ **Local Processing**: All PDFs parsed on your machine
- ✅ **No Upload to Cloud**: Files stay on your system
- ✅ **Vector Storage**: Only embeddings stored, not full PDFs
- ✅ **Session Based**: Data isolated by session ID

## Examples

### Example 1: Single Paper Upload

```
1. Click "Upload Your Own Papers"
2. Select "my_research_paper.pdf"
3. Click "Upload & Parse Papers"
4. See: "✅ Successfully uploaded 1 paper!"
5. Paper now available in all searches
```

### Example 2: Batch Upload

```
1. Click "Upload Your Own Papers"
2. Select multiple files:
   - paper1.pdf
   - paper2.pdf
   - paper3.pdf
3. Click "Upload & Parse Papers"
4. See details for each paper uploaded
5. All papers added to FAISS database
```

### Example 3: Integration with Search

```
1. Upload 3 private papers
2. Run search query: "machine learning applications"
3. Results include:
   - Your 3 uploaded papers (if relevant)
   - Papers from arXiv, PubMed, etc.
4. Select papers from both sources
5. Generate literature review including all papers
```

## API Integration

For programmatic access:

```python
from src.agents.pdf_parser import PDFPaperParser
from src.agents.embedding_agent import EmbeddingAgent

# Initialize
parser = PDFPaperParser()
embedding_agent = EmbeddingAgent()

# Parse PDF
paper_data = parser.parse_pdf_file("path/to/paper.pdf")

# Add to database
if paper_data:
    embedding_agent.vector_db.add_papers_batch(
        papers=[paper_data],
        search_query="user_upload",
        session_id="my_session"
    )
```

## Future Enhancements

Planned improvements:
- 📸 OCR support for scanned PDFs
- 🌐 Multi-language support
- 📊 Improved metadata extraction
- 🔗 Citation graph extraction
- 📁 Folder/directory uploads
- 💾 Export uploaded papers list

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in upload status
3. Check terminal logs for detailed errors
4. Submit issues on GitHub

---

**Version**: 1.0.0  
**Last Updated**: October 11, 2025  
**Feature Status**: ✅ Production Ready
