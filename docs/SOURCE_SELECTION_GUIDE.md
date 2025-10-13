# 🌐 Source Selection Guide

## Overview

The Research Assistant now allows you to **choose which databases to search**, giving you complete control over where your research papers come from. You can search all databases, select specific ones, or even search only your uploaded papers!

## Feature Location

The **Search Sources** selector is located in:
- **Tab:** 🔍 Enhanced Search
- **Section:** ⚙️ Advanced Options (expandable accordion)
- **Control:** 🌐 Search Sources (multi-select checkboxes)

---

## Available Sources

### 1. 📚 Google Scholar (SerpAPI)
- **Coverage:** Comprehensive academic literature across all disciplines
- **Strengths:** 
  - Largest database with millions of papers
  - Includes citations from various sources
  - Best for broad, comprehensive searches
- **Best For:** General academic research, finding highly-cited papers
- **Note:** Requires SerpAPI key (configured in environment)

### 2. 📄 arXiv
- **Coverage:** Preprints in physics, mathematics, computer science, biology, and more
- **Strengths:**
  - Latest research before peer review
  - Full-text access available
  - Strong in STEM fields
- **Best For:** Cutting-edge research, preprints, computer science, physics
- **Free:** No API key required

### 3. 🔬 CrossRef
- **Coverage:** Scholarly publications with DOIs
- **Strengths:**
  - Reliable metadata (DOIs, citations)
  - Peer-reviewed content
  - Good journal coverage
- **Best For:** Finding published, peer-reviewed papers with verified metadata
- **Free:** No API key required

### 4. 🌍 OpenAlex
- **Coverage:** Open-access scholarly works
- **Strengths:**
  - Completely open and free
  - Good coverage of recent papers
  - Fast API response
- **Best For:** Open-access research, alternative to Google Scholar
- **Free:** No API key required

---

## Usage Scenarios

### Scenario 1: Comprehensive Search (Default)
**Use Case:** You want the most complete results possible

**Settings:**
```
✅ Google Scholar (SerpAPI)
✅ arXiv
✅ CrossRef
✅ OpenAlex
```

**Result:** Search all 4 databases simultaneously and get papers from all sources ranked by relevance.

**Example:**
```
Query: "machine learning in healthcare"
Sources: All 4 checked
Result: ~40-80 papers from various sources, ranked by AI relevance
```

---

### Scenario 2: Latest Research Only
**Use Case:** You're interested in the newest papers, including preprints

**Settings:**
```
⬜ Google Scholar (SerpAPI)
✅ arXiv
⬜ CrossRef
✅ OpenAlex
```

**Result:** Focus on arXiv preprints and OpenAlex's recent publications.

**Example:**
```
Query: "transformer models 2024"
Sources: arXiv + OpenAlex
Result: Latest papers and preprints, potentially before peer review
```

---

### Scenario 3: Peer-Reviewed Only
**Use Case:** You need only published, peer-reviewed papers

**Settings:**
```
✅ Google Scholar (SerpAPI)
⬜ arXiv
✅ CrossRef
⬜ OpenAlex
```

**Result:** More established, peer-reviewed content without preprints.

**Example:**
```
Query: "clinical trials diabetes treatment"
Sources: Google Scholar + CrossRef
Result: Published journal articles with citations
```

---

### Scenario 4: Private Papers Only
**Use Case:** You want to search only your uploaded PDFs (no online search)

**Settings:**
```
⬜ Google Scholar (SerpAPI)
⬜ arXiv
⬜ CrossRef
⬜ OpenAlex
```

**Result:** Search performed **only on your uploaded papers** stored in FAISS.

**Example:**
```
Query: "internal company research machine learning"
Sources: None selected
Result: Only papers you've uploaded that match the query
```

**Perfect For:**
- Private/confidential research
- Internal company documents
- Papers behind paywalls you have access to
- Your personal research library

---

### Scenario 5: Hybrid Search
**Use Case:** Combine your private papers with specific databases

**Settings:**
```
⬜ Google Scholar (SerpAPI)
✅ arXiv
⬜ CrossRef
⬜ OpenAlex
+ Your uploaded papers
```

**Result:** Papers from arXiv PLUS relevant papers from your uploads.

**Example:**
```
Query: "neural network architectures"
Sources: arXiv only
Uploaded: 5 private papers on neural nets
Result: Latest arXiv papers + your private papers that match
```

---

## How Source Selection Works

### Backend Process

1. **Source Mapping:**
   ```
   UI Selection          → Database Name
   "Google Scholar..."   → "google_scholar_serpapi"
   "arXiv"              → "arxiv"
   "CrossRef"           → "crossref"
   "OpenAlex"           → "openalex"
   ```

2. **Search Execution:**
   - Selected sources are queried in parallel
   - Each source returns up to N papers
   - Results are deduplicated by DOI/title
   - Papers are validated by Google Gemini AI

3. **Upload Integration:**
   - Uploaded papers are **always** checked for relevance
   - FAISS semantic search finds matching uploads
   - Uploaded papers are merged with database results
   - Combined results sorted by relevance + similarity

4. **Final Ranking:**
   ```
   Score = relevance_score + similarity_score
   ```
   - Papers sorted by combined score
   - Top 20 papers displayed
   - Both database and uploaded papers included

---

## Status Messages

The search results will show which sources were used:

### Example 1: All Sources
```
🎉 Search Complete!

🌐 Sources: Google Scholar Serpapi, Arxiv, Crossref, Openalex
📊 Found: 45 relevant papers from databases in 89.3s
📤 Uploaded Papers: 2 matching papers found in your uploads
🏆 Showing: Top 20 most relevant papers (database + uploads)
🔍 Query: deep learning optimization
```

### Example 2: arXiv Only
```
🎉 Search Complete!

🌐 Sources: Arxiv
📊 Found: 12 relevant papers from databases in 23.1s
🏆 Showing: Top 12 most relevant papers (from databases)
🔍 Query: quantum computing algorithms
```

### Example 3: Uploads Only
```
🎉 Search Complete!

🌐 Sources: None (searching only uploaded papers)
📤 Uploaded Papers: 3 matching papers found in your uploads
🏆 Showing: Top 3 most relevant papers (from uploads)
🔍 Query: internal project documentation
```

---

## Best Practices

### 1. Start Broad, Then Narrow
- First search: Use all sources
- Review results
- Refine search with specific sources if needed

### 2. Match Sources to Field
- **Computer Science:** arXiv + Google Scholar
- **Medical Research:** CrossRef + Google Scholar (peer-reviewed)
- **Physics/Math:** arXiv + OpenAlex
- **Interdisciplinary:** All sources

### 3. API Rate Limits
- Using fewer sources = faster searches
- If one source is slow/failing, disable it temporarily

### 4. Private Research
- Upload papers first
- Then search with no sources selected
- Your papers become a private searchable database

### 5. Combine Intelligently
- Use uploads + arXiv for cutting-edge + your proprietary research
- Use CrossRef + uploads for validated + private content

---

## Performance Considerations

### Search Speed by Source Count

| Sources Selected | Typical Duration | Papers Found |
|-----------------|------------------|--------------|
| 1 source        | 15-30 seconds    | 10-20 papers |
| 2 sources       | 30-50 seconds    | 20-40 papers |
| 3 sources       | 50-70 seconds    | 30-60 papers |
| 4 sources (all) | 70-120 seconds   | 40-80 papers |
| 0 sources       | <5 seconds       | Your uploads only |

**Note:** Times depend on:
- API response times
- Number of results to validate
- Network conditions
- Gemini AI processing time

---

## Troubleshooting

### Problem: "No papers found"

**Solutions:**
1. Check if at least one source is selected OR you have uploaded papers
2. Verify your query isn't too specific
3. Try different source combinations
4. Check API keys are configured (for Google Scholar)

### Problem: "Search too slow"

