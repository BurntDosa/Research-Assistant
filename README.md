# 🔬 Research Assistant

A modern, AI-powered research discovery hub built with **Google Gemini 2.5 Flash** and **FAISS vector database**. This sophisticated tool provides intelligent paper discovery, relevance validation, and automated literature review generation with a beautiful, intuitive interface.

## ✨ Features

### 🤖 AI-Powered Paper Discovery
- **Google Gemini 2.5 Flash Integration**: Advanced relevance scoring and paper validation
- **Multi-Source Search**: Automatic discovery from arXiv, PubMed, and other academic databases
- **Intelligent Query Augmentation**: AI-enhanced keyword expansion for better results
- **Real-time Relevance Scoring**: Dynamic assessment of paper relevance to your research query

### 🔍 Vector-Based Similarity Search  
- **FAISS Vector Database**: High-performance semantic similarity search
- **Google's Embedding Models**: State-of-the-art text embeddings for accurate matching
- **Duplicate Detection**: Intelligent deduplication across multiple sources
- **Iterative Search**: Expand your research with related papers

### 📝 Automated Literature Review Generation
- **Multi-Agent System**: Collaborative AI agents for structured review creation
- **Manager Agent**: Maintains review structure and provides oversight
- **Writing Agent**: Generates coherent, well-structured literature reviews
- **Export Capabilities**: Download reviews in Markdown format

### 🎨 Modern User Interface
- **Streamlit-Powered**: Beautiful, responsive web interface
- **Real-time Progress**: Live updates during search and analysis
- **Interactive Paper Management**: Easy selection and organization
- **Modern Design**: Gradient themes and intuitive navigation

### 📊 Advanced Analytics
- **Paper Type Classification**: Automatic categorization (Journal, Conference, Review)
- **Citation Analysis**: Impact factor and citation count tracking
- **Search Session Management**: Persistent research sessions
- **Performance Metrics**: Detailed analytics and insights

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ 
- Google API Key (for Gemini 2.5 Flash)
- 8GB+ RAM (recommended for FAISS operations)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/BurntDosa/Research-Assistant.git
cd Research-Assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
echo "RESEARCH_EMAIL=your_email@example.com" >> .env
```

4. **Run the application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |
| `RESEARCH_EMAIL` | Email for API politeness | ✅ Yes |

### Optional Configuration

- **FAISS Settings**: Vector database automatically initializes with optimal settings
- **Search Limits**: Configurable in `control_agent.py` (`PipelineConfig` class)
- **Model Parameters**: Adjust temperature and other settings in respective agent files

## 📚 Usage Guide

### 1. Basic Paper Search

1. **Enter your research query** in the search box
2. **Configure search filters** (optional):
   - Publication date range
   - Source selection (arXiv, PubMed, etc.)
   - Maximum number of papers
3. **Click "Start Research"** to begin discovery
4. **Review results** with AI-generated relevance scores
5. **Select papers** of interest for your collection

### 2. Advanced Features

#### Iterative Search
- Use "Phase 2 Search" to find related papers based on your selections
- AI automatically generates expanded queries from selected papers
- Discovers papers you might have missed in initial search

#### Literature Review Generation
1. Navigate to the **Literature Review** section
2. Enter your **research topic**
3. Set **maximum papers** to include
4. Click **"Generate Literature Review"**
5. Download the generated review in Markdown format

#### Vector Search
- Papers are automatically embedded into FAISS database
- Use similarity search to find related papers
- Leverage semantic understanding for better discovery

### 3. Paper Management

- **Selection**: Click papers to add them to your collection
- **Organization**: Papers are automatically categorized by type
- **Export**: Download your selections and reviews
- **Sessions**: Your research sessions are automatically saved

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  Control Agent  │    │ Literature Agent│
│                 │◄──►│                 │◄──►│                 │
│  - Modern UI    │    │  - Orchestration│    │ - Paper Search  │
│  - User Input   │    │  - Session Mgmt │    │ - Gemini Valid. │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Embedding Agent │    │   FAISS Vector  │    │ Review Agents   │
│                 │◄──►│    Database     │    │                 │
│ - Text Embeddings│   │                 │    │ - Manager Agent │
│ - Similarity    │    │ - Vector Search │    │ - Writing Agent │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 🎯 **Control Agent** (`control_agent.py`)
- **Enhanced Research Pipeline**: Orchestrates the entire research workflow
- **Session Management**: Maintains state across research sessions
- **Agent Coordination**: Manages communication between different agents
- **Configuration Management**: Handles pipeline parameters and settings

#### 📖 **Literature Agent** (`literature_agent.py`)
- **Multi-Source Discovery**: Searches arXiv, PubMed, and other academic sources
- **Gemini Integration**: Uses Gemini 2.5 Flash for relevance validation
- **Advanced Filtering**: Sophisticated search parameter management
- **Real-time Processing**: Asynchronous paper processing and validation

#### 🧠 **Embedding Agent** (`embedding_agent.py`)
- **FAISS Integration**: High-performance vector database operations
- **Google Embeddings**: State-of-the-art text embedding generation
- **Similarity Search**: Semantic paper matching and discovery
- **Metadata Management**: Comprehensive paper metadata storage

#### 📝 **Literature Review Agents** (`literature_review_agents.py`)
- **Manager Agent**: Maintains review structure and provides oversight
- **Writing Agent**: Generates coherent literature reviews
- **Multi-Agent Collaboration**: Coordinated review generation process
- **Quality Assurance**: Built-in review validation and improvement

#### 🖥️ **UI Components** (`ui_components.py`)
- **Modern Interface**: Beautiful, responsive Streamlit components
- **Real-time Updates**: Live progress tracking and status updates
- **Interactive Elements**: User-friendly paper selection and management
- **Export Features**: Download capabilities for reviews and data

#### 🗄️ **MCP Server** (`mcp_server.py`)
- **Database Management**: SQLite-based paper and session storage
- **Analytics Tracking**: Performance metrics and usage statistics
- **Data Persistence**: Long-term storage of research sessions
- **API Integration**: RESTful endpoints for data access

## 🛠️ Development

### Project Structure

```
Research-Assistant/
├── app.py                      # Main Streamlit application
├── control_agent.py            # Research pipeline orchestration
├── literature_agent.py         # Paper discovery and validation
├── embedding_agent.py          # Vector database management
├── literature_review_agents.py # Multi-agent review generation
├── ui_components.py            # UI components and layouts
├── mcp_server.py               # Database and API server
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (create this)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

