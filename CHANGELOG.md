# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-10-13

### 🔒 Security

#### API Key Exposure Fix
- **Fixed exposed API key vulnerability**: Prevented `.env` backup files from being committed to repository
- **Enhanced .gitignore**: Added comprehensive patterns to exclude sensitive backup files
  - `*.env.backup`
  - `*.env.backup.*`
  - `.env.backup*`
  - `.env.*`
- **Removed compromised keys**: Cleaned up exposed API keys from repository history
- **Updated API key manager**: Improved security checks in `src/utils/api_key_manager.py`

### 📝 Documentation

- **README improvements**: Fixed duplications and improved code formatting
- **Security documentation**: Added immediate action guide for API key exposure incidents

### 🛠️ Maintenance

- **Git tracking cleanup**: Removed backup files from git tracking
- **Code quality**: Fixed formatting issues and improved code organization

---

## [1.0.0] - 2025-10-13

### 🎉 Initial Public Release

The first stable release of Research Assistant - an AI-powered research discovery and literature review platform.

### ✨ Features

#### AI-Powered Paper Discovery
- **Multi-Source Search**: Integrated search across arXiv, CrossRef, OpenAlex, and Google Scholar
- **Google Gemini 2.5 Flash**: Intelligent relevance scoring and paper validation
- **Smart Query Augmentation**: AI-enhanced keyword expansion for better results
- **Real-time Relevance Scoring**: Dynamic assessment of paper relevance to research queries

#### PDF Upload & Private Papers
- **Local PDF Upload**: Upload your own research papers in PDF format
- **Automatic Parsing**: Intelligent extraction of title, authors, abstract, and content
- **Batch Upload**: Process multiple PDF files simultaneously
- **Private Paper Access**: Include unpublished work and internal documents
- **Seamless Integration**: Uploaded papers work with all search and review features

#### Flexible Source Selection
- **Customizable Databases**: Choose which academic sources to search
- **Uploads-Only Mode**: Search exclusively within your uploaded papers
- **Hybrid Search**: Combine any database sources with private papers
- **Smart Filtering**: Match sources to your research field

#### Vector-Based Semantic Search
- **FAISS Integration**: High-performance similarity search with optimized indexing
- **Google Embeddings**: State-of-the-art text embeddings for accurate matching
- **Duplicate Detection**: Intelligent deduplication across sources using DOI and title matching
- **Iterative Search**: AI-powered query augmentation from selected papers
- **Session-Based Storage**: Persistent paper collections with comprehensive metadata

#### Automated Literature Review Generation
- **Multi-Agent System**: Collaborative AI agents for structured review creation
- **Manager Agent**: Maintains review structure and provides oversight
- **Writing Agent**: Generates coherent, well-structured literature reviews
- **Markdown Export**: Download reviews in markdown format with proper citations

#### Modern User Interface
- **Gradio-Powered**: Beautiful, responsive web interface with modern design
- **Interactive Selection**: Checkboxes for precise paper selection (up to 20 papers)
- **Real-time Progress**: Live updates during search and analysis
- **Multi-Tab Interface**: Organized workflow with separate tabs
- **Batch Operations**: Save selected papers or save all with one click

#### Advanced Analytics
- **Paper Classification**: Automatic categorization (Journal, Conference, Review)
- **Citation Analysis**: Impact factor and citation count tracking
- **Search Session Management**: Persistent research sessions
- **Performance Metrics**: Detailed analytics and timing

### 🔧 Technical Features

#### Architecture
- **Control Agent**: Enhanced research pipeline orchestration with iterative capabilities
- **Literature Agent**: Multi-source discovery with Gemini validation
- **Embedding Agent**: FAISS vector database management
- **Review Agents**: Multi-agent literature review generation system
- **MCP Server**: SQLite-based metadata and analytics storage

#### Configuration
- **BYOK (Bring Your Own Key)**: User-provided API keys for privacy
- **Environment Variables**: Secure configuration via .env files
- **First-Launch Setup**: Interactive API key configuration screen
- **Flexible Pipeline Config**: Adjustable search parameters and thresholds

#### Performance
- **Asynchronous Processing**: Non-blocking paper discovery and validation
- **Batch Operations**: Efficient processing of multiple papers
- **Caching**: Session-based result caching
- **Memory Optimization**: Efficient handling of large datasets

### 🛠️ Tech Stack

- **AI/ML**: Google Gemini 2.5 Flash, LangChain
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Frontend**: Gradio 4.x
- **Data Processing**: Pandas, NumPy
- **PDF Processing**: PyMuPDF
- **Web Scraping**: BeautifulSoup, aiohttp
- **Database**: SQLite with MCP server architecture

### 📚 Documentation

- Comprehensive README with quick start guide
- Detailed usage instructions with examples
- Troubleshooting section for common issues
- Architecture overview and component descriptions
- API reference and configuration options
- Performance optimization tips

### 🔐 Security & Privacy

- Local-only API key storage (never transmitted)
- .gitignore protection for sensitive files
- User data stored locally in SQLite database
- No telemetry or external data collection
- BYOK model ensures user control

### 🎯 Target Users

- Academic researchers conducting literature reviews
- Graduate students exploring research topics
- Research groups managing paper collections
- Anyone needing intelligent paper discovery and organization

---

## Release Notes

This is the first stable release of Research Assistant, ready for public use. The platform has been tested extensively and provides a robust, feature-complete solution for AI-powered research discovery and literature review generation.

### Getting Started

```bash
git clone https://github.com/BurntDosa/Research-Assistant.git
cd Research-Assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)

---

**Full Changelog**: https://github.com/BurntDosa/Research-Assistant/commits/v1.0.0