**Solutions:**
1. Select fewer sources (1-2 instead of all 4)
2. Disable Google Scholar if you have API rate limits
3. Use OpenAlex + arXiv for faster results

### Problem: "Too many irrelevant results"

**Solutions:**
1. Use more specific sources:
   - CrossRef for peer-reviewed only
   - arXiv for preprints only
2. Adjust date filters in Advanced Options
3. Be more specific in your query

### Problem: "Missing recent papers"

**Solutions:**
1. Include arXiv (has latest preprints)
2. Include OpenAlex (updated frequently)
3. Don't rely only on CrossRef (slower to index)

---

## Technical Details

### Source Selection Flow

```
User Interface
    ↓
CheckboxGroup (Gradio)
    ↓
execute_search(search_sources=[...])
    ↓
Map UI names → database names
    ↓
EnhancedResearchPipeline.execute_initial_search(sources=[...])
    ↓
LiteratureAgent.search_papers(sources=[...])
    ↓
Filter available_sources based on selection
    ↓
Execute searches sequentially
    ↓
Deduplicate & validate with Gemini
    ↓
Combine with uploaded papers from FAISS
    ↓
Return ranked results
```

### Code Integration Points

1. **UI Component** (`app_gradio_new.py`):
   ```python
   search_sources = gr.CheckboxGroup(
       label="🌐 Search Sources",
       choices=[...],
       value=[...],  # All selected by default
   )
   ```

2. **Execute Search** (`app_gradio_new.py`):
   ```python
   def execute_search(..., search_sources: List[str], ...):
       enabled_sources = [source_mapping[src] for src in search_sources]
       results = self.pipeline.execute_initial_search(
           query=query,
           filters=filters,
           sources=enabled_sources  # Pass to pipeline
       )
   ```

3. **Literature Agent** (`literature_agent.py`):
   ```python
   async def search_papers_async(..., sources: Optional[List[str]] = None):
       all_sources = [(...), (...), (...), (...)]
       if sources:
           available_sources = [s for s in all_sources if s[0] in sources]
       # Execute only selected sources
   ```

---

## Examples in Action

### Example 1: Finding Latest ML Papers
```
Query: "attention mechanisms transformers"
Sources: ✅ arXiv  ✅ OpenAlex
Year Range: 2023-2024
Result: 25 recent papers on transformer attention, mostly preprints
```

### Example 2: Clinical Research Review
```
Query: "diabetes treatment effectiveness"
Sources: ✅ Google Scholar  ✅ CrossRef
Min Citations: 50
Result: 30 highly-cited, peer-reviewed clinical papers
```

### Example 3: Company Internal + Public Research
```
Query: "product recommendation systems"
Sources: ✅ arXiv
Uploaded: 3 internal research docs
Result: 15 arXiv papers + 3 matching internal docs = 18 total
```

### Example 4: Personal Library Search
```
Query: "specific concept from my papers"
Sources: (none selected)
Uploaded: 50 papers from your library
Result: 8 papers from your library that match the concept
```

---

## Future Enhancements

Planned features for source selection:

1. **Source Statistics:**
   - Show paper count from each source
   - Display success/failure rates per source

2. **Smart Defaults:**
   - Remember your preferred source combinations
   - Suggest sources based on query topic

3. **Source Prioritization:**
   - Weight certain sources higher
   - Custom ranking algorithms per source

4. **Additional Sources:**
   - PubMed (medical research)
   - IEEE Xplore (engineering)
   - Semantic Scholar
   - Microsoft Academic (deprecated but archive access)

5. **Source Health Monitoring:**
   - Real-time API status
   - Auto-disable failing sources

---

## Summary

✅ **Full Control:** Choose exactly which databases to search  
✅ **Flexible:** From all sources to uploads-only  
✅ **Intelligent:** Automatic deduplication and AI ranking  
✅ **Fast:** Search fewer sources for quicker results  
✅ **Private:** Search your own papers without online databases  
✅ **Hybrid:** Combine public and private research seamlessly  

The source selection feature gives you unprecedented control over your research discovery process!
