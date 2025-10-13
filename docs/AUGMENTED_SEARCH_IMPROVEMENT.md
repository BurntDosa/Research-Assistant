# Augmented Search Query Improvement

## Overview
Enhanced the secondary/augmented search feature to use AI-powered keyword extraction and query restructuring for deeper, more precise literature discovery.

## What Changed

### Previous Approach (Simple)
- Basic word frequency analysis
- Extracted common words from titles/abstracts
- Simple concatenation: `original_query + top_3_keywords`
- No semantic understanding
- Generic results

### New Approach (AI-Powered)

#### Primary Method: Gemini AI Enhancement
Uses **Gemini 2.0 Flash** to intelligently:

1. **Extract Technical Keywords**
   - Identifies methodologies, techniques, and domain-specific terms
   - Filters out generic academic words (paper, study, research, etc.)
   - Focuses on specialized concepts

2. **Restructure Query**
   - Transforms casual queries into academic search terms
   - Uses technical/academic language
   - Optimizes for scholarly database searches
   - Limits to 15 words for precision

3. **Deep Analysis**
   - Analyzes up to 5 selected papers
   - Processes titles and first 300 chars of abstracts
   - Identifies patterns across multiple papers
   - Synthesizes concepts for focused search

#### Fallback Method: Enhanced Keyword Extraction
If Gemini API is unavailable:
- Improved word frequency analysis
- Expanded stop-word list (filters 12+ common terms)
- Requires minimum 2 occurrences for relevance
- Extracts top 5 most frequent terms

## Example Transformations

### Example 1: Machine Learning
**Original Query:** "machine learning in healthcare"

**AI-Augmented Query:** "deep learning diagnostic imaging clinical decision support systems medical image classification"

### Example 2: Climate Science
**Original Query:** "climate change impacts"

**AI-Augmented Query:** "anthropogenic warming ecosystem adaptation carbon sequestration biodiversity loss mitigation strategies"

### Example 3: Quantum Computing
**Original Query:** "quantum computing applications"

**AI-Augmented Query:** "quantum algorithms superconducting qubits error correction quantum supremacy cryptographic protocols"

## Benefits

1. **Deeper Discovery**
   - Finds specialized papers missed in initial search
   - Targets niche subtopics and methodologies
   - Reduces irrelevant results

2. **Academic Precision**
   - Uses terminology from actual research papers
   - Optimized for Google Scholar, arXiv, CrossRef, OpenAlex
   - Matches how researchers write about topics

3. **Contextual Understanding**
   - Learns from your selected papers
   - Adapts to your specific research direction
   - Follows research threads naturally

4. **Fallback Reliability**
   - Graceful degradation if API fails
   - Always returns a valid query
   - Never blocks the search process

## Technical Implementation

### File: `src/agents/control_agent.py`

#### Main Function: `_generate_augmented_query()`
```python
def _generate_augmented_query(self, original_query: str, selected_papers: List[Any]) -> str:
    """Generate augmented query using AI to extract keywords and restructure"""
    # 1. Extract paper content (titles + abstracts)
    # 2. Format prompt for Gemini
    # 3. Get AI-generated query
    # 4. Validate and return
    # 5. Fallback to simple extraction if needed
```

#### Fallback Function: `_simple_keyword_extraction()`
```python
def _simple_keyword_extraction(self, original_query: str, selected_papers: List[Any]) -> str:
    """Fallback method using word frequency analysis"""
    # 1. Extract text from papers
    # 2. Filter stop words
    # 3. Count word frequencies
    # 4. Return top keywords appended to original query
```

## Gemini Prompt Design

### Key Components:
1. **Context**: Original query + selected papers
2. **Instructions**: Extract keywords, restructure, use academic language
3. **Constraints**: Max 15 words, technical terms only, no generic words
4. **Output Format**: Single query string only

### Prompt Engineering:
- Clear task definition
- Specific requirements list
- Output format constraints
- Examples of what to avoid

## Usage in Application

### When Augmented Search is Triggered:
1. User conducts initial search
2. User selects relevant papers (checkboxes)
3. User clicks "🔬 Augment Search with Selected Papers"
4. System calls `_generate_augmented_query()` with selected papers
5. AI analyzes papers and generates new query
6. New query searches databases for deeper results
7. Results combined with selected papers and re-ranked

### Error Handling:
- API key missing → Fallback to simple extraction
- API timeout → Fallback to simple extraction
- Invalid response → Fallback to simple extraction
- Empty papers → Return original query
- Any exception → Return original query

## Performance

### Timing:
- AI generation: ~2-3 seconds
- Fallback extraction: <100ms
- Total impact: Minimal (async operation)

### API Usage:
- Model: `gemini-2.0-flash-exp` (fast, cost-effective)
- Input: ~1000-2000 tokens per request
- Output: ~20-50 tokens per request
- Cost: Negligible (<$0.01 per augmented search)

## Future Enhancements

Potential improvements:
1. **Multi-stage refinement**: Iterative query improvement
2. **Domain detection**: Tailor augmentation to research field
3. **Citation network analysis**: Use paper references for keywords
4. **User feedback loop**: Learn from which augmented queries work best
5. **Query templates**: Pre-built patterns for common research areas
6. **Multilingual support**: Handle non-English papers

## Testing

To test the improvement:
1. Search for: "machine learning healthcare"
2. Select 2-3 relevant papers
3. Click augmented search
4. Check console logs for: "AI-augmented query: ..."
5. Compare results depth with previous searches

## Configuration

### Required:
- `GEMINI_API_KEY` in `.env` file

### Optional Tuning:
```python
# In control_agent.py
MAX_PAPERS_FOR_AUGMENTATION = 5  # Currently uses first 5 papers
MAX_ABSTRACT_LENGTH = 300        # Characters of abstract to analyze
MAX_AUGMENTED_WORDS = 15         # Word limit for query
```

## Monitoring

### Log Messages:
- `"AI-augmented query: {query}"` - Success
- `"GEMINI_API_KEY not found, falling back"` - Missing key
- `"AI-generated query invalid, using fallback"` - Bad response
- `"Simple keyword augmentation: {terms}"` - Fallback used
- `"Failed to generate AI-augmented query: {error}"` - Exception

## Conclusion

This improvement transforms augmented search from a simple keyword append to an intelligent query restructuring system that understands academic context and research terminology. It enables deeper, more focused literature discovery while maintaining reliability through graceful fallback mechanisms.
