# Research Assistant

> A modern, AI-powered research discovery hub built with **Google Gemini 2.5 Flash** and **FAISS vector database**. This sophisticated tool provides intelligent paper discovery, iterative search augmentation, individual paper selection, and automated literature review generation through a beautiful **Gradio interface** with multi-agent coordination.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)

## Features

### AI-Powered Discovery
- Multi-source academic search (arXiv, CrossRef, OpenAlex, Google Scholar)
- Google Gemini 2.5 Flash for intelligent relevance scoring
- AI-enhanced query augmentation for better results

### PDF Upload & Private Papers
- Upload your own research papers (PDF format)
- Include unpublished work and internal documents
- Automatic text extraction and metadata parsing
- Seamless integration with search and review features

### Smart Search
- FAISS vector database for semantic similarity search
- Customizable search sources (choose databases or search only your uploads)
- Advanced filters: publication date, paper type, citation count
- Intelligent duplicate detection across sources

### Automated Literature Reviews
- Multi-agent system for structured review generation
- Export in Markdown format
- Proper citations and academic formatting

### Modern Interface
- Beautiful Gradio web interface
- Real-time progress tracking
- Interactive paper selection (checkboxes for individual papers)
- Multi-tab workflow organization

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Google API Key (for Gemini 2.5 Flash)
- 8GB+ RAM (recommended for FAISS operations)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/BurntDosa/Research-Assistant.git
cd Research-Assistant

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create configuration file
cp .env.example .env
# Edit .env with your API key:
# GOOGLE_API_KEY=your_api_key_here
# RESEARCH_EMAIL=your_email@example.com

# 5. Launch the application
python main.py
```

The interface will open automatically at `http://localhost:7860`

### First Launch - API Key Configuration

When you first launch the application, you'll see an **API Key Configuration Screen**:

1. Click the links to get your API keys
2. Paste them into the configuration form
3. Click "Save & Continue"
4. Start using the Research Assistant!

Your API keys are stored securely in a local `.env` file and never shared with anyone except the respective API providers.

### Verification

You can verify your installation by running:

```bash
# Check Python environment
python -c "import sys; sys.path.insert(0, 'src'); from src.apps.app_gradio_new import EnhancedGradioResearchApp; print('✅ Core dependencies installed')"

# Verify file structure
python -c "
import os
required_files = ['main.py', 'src/agents/control_agent.py', 'src/agents/literature_agent.py', 'src/agents/embedding_agent.py', 'src/apps/app_gradio_new.py']
missing = [f for f in required_files if not os.path.exists(f)]
if not missing:
    print('✅ All core files present')
else:
    print(f'❌ Missing files: {missing}')
"
```

---

## Usage Guide

### 1. Upload Your Own Papers (Optional)

**Add your private research papers before searching:**

1. Click **"Upload Your Own Papers"** accordion at the top
2. Select one or multiple PDF files from your computer
3. Click **"Upload & Parse Papers"** button
4. Papers are automatically parsed and added to the database

**Perfect for:**
- Unpublished or private research
- Papers you already have locally
- Internal company documents
- Subscription-only papers you have access to

### 2. Search for Papers

1. **Enter your research query** (e.g., "machine learning transformers")
2. **Choose search sources** in Advanced Options:
   - Google Scholar (requires SerpAPI key)
   - arXiv (free)
   - CrossRef (free)
   - OpenAlex (free)
   - Or uncheck all to search ONLY your uploaded papers
3. **Configure filters** (optional):
   - Paper type (Journal/Conference/Review)
   - Publication date range (start/end year)
   - Minimum citation count
4. **Click "Find Research Papers"**
5. **Select papers** using checkboxes (up to 20 displayed)
6. **Save selected papers** or save all results

### 2.5. Choosing Search Sources

In the **Advanced Options** section, you can now select which databases to search:

#### Available Sources:
- **Google Scholar (SerpAPI)**: Most comprehensive, requires API key
- **arXiv**: Latest preprints in STEM fields (free)
- **CrossRef**: Peer-reviewed papers with DOIs (free)
- **OpenAlex**: Open-access scholarly works (free)

#### Usage Scenarios:
```
All Sources (Default)     → Most comprehensive results
arXiv + OpenAlex          → Latest research only
Google Scholar + CrossRef → Peer-reviewed papers only
None Selected             → Search ONLY your uploaded papers!
```

**Pro Tips:**
- Use fewer sources for faster searches
- Uncheck all sources to search only your uploaded PDFs
- Mix sources with uploads for hybrid search

### 3. Advanced Features

#### Individual Paper Selection & Management
- **Interactive Checkboxes**: Select specific papers from search results (up to 20 papers)
- **Select All Toggle**: Quickly select or deselect all papers with one click
- **Batch Operations**: 
  - Save selected papers only
  - Save all papers from current search
  - Use selected papers for augmented search

#### Iterative Search & Query Augmentation
- Use **"Find More Related Papers"** for Phase 2 augmented search
- AI automatically generates expanded queries from selected paper content
- Discovers papers you might have missed in initial search
- Maintains session continuity across multiple iterations
- Shows query evolution and augmentation tracking

#### Literature Review Generation
1. Navigate to the **Literature Review** tab
2. Enter your **research topic** in the text field
3. Set **maximum papers** to include (10-50 papers)
4. Click **"Generate Literature Review"**
5. **Copy and save** the generated review in Markdown format

#### Vector Search & Semantic Discovery
- Papers are automatically embedded into FAISS vector database
- Use similarity search to find semantically related papers
- Leverage AI understanding for better discovery beyond keyword matching
- Persistent storage enables cross-session paper discovery

### 4. Paper Management

- **Selection Interface**: Interactive checkboxes for precise paper selection
- **Organization**: Papers are automatically categorized by type (Journal, Conference, Review)
- **Batch Actions**: Save selected papers or all papers with dedicated buttons
- **Export**: Download literature reviews and paper collections
- **Sessions**: Research sessions are automatically tracked and managed

---

## Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │  Control Agent  │    │ Literature Agent│
│                 │◄──►│                 │◄──►│                 │
│  - Modern UI    │    │  - Orchestration│    │ - Paper Search  │
│  - Checkboxes   │    │  - Session Mgmt │    │ - Gemini Valid. │
│  - Multi-Tab    │    │  - Iterative    │    │ - Query Augment.│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Embedding Agent │    │   FAISS Vector  │    │ Review Agents   │
│                 │◄──►│    Database     │    │                 │
│ - Text Embeddings│   │                 │    │ - Manager Agent │
│ - Similarity    │    │ - Vector Search │    │ - Writing Agent │
│ - Metadata      │    │ - Session Store │    │ - Multi-Agent   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### Control Agent (`src/agents/control_agent.py`)
- **Enhanced Research Pipeline**: Orchestrates the entire research workflow with iterative capabilities
- **Session Management**: Maintains state across research sessions with comprehensive tracking
- **Agent Coordination**: Manages communication between different agents and components
- **Configuration Management**: Handles pipeline parameters, search limits, and quality thresholds
- **Paper Selection Logic**: Manages individual paper selection and batch operations
- **Query Augmentation**: Coordinates AI-powered keyword expansion from selected papers

#### Literature Agent (`src/agents/literature_agent.py`)
- **Multi-Source Discovery**: Searches arXiv, PubMed, and other academic sources with intelligent routing
- **Gemini Integration**: Uses Gemini 2.5 Flash for relevance validation and confidence scoring
- **Advanced Filtering**: Sophisticated search parameter management with date, citation, and type filters
- **Real-time Processing**: Asynchronous paper processing and validation with progress tracking
- **Database Integration**: Enhanced SQLite database with comprehensive paper metadata and analytics

#### Embedding Agent (`src/agents/embedding_agent.py`)
- **FAISS Integration**: High-performance vector database operations with optimized indexing
- **Google Embeddings**: State-of-the-art text embedding generation for semantic search
- **Similarity Search**: Advanced semantic paper matching and discovery with configurable thresholds
- **Metadata Management**: Comprehensive paper metadata storage with search session tracking
- **Batch Processing**: Efficient batch operations for paper embedding and storage

#### Literature Review Agents (`src/agents/literature_review_agents.py`)
- **Manager Agent**: Maintains review structure and provides oversight with outline generation
- **Writing Agent**: Generates coherent literature reviews with proper citations and formatting
- **Multi-Agent Collaboration**: Coordinated review generation process with feedback loops
- **Quality Assurance**: Built-in review validation and improvement with iterative refinement
- **LangChain Integration**: Advanced prompt engineering and response optimization

#### Gradio Interface (`src/apps/app_gradio_new.py`)
- **Modern Interface**: Beautiful, responsive Gradio-based web interface with professional styling
- **Interactive Elements**: Individual paper checkboxes, progress bars, and real-time updates
- **Multi-Tab Layout**: Organized workflow with separate tabs for search and literature review
- **Batch Operations**: Comprehensive paper selection and management capabilities
- **Export Features**: Download capabilities for reviews and data with markdown support
- **Session Continuity**: Maintains application state across interactions and iterations

---

## Configuration

### Required Environment Variables

Create a `.env` file in the root directory:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here
RESEARCH_EMAIL=your_email@example.com

# Optional (for Google Scholar search)
SERPAPI_KEY=your_serpapi_key_here
```

### Advanced Configuration

Edit configuration in `src/agents/control_agent.py`:

```python
@dataclass
class PipelineConfig:
    INITIAL_PAPERS_PER_SOURCE = 5      # Papers per source in initial search
    SECONDARY_PAPERS_PER_SOURCE = 2    # Papers per source in augmented search
    RELEVANCE_THRESHOLD = 0.7          # Minimum AI relevance score
    TOP_DISPLAY_RESULTS = 10           # Results shown to user
    SIMILARITY_THRESHOLD = 0.7         # Vector similarity threshold