### Key Technologies

- **Frontend**: Streamlit for modern web interface
- **AI/ML**: Google Gemini 2.5 Flash, LangChain framework
- **Vector DB**: FAISS for high-performance similarity search
- **Data Processing**: Pandas, NumPy for data manipulation
- **Web Scraping**: BeautifulSoup, aiohttp for content extraction
- **Database**: SQLite for metadata and session storage
- **PDF Processing**: PyMuPDF for text extraction

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

## 🔍 API Reference

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

## 🐛 Troubleshooting

### Common Issues

#### 1. **FAISS Installation Issues**
```bash
# For CPU-only version
pip install faiss-cpu

# For GPU version (if CUDA available)
pip install faiss-gpu
```

#### 2. **Google API Key Issues**
- Ensure your API key has Gemini API access enabled
- Check quota limits in Google Cloud Console
- Verify the key is correctly set in `.env` file

#### 3. **Memory Issues with Large Datasets**
- Reduce `max_papers` in search filters
- Use pagination for large result sets
- Consider upgrading system RAM

#### 4. **Network Timeout Issues**
- Check internet connection stability
- Increase timeout values in configuration
- Use VPN if accessing restricted academic sources

### Performance Optimization

#### For Large-Scale Research
- **Batch Processing**: Process papers in smaller batches
- **Caching**: Enable result caching for repeated queries
- **Parallel Processing**: Increase concurrent request limits
- **Database Indexing**: Optimize SQLite indexes for large datasets

#### Memory Management
- **Vector Database**: Use memory mapping for large FAISS indexes
- **Garbage Collection**: Explicit cleanup of large objects
- **Streaming**: Process papers in streaming fashion for large sets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini Team** for the powerful Gemini 2.5 Flash model
- **FAISS Team** at Facebook AI Research for vector search capabilities  
- **LangChain Community** for the excellent AI framework
- **Streamlit Team** for the amazing web app framework
- **Academic Community** for making research papers accessible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)
- **Email**: Contact via the email configured in your `.env` file

---

**Happy Researching! 🎓**

*Built with ❤️ for the research community*