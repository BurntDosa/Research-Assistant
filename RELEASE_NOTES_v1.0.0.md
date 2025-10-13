# 🎉 Research Assistant v1.0.0

**Initial Public Release** - AI-Powered Research Discovery Platform

---

## � Welcome

This is the **first stable release** of Research Assistant - a comprehensive AI-powered platform for academic research discovery and literature review generation.

### ✨ Key Features

#### 🔍 Multi-Source Paper Discovery
- **Integrated Search**: arXiv, CrossRef, OpenAlex, and Google Scholar
- **AI Validation**: Google Gemini 2.5 Flash for intelligent relevance scoring
- **Smart Query**: AI-enhanced keyword expansion for better results
- **Real-time Scoring**: Dynamic assessment of paper relevance

#### 📄 PDF Upload & Private Papers
- **Local PDF Upload**: Add your own research papers in PDF format
- **Automatic Parsing**: Intelligent extraction of metadata and content
- **Batch Processing**: Handle multiple PDFs simultaneously
- **Private Papers**: Include unpublished work and internal documents

#### 🧠 Vector-Based Semantic Search
- **FAISS Integration**: High-performance similarity search
- **Google Embeddings**: State-of-the-art text embeddings
- **Smart Deduplication**: Intelligent matching across sources
- **Iterative Search**: AI-powered query augmentation

#### 📝 Automated Literature Reviews
- **Multi-Agent System**: Collaborative AI for structured reviews
- **Professional Output**: Well-structured, citation-rich reviews
- **Markdown Export**: Download reviews with proper formatting

#### 💻 Modern Interface
- **Gradio-Powered**: Beautiful, responsive web interface
- **Interactive Selection**: Precise paper selection (up to 20 papers)
- **Real-time Progress**: Live updates during search
- **Multi-Tab Workflow**: Organized research process

### 🔒 Security & Privacy

### 🔒 Security & Privacy

- **BYOK Model**: Bring Your Own Key - full user control
- **Local Storage**: All data stored locally in SQLite
- **Secure .gitignore**: Comprehensive protection for sensitive files
- **No Telemetry**: Zero external data collection
- **API Key Protection**: Enhanced patterns to prevent accidental exposure

---

## 📦 Installation

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/BurntDosa/Research-Assistant.git
cd Research-Assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env with your Google Gemini API key

# 5. Launch the application
python main.py
```

The application will open in your default browser at `http://localhost:7860`

---

## 🎯 What You Can Do

### Research Discovery
1. **Enter your research query** - Describe your research topic
2. **Select sources** - Choose databases or upload your PDFs
3. **Review results** - AI-scored papers with relevance metrics
4. **Select papers** - Pick up to 20 papers for your review

### Literature Review Generation
1. **Auto-generate reviews** - AI creates structured literature reviews
2. **Export markdown** - Download professional-quality reviews
3. **Iterative refinement** - Augment searches based on selections

### Paper Management
1. **Upload PDFs** - Add your private papers
2. **Batch processing** - Handle multiple papers at once
3. **Semantic search** - Find similar papers across all sources
4. **Session persistence** - Your papers are saved between sessions

---

## 🛠️ Tech Stack

- **AI/ML**: Google Gemini 2.5 Flash, LangChain
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Frontend**: Gradio 4.x
- **Data**: Pandas, NumPy, SQLite
- **PDF**: PyMuPDF
- **Web**: BeautifulSoup, aiohttp

---

## 🎓 Best Practices

✅ **DO**: Keep API keys in `.env` file only  
✅ **DO**: Use `.env.example` as template  
✅ **DO**: Verify `.gitignore` before committing  
✅ **DO**: Upload relevant papers for better results  
❌ **DON'T**: Commit `.env` files to git  
❌ **DON'T**: Share API keys publicly  
❌ **DON'T**: Create backup files of `.env` in repo  

---

## 🛡️ Security

We take security seriously. This release includes:

## 🛡️ Security

We take security seriously. This release includes:

- Comprehensive `.gitignore` patterns for sensitive files
- Protection against `.env` backup file exposure
- Secure API key management
- Local-only data storage

If you discover security issues, please report them responsibly:
- **Email**: Report via repository settings email
- **Private**: Do not create public issues for vulnerabilities

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Thank you to the open-source community and all contributors who helped make this project possible.

---

**Documentation**: See [README.md](README.md) for detailed usage instructions  
**Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history

---

**Happy Researching! 🎓**

*Built with ❤️ for the research community*