```

### Optional Configuration

- **FAISS Settings**: Vector database automatically initializes with optimal settings
- **Search Limits**: Configurable in `control_agent.py` (`PipelineConfig` class)
- **Model Parameters**: Adjust temperature and other settings in respective agent files

---

## Development

### Project Structure

```
Research-Assistant/
├── main.py                             # Main application entry point (Gradio)
├── src/                                # Source code directory
│   ├── agents/                         # AI agent implementations
│   │   ├── control_agent.py            # Research pipeline orchestration
│   │   ├── literature_agent.py         # Paper discovery and validation
│   │   ├── embedding_agent.py          # Vector database management
│   │   └── literature_review_agents.py # Multi-agent review generation
│   └── apps/                           # Application interfaces
│       └── app_gradio_new.py           # Enhanced Gradio frontend
├── data/                               # Data storage directory
├── requirements.txt                    # Python dependencies
├── .env                                # Environment configuration (create this)
├── .gitignore                          # Git ignore rules
└── README.md                           # This file
```

### Key Technologies

- **Frontend**: Gradio for modern, interactive web interface with real-time updates
- **AI/ML**: Google Gemini 2.5 Flash, LangChain framework for advanced language processing
- **Vector DB**: FAISS for high-performance similarity search and semantic matching
- **Data Processing**: Pandas, NumPy for data manipulation and analysis
- **Web Scraping**: BeautifulSoup, aiohttp for content extraction and async operations
- **Database**: SQLite for metadata and session storage with MCP server architecture
- **PDF Processing**: PyMuPDF for text extraction and document processing
- **Environment Management**: python-dotenv for configuration management

### Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `python -m pytest` (if tests exist)
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Add docstrings for all functions and classes
- Keep functions focused and modular

---

## API Reference

### Pipeline Configuration

```python
@dataclass
class PipelineConfig:
    INITIAL_PAPERS_PER_SOURCE = 5      # Papers per source initially
    SECONDARY_PAPERS_PER_SOURCE = 2    # Papers per source in phase 2
    RELEVANCE_THRESHOLD = 0.7          # Minimum relevance score
    TOP_DISPLAY_RESULTS = 10           # Results shown to user
    SIMILARITY_THRESHOLD = 0.7         # Vector similarity threshold
    SECONDARY_DISPLAY_RESULTS = 20     # Phase 2 results limit
```

### Core Classes

#### EnhancedResearchPipeline
```python
pipeline = EnhancedResearchPipeline()
results = await pipeline.search_papers(
    query="machine learning transformers",
    filters=SearchFilters(
        max_papers=50,
        date_range=(2020, 2024),
        sources=['arxiv', 'pubmed']
    )
)
```

#### GeminiRelevanceValidator
```python
validator = GeminiRelevanceValidator(api_key="your_key")
score = await validator.validate_paper_async(
    paper=paper_object,
    query="research query",
    criteria=validation_criteria
)
```

---

## Troubleshooting

### Common Issues

#### 1. FAISS Installation Issues
```bash
# For CPU-only version
pip install faiss-cpu

# For GPU version (if CUDA available)
pip install faiss-gpu
```

#### 2. Google API Key Issues
- Ensure your API key has Gemini API access enabled
- Check quota limits in Google Cloud Console
- Verify the key is correctly set in `.env` file

#### 3. Gradio Interface Issues
- Check if port 7860 is available or specify a different port
- Ensure all dependencies are properly installed
- Clear browser cache if interface doesn't load properly

#### 4. Memory Issues with Large Datasets
- Reduce `max_papers` in search filters
- Use individual paper selection instead of "Save All"
- Consider upgrading system RAM for large FAISS indexes

#### 5. Network Timeout Issues
- Check internet connection stability
- Increase timeout values in configuration
- Use VPN if accessing restricted academic sources

#### 6. Paper Selection Issues
- If checkboxes don't appear, ensure papers were found in the search
- Maximum 20 papers can be displayed for selection at once
- Use iterative search to process larger result sets

### Performance Optimization

#### For Large-Scale Research
- **Batch Processing**: Process papers in smaller batches using individual selection
- **Caching**: Enable result caching for repeated queries through session management
- **Parallel Processing**: Increase concurrent request limits in configuration
- **Iterative Approach**: Use Phase 2 augmented search instead of large initial searches

#### Memory Management
- **Vector Database**: Use memory mapping for large FAISS indexes
- **Garbage Collection**: Explicit cleanup of large objects between searches
- **Streaming**: Process papers in streaming fashion for large sets

#### Interface Optimization
- **Progressive Loading**: Papers load progressively with real-time updates
- **Checkbox Limits**: Maximum 20 papers displayed for optimal interface performance
- **Tab Management**: Use separate tabs to organize workflow and reduce memory usage

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Google Gemini Team** for the powerful Gemini 2.5 Flash model and advanced AI capabilities
- **FAISS Team** at Facebook AI Research for vector search capabilities and optimization  
- **LangChain Community** for the excellent AI framework and multi-agent coordination
- **Gradio Team** for the amazing web interface framework and interactive components
- **Academic Community** for making research papers accessible and promoting open science

---

## Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)
- **Email**: Contact via the email configured in your `.env` file

---

**Happy Researching!**

*Built with care for the research community*
