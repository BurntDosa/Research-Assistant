# Quick Start Guide - Research Discovery Hub

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd Research-Assistant

# Create virtual environment
python -m venv venv_gemini

# Activate virtual environment
# On macOS/Linux:
source venv_gemini/bin/activate
# On Windows:
venv_gemini\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure API Keys

When you first launch the application, you'll see an API key configuration screen.

#### Required API Keys:

1. **Google Gemini API Key** 🤖
   - Get it: https://makersuite.google.com/app/apikey
   - Free tier: 60 requests/minute
   - Format: `AIzaSy...`

2. **SerpAPI Key** 🔍
   - Get it: https://serpapi.com/manage-api-key
   - Free tier: 100 searches/month
   - Format: any string

#### Optional API Keys:

3. **OpenAI API Key** 🧠 (Optional)
   - Get it: https://platform.openai.com/api-keys
   - Format: `sk-...`

### Step 3: Launch the Application

```bash
python main.py
```

The application will open at:
- **Local:** http://localhost:7860
- **Public:** A Gradio share link (valid for 24 hours)

---

## 📋 First Time Setup

### What You'll See

1. **API Key Configuration Screen** 🔑
   - Instructions on how to get each API key
   - Input fields for your keys
   - "Save & Continue" button

2. **Main Application Screen** 🔬
   - Search for research papers
   - Generate literature reviews
   - Analyze research gaps
   - Assess project feasibility
   - Format documents to LaTeX

### Configuration Process

```
┌─────────────────────────────┐
│  🔑 API Key Configuration   │
├─────────────────────────────┤
│                             │
│  1. Click links to get keys │
│  2. Paste keys in fields    │
│  3. Click "Save & Continue" │
│                             │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│  🔬 Research Discovery Hub  │
├─────────────────────────────┤
│                             │
│  Ready to use all features! │
│                             │
└─────────────────────────────┘
```

---

## 🔐 API Key Storage

Your API keys are stored securely in a `.env` file:

```bash
Research-Assistant/
├── .env          ← Your API keys (created after first setup)
├── .env.example  ← Template file
├── main.py
└── ...
```

**Security Notes:**
- ✅ `.env` is in `.gitignore` (won't be committed to Git)
- ✅ Keys are only used to call respective APIs
- ✅ Keys stay on your local machine
- ✅ You control all costs and usage

---

## 💡 Quick Tips

### First-Time Users

1. **Start with Free Tiers**: Both Gemini and SerpAPI offer free tiers perfect for testing
2. **Get SerpAPI First**: Requires registration but gives you 100 free searches
3. **Gemini is Generous**: 60 requests/minute is plenty for research use
4. **Save Time**: Once configured, you won't need to enter keys again

### Testing the Setup

After configuration, try these features:

1. **Literature Search** 📚
   ```
   Query: "machine learning transformer architecture"
   Results: 10-20 papers
   ```

2. **Generate Review** 📝
   - Search for papers → Select a few → Generate review
   - Tests Gemini API integration

3. **Upload PDF** 📤
   - Upload a research paper PDF
   - System extracts metadata automatically

---

## 🎯 Core Features

### 1. Literature Discovery
- 🔍 Smart Google Scholar search
- 📊 Citation-based filtering
- 🔄 Iterative query refinement
- 💾 Save papers to collection

### 2. Literature Review Generation
- 📖 AI-powered synthesis
- 🎨 Multiple templates (Comprehensive, Comparative, Gap-Focused, etc.)
- 📑 Structured output (Introduction, Analysis, Synthesis, Conclusion)
- 💾 Export as PDF or Markdown

### 3. Research Gap Analysis
- 🔬 Identify unexplored areas
- 💡 Generate research questions
- 📊 Categorize gaps (methodological, theoretical, empirical)
- 🎯 Priority ranking

### 4. Feasibility Assessment
- ⚖️ Evaluate project viability
- 📋 7 resource categories:
  - Computational resources
  - Funding
  - Time
  - Personnel
  - Data access
  - Equipment
  - Expertise
- 🎯 Scoring (0-100)
- 💡 AI-powered recommendations

### 5. LaTeX Writing Assistant
- 📝 8 built-in templates (IEEE, ACM, Springer, etc.)
- 📤 Upload your own template
- 📄 Upload complete document (PDF/DOCX/TXT/MD)
- 🤖 AI extracts sections automatically
- 🖼️ Image processing and placement
- 📚 Bibliography generation
- 📦 Complete LaTeX project (ZIP download)

---

## 🛠️ Troubleshooting

### Application Won't Start

**Problem:** Error on launch

**Solutions:**
1. Check Python version (3.8+)
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check for port conflicts (7860)

### API Key Configuration Issues

**Problem:** "Invalid API key" or "Keys not configured"

**Solutions:**
1. Check key formats:
   - Gemini: starts with `AIza`
   - OpenAI: starts with `sk-`
2. Ensure no extra spaces
3. Delete `.env` and reconfigure if needed

### Can't See API Key Screen

**Problem:** Application shows main interface, but I want to reconfigure keys

**Solutions:**
1. Option A: Edit `.env` file directly
2. Option B: Delete `.env` and restart application
3. Option C: Create new `.env` from `.env.example`

---

## 📊 Usage Examples

### Example 1: Literature Search → Review

```
1. Search: "neural architecture search"
2. Filter: 2020-2024, min 50 citations
3. Select: 10 papers
4. Generate: Comprehensive Review
5. Export: PDF
```

### Example 2: Research Gap Analysis

```
1. Search: "federated learning privacy"
2. Add papers to collection
3. Go to Gap Analysis tab
4. Select papers
5. Generate gap analysis
6. Review research questions
```

### Example 3: Feasibility Assessment

```
1. Navigate to Feasibility tab
2. Fill in available resources:
   - Computational: GPU cluster
   - Funding: $10,000
   - Time: 6 months
   - Team: 2 researchers
3. Generate assessment
4. Review recommendations
```

### Example 4: Format Paper to LaTeX

```
Option A - Upload Document:
1. Navigate to LaTeX Writer
2. Upload your DOCX/PDF
3. Select template (e.g., IEEE)
4. Add images if needed
5. Generate LaTeX project
6. Download ZIP

Option B - Manual Entry:
1. Enter title, authors
2. Fill in sections
3. Select template
4. Generate
```

---

## 🔄 Workflow Integration

### Typical Research Workflow

```
┌─────────────────┐
│  Search Papers  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Save to DB     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Generate       │
│  Review         │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Analyze Gaps   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Assess         │
│  Feasibility    │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Conduct        │
│  Research       │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Format to      │
│  LaTeX          │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Submit Paper!  │
└─────────────────┘
```

---

## 📚 Documentation

- **API Key Setup:** See `docs/API_KEY_SETUP.md`
- **Research Gap Analysis:** See `docs/RESEARCH_GAP_ANALYSIS.md`
- **Feasibility Assessment:** See `docs/FEASIBILITY_ASSESSMENT.md`
- **LaTeX Writing:** See `docs/LATEX_WRITING_ASSISTANT.md`

---

## 🆘 Support

### Common Issues

1. **Rate Limits**: Wait a minute or upgrade API plan
2. **No Search Results**: Try broader query terms
3. **PDF Upload Fails**: Ensure PDF is text-based (not scanned)
4. **LaTeX Generation Slow**: Large documents take 30-60 seconds

### Getting Help

1. Check documentation in `docs/` folder
2. Review error messages in terminal
3. Verify API key status in provider dashboards
4. Check application logs

---

## 🎉 You're Ready!

Launch the application and start discovering research!

```bash
python main.py
```

Happy researching! 🔬📚

---

*Last Updated: October 2025*
