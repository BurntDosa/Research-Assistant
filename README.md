# 🔬 Research Assistant# 🔬 Research Assistant



> An AI-powered research discovery hub built with **Google Gemini 2.5 Flash** and **FAISS vector database**. Discover papers, manage literature, and generate automated reviews through an intuitive interface.A modern, AI-powered research discovery hub built with **Google Gemini 2.5 Flash** and **FAISS vector database**. This sophisticated tool provides intelligent paper discovery, iterative search augmentation, individual paper selection, and automated literature review generation through a beautiful **Gradio interface** with multi-agent coordination.



[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)## 🚀 Quick Start

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)### Prerequisites

- Python 3.8 or higher

## ✨ Features- API Keys (configured on first launch):

  - **Google Gemini API** - [Get it here](https://makersuite.google.com/app/apikey) (Free tier available)

### 🤖 **AI-Powered Discovery**  - **SerpAPI** - [Get it here](https://serpapi.com/manage-api-key) (100 free searches/month)

- Multi-source academic search (arXiv, CrossRef, OpenAlex, Google Scholar)  - **OpenAI API** (Optional) - [Get it here](https://platform.openai.com/api-keys)

- Google Gemini 2.5 Flash for intelligent relevance scoring

- AI-enhanced query augmentation for better results### Installation



### 📤 **PDF Upload & Private Papers**```bash

- Upload your own research papers (PDF format)# Clone the repository

- Include unpublished work and internal documentsgit clone <repository-url>

- Automatic text extraction and metadata parsingcd Research-Assistant

- Seamless integration with search and review features

# Create and activate virtual environment

### 🔍 **Smart Search**python -m venv venv_gemini

- FAISS vector database for semantic similarity searchsource venv_gemini/bin/activate  # On Windows: venv_gemini\Scripts\activate

- Customizable search sources (choose databases or search only your uploads)

- Advanced filters: publication date, paper type, citation count# Install dependencies

- Intelligent duplicate detection across sourcespip install -r requirements.txt



### 📝 **Automated Literature Reviews**# Launch the application

- Multi-agent system for structured review generationpython main.py

- Export in Markdown format```

- Proper citations and academic formatting

### First Launch - API Key Configuration

### 🎨 **Modern Interface**

- Beautiful Gradio web interfaceWhen you first launch the application, you'll see an **API Key Configuration Screen**:

- Real-time progress tracking

- Interactive paper selection (checkboxes for individual papers)1. 🔑 Click the links to get your API keys

- Multi-tab workflow organization2. ✍️ Paste them into the configuration form

3. 💾 Click "Save & Continue"

---4. 🎉 Start using the Research Assistant!



## 🚀 Quick StartYour API keys are stored securely in a local `.env` file and never shared with anyone except the respective API providers.



### Prerequisites📖 **Detailed Setup Guide**: See [docs/QUICK_START.md](docs/QUICK_START.md)  

🔐 **API Key Documentation**: See [docs/API_KEY_SETUP.md](docs/API_KEY_SETUP.md)

- **Python 3.9 or higher**

- **Google Gemini API Key** - [Get it FREE here](https://makersuite.google.com/app/apikey)## ✨ Features

- **8GB RAM** (recommended for FAISS operations)

### 📤 PDF Upload & Private Paper Management

### Installation- **Upload Local Papers**: Add your own PDF research papers from your system

- **Private Paper Access**: Include unpublished work, internal documents, or subscription-only papers

```bash- **Automatic Parsing**: Intelligent extraction of title, authors, abstract, and content

# 1. Clone the repository- **Batch Upload**: Upload multiple PDF files simultaneously

git clone https://github.com/BurntDosa/Research-Assistant.git- **Seamless Integration**: Uploaded papers work with all search and review features

cd Research-Assistant

### 🌐 Flexible Source Selection (NEW!)

# 2. Create virtual environment (recommended)- **Choose Your Databases**: Select from Google Scholar, arXiv, CrossRef, and OpenAlex

python -m venv venv- **Uploads-Only Mode**: Search only your uploaded papers without internet searches

source venv/bin/activate  # On Windows: venv\Scripts\activate- **Hybrid Search**: Combine any database sources with your private papers

- **Smart Filtering**: Match sources to your research field (STEM, medical, interdisciplinary)

# 3. Install dependencies- **Performance Control**: Search fewer sources for faster results

pip install -r requirements.txt

### 🤖 AI-Powered Paper Discovery

# 4. Create configuration file- **Google Gemini 2.5 Flash Integration**: Advanced relevance scoring and paper validation

cp .env.example .env- **Multi-Source Search**: Automatic discovery from arXiv, PubMed, and other academic databases

# Edit .env with your API key:- **Intelligent Query Augmentation**: AI-enhanced keyword expansion for better results

# GOOGLE_API_KEY=your_api_key_here- **Real-time Relevance Scoring**: Dynamic assessment of paper relevance to your research query

# RESEARCH_EMAIL=your_email@example.com

### 🔍 Vector-Based Similarity Search  

# 5. Launch the application- **FAISS Vector Database**: High-performance semantic similarity search with optimized indexing

python main.py- **Google's Embedding Models**: State-of-the-art text embeddings for accurate matching

```- **Duplicate Detection**: Intelligent deduplication across multiple sources using DOI and title matching

- **Iterative Search Enhancement**: AI-powered query augmentation and keyword expansion from selected papers

The interface will open automatically at `http://localhost:7860`- **Session-Based Storage**: Persistent paper collections with comprehensive metadata tracking



### First-Time Setup### 📝 Automated Literature Review Generation

- **Multi-Agent System**: Collaborative AI agents for structured review creation

When you first launch, you'll see an **API Key Configuration Screen**:- **Manager Agent**: Maintains review structure and provides oversight

- **Writing Agent**: Generates coherent, well-structured literature reviews

1. Click the link to get your free Google Gemini API key- **Export Capabilities**: Download reviews in Markdown format

2. Paste your API key and email into the form

3. Click "Save & Continue"### 🔄 Enhanced Research Pipeline

4. Start researching!- **Iterative Search**: Phase 2 augmented search with AI-generated keywords from selected papers

- **Individual Paper Selection**: Precise paper selection with interactive checkboxes (up to 20 papers)

Your API keys are stored locally in `.env` and never shared.- **Batch Operations**: Save selected papers or save all papers with one click

- **Query Enhancement**: AI-powered keyword augmentation based on paper content and abstracts

---- **Session Continuity**: Maintain research state across multiple search iterations

- **Smart Deduplication**: Advanced duplicate detection using DOI, title, and content similarity

## 📖 Usage Guide

### 🎨 Modern User Interface

### 1. Upload Your Papers (Optional)- **Gradio-Powered**: Beautiful, responsive web interface with modern design

- **Individual Paper Selection**: Interactive checkboxes for precise paper selection (up to 20 papers)

**Add your private research papers before searching:**- **Real-time Progress**: Live updates during search and analysis with progress bars

- **Interactive Paper Management**: Easy selection, organization, and bulk operations

1. Click **"📤 Upload Your Own Papers"** at the top- **Modern Design**: Gradient themes, intuitive navigation, and professional styling

2. Select one or multiple PDF files- **Multi-Tab Interface**: Organized workflow with separate tabs for search and review generation

3. Click **"📤 Upload & Parse Papers"**

4. Papers are automatically parsed and added to the database### 📊 Advanced Analytics

- **Paper Type Classification**: Automatic categorization (Journal, Conference, Review, Unknown)

**Perfect for:**- **Citation Analysis**: Impact factor and citation count tracking with relevance scoring

- 🔒 Unpublished or private research- **Search Session Management**: Persistent research sessions with comprehensive analytics

- 📚 Papers you already have locally- **Performance Metrics**: Detailed search analytics, timing, and success tracking

- 🏢 Internal company documents- **Interactive Selection**: Individual paper checkboxes with batch operations (save selected/all)

- 📖 Subscription-only papers you have access to- **Query Augmentation Tracking**: Monitor iterative search improvements and keyword evolution



### 2. Search for Papers## 🚀 Quick Start



1. **Enter your research query** (e.g., "machine learning transformers")### Prerequisites

2. **Choose search sources** in Advanced Options:

   - ✅ Google Scholar (requires SerpAPI key)- Python 3.9+ 

   - ✅ arXiv (free)- Google API Key (for Gemini 2.5 Flash)

   - ✅ CrossRef (free)- 8GB+ RAM (recommended for FAISS operations)

   - ✅ OpenAlex (free)

   - Or uncheck all to search ONLY your uploaded papers### Installation

3. **Configure filters** (optional):

   - Paper type (Journal/Conference/Review)1. **Clone the repository**

   - Publication date range```bash

   - Minimum citation countgit clone https://github.com/BurntDosa/Research-Assistant.git

4. **Click "🔍 Find Research Papers"**cd Research-Assistant

5. **Select papers** using checkboxes (up to 20 displayed)```

6. **Save selected papers** or save all results

2. **Install dependencies**

### 3. Augmented Search```bash

pip install -r requirements.txt

Use **"🔄 Find More Related Papers"** to:```

- Let AI generate expanded queries from your selected papers

- Discover papers missed in initial search3. **Set up environment variables**

- Maintain session continuity across iterations```bash

# Copy the example file and edit with your values

### 4. Generate Literature Reviewcp .env.example .env

# Edit .env with your actual API key and email

1. Switch to **"📚 Literature Review"** tab```

2. Enter your research topic

3. Set maximum papers to include (10-50)Or create manually:

4. Click **"📚 Generate Literature Review"**```bash

5. Copy and export the generated review (Markdown format)# Create .env file

echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env

---echo "RESEARCH_EMAIL=your_email@example.com" >> .env

```

## 🏗️ Architecture

4. **Run the application**

``````bash

┌─────────────────┐python main.py

│   Gradio UI     │  Modern web interface```

│                 │

└────────┬────────┘The application will launch with the Gradio interface at `http://localhost:7860`

         │

         ▼### Verification

┌─────────────────┐

│  Control Agent  │  Orchestrates research pipelineYou can verify your installation by running:

│                 │```bash

└────────┬────────┘# Check Python environment

         │python -c "import sys; sys.path.insert(0, 'src'); from src.apps.app_gradio_new import EnhancedGradioResearchApp; print('✅ Core dependencies installed')"

         ├──► Literature Agent  → Multi-source paper search

         │                       → Gemini validation# Verify file structure

         │python -c "

         ├──► Embedding Agent   → FAISS vector databaseimport os

         │                       → Semantic similarity searchrequired_files = ['main.py', 'src/agents/control_agent.py', 'src/agents/literature_agent.py', 'src/agents/embedding_agent.py', 'src/apps/app_gradio_new.py']

         │missing = [f for f in required_files if not os.path.exists(f)]

         └──► Review Agents     → Manager + Writing agentsif not missing:

                                 → Multi-agent collaboration    print('✅ All core files present')

```else:

    print(f'❌ Missing files: {missing}')

### Core Components"

```

| Component | File | Purpose |

|-----------|------|---------|## 🔧 Configuration

| **Control Agent** | `src/agents/control_agent.py` | Pipeline orchestration & session management |

| **Literature Agent** | `src/agents/literature_agent.py` | Multi-source discovery & validation |### Required Environment Variables

| **Embedding Agent** | `src/agents/embedding_agent.py` | FAISS vector database operations |

| **Review Agents** | `src/agents/literature_review_agents.py` | Automated review generation || Variable | Description | Required |

| **Gradio Interface** | `src/apps/app_gradio_new.py` | Web UI & user interactions ||----------|-------------|----------|

| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |

---| `RESEARCH_EMAIL` | Email for API politeness | ✅ Yes |



## 🔧 Configuration### Optional Configuration



### Required Environment Variables- **FAISS Settings**: Vector database automatically initializes with optimal settings

- **Search Limits**: Configurable in `control_agent.py` (`PipelineConfig` class)

Create a `.env` file in the root directory:- **Model Parameters**: Adjust temperature and other settings in respective agent files



```env## 📚 Usage Guide

# Required

GOOGLE_API_KEY=your_gemini_api_key_here### 1. Upload Your Own Papers (New!)

RESEARCH_EMAIL=your_email@example.com

**Before searching, you can add your private research papers:**

# Optional (for Google Scholar search)

SERPAPI_KEY=your_serpapi_key_here1. **Click "📤 Upload Your Own Papers"** accordion at the top

```2. **Select PDF files** from your computer (single or multiple files)

3. **Click "📤 Upload & Parse Papers"** button

### Advanced Configuration4. The system will:

   - Extract title, authors, and abstract automatically

Edit configuration in `src/agents/control_agent.py`:   - Add papers to the FAISS vector database

   - Make them available for search and literature review generation

```python

@dataclass**Perfect for:**

class PipelineConfig:- 🔒 Private or unpublished papers

    INITIAL_PAPERS_PER_SOURCE = 5      # Papers per source in initial search- 📚 Papers you already have saved locally

    SECONDARY_PAPERS_PER_SOURCE = 2    # Papers per source in augmented search- 💼 Internal company research documents

    RELEVANCE_THRESHOLD = 0.7          # Minimum AI relevance score- 📖 Papers from subscription journals you have access to

    TOP_DISPLAY_RESULTS = 10           # Results shown to user

    SIMILARITY_THRESHOLD = 0.7         # Vector similarity threshold### 2. Basic Paper Search

```

1. **Enter your research query** in the search box

---2. **Configure search filters** (optional):

   - Paper type (Journal, Conference, Review, All Types)

## 🐛 Troubleshooting   - Publication date range (start/end year)

   - Minimum citation count

### Common Issues   - **Search sources** (NEW): Choose which databases to search

3. **Click "🔍 Find Research Papers"** to begin discovery

**FAISS Installation Errors:**4. **Review results** with AI-generated relevance scores and paper type indicators

```bash5. **Select individual papers** using the interactive checkboxes (up to 20 papers displayed)

# CPU version (most compatible)

pip install faiss-cpu### 2.5. Choosing Search Sources (NEW!)



# GPU version (requires CUDA)In the **⚙️ Advanced Options** section, you can now select which databases to search:

pip install faiss-gpu

```#### Available Sources:

- ✅ **Google Scholar (SerpAPI)**: Most comprehensive, requires API key

**Google API Key Issues:**- ✅ **arXiv**: Latest preprints in STEM fields (free)

- Verify your key at [Google AI Studio](https://makersuite.google.com/app/apikey)- ✅ **CrossRef**: Peer-reviewed papers with DOIs (free)

- Check quota limits in your Google Cloud Console- ✅ **OpenAlex**: Open-access scholarly works (free)

- Ensure the key is correctly saved in `.env`

#### Usage Scenarios:

**Port Already in Use:**```

```bashAll Sources (Default)     → Most comprehensive results

# Use a different portarXiv + OpenAlex          → Latest research only

python main.py --port 7861Google Scholar + CrossRef → Peer-reviewed papers only

```None Selected             → Search ONLY your uploaded papers!

```

**Memory Issues with Large Searches:**

- Reduce `max_papers` in search filters**Pro Tips:**

- Use individual paper selection instead of "Save All"- Use fewer sources for faster searches

- Process papers in smaller batches with augmented search- Uncheck all sources to search only your uploaded PDFs

- Mix sources with uploads for hybrid search

**Papers Not Loading:**- See `SOURCE_SELECTION_QUICKSTART.md` for detailed guide

- Check your internet connection

- Verify API keys are valid### 3. Advanced Features

- Try selecting fewer search sources

#### Individual Paper Selection & Management

### Performance Tips- **Interactive Checkboxes**: Select specific papers from search results (up to 20 papers)

- **Select All Toggle**: Quickly select or deselect all papers with one click

**For Large-Scale Research:**- **Batch Operations**: 

- Use iterative search (augmented search) instead of large initial searches  - Save selected papers only

- Select individual papers rather than saving all at once  - Save all papers from current search

- Enable result caching through session management  - Use selected papers for augmented search



**Memory Optimization:**#### Iterative Search & Query Augmentation

- Close other applications when running large FAISS operations- Use **"🔄 Find More Related Papers"** for Phase 2 augmented search

- Process papers in batches using iterative search- AI automatically generates expanded queries from selected paper content

- Clear old sessions from database periodically- Discovers papers you might have missed in initial search

- Maintains session continuity across multiple iterations

---- Shows query evolution and augmentation tracking



## 📁 Project Structure#### Literature Review Generation

1. Navigate to the **📚 Literature Review** tab

```2. Enter your **research topic** in the text field

Research-Assistant/3. Set **maximum papers** to include (10-50 papers)

├── main.py                    # Application entry point4. Click **"📚 Generate Literature Review"**

├── requirements.txt           # Python dependencies5. **Copy and save** the generated review in Markdown format

├── .env.example              # Example environment configuration

├── .gitignore                # Git ignore rules#### Vector Search & Semantic Discovery

├── README.md                 # This file- Papers are automatically embedded into FAISS vector database

│- Use similarity search to find semantically related papers

├── src/- Leverage AI understanding for better discovery beyond keyword matching

│   ├── agents/               # AI agent implementations- Persistent storage enables cross-session paper discovery

│   │   ├── control_agent.py

│   │   ├── literature_agent.py### 3. Paper Management

│   │   ├── embedding_agent.py

│   │   └── literature_review_agents.py- **Selection Interface**: Interactive checkboxes for precise paper selection

│   │- **Organization**: Papers are automatically categorized by type (📖 Journal, 🎯 Conference, 📋 Review)

│   └── apps/- **Batch Actions**: Save selected papers or all papers with dedicated buttons

│       └── app_gradio_new.py # Gradio web interface- **Export**: Download literature reviews and paper collections

│- **Sessions**: Research sessions are automatically tracked and managed

├── data/                     # Database & uploaded papers (auto-created)

├── latex_output/             # Generated LaTeX projects (auto-created)## 🏗️ Architecture

└── venv/                     # Virtual environment (create manually)

```### System Overview



---```

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

## 🛠️ Tech Stack│   Gradio UI     │    │  Control Agent  │    │ Literature Agent│

│                 │◄──►│                 │◄──►│                 │

| Category | Technology |│  - Modern UI    │    │  - Orchestration│    │ - Paper Search  │

|----------|------------|│  - Checkboxes   │    │  - Session Mgmt │    │ - Gemini Valid. │

| **AI/ML** | Google Gemini 2.5 Flash, LangChain |│  - Multi-Tab    │    │  - Iterative    │    │ - Query Augment.│

| **Vector DB** | FAISS (Facebook AI Similarity Search) |└─────────────────┘    └─────────────────┘    └─────────────────┘

| **Frontend** | Gradio |                                │

| **Data Processing** | Pandas, NumPy |                                ▼

| **PDF Processing** | PyMuPDF |┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

| **Web** | BeautifulSoup, aiohttp |│ Embedding Agent │    │   FAISS Vector  │    │ Review Agents   │

| **Database** | SQLite |│                 │◄──►│    Database     │    │                 │

│ - Text Embeddings│   │                 │    │ - Manager Agent │

---│ - Similarity    │    │ - Vector Search │    │ - Writing Agent │

│ - Metadata      │    │ - Session Store │    │ - Multi-Agent   │

## 🤝 Contributing└─────────────────┘    └─────────────────┘    └─────────────────┘

                                │

Contributions are welcome! Here's how:                                ▼

                       ┌─────────────────┐

1. Fork the repository                       │   MCP Server    │

2. Create a feature branch: `git checkout -b feature/amazing-feature`                       │                 │

3. Commit changes: `git commit -m 'Add amazing feature'`                       │ - SQLite DB     │

4. Push to branch: `git push origin feature/amazing-feature`                       │ - Analytics     │

5. Open a Pull Request                       │ - API Endpoints │

                       └─────────────────┘

**Code Style:**```

- Follow PEP 8 guidelines

- Use type hints where possible### Core Components

- Add docstrings for functions and classes

- Keep functions focused and modular#### 🎯 **Control Agent** (`src/agents/control_agent.py`)

- **Enhanced Research Pipeline**: Orchestrates the entire research workflow with iterative capabilities

---- **Session Management**: Maintains state across research sessions with comprehensive tracking

- **Agent Coordination**: Manages communication between different agents and components

## 📄 License- **Configuration Management**: Handles pipeline parameters, search limits, and quality thresholds

- **Paper Selection Logic**: Manages individual paper selection and batch operations

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.- **Query Augmentation**: Coordinates AI-powered keyword expansion from selected papers



---#### 📖 **Literature Agent** (`src/agents/literature_agent.py`)

- **Multi-Source Discovery**: Searches arXiv, PubMed, and other academic sources with intelligent routing

## 🙏 Acknowledgments- **Gemini Integration**: Uses Gemini 2.5 Flash for relevance validation and confidence scoring

- **Advanced Filtering**: Sophisticated search parameter management with date, citation, and type filters

- **Google Gemini Team** - Powerful AI model- **Real-time Processing**: Asynchronous paper processing and validation with progress tracking

- **FAISS Team** - High-performance vector search- **Database Integration**: Enhanced SQLite database with comprehensive paper metadata and analytics

- **LangChain Community** - AI framework

- **Gradio Team** - Amazing web interface framework#### 🧠 **Embedding Agent** (`src/agents/embedding_agent.py`)

- **Academic Community** - Open science and accessibility- **FAISS Integration**: High-performance vector database operations with optimized indexing

- **Google Embeddings**: State-of-the-art text embedding generation for semantic search

---- **Similarity Search**: Advanced semantic paper matching and discovery with configurable thresholds

- **Metadata Management**: Comprehensive paper metadata storage with search session tracking

## 📞 Support- **Batch Processing**: Efficient batch operations for paper embedding and storage



- **Issues:** [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)#### 📝 **Literature Review Agents** (`src/agents/literature_review_agents.py`)

- **Discussions:** [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)- **Manager Agent**: Maintains review structure and provides oversight with outline generation

- **Writing Agent**: Generates coherent literature reviews with proper citations and formatting

---- **Multi-Agent Collaboration**: Coordinated review generation process with feedback loops

- **Quality Assurance**: Built-in review validation and improvement with iterative refinement

**Happy Researching! 🎓**- **LangChain Integration**: Advanced prompt engineering and response optimization



*Built with ❤️ for the research community*#### 🖥️ **Gradio Interface** (`src/apps/app_gradio_new.py`)

- **Modern Interface**: Beautiful, responsive Gradio-based web interface with professional styling
- **Interactive Elements**: Individual paper checkboxes, progress bars, and real-time updates
- **Multi-Tab Layout**: Organized workflow with separate tabs for search and literature review
- **Batch Operations**: Comprehensive paper selection and management capabilities
- **Export Features**: Download capabilities for reviews and data with markdown support
- **Session Continuity**: Maintains application state across interactions and iterations

#### 🗄️ **MCP Server** (`mcp_server.py`)
- **Database Management**: SQLite-based paper and session storage
- **Analytics Tracking**: Performance metrics and usage statistics
- **Data Persistence**: Long-term storage of research sessions
- **API Integration**: RESTful endpoints for data access

## 🛠️ Development

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
├── config/                             # Configuration files
│   └── mcp_server.py                   # MCP server and database management
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

#### 3. **Gradio Interface Issues**
- Check if port 7860 is available or specify a different port
- Ensure all dependencies are properly installed
- Clear browser cache if interface doesn't load properly

#### 4. **Memory Issues with Large Datasets**
- Reduce `max_papers` in search filters
- Use individual paper selection instead of "Save All"
- Consider upgrading system RAM for large FAISS indexes

#### 5. **Network Timeout Issues**
- Check internet connection stability
- Increase timeout values in configuration
- Use VPN if accessing restricted academic sources

#### 6. **Paper Selection Issues**
- If checkboxes don't appear, ensure papers were found in the search
- Maximum 20 papers can be displayed for selection at once
- Use iterative search to process larger result sets

### Performance Optimization

#### For Large-Scale Research
- **Batch Processing**: Process papers in smaller batches using individual selection
- **Caching**: Enable result caching for repeated queries through session management
- **Parallel Processing**: Increase concurrent request limits in configuration
- **Database Indexing**: Optimize SQLite indexes for large datasets in MCP server
- **Iterative Approach**: Use Phase 2 augmented search instead of large initial searches

#### Memory Management
- **Vector Database**: Use memory mapping for large FAISS indexes
- **Garbage Collection**: Explicit cleanup of large objects between searches
- **Streaming**: Process papers in streaming fashion for large sets
- **Session Cleanup**: Use database cleanup functionality between major searches

#### Interface Optimization
- **Progressive Loading**: Papers load progressively with real-time updates
- **Checkbox Limits**: Maximum 20 papers displayed for optimal interface performance
- **Tab Management**: Use separate tabs to organize workflow and reduce memory usage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini Team** for the powerful Gemini 2.5 Flash model and advanced AI capabilities
- **FAISS Team** at Facebook AI Research for vector search capabilities and optimization  
- **LangChain Community** for the excellent AI framework and multi-agent coordination
- **Gradio Team** for the amazing web interface framework and interactive components
- **Academic Community** for making research papers accessible and promoting open science
- **MCP (Model Context Protocol)** for standardized AI-database integration patterns

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)
- **Email**: Contact via the email configured in your `.env` file

---

**Happy Researching! 🎓**

*Built with ❤️ for the research community*