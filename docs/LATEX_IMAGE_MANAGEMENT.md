# LaTeX Image Management & Overleaf Integration

## Overview

Enhanced the LaTeX Writing Assistant with advanced image management and Overleaf integration capabilities.

---

## New Features

### 1. Image Metadata Input System

Users can now provide detailed metadata for each image:

#### **Figure Captions**
- One caption per line (in same order as uploaded images)
- Supports standard academic caption format
- Automatically extracts figure numbers

**Example:**
```
Figure 1: System Architecture Overview
Figure 2: Experimental Results Comparison
Figure 3: Performance Metrics Over Time
```

#### **Section Placement**
- Specify which section each image should appear in
- One section name per line
- Supports any section name in the paper

**Example:**
```
Methodology
Results
Results
```

#### **Automatic Processing**
- Figure numbers extracted from captions
- Labels generated automatically (e.g., `fig:1`, `fig:2`)
- Proper LaTeX figure environments created
- Images placed in specified sections

---

### 2. Important Notice for Document Upload

**⚠️ Critical Information:**

When uploading a complete document (PDF, DOCX, TXT, MD):
- **Images are NOT parsed automatically**
- You MUST upload images separately
- You MUST provide captions and section placement
- This ensures proper image formatting and placement

---

### 3. Overleaf Integration

#### **"Open in Overleaf" Button**
- Appears after successful LaTeX generation
- Provides instructions for Overleaf upload
- Enables direct online editing and compilation

#### **Three Methods to Use Overleaf**

**Method 1: Direct Upload (Recommended)**
1. Go to https://www.overleaf.com
2. Click "New Project" → "Upload Project"
3. Upload the downloaded ZIP file
4. Start editing immediately

**Method 2: Via URL (For hosted files)**
```
https://www.overleaf.com/docs?snip_uri=YOUR_ZIP_URL
```

**Method 3: Manual Import**
1. Extract ZIP file locally
2. Create blank project in Overleaf
3. Upload extracted files
4. Compile and edit

---

## User Interface Changes

### LaTeX Writer Tab

#### **Images & Figures Section**

**Before:**
```
Upload Images: [File Upload]
```

**After:**
```
⚠️ Important: When uploading a complete document, images are NOT parsed automatically.
You must upload images separately here with their metadata (figure number, caption, section).

Upload Images: [File Upload]

Image Captions (one per line, in same order):
[Text Area]

Place Images in Sections (one per line):
[Text Area]
```

#### **Output Section**

**Before:**
```
[Output Markdown]
📄 Main .tex File
📦 Complete Project (ZIP)
```

**After:**
```
[Output Markdown]
📄 Main .tex File
📦 Complete Project (ZIP)
🌐 Open in Overleaf [Button]
[Overleaf Instructions - shown when button clicked]
```

---

## Technical Implementation

### Image Metadata Structure

```python
images = [{
    'path': 'path/to/image.png',
    'filename': 'figure_1.png',
    'caption': 'Figure 1: System Architecture',
    'label': 'fig:1',
    'section': 'Methodology',
    'width': '0.8\\textwidth'
}]
```

### LaTeX Generation

The AI prompt now includes specific placement instructions:

```
**Image Placement Instructions:**
- Place figure_1.png in 'Methodology' section with caption: Figure 1: System Architecture (\label{fig:1})
- Place figure_2.png in 'Results' section with caption: Figure 2: Experimental Results (\label{fig:2})
```

### Figure Environment

Generated LaTeX code:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/figure_1.png}
    \caption{System Architecture}
    \label{fig:1}
\end{figure}
```

---

## Usage Examples

### Example 1: Research Paper with 3 Figures

**1. Upload Images:**
- `architecture.png`
- `results_chart.png`
- `comparison_table.png`

**2. Provide Captions:**
```
Figure 1: Proposed System Architecture
Figure 2: Performance Comparison with Baseline Methods
Figure 3: Results Summary Table
```

**3. Specify Sections:**
```
Methodology
Results
Results
```

**Result:**
- Figure 1 appears in Methodology section
- Figures 2 and 3 appear in Results section
- All properly labeled and referenceable

---

### Example 2: Conference Paper with Detailed Captions

**Captions:**
```
Figure 1: Overview of the deep learning pipeline used in our experiments
Figure 2: Accuracy metrics across different training epochs (a) Training accuracy, (b) Validation accuracy
Figure 3: Comparison with state-of-the-art methods on benchmark datasets
```

**Sections:**
```
Introduction
Experiments
Discussion
```

---

## Benefits

### For Users

1. **Precise Control**: Specify exactly where each image appears
2. **Professional Captions**: Use standard academic figure notation
3. **Easy Referencing**: Automatic label generation for cross-references
4. **Quick Editing**: Open in Overleaf for immediate online editing
5. **No Manual Placement**: AI handles LaTeX figure environment creation

### For Workflow

1. **Document Upload + Manual Images**: Upload text document, then add images with metadata
2. **Manual Entry + Images**: Write sections manually, upload images with captions
3. **Hybrid Approach**: Mix uploaded content with manual section editing
4. **Post-Processing**: Edit in Overleaf after generation

---

## Tips & Best Practices

### Image Captions

✅ **Good Examples:**
```
Figure 1: System Architecture Overview
Figure 2: Performance Metrics (a) Training (b) Testing
Figure 3: Comparison of Methods A, B, and C
```

❌ **Avoid:**
```
image1
My picture
graph
```

### Section Names

✅ **Use Exact Section Names:**
```
Introduction
Related Work
Methodology
Results
Discussion
Conclusion
```

❌ **Avoid Typos:**
```
Intro  (use "Introduction")
Method  (use "Methodology")
Rsults  (typo)
```

### Number of Images

- Ensure number of captions matches number of uploaded images
- Ensure number of sections matches number of images
- If mismatch, defaults will be used:
  - Caption: "Figure X: [Add caption here]"
  - Section: "Results"

---

## Troubleshooting

### Images Not Appearing

**Problem**: Images missing in generated PDF

**Solutions:**
1. Check file paths in figures/ directory
2. Verify image files were uploaded
3. Ensure correct file extensions
4. Check LaTeX log for errors

### Wrong Section Placement

**Problem**: Image appears in wrong section

**Solutions:**
1. Check section name spelling
2. Ensure section exists in document
3. Verify line count matches image count
4. Check section name case sensitivity

### Overleaf Upload Issues

**Problem**: Can't upload to Overleaf

**Solutions:**
1. Ensure ZIP file downloaded completely
2. Try extracting and re-uploading files manually
3. Check Overleaf account status
4. Verify file size limits

---

## Future Enhancements

Planned improvements:

- [ ] Direct Overleaf API integration (upload without manual step)
- [ ] Image extraction from uploaded PDFs
- [ ] Automatic figure placement optimization
- [ ] Caption generation using AI
- [ ] Figure cross-reference suggestions
- [ ] Multi-panel figure support
- [ ] Image quality optimization
- [ ] Automatic image format conversion

---

## Related Documentation

- **LaTeX Writing Assistant**: `docs/LATEX_WRITING_ASSISTANT.md`
- **Implementation Details**: `docs/LATEX_IMPLEMENTATION.md`
- **Quick Start Guide**: `docs/QUICK_START.md`

---

*Last Updated: October 2025*
