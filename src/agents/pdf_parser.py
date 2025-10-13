"""
PDF Parser - Extract metadata and content from uploaded PDF research papers

This module implements intelligent PDF parsing to extract paper metadata,
including title, authors, abstract, and full text for FAISS embedding.
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFPaperParser:
    """Parser for extracting research paper information from PDFs"""
    
    def __init__(self):
        """Initialize the PDF parser"""
        self.current_year = datetime.now().year
    
    def parse_pdf_file(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a PDF file and extract paper metadata
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with paper information or None if parsing fails
        """
        try:
            logger.info(f"Parsing PDF: {pdf_path}")
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Extract text from first few pages (metadata usually on first 2 pages)
            first_pages_text = ""
            for page_num in range(min(3, len(doc))):
                first_pages_text += doc[page_num].get_text()
            
            # Extract full text
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            doc.close()
            
            # Extract metadata
            title = self._extract_title(first_pages_text, os.path.basename(pdf_path))
            authors = self._extract_authors(first_pages_text)
            abstract = self._extract_abstract(first_pages_text)
            year = self._extract_year(first_pages_text)
            keywords = self._extract_keywords(first_pages_text)
            
            # Create paper object
            paper_data = {
                'paper_id': f"uploaded_{hash(pdf_path) % 100000000}",
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'publication_date': str(year) if year else str(self.current_year),
                'journal': 'User Uploaded Paper',
                'citation_count': 0,
                'relevance_score': 0.85,  # Default high relevance for uploaded papers
                'confidence_score': 0.9,
                'url': f"file://{pdf_path}",
                'doi': None,
                'keywords': keywords,
                'categories': ['User Upload'],
                'source': 'user_upload',
                'paper_type': self._infer_paper_type(title, first_pages_text),
                'gemini_reasoning': 'User uploaded paper - high relevance assumed',
                'key_matches': ['user uploaded'],
                'concerns': [],
                'full_text': full_text[:10000]  # First 10k chars for embedding
            }
            
            logger.info(f"Successfully parsed: {title}")
            return paper_data
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}")
            return None
    
    def _extract_title(self, text: str, filename: str) -> str:
        """Extract paper title from PDF text"""
        try:
            # Common title patterns in research papers
            lines = text.split('\n')[:20]  # Check first 20 lines
            
            # Filter out very short lines and common headers
            skip_keywords = ['abstract', 'introduction', 'ieee', 'acm', 'springer', 
                           'elsevier', 'arxiv', 'preprint', 'copyright', 'published']
            
            candidates = []
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines, very short lines, and lines with common headers
                if len(line) < 10 or len(line) > 200:
                    continue
                
                if any(keyword in line.lower() for keyword in skip_keywords):
                    continue
                
                # Title is often in the first few substantive lines
                # and has reasonable length
                if 20 <= len(line) <= 150 and not line.isupper():
                    candidates.append((i, line))
            
            # Return the earliest substantial line as title
            if candidates:
                return candidates[0][1]
            
            # Fallback to filename without extension
            return os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
            
        except Exception as e:
            logger.warning(f"Title extraction failed: {e}")
            return os.path.splitext(filename)[0]
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract author names from PDF text"""
        try:
            # Look for common author patterns
            lines = text.split('\n')[:30]
            
            authors = []
            
            # Pattern 1: Name followed by affiliation/email
            name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:,? [A-Z][a-z]+)*)\b'
            
            for line in lines:
                # Skip lines that are clearly not author lines
                if any(skip in line.lower() for skip in ['abstract', 'introduction', 'university', 'department', '@']):
                    continue
                
                # Look for capitalized names
                matches = re.findall(name_pattern, line)
                for match in matches:
                    if 2 <= len(match.split()) <= 4:  # Reasonable name length
                        authors.append(match)
            
            # Deduplicate while preserving order
            seen = set()
            unique_authors = []
            for author in authors:
                if author not in seen:
                    seen.add(author)
                    unique_authors.append(author)
            
            # Limit to first 5 authors
            return unique_authors[:5] if unique_authors else ['Unknown Author']
            
        except Exception as e:
            logger.warning(f"Author extraction failed: {e}")
            return ['Unknown Author']
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract from PDF text"""
        try:
            text_lower = text.lower()
            
            # Find abstract section
            abstract_start = text_lower.find('abstract')
            if abstract_start == -1:
                # Try alternative markers
                for marker in ['summary', 'overview']:
                    abstract_start = text_lower.find(marker)
                    if abstract_start != -1:
                        break
            
            if abstract_start == -1:
                # No abstract found, use first paragraph
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if len(para.strip()) > 100:
                        return para.strip()[:500]
                return "No abstract available"
            
            # Extract text after "abstract" marker
            abstract_text = text[abstract_start:]
            
            # Find end of abstract (common markers)
            end_markers = ['\nintroduction', '\n1.', '\nkeywords:', '\nindex terms']
            end_pos = len(abstract_text)
            
            for marker in end_markers:
                pos = abstract_text.lower().find(marker)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
            
            abstract = abstract_text[:end_pos].replace('abstract', '', 1).strip()
            
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)
            abstract = abstract[:1000]  # Limit length
            
            return abstract if len(abstract) > 50 else "No abstract available"
            
        except Exception as e:
            logger.warning(f"Abstract extraction failed: {e}")
            return "No abstract available"
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract publication year from PDF text"""
        try:
            # Look for year patterns (1900-2030)
            year_pattern = r'\b(19\d{2}|20[0-3]\d)\b'
            matches = re.findall(year_pattern, text[:2000])  # Check first 2000 chars
            
            if matches:
                # Return the most recent reasonable year
                years = [int(y) for y in matches if 1990 <= int(y) <= self.current_year + 1]
                if years:
                    return max(years)
            
            return None
            
        except Exception as e:
            logger.warning(f"Year extraction failed: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from PDF text"""
        try:
            text_lower = text.lower()
            
            # Find keywords section
            keywords_start = -1
            for marker in ['keywords:', 'keywords', 'index terms', 'key words']:
                pos = text_lower.find(marker)
                if pos != -1:
                    keywords_start = pos
                    break
            
            if keywords_start == -1:
                return []
            
            # Extract keywords
            keywords_text = text[keywords_start:keywords_start+500]
            
            # Stop at common section markers
            for marker in ['\n1.', '\nintroduction', '\nabstract']:
                pos = keywords_text.lower().find(marker)
                if pos != -1:
                    keywords_text = keywords_text[:pos]
            
            # Clean and split
            keywords_text = keywords_text.replace('keywords:', '').replace('Keywords', '')
            keywords = re.split(r'[;,\n]', keywords_text)
            
            # Clean individual keywords
            cleaned = []
            for kw in keywords:
                kw = kw.strip()
                if 3 <= len(kw) <= 50 and not kw.isdigit():
                    cleaned.append(kw)
            
            return cleaned[:10]  # Limit to 10 keywords
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    def _infer_paper_type(self, title: str, text: str) -> str:
        """Infer paper type from title and content"""
        title_lower = title.lower()
        text_lower = text[:1000].lower()
        
        # Check for review paper indicators
        review_indicators = ['review', 'survey', 'overview', 'state of the art', 'state-of-the-art']
        if any(indicator in title_lower for indicator in review_indicators):
            return 'review'
        
        # Check for conference indicators
        conference_indicators = ['conference', 'proceedings', 'workshop', 'symposium']
        if any(indicator in text_lower for indicator in conference_indicators):
            return 'conference'
        
        # Default to journal
        return 'journal'
    
    def parse_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple PDF files
        
        Args:
            pdf_paths: List of paths to PDF files
            
        Returns:
            List of paper data dictionaries
        """
        papers = []
        
        for pdf_path in pdf_paths:
            paper_data = self.parse_pdf_file(pdf_path)
            if paper_data:
                papers.append(paper_data)
        
        logger.info(f"Successfully parsed {len(papers)} out of {len(pdf_paths)} PDFs")
        return papers
