# 🎉 Research Assistant v1.0.0

**First Stable Release** - AI-Powered Research Discovery & Literature Review Platform

---

## 🌟 What's New

Research Assistant v1.0.0 is a complete, production-ready platform for intelligent academic paper discovery and automated literature review generation. Built with Google Gemini 2.5 Flash and FAISS vector database.

### ✨ Key Features

#### 🤖 **AI-Powered Paper Discovery**
- Multi-source search across arXiv, CrossRef, OpenAlex, and Google Scholar
- Google Gemini 2.5 Flash for intelligent relevance scoring
- AI-enhanced query augmentation for better results
- Real-time relevance assessment and paper validation

#### 📤 **PDF Upload & Private Papers**
- Upload your own research papers (PDF format)
- Automatic text extraction and metadata parsing
- Include unpublished work and internal documents
- Batch upload support for multiple files
- Seamless integration with all search features

#### 🔍 **Smart Search & Discovery**
- FAISS vector database for semantic similarity search
- Customizable search sources (mix databases or search only uploads)
- Advanced filters: publication date, paper type, citation count
- Intelligent duplicate detection across sources
- Iterative search with AI-powered keyword expansion

#### 📝 **Automated Literature Reviews**
- Multi-agent system for structured review generation
- Proper citations and academic formatting
- Export in Markdown format
- Manager and Writing agents collaborate for quality

#### 🎨 **Modern Interface**
- Beautiful Gradio web interface
- Interactive paper selection with checkboxes
- Real-time progress tracking
- Multi-tab workflow organization
- Batch operations for efficiency

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/BurntDosa/Research-Assistant.git
cd Research-Assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your Google Gemini API key

# 5. Launch
python main.py
```

### First Launch

When you first run the app, you'll see an **API Key Configuration Screen**:

1. Get your free Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Paste your API key and email
3. Click "Save & Continue"
4. Start researching!

---

## 📋 What's Included

### Core Features

✅ Multi-source academic paper search  
✅ PDF upload and parsing  
✅ AI-powered relevance scoring  
✅ FAISS semantic similarity search  
✅ Iterative query augmentation  
✅ Automated literature review generation  
✅ Interactive paper selection  
✅ Batch operations  
✅ Session management  
✅ Export capabilities  

### Technical Components

- **Control Agent**: Research pipeline orchestration
- **Literature Agent**: Multi-source discovery & validation
- **Embedding Agent**: FAISS vector database management
- **Review Agents**: Multi-agent review generation
- **Gradio Interface**: Modern web UI
- **MCP Server**: Metadata and analytics storage

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **AI/ML** | Google Gemini 2.5 Flash, LangChain |
| **Vector DB** | FAISS |
| **Frontend** | Gradio 4.x |
| **Data** | Pandas, NumPy |
| **PDF** | PyMuPDF |
| **Web** | BeautifulSoup, aiohttp |
| **Database** | SQLite |

---

## 📚 Documentation

- **README**: Complete setup and usage guide
- **CHANGELOG**: Detailed version history
- **LICENSE**: MIT License (open source)
- **Code Comments**: Inline documentation throughout

---

## 🎯 Use Cases

Perfect for:

- 📖 **Academic Researchers** conducting literature reviews
- 🎓 **Graduate Students** exploring research topics
- 👥 **Research Groups** managing paper collections
- 🔬 **Scientists** discovering relevant publications
- 💼 **R&D Teams** tracking industry research

---

## 🔐 Privacy & Security

- ✅ Local-only API key storage
- ✅ No telemetry or tracking
- ✅ User data stays on your machine
- ✅ BYOK (Bring Your Own Key) model
- ✅ Open source and auditable

---

## 📊 System Requirements

- **Python**: 3.9 or higher
- **RAM**: 8GB recommended (for FAISS operations)
- **OS**: Windows, macOS, or Linux
- **Internet**: Required for API calls and paper discovery

---

## 🐛 Known Issues

None reported. If you encounter issues, please [open a ticket](https://github.com/BurntDosa/Research-Assistant/issues).

---

## 🤝 Contributing

Contributions welcome! See our [Contributing Guidelines](https://github.com/BurntDosa/Research-Assistant#contributing) in the README.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BurntDosa/Research-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BurntDosa/Research-Assistant/discussions)

---

## 🙏 Acknowledgments

Special thanks to:
- Google Gemini Team for the powerful AI model
- FAISS Team for vector search capabilities
- LangChain Community for the excellent framework
- Gradio Team for the amazing web interface
- Academic Community for promoting open science

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

## 🎓 Citation

If you use Research Assistant in your research, please cite:

```bibtex
@software{research_assistant_2025,
  author = {BurntDosa},
  title = {Research Assistant: AI-Powered Research Discovery Platform},
  year = {2025},
  version = {1.0.0},
  url = {https://github.com/BurntDosa/Research-Assistant}
}
```

---

**Happy Researching! 🔬**

Built with ❤️ for the research community
