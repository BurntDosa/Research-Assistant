#!/usr/bin/env python3
"""
LaTeX Writing Assistant
Formats research documents according to academic journal and conference templates
Handles text, images, graphs, tables, and other visual elements
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import shutil
import zipfile
import base64

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LaTeXTemplate:
    """Represents a LaTeX template"""
    
    def __init__(self, name: str, template_type: str, description: str, 
                 base_template: str, required_packages: List[str]):
        self.name = name
        self.template_type = template_type  # 'journal' or 'conference'
        self.description = description
        self.base_template = base_template
        self.required_packages = required_packages


class LaTeXWritingAssistant:
    """LaTeX writing assistant for academic papers"""
    
    # Built-in templates
    TEMPLATES = {
        'ieee_journal': LaTeXTemplate(
            name='IEEE Journal',
            template_type='journal',
            description='IEEE Transactions journal format',
            base_template='IEEEtran',
            required_packages=['cite', 'amsmath', 'graphicx', 'subfig']
        ),
        'acm_conference': LaTeXTemplate(
            name='ACM Conference',
            template_type='conference',
            description='ACM conference proceedings format',
            base_template='acmart',
            required_packages=['graphicx', 'booktabs', 'hyperref']
        ),
        'springer_lncs': LaTeXTemplate(
            name='Springer LNCS',
            template_type='conference',
            description='Springer Lecture Notes in Computer Science',
            base_template='llncs',
            required_packages=['graphicx', 'cite', 'amsmath']
        ),
        'elsevier': LaTeXTemplate(
            name='Elsevier Journal',
            template_type='journal',
            description='Elsevier journal article format',
            base_template='elsarticle',
            required_packages=['graphicx', 'amsmath', 'natbib', 'hyperref']
        ),
        'arxiv': LaTeXTemplate(
            name='arXiv',
            template_type='preprint',
            description='arXiv preprint format',
            base_template='article',
            required_packages=['graphicx', 'amsmath', 'hyperref', 'natbib']
        ),
        'neurips': LaTeXTemplate(
            name='NeurIPS',
            template_type='conference',
            description='NeurIPS conference format',
            base_template='neurips_2024',
            required_packages=['graphicx', 'amsmath', 'algorithm', 'algorithmic']
        ),
        'cvpr': LaTeXTemplate(
            name='CVPR',
            template_type='conference',
            description='CVPR conference format',
            base_template='cvpr',
            required_packages=['graphicx', 'amsmath', 'times', 'epsfig']
        ),
        'aaai': LaTeXTemplate(
            name='AAAI',
            template_type='conference',
            description='AAAI conference format',
            base_template='aaai24',
            required_packages=['graphicx', 'amsmath', 'booktabs']
        )
    }
    
    def __init__(self, output_dir: str = "latex_output"):
        """Initialize the LaTeX Writing Assistant"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("LaTeX Writing Assistant initialized with Gemini 2.5 Flash")
    
    def format_document(
        self,
        content: str,
        template_name: str,
        title: str,
        authors: List[str],
        abstract: str,
        keywords: List[str],
        sections: Dict[str, str],
        references: List[str],
        images: Optional[List[Dict[str, Any]]] = None,
        tables: Optional[List[Dict[str, Any]]] = None,
        equations: Optional[List[str]] = None,
        custom_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format a research document into LaTeX
        
        Args:
            content: Raw document content
            template_name: Name of template to use
            title: Paper title
            authors: List of author names
            abstract: Abstract text
            keywords: List of keywords
            sections: Dictionary of section_name: section_content
            references: List of bibliography entries
            images: List of image metadata (path, caption, label)
            tables: List of table data
            equations: List of mathematical equations
            custom_template: Custom template content (if not using built-in)
        
        Returns:
            Dictionary containing LaTeX code and metadata
        """
        try:
            logger.info(f"Formatting document with template: {template_name}")
            
            # Get template
            if custom_template:
                template = self._parse_custom_template(custom_template)
            else:
                if template_name not in self.TEMPLATES:
                    raise ValueError(f"Unknown template: {template_name}")
                template = self.TEMPLATES[template_name]
            
            # Create project directory
            project_name = self._sanitize_filename(title)
            project_dir = self.output_dir / project_name
            project_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (project_dir / "figures").mkdir(exist_ok=True)
            (project_dir / "tables").mkdir(exist_ok=True)
            
            # Process and save images
            image_info = []
            if images:
                image_info = self._process_images(images, project_dir / "figures")
            
            # Process tables
            table_info = []
            if tables:
                table_info = self._process_tables(tables)
            
            # Pre-generate citation keys from references
            citation_keys = []
            if references:
                for i, ref in enumerate(references, 1):
                    parsed = self._parse_reference(ref.strip())
                    key = self._generate_citation_key(parsed['author'], parsed['year'], i)
                    citation_keys.append(key)
                logger.info(f"Pre-generated citation keys: {citation_keys}")
            
            # Generate LaTeX code using AI (now with citation keys)
            latex_code = self._generate_latex_with_ai(
                template=template,
                title=title,
                authors=authors,
                abstract=abstract,
                keywords=keywords,
                sections=sections,
                references=references,
                citation_keys=citation_keys,  # Pass the keys
                images=image_info,
                tables=table_info,
                equations=equations
            )
            
            # Save main .tex file
            main_tex_path = project_dir / f"{project_name}.tex"
            with open(main_tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            # Create bibliography file with same citation keys
            if references:
                bib_path = project_dir / "references.bib"
                generated_keys = self._create_bibliography(references, bib_path)
                # Verify they match
                if generated_keys != citation_keys:
                    logger.warning(f"Citation key mismatch! Expected: {citation_keys}, Got: {generated_keys}")
            
            # Create README with compilation instructions
            self._create_readme(project_dir, project_name, template)
            
            # Create compilation script
            self._create_compile_script(project_dir, project_name)
            
            # Create ZIP archive
            zip_path = self._create_zip_archive(project_dir, project_name)
            
            result = {
                'success': True,
                'latex_code': latex_code,
                'project_dir': str(project_dir),
                'main_file': str(main_tex_path),
                'zip_file': str(zip_path),
                'template_used': template.name,
                'images_processed': len(image_info),
                'tables_processed': len(table_info),
                'sections': list(sections.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Document formatted successfully: {project_name}")
            return result
            
        except Exception as e:
            logger.error(f"Document formatting failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Formatting error: {str(e)}'
            }
    
    def _generate_latex_with_ai(
        self,
        template: LaTeXTemplate,
        title: str,
        authors: List[str],
        abstract: str,
        keywords: List[str],
        sections: Dict[str, str],
        references: List[str],
        citation_keys: List[str],  # Add citation keys parameter
        images: Optional[List[Dict[str, Any]]],
        tables: Optional[List[Dict[str, Any]]],
        equations: Optional[List[str]]
    ) -> str:
        """Use AI to generate LaTeX code"""
        
        # Prepare content summary
        sections_text = "\n\n".join([f"## {name}\n{content}" for name, content in sections.items()])
        
        # Prepare citation information
        citation_info = ""
        if references and citation_keys:
            citation_info = "\n**Citation Keys to Use:**\n"
            for i, (ref, key) in enumerate(zip(references, citation_keys), 1):
                # Show first 80 chars of reference
                ref_preview = ref[:80] + "..." if len(ref) > 80 else ref
                citation_info += f"{i}. Use `\\cite{{{key}}}` for: {ref_preview}\n"
        
        # Prepare image placement information
        image_placements = ""
        if images:
            image_placements = "\n**Image Placement Instructions:**\n"
            for i, img in enumerate(images):
                section = img.get('section', 'Results')
                caption = img.get('caption', f'Figure {i+1}')
                label = img.get('label', f'fig:{i+1}')
                filename = img.get('filename', f'image_{i+1}')
                image_placements += f"- Place {filename} in '{section}' section with caption: {caption} (\\label{{{label}}})\n"
        
        prompt = f"""You are an expert LaTeX document formatter. Generate a complete, compilable LaTeX document.

**Template Information:**
- Template: {template.name}
- Document Class: {template.base_template}
- Type: {template.template_type}
- Required Packages: {', '.join(template.required_packages)}

**Document Content:**

Title: {title}

Authors: {', '.join(authors)}

Abstract:
{abstract}

Keywords: {', '.join(keywords)}

**Sections:**
{sections_text}

**Visual Elements:**
- Images: {len(images) if images else 0}
- Tables: {len(tables) if tables else 0}
- Equations: {len(equations) if equations else 0}

{image_placements}

{citation_info}

**References:** {len(references)} citations provided in references.bib

**Instructions:**
1. Generate a complete LaTeX document with proper structure
2. Use the specified document class: \\documentclass{{{template.base_template}}}
3. Include all required packages: {', '.join(template.required_packages)}
4. Format title, authors, abstract, and keywords according to template style
5. Structure all sections with proper LaTeX commands
6. **IMPORTANT: Place each image in its specified section using:**
   ```latex
   \\begin{{figure}}[htbp]
       \\centering
       \\includegraphics[width=WIDTH]{{figures/FILENAME}}
       \\caption{{CAPTION}}
       \\label{{LABEL}}
   \\end{{figure}}
   ```
7. For tables: Create well-formatted tables with booktabs style
8. For equations: Use proper math environments (equation, align, etc.)
9. Add bibliography style appropriate for the template
10. Include comments for clarity
11. Ensure all figure references in text match the labels
12. Ensure the document is ready to compile
13. **CRITICAL: For bibliography, use \\bibliographystyle{{IEEEtran}} and \\bibliography{{references}}**
14. **DO NOT add a manual \\section*{{References}} heading - the \\bibliography command will add it automatically**
15. **CRITICAL: When citing references, use ONLY the citation keys provided above**
16. **Use \\cite{{key}} commands with the EXACT keys shown in the Citation Keys list**
17. **Do NOT make up citation keys like "bert" or "quality_score" - use only the provided keys**

**Image Placeholders:** {"Use: " + ", ".join([f"figures/{img.get('filename', f'image_{i}.png')}" for i, img in enumerate(images)]) if images else "No images"}

**Table Placeholders:** {"Include " + str(len(tables)) + " tables with proper formatting" if tables else "No tables"}

**Equation Placeholders:** {"Include these equations: " + "; ".join(equations[:3]) if equations else "No equations"}

Generate ONLY the LaTeX code, starting with \\documentclass and ending with \\end{{document}}. 
Make it publication-ready and properly formatted according to {template.name} standards.

IMPORTANT: 
- Do NOT use markdown code fences (```latex)
- Output raw LaTeX code only
- Ensure all braces {{ }} are balanced
- Use proper LaTeX syntax throughout
- **Use ONLY the citation keys provided in the Citation Keys list above**
"""

        try:
            response = self.model.generate_content(prompt)
            latex_code = response.text.strip()
            
            # Clean up any markdown artifacts
            latex_code = re.sub(r'^```latex\s*', '', latex_code)
            latex_code = re.sub(r'^```\s*', '', latex_code)
            latex_code = re.sub(r'\s*```$', '', latex_code)
            
            # Verify it starts with \documentclass
            if not latex_code.strip().startswith('\\documentclass'):
                logger.warning("Generated LaTeX doesn't start with \\documentclass, attempting to fix...")
                # Try to extract LaTeX if it's embedded in other text
                match = re.search(r'(\\documentclass.*?\\end\{document\})', latex_code, re.DOTALL)
                if match:
                    latex_code = match.group(1)
            
            # Remove duplicate References section headings
            # This removes manual \section{References} or \section*{References} that appear right before \bibliographystyle
            latex_code = re.sub(
                r'\\section\*?\{References\}\s*(?=\\bibliographystyle)',
                '',
                latex_code,
                flags=re.IGNORECASE
            )
            
            # Also remove if there's a References heading right before \bibliography
            latex_code = re.sub(
                r'\\section\*?\{References\}\s*(?=\\bibliography)',
                '',
                latex_code,
                flags=re.IGNORECASE
            )
            
            return latex_code
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            # Return a basic template as fallback
            return self._generate_basic_template(template, title, authors, abstract, keywords, sections)
    
    def _generate_basic_template(
        self,
        template: LaTeXTemplate,
        title: str,
        authors: List[str],
        abstract: str,
        keywords: List[str],
        sections: Dict[str, str]
    ) -> str:
        """Generate a basic LaTeX template as fallback"""
        
        packages = '\n'.join([f'\\usepackage{{{pkg}}}' for pkg in template.required_packages])
        authors_formatted = ' \\and '.join(authors)
        keywords_formatted = ', '.join(keywords)
        sections_formatted = '\n\n'.join([
            f'\\section{{{name}}}\n{content}' for name, content in sections.items()
        ])
        
        return f"""\\documentclass{{{template.base_template}}}

% Packages
{packages}

% Document metadata
\\title{{{title}}}
\\author{{{authors_formatted}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\textbf{{Keywords:}} {keywords_formatted}

{sections_formatted}

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""
    
    def _process_images(self, images: List[Dict[str, Any]], figures_dir: Path) -> List[Dict[str, str]]:
        """Process and copy images to project directory"""
        processed = []
        
        for i, img in enumerate(images):
            try:
                source_path = img.get('path')
                if not source_path or not os.path.exists(source_path):
                    logger.warning(f"Image {i} path not found: {source_path}")
                    continue
                
                # Get file extension
                ext = Path(source_path).suffix
                filename = img.get('filename', f'image_{i}{ext}')
                
                # Copy to figures directory
                dest_path = figures_dir / filename
                shutil.copy2(source_path, dest_path)
                
                processed.append({
                    'filename': filename,
                    'caption': img.get('caption', f'Figure {i+1}'),
                    'label': img.get('label', f'fig:{i+1}'),
                    'width': img.get('width', '0.8\\textwidth')
                })
                
                logger.info(f"Processed image: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to process image {i}: {e}")
        
        return processed
    
    def _process_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Process table data into LaTeX format"""
        processed = []
        
        for i, table in enumerate(tables):
            try:
                caption = table.get('caption', f'Table {i+1}')
                label = table.get('label', f'tab:{i+1}')
                data = table.get('data', [])
                
                processed.append({
                    'caption': caption,
                    'label': label,
                    'rows': len(data),
                    'columns': len(data[0]) if data else 0
                })
                
            except Exception as e:
                logger.error(f"Failed to process table {i}: {e}")
        
        return processed
    
    def _create_bibliography(self, references: List[str], bib_path: Path):
        """Create BibTeX bibliography file from plain text references"""
        try:
            citation_keys = []  # Store generated keys for reference
            
            with open(bib_path, 'w', encoding='utf-8') as f:
                for i, ref in enumerate(references, 1):
                    ref_clean = ref.strip()
                    if not ref_clean:
                        continue
                    
                    # Try to parse citation information from plain text
                    parsed = self._parse_reference(ref_clean)
                    
                    # Generate a meaningful citation key based on author and year
                    citation_key = self._generate_citation_key(parsed['author'], parsed['year'], i)
                    citation_keys.append(citation_key)
                    
                    # Determine entry type based on content
                    entry_type = "article"
                    if any(word in ref_clean.lower() for word in ["conference", "proceedings", "workshop"]):
                        entry_type = "inproceedings"
                    elif any(word in ref_clean.lower() for word in ["book", "chapter"]):
                        entry_type = "book"
                    elif "arxiv" in ref_clean.lower() or "preprint" in ref_clean.lower():
                        entry_type = "misc"
                    
                    # Write BibTeX entry with meaningful key
                    f.write(f"@{entry_type}{{{citation_key},\n")
                    f.write(f"  author={{{parsed['author']}}},\n")
                    f.write(f"  title={{{parsed['title']}}},\n")
                    
                    if parsed['year']:
                        f.write(f"  year={{{parsed['year']}}},\n")
                    
                    if parsed['journal']:
                        if entry_type == "inproceedings":
                            f.write(f"  booktitle={{{parsed['journal']}}},\n")
                        else:
                            f.write(f"  journal={{{parsed['journal']}}},\n")
                    
                    if parsed['volume']:
                        f.write(f"  volume={{{parsed['volume']}}},\n")
                    
                    if parsed['pages']:
                        f.write(f"  pages={{{parsed['pages']}}},\n")
                    
                    if parsed['doi']:
                        f.write(f"  doi={{{parsed['doi']}}},\n")
                    
                    # Add note with original reference for context
                    f.write(f"  note={{Original: {ref_clean[:100]}}}\n")
                    f.write(f"}}\n\n")
            
            logger.info(f"Created bibliography file with {len(references)} entries at {bib_path}")
            logger.info(f"Generated citation keys: {', '.join(citation_keys)}")
            
            return citation_keys  # Return the keys so they can be used
            
        except Exception as e:
            logger.error(f"Failed to create bibliography: {e}")
            logger.exception("Full traceback:")
            return []
    
    def _generate_citation_key(self, author: str, year: str, index: int) -> str:
        """Generate a meaningful citation key from author name and year"""
        # Extract last name from author string
        # Handle formats like "Smith, J.", "J. Smith", "Smith et al."
        
        # Remove "et al." and similar
        author_clean = re.sub(r'\s+et\s+al\.?', '', author, flags=re.IGNORECASE)
        author_clean = re.sub(r'\s+and\s+.*', '', author_clean, flags=re.IGNORECASE)
        
        # Try to extract last name
        # Format: "Last, First" or "First Last"
        if ',' in author_clean:
            last_name = author_clean.split(',')[0].strip()
        else:
            # Take the first word (likely last name in "Last First" format)
            words = author_clean.split()
            last_name = words[0] if words else 'author'
        
        # Clean the last name - remove special characters, keep only alphanumeric
        last_name = re.sub(r'[^a-zA-Z]', '', last_name)
        last_name = last_name.lower()
        
        # Fallback if we couldn't extract a name
        if not last_name or len(last_name) < 2:
            last_name = f'ref{index}'
        
        # Add year if available
        if year:
            citation_key = f"{last_name}{year}"
        else:
            citation_key = f"{last_name}{index}"
        
        return citation_key
    
    def _parse_reference(self, ref: str) -> Dict[str, str]:
        """Parse a plain text reference to extract citation information"""
        result = {
            'author': '',
            'title': '',
            'journal': '',
            'year': '',
            'volume': '',
            'pages': '',
            'doi': ''
        }
        
        try:
            # Extract year (look for 4-digit number in parentheses or standalone)
            year_match = re.search(r'\((\d{4})\)|\b(\d{4})\b', ref)
            if year_match:
                result['year'] = year_match.group(1) or year_match.group(2)
            
            # Extract DOI
            doi_match = re.search(r'doi[:\s]+([^\s,]+)|10\.\d{4,}/[^\s,]+', ref, re.IGNORECASE)
            if doi_match:
                result['doi'] = doi_match.group(1) if doi_match.group(1) else doi_match.group(0)
            
            # Extract volume and pages (e.g., "vol. 5, pp. 123-456" or "5(2):123-456")
            vol_pages_match = re.search(r'(?:vol\.?\s*|volume\s+)?(\d+)(?:\((\d+)\))?[:\s,]+(?:pp?\.?\s*)?(\d+(?:-\d+)?)', ref, re.IGNORECASE)
            if vol_pages_match:
                result['volume'] = vol_pages_match.group(1)
                result['pages'] = vol_pages_match.group(3)
            
            # Split by period to get major parts
            parts = ref.split('.')
            
            if len(parts) >= 2:
                # First part is usually author
                author_part = parts[0].strip()
                # Remove year if it's at the end
                author_part = re.sub(r'\s*\(\d{4}\)\s*$', '', author_part)
                result['author'] = author_part if author_part else 'Anonymous'
                
                # Second part is usually title
                title_part = parts[1].strip()
                # Remove year if present
                title_part = re.sub(r'\s*\(\d{4}\)\s*', '', title_part)
                result['title'] = title_part if title_part else ref[:100]
                
                # Third part onwards might be journal/venue
                if len(parts) >= 3:
                    journal_part = parts[2].strip()
                    # Remove volume/pages info
                    journal_part = re.sub(r'\s*\d+(?:\(\d+\))?[:\s,]+(?:pp?\.?\s*)?\d+(?:-\d+)?.*', '', journal_part)
                    result['journal'] = journal_part
            else:
                # If we can't parse it well, use the whole thing as title
                result['author'] = 'Author et al.'
                result['title'] = ref[:200]
            
            # Fallback: ensure we at least have author and title
            if not result['author']:
                result['author'] = 'Author et al.'
            if not result['title']:
                result['title'] = ref[:200]
            
        except Exception as e:
            logger.warning(f"Failed to parse reference: {e}")
            # Return safe defaults
            result['author'] = 'Author et al.'
            result['title'] = ref[:200]
        
        return result
    
    def _create_readme(self, project_dir: Path, project_name: str, template: LaTeXTemplate):
        """Create README with compilation instructions"""
        readme_content = f"""# {project_name}

LaTeX document generated using {template.name} template.

## Compilation Instructions

### Using pdflatex:
```bash
pdflatex {project_name}.tex
bibtex {project_name}
pdflatex {project_name}.tex
pdflatex {project_name}.tex
```

### Using the provided script:
```bash
chmod +x compile.sh
./compile.sh
```

### Using latexmk (recommended):
```bash
latexmk -pdf {project_name}.tex
```

## Directory Structure

- `{project_name}.tex` - Main LaTeX file
- `references.bib` - Bibliography file
- `figures/` - Image files
- `tables/` - Table data (if any)

## Template Information

- **Template**: {template.name}
- **Type**: {template.template_type}
- **Document Class**: {template.base_template}

## Required Packages

{chr(10).join([f'- {pkg}' for pkg in template.required_packages])}

## Notes

- Ensure all required packages are installed in your LaTeX distribution
- Images should be in the `figures/` directory
- Modify the .tex file as needed for your specific requirements

Generated by LaTeX Writing Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_compile_script(self, project_dir: Path, project_name: str):
        """Create bash script for compilation"""
        script_content = f"""#!/bin/bash
# LaTeX compilation script

echo "Compiling {project_name}.tex..."

pdflatex {project_name}.tex
if [ -f references.bib ]; then
    bibtex {project_name}
    pdflatex {project_name}.tex
fi
pdflatex {project_name}.tex

# Clean up auxiliary files
rm -f *.aux *.log *.out *.bbl *.blg

echo "Compilation complete! Output: {project_name}.pdf"
"""
        
        script_path = project_dir / "compile.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
    
    def _create_zip_archive(self, project_dir: Path, project_name: str) -> Path:
        """Create ZIP archive of the project"""
        zip_path = self.output_dir / f"{project_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_dir.parent)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Created ZIP archive: {zip_path}")
        return zip_path
    
    def _parse_custom_template(self, template_content: str) -> LaTeXTemplate:
        """Parse custom template uploaded by user"""
        # Extract document class
        doc_class_match = re.search(r'\\documentclass(?:\[.*?\])?\{(.*?)\}', template_content)
        doc_class = doc_class_match.group(1) if doc_class_match else 'article'
        
        # Extract packages
        packages = re.findall(r'\\usepackage(?:\[.*?\])?\{(.*?)\}', template_content)
        
        return LaTeXTemplate(
            name='Custom Template',
            template_type='custom',
            description='User-provided custom template',
            base_template=doc_class,
            required_packages=packages
        )
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove or replace invalid characters
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename[:50]  # Limit length
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available built-in templates"""
        return [
            {
                'id': key,
                'name': template.name,
                'type': template.template_type,
                'description': template.description,
                'document_class': template.base_template
            }
            for key, template in self.TEMPLATES.items()
        ]
    
    def preview_template(self, template_name: str) -> str:
        """Generate a preview/example of a template"""
        if template_name not in self.TEMPLATES:
            return f"Template '{template_name}' not found"
        
        template = self.TEMPLATES[template_name]
        
        # Build package list
        packages_list = '\n'.join([f'- \\usepackage{{{pkg}}}' for pkg in template.required_packages])
        
        # Build document class string
        doc_class = f'\\documentclass{{{template.base_template}}}'
        
        # Build example packages
        example_packages = '\n'.join([f'\\usepackage{{{pkg}}}' for pkg in template.required_packages])
        
        preview = f"""# {template.name} Template Preview

**Type:** {template.template_type}
**Description:** {template.description}
**Document Class:** {doc_class}

## Required Packages
{packages_list}

## Example Structure

```latex
{doc_class}

% Packages
{example_packages}

\\title{{Your Paper Title}}
\\author{{Your Name}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
Your abstract here...
\\end{{abstract}}

\\section{{Introduction}}
Your introduction...

\\section{{Related Work}}
Related work section...

\\section{{Methodology}}
Your methodology...

\\section{{Results}}
Results and discussion...

\\section{{Conclusion}}
Concluding remarks...

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
```

## Typical Use Cases
"""
        
        if template.template_type == 'journal':
            preview += "\n- Journal article submissions\n- Extended research papers\n- Comprehensive literature reviews"
        elif template.template_type == 'conference':
            preview += "\n- Conference paper submissions\n- Workshop papers\n- Short technical reports"
        else:
            preview += "\n- Preprints and arXiv submissions\n- Technical reports\n- General academic writing"
        
        return preview


if __name__ == "__main__":
    # Example usage
    assistant = LaTeXWritingAssistant()
    
    # Get available templates
    templates = assistant.get_available_templates()
    print(f"Available templates: {len(templates)}")
    for template in templates:
        print(f"  - {template['name']} ({template['type']})")
    
    # Example document
    result = assistant.format_document(
        content="Research paper content...",
        template_name='ieee_journal',
        title="Deep Learning for Computer Vision",
        authors=["John Doe", "Jane Smith"],
        abstract="This paper presents a novel approach to computer vision using deep learning...",
        keywords=["deep learning", "computer vision", "neural networks"],
        sections={
            "Introduction": "Introduction content...",
            "Related Work": "Related work content...",
            "Methodology": "Our approach...",
            "Results": "Experimental results...",
            "Conclusion": "Concluding remarks..."
        },
        references=[
            "LeCun et al. Deep Learning, Nature 2015",
            "Krizhevsky et al. ImageNet Classification, NIPS 2012"
        ]
    )
    
    if result['success']:
        print(f"\n✅ Document formatted successfully!")
        print(f"Output: {result['main_file']}")
        print(f"ZIP: {result['zip_file']}")
    else:
        print(f"❌ Error: {result['message']}")
