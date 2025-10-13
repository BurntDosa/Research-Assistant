# 📝 LaTeX Writing Assistant

## Overview

The **LaTeX Writing Assistant** is an AI-powered tool that transforms your research content into publication-ready LaTeX documents. It supports major academic journals and conferences, handles images and visual elements, and generates complete, compilable LaTeX projects.

## Key Features

### 📚 Built-in Templates
**8 Professional Academic Templates:**
- **IEEE Journal** - IEEE Transactions format
- **ACM Conference** - ACM proceedings format  
- **Springer LNCS** - Lecture Notes in Computer Science
- **Elsevier Journal** - Elsevier article format
- **arXiv Preprint** - arXiv standard format
- **NeurIPS** - NeurIPS conference format
- **CVPR** - Computer Vision conference format
- **AAAI** - AAAI conference format

### ✨ Core Capabilities
- **AI-Powered Formatting**: Gemini 2.0 Flash generates properly structured LaTeX code
- **Custom Template Support**: Upload your own .tex template for specific requirements
- **Image Handling**: Automatic processing and placement of figures
- **Complete Projects**: Generates ready-to-compile LaTeX projects with all files
- **ZIP Download**: Get entire project as downloadable archive
- **Compilation Scripts**: Includes bash scripts for easy compilation

### 📦 Output Package
Each generated project includes:
1. **Main .tex file** - Complete LaTeX document
2. **references.bib** - Bibliography in BibTeX format
3. **figures/** - All images properly formatted
4. **README.md** - Compilation instructions
5. **compile.sh** - Bash script for compilation

---

## How to Use

### Step 1: Enter Document Information

#### Required Fields:
```
Paper Title: "Deep Learning for Medical Image Analysis"

Authors: John Doe, Jane Smith, Alex Johnson

Template: IEEE Journal (or choose from 8 options)

Abstract: 
"This paper presents a novel deep learning approach for 
automated medical image analysis..."

Keywords: deep learning, medical imaging, CNN, diagnosis
```

### Step 2: Write Your Sections

Fill in the content for each section:

**1. Introduction**
```
Background, motivation, and overview of your work
```

**2. Related Work**
```
Survey of previous research and how yours differs
```

**3. Methodology**
```
Detailed explanation of your approach
```

**4. Results**
```
Experimental results and analysis
```

**5. Conclusion**
```
Summary, contributions, and future work
```

### Step 3: Add Visual Elements

#### Upload Images:
- Click "Upload Images"
- Select multiple images (PNG, JPG, PDF)
- Images will be automatically processed and placed

#### Add References:
```
LeCun et al. Deep Learning, Nature 2015
Krizhevsky et al. ImageNet Classification, NIPS 2012
He et al. Deep Residual Learning, CVPR 2016
```
(One reference per line)

### Step 4: Generate Document

Click **"📝 Generate LaTeX Document"**

The AI will:
1. Analyze your content
2. Apply the selected template
3. Format all sections properly
4. Place images with captions
5. Create bibliography
6. Generate complete project

### Step 5: Download and Compile

1. **Download ZIP** file
2. **Extract** to your directory
3. **Compile** using one of these methods:

**Option A: Using pdflatex**
```bash
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

**Option B: Using the script**
```bash
chmod +x compile.sh
./compile.sh
```

**Option C: Using latexmk (recommended)**
```bash
latexmk -pdf paper.tex
```

---

## Template Guide

### IEEE Journal Template
**Best for:**
- IEEE Transactions submissions
- Journal articles in engineering/CS
- Technical papers with equations

**Features:**
- Two-column layout
- IEEE citation style
- Optimized for equations and algorithms

**Document Class:** `IEEEtran`

**Example Use Cases:**
- IEEE Transactions on Pattern Analysis
- IEEE Transactions on Neural Networks
- IEEE Signal Processing Letters

---

### ACM Conference Template
**Best for:**
- ACM conference submissions
- SIGCHI, SIGCOMM, SIGMOD papers
- Computer science research

**Features:**
- ACM standard format
- Proper metadata handling
- Rights management support

**Document Class:** `acmart`

**Example Use Cases:**
- CHI conference
- SIGCOMM
- WWW conference

---

### Springer LNCS Template
**Best for:**
- Springer conference proceedings
- Computer science conferences
- Lecture note submissions

**Features:**
- Classic Springer format
- Numbered sections
- Running headers

**Document Class:** `llncs`

**Example Use Cases:**
- ICML (some years)
- ECML PKDD
- Various CS conferences

---

### Elsevier Journal Template
**Best for:**
- Elsevier journal submissions
- Medical/biological research
- Multidisciplinary journals

**Features:**
- Flexible formatting options
- Multiple bibliography styles
- Author affiliations

**Document Class:** `elsarticle`

**Example Use Cases:**
- Medical Image Analysis
- Pattern Recognition
- Computer Vision and Image Understanding

---

### NeurIPS Conference Template
**Best for:**
- NeurIPS submissions
- Machine learning research
- Neural network papers

**Features:**
- NeurIPS 2024 style
- Anonymous submission support
- Algorithm environments

**Document Class:** `neurips_2024`

**Example Use Cases:**
- NeurIPS main conference
- NeurIPS workshops
- Similar ML conferences

---

### CVPR Conference Template
**Best for:**
- CVPR submissions
- Computer vision research
- Image processing papers

**Features:**
- CVPR official style
- Figure-heavy layouts
- Tight formatting

**Document Class:** `cvpr`

**Example Use Cases:**
- CVPR main conference
- ICCV (similar format)
- ECCV (similar format)

---

### arXiv Preprint Template
**Best for:**
- arXiv submissions
- Pre-publication sharing
- General academic writing

**Features:**
- Clean, readable format
- Flexible structure
- Standard packages

**Document Class:** `article`

**Example Use Cases:**
- Preprints before conference
- Early research sharing
- Technical reports

---

## Custom Template Usage

### How to Use Custom Templates

If your target conference/journal provides a specific LaTeX template:

1. **Download** their .tex template file
2. **Upload** via "Custom Template" field
3. The system will:
   - Extract document class
   - Identify required packages
   - Adapt your content to their format

### Custom Template Requirements:
- Must be a valid .tex file
- Should include `\documentclass{}`
- Should have standard structure

### Example Custom Template:
```latex
\documentclass[conference]{IEEEtran}
\usepackage{graphicx}
\usepackage{amsmath}
% ... other packages

% Your template structure
```

---

## Advanced Features

### Image Processing

The assistant automatically:
- **Copies images** to figures/ directory
- **Renames** systematically (image_1.png, image_2.png, etc.)
- **Generates captions** (Figure 1, Figure 2, etc.)
- **Creates labels** (fig:1, fig:2, etc.)
- **Sets width** (default: 0.8\textwidth)

### Customizing Images in LaTeX:
After generation, edit the .tex file:

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/image_1.png}
\caption{Your custom caption here}
\label{fig:results}
\end{figure}
```

### Bibliography Management

References are converted to BibTeX format:

**Input:**
```
LeCun et al. Deep Learning, Nature 2015
```

**Output (.bib file):**
```bibtex
@article{ref1,
  title={Deep Learning, Nature 2015},
  author={LeCun et al.},
  year={2015}
}
```

**Tip:** Edit references.bib for accurate citations!

---

## Best Practices

### 1. Content Preparation

**✅ DO:**
- Write clear, well-structured content
- Use proper grammar and formatting
- Include all required sections
- Provide complete abstracts

**❌ DON'T:**
- Leave sections empty
- Use LaTeX commands in content (AI handles formatting)
- Include special characters without escaping

### 2. Image Guidelines

**✅ DO:**
- Use high-resolution images (300 DPI+)
- Supported formats: PNG, JPG, PDF
- Name images descriptively
- Upload in order of appearance

**❌ DON'T:**
- Use very large images (>10 MB)
- Mix low and high quality
- Include LaTeX-sensitive filenames

### 3. References

**✅ DO:**
- Provide complete citations
- Use consistent format
- Include year and publication
- One reference per line

**❌ DON'T:**
- Use incomplete citations
- Mix citation styles
- Include special LaTeX characters

### 4. After Generation

**✅ DO:**
- Review generated LaTeX code
- Compile locally to check
- Customize as needed
- Add equations manually
- Refine figure placement

**❌ DON'T:**
- Submit without reviewing
- Assume 100% perfection
- Skip local compilation test

---

## Common Workflows

### Workflow 1: Conference Paper Submission

```
1. Select appropriate template (e.g., NeurIPS, CVPR)
2. Fill in all content sections
3. Upload figures
4. Add references
5. Generate LaTeX
6. Download ZIP
7. Extract and compile
8. Review PDF
9. Make manual adjustments
10. Submit to conference
```

### Workflow 2: Journal Article

```
1. Choose journal template (IEEE, Elsevier)
2. Write comprehensive sections
3. Include high-quality figures
4. Add complete references
5. Generate LaTeX project
6. Compile and review
7. Add complex equations manually
8. Format tables (if needed)
9. Final compilation
10. Submit to journal
```

### Workflow 3: arXiv Preprint

```
1. Use arXiv template
2. Include all content
3. Upload figures
4. Generate document
5. Quick review
6. Upload to arXiv
```

### Workflow 4: Custom Template

```
1. Download conference template
2. Upload as custom template
3. Fill content
4. Generate
5. Verify format compliance
6. Submit
```

---

## Limitations & Workarounds

### Current Limitations

❌ **Complex Equations**
- **Limitation**: Must be added manually to .tex file
- **Workaround**: Edit generated .tex, add in proper environments

❌ **Tables**
- **Limitation**: Not automatically generated
- **Workaround**: Create tables in .tex after generation

❌ **Algorithms**
- **Limitation**: Algorithm pseudocode not included
- **Workaround**: Use `algorithm` and `algorithmic` packages manually

❌ **Cross-References**
- **Limitation**: Internal references need manual setup
- **Workaround**: Add `\label{}` and `\ref{}` commands

### Planned Features

🔄 **Coming Soon:**
- Table generation from data
- Equation input support
- Algorithm pseudocode
- Cross-reference automation
- Multiple file management
- Supplementary material handling

---

## Troubleshooting

### Issue: Compilation Errors

**Problem:** LaTeX won't compile

**Solutions:**
1. Check error message carefully
2. Ensure all required packages installed
3. Verify image files exist in figures/
4. Check for special characters
5. Try compiling twice (for references)

### Issue: Images Not Showing

**Problem:** Figures missing in PDF

**Solutions:**
1. Verify images in figures/ directory
2. Check file extensions match .tex
3. Ensure images are not corrupted
4. Try different image format

### Issue: Bibliography Empty

**Problem:** No references appear

**Solutions:**
1. Run `bibtex` after first `pdflatex`
2. Check references.bib format
3. Compile sequence: pdflatex → bibtex → pdflatex → pdflatex
4. Verify `\bibliography{references}` in .tex

### Issue: Format Doesn't Match Template

**Problem:** Output looks different from expected

**Solutions:**
1. Verify correct template selected
2. Check if custom template uploaded correctly
3. Review template-specific requirements
4. Manually adjust in .tex if needed

---

## FAQ

### Q: Can I use this for my thesis?

**A**: Yes, but you'll need to provide a custom thesis template. Most universities provide LaTeX thesis templates.

### Q: Does this handle equations?

**A**: Currently, you need to add complex equations manually to the generated .tex file. Simple inline math is handled.

### Q: What about multiple authors with affiliations?

**A**: The AI formats authors appropriately for each template. For complex affiliations, edit the .tex file after generation.

### Q: Can I generate multiple formats?

**A**: Yes! Generate once for each template you need. Compare outputs to choose the best format.

### Q: Is the generated LaTeX perfect?

**A**: No. Review and edit the .tex file for:
- Equations
- Tables
- Complex formatting
- Cross-references
- Special styling

### Q: How do I cite figures in text?

**A**: After generation, use LaTeX commands:
```latex
See Figure~\ref{fig:1} for results...
```

### Q: Can I add more sections?

**A**: Yes! Edit the .tex file and add new sections:
```latex
\section{Your New Section}
Content here...
```

### Q: What LaTeX distribution do I need?

**A**: Any modern distribution:
- **Windows**: MiKTeX or TeX Live
- **Mac**: MacTeX
- **Linux**: TeX Live

### Q: How do I edit the generated document?

**A**: Use any LaTeX editor:
- Overleaf (online)
- TeXstudio (cross-platform)
- TeXmaker (cross-platform)
- VS Code with LaTeX Workshop

---

## Tips for Best Results

### Content Tips

✅ **Write clearly** - AI formats better with well-written content
✅ **Structure properly** - Use clear section breaks
✅ **Be specific** - Detailed content = better formatting
✅ **Include context** - Help AI understand your field

### Template Selection Tips

✅ **Match your target** - Use the template where you'll submit
✅ **When in doubt** - Start with IEEE or arXiv
✅ **Check guidelines** - Verify template matches submission requirements
✅ **Test compile** - Always compile locally before submitting

### Image Tips

✅ **High resolution** - Use 300 DPI or higher
✅ **Vector graphics** - PDF format for diagrams
✅ **Consistent style** - Match figure aesthetics
✅ **Label clearly** - Make figures self-explanatory

### Reference Tips

✅ **Complete info** - Include all citation details
✅ **Consistent format** - Pick one style and stick to it
✅ **Recent work** - Include latest relevant papers
✅ **Verify** - Double-check after generation

---

## Integration with Research Assistant

### Workflow: From Search to Paper

```
1. Literature Search
   └─→ Find relevant papers
   
2. Save Papers
   └─→ Build your collection
   
3. Literature Review
   └─→ Generate comprehensive review
   
4. Gap Analysis
   └─→ Identify research opportunities
   
5. Feasibility Assessment
   └─→ Check if project is viable
   
6. Conduct Research
   └─→ Do your experiments
   
7. LaTeX Writing Assistant ← YOU ARE HERE
   └─→ Format results as paper
   
8. Submit Paper
   └─→ Submit to conference/journal
```

### Using Search Results for References

**Tip:** Papers found via literature search can be used as references!

1. Save relevant papers
2. Export citations
3. Paste into LaTeX Writer references field
4. Generate document with proper citations

---

## 🚀 Get Started

Ready to format your research paper?

1. Navigate to **"📝 LaTeX Writer"** tab
2. Fill in document information
3. Write your sections
4. Upload images (if any)
5. Click **"📝 Generate LaTeX Document"**
6. Download ZIP and compile locally
7. Review and refine
8. Submit your paper!

**Remember**: This tool generates a strong foundation. Review and customize the LaTeX code for your specific needs!

---

## Future: Open Source Model Training

**Current**: Using Gemini 2.0 Flash for LaTeX generation

**Future Plan**: Train specialized open-source model on LaTeX
- **Goal**: 100% accurate LaTeX code
- **Approach**: Fine-tune on millions of LaTeX documents
- **Benefits**: Offline use, faster generation, perfect formatting
- **Timeline**: Planned for future release

**Why it matters**: A specialized LaTeX model will understand:
- Complex equation formatting
- Table structures
- Algorithm pseudocode
- Cross-reference systems
- Template-specific nuances

Stay tuned for updates! 🔬

---

*Generated LaTeX projects are ready to compile with any standard LaTeX distribution. Happy writing! 📝*
