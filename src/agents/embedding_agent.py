"""
Embedding Agent - Vector Database Management for Research Papers

This module implements a sophisticated embedding system using Google's embedding models
and FAISS for vector similarity search, specifically designed for academic paper analysis.
"""

import os
import logging
import json
import pickle
import numpy as np
import requests
import fitz  # PyMuPDF
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
try:
    import faiss
except ImportError:
    print("FAISS not installed. Please install with: pip install faiss-cpu")
    faiss = None

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import uuid

# Configure email for API politeness
RESEARCH_EMAIL = os.getenv("RESEARCH_EMAIL", "research@example.com")

def _scrape_for_pdf_url(doi: str) -> Optional[str]:
    """Scrape publisher's page for PDF link"""
    try:
        doi_url = f"https://doi.org/{doi}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        logger.info(f"Scraping landing page: {doi_url}")
        response = requests.get(doi_url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        publisher_url = response.url
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try meta tag first
        meta_tag = soup.find('meta', attrs={'name': re.compile(r'citation_pdf_url', re.I)})
        if meta_tag and meta_tag.has_attr('content'):
            return meta_tag['content']

        # Try direct PDF links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href'].lower()
            # Direct PDF files
            if href.endswith('.pdf') or '.pdf?' in href:
                return urljoin(publisher_url, link['href'])
            # PDF in path
            if any(substring in href for substring in ['/pdf/', '/content/', 'fulltext', '/epdf/']):
                return urljoin(publisher_url, link['href'])
            # Check link text and attributes
            if re.search(r'download|pdf|full.?text', link.get_text(), re.I):
                return urljoin(publisher_url, link['href'])
                
        return None

    except Exception as e:
        logger.error(f"Error scraping for PDF: {str(e)}")
        return None

def get_pdf_url(doi: str) -> Optional[str]:
    """Get PDF URL using multiple methods"""
    # Handle arXiv
    if "arxiv" in doi.lower():
        arxiv_id = doi.split('arXiv.')[-1]
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # Try Unpaywall
    try:
        response = requests.get(
            f"https://api.unpaywall.org/v2/{doi}",
            params={'email': RESEARCH_EMAIL},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('best_oa_location') and data['best_oa_location'].get('url_for_pdf'):
                return data['best_oa_location']['url_for_pdf']
    except Exception as e:
        logger.warning(f"Unpaywall API request failed: {str(e)}")

    # Fallback to scraping
    return _scrape_for_pdf_url(doi)

def extract_text_from_pdf_url(pdf_url: str) -> Optional[str]:
    """Download and extract text from PDF"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
            
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return None

def extract_sections(full_text: str) -> Dict[str, str]:
    """Extract key sections from paper text"""
    logger.info("Extracting paper sections...")
    lower_text = full_text.lower()
    
    patterns = {
        'abstract': r'\babstract\b',
        'introduction': r'\n1\.?\s+introduction\b',
        'conclusion': r'\b(conclusions?|conclusion and future work|discussion)\b'
    }
    
    end_markers = {
        'introduction': r'\n2\.?\s+',
        'conclusion': r'\b(acknowledgments?|references|bibliography)\b'
    }
    
    results = {}
    
    # Extract abstract
    try:
        abstract_match = re.search(patterns['abstract'], lower_text)
        intro_match = re.search(patterns['introduction'], lower_text)
        if abstract_match and intro_match:
            results['abstract'] = full_text[abstract_match.end():intro_match.start()].strip()
        elif abstract_match:
            results['abstract'] = full_text[abstract_match.end():abstract_match.end()+2000].strip().split('\n\n')[0]
    except:
        results['abstract'] = None

    # Extract introduction
    try:
        intro_match = re.search(patterns['introduction'], lower_text)
        intro_end_match = re.search(end_markers['introduction'], lower_text[intro_match.end():])
        if intro_match and intro_end_match:
            end = intro_match.end() + intro_end_match.start()
            results['introduction'] = full_text[intro_match.end():end].strip()
        elif intro_match:
            results['introduction'] = full_text[intro_match.end():intro_match.end()+5000].strip()
    except:
        results['introduction'] = None

    # Extract conclusion
    try:
        conclusion_match = re.search(patterns['conclusion'], lower_text)
        conclusion_end_match = re.search(end_markers['conclusion'], lower_text[conclusion_match.end():])
        if conclusion_match and conclusion_end_match:
            end = conclusion_match.end() + conclusion_end_match.start()
            results['conclusion'] = full_text[conclusion_match.end():end].strip()
        elif conclusion_match:
            results['conclusion'] = full_text[conclusion_match.end():conclusion_match.end()+5000].strip()
    except:
        results['conclusion'] = None

    return results

# Google Embeddings
import google.generativeai as genai

# Data validation
from pydantic import BaseModel, Field, validator

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddedPaper:
    """Comprehensive paper representation with embedding data"""
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    publication_date: str
    citation_count: int
    relevance_score: float
    confidence_score: float
    url: str
    doi: Optional[str]
    keywords: List[str]
    categories: List[str]
    source: str
    gemini_reasoning: Optional[str]
    key_matches: List[str]
    concerns: List[str]
    search_query: str
    session_id: str
    timestamp: str
    embedding: Optional[np.ndarray] = None
    similarity_score: Optional[float] = None
    paper_type: Optional[str] = None
    # Full text sections
    introduction: Optional[str] = None
    conclusion: Optional[str] = None
    full_text: Optional[str] = None
    pdf_url: Optional[str] = None
    
    def extract_full_text(self) -> bool:
        """Extract full text content from paper PDF if available"""
        if not self.doi:
            logger.warning(f"No DOI available for paper: {self.title}")
            return False
            
        try:
            pdf_url = get_pdf_url(self.doi)
            if not pdf_url:
                logger.warning(f"Could not find PDF URL for DOI: {self.doi}")
                return False
                
            self.pdf_url = pdf_url
            full_text = extract_text_from_pdf_url(pdf_url)
            
            if full_text:
                sections = extract_sections(full_text)
                self.full_text = full_text
                self.introduction = sections.get('introduction')
                self.conclusion = sections.get('conclusion')
                # Update abstract if it was empty
                if not self.abstract:
                    self.abstract = sections.get('abstract')
                return True
                
        except Exception as e:
            logger.error(f"Error extracting full text for {self.doi}: {str(e)}")
            return False

class PaperTypeClassifier:
    """Classify papers into Review, Conference, or Journal types"""
    
    def __init__(self):
        # Keywords and patterns for classification
        self.review_keywords = [
            'review', 'survey', 'meta-analysis', 'systematic review', 
            'literature review', 'overview', 'synthesis', 'state-of-the-art',
            'comprehensive review', 'critical review', 'scoping review'
        ]
        
        self.conference_patterns = [
            'proceedings', 'conference', 'workshop', 'symposium', 'congress',
            'international conference', 'acm', 'ieee conference', 'workshop on',
            'advances in', 'annual conference', 'icml', 'nips', 'neurips',
            'aaai', 'ijcai', 'cvpr', 'iccv', 'eccv', 'sigkdd', 'www conference'
        ]
        
        self.journal_patterns = [
            'journal of', 'journal', 'nature', 'science', 'cell', 'plos',
            'proceedings of the national academy', 'ieee transactions',
            'acm transactions', 'quarterly', 'annual review', 'elsevier',
            'springer', 'wiley', 'oxford', 'cambridge', 'taylor & francis'
        ]
    
    def classify_paper(self, title: str, journal: str, abstract: str = "") -> str:
        """
        Classify paper into Review, Conference, or Journal type
        
        Args:
            title: Paper title
            journal: Journal/venue name
            abstract: Paper abstract (optional)
            
        Returns:
            str: 'review', 'conference', or 'journal'
        """
        text_to_analyze = f"{title} {journal} {abstract}".lower()
        
        # Check for review papers first (highest priority)
        review_score = sum(1 for keyword in self.review_keywords if keyword in text_to_analyze)
        if review_score >= 1:
            return 'review'
        
        # Check for conference papers
        conference_score = sum(1 for pattern in self.conference_patterns if pattern in text_to_analyze)
        
        # Check for journal papers
        journal_score = sum(1 for pattern in self.journal_patterns if pattern in text_to_analyze)
        
        # Decision logic
        if conference_score > journal_score:
            return 'conference'
        elif journal_score > 0:
            return 'journal'
        else:
            # Default classification based on venue characteristics
            if any(term in journal.lower() for term in ['conference', 'proceedings', 'workshop']):
                return 'conference'
            else:
                return 'journal'

class FAISSVectorDatabase:
    """FAISS-based vector database for paper embeddings with comprehensive metadata"""
    
    def __init__(self, db_path: str = "data/faiss_paper_embeddings"):
        self.db_path = db_path
        self.dimension = 768  # Google's embedding dimension
        self.index = None
        self.papers_metadata = {}
        self.paper_ids = []
        self.classifier = PaperTypeClassifier()
        
        # Initialize Google Generative AI - check both GEMINI_API_KEY and GOOGLE_API_KEY
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
        else:
            logger.warning("No Gemini API key found - embeddings may not work correctly")
        
        # Check if FAISS is available
        if faiss is None:
            logger.error("FAISS not available. Please install with: pip install faiss-cpu")
            return
        
        # Load existing database if available
        self.load_database()
        
    def load_database(self):
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(f"{self.db_path}.index"):
                self.index = faiss.read_index(f"{self.db_path}.index")
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # No existing index, initialize empty one
                self._initialize_empty_database()
                
            if os.path.exists(f"{self.db_path}_metadata.pkl"):
                with open(f"{self.db_path}_metadata.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.papers_metadata = data.get('metadata', {})
                    self.paper_ids = data.get('paper_ids', [])
                logger.info(f"Loaded metadata for {len(self.papers_metadata)} papers")
                
        except Exception as e:
            logger.warning(f"Could not load existing database: {e}")
            self._initialize_empty_database()
    
    def _initialize_empty_database(self):
        """Initialize empty FAISS index"""
        if faiss is None:
            logger.error("Cannot initialize database: FAISS not available")
            return
            
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.papers_metadata = {}
        self.paper_ids = []
        logger.info("Initialized empty FAISS database")
    
    def save_database(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, f"{self.db_path}.index")
            
            with open(f"{self.db_path}_metadata.pkl", 'wb') as f:
                pickle.dump({
                    'metadata': self.papers_metadata,
                    'paper_ids': self.paper_ids
                }, f)
            
            logger.info(f"Saved database with {len(self.papers_metadata)} papers")
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using Google's embedding model"""
        try:
            # Use Google's embedding model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = np.array(result['embedding'], dtype=np.float32)
            
            # Normalize for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.dimension, dtype=np.float32)
    
    def add_papers_batch(self, papers: List[Dict[str, Any]], search_query: str, session_id: str) -> List[EmbeddedPaper]:
        """
        Add a batch of papers to the vector database
        
        Args:
            papers: List of paper dictionaries
            search_query: Original search query
            session_id: Search session identifier
            
        Returns:
            List of EmbeddedPaper objects with embeddings
        """
        if faiss is None:
            logger.error("Cannot add papers: FAISS not available")
            return []
            
        embedded_papers = []
        embeddings_to_add = []
        
        for paper in papers:
            try:
                # Create comprehensive text for embedding
                embedding_text = f"""
                Title: {paper.get('title', '')}
                Abstract: {paper.get('abstract', '')}
                Keywords: {', '.join(paper.get('keywords', []))}
                Categories: {', '.join(paper.get('categories', []))}
                Journal: {paper.get('journal', '')}
                """
                
                # Generate embedding
                embedding = self.generate_embedding(embedding_text.strip())
                
                # Classify paper type
                paper_type = self.classifier.classify_paper(
                    paper.get('title', ''),
                    paper.get('journal', ''),
                    paper.get('abstract', '')
                )
                
                # Create EmbeddedPaper object with safe value handling
                def safe_float(value, default=0.0):
                    if value is None:
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(value, default=0):
                    if value is None:
                        return default
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return default
                
                embedded_paper = EmbeddedPaper(
                    paper_id=paper.get('paper_id', str(uuid.uuid4())[:8]),
                    title=paper.get('title', ''),
                    authors=paper.get('authors', []),
                    abstract=paper.get('abstract', ''),
                    journal=paper.get('journal', ''),
                    publication_date=paper.get('publication_date', ''),
                    citation_count=safe_int(paper.get('citation_count')),
                    relevance_score=safe_float(paper.get('relevance_score')),
                    confidence_score=safe_float(paper.get('confidence_score')),
                    url=paper.get('url', ''),
                    doi=paper.get('doi'),
                    keywords=paper.get('keywords', []),
                    categories=paper.get('categories', []),
                    source=paper.get('source', 'unknown'),
                    gemini_reasoning=paper.get('gemini_reasoning'),
                    key_matches=paper.get('key_matches', []),
                    concerns=paper.get('concerns', []),
                    search_query=search_query,
                    session_id=session_id,
                    timestamp=datetime.now().isoformat(),
                    embedding=embedding,
                    paper_type=paper_type
                )
                
                # Store metadata with paper type
                metadata = asdict(embedded_paper)
                metadata.pop('embedding')  # Don't store embedding in metadata
                
                self.papers_metadata[embedded_paper.paper_id] = metadata
                self.paper_ids.append(embedded_paper.paper_id)
                
                embeddings_to_add.append(embedding)
                embedded_papers.append(embedded_paper)
                
                logger.info(f"Processed paper: {embedded_paper.title[:50]}... (Type: {paper_type})")
                
            except Exception as e:
                logger.error(f"Failed to process paper {paper.get('title', 'Unknown')}: {e}")
                continue
        
        # Add embeddings to FAISS index
        if embeddings_to_add and self.index is not None:
            embeddings_array = np.array(embeddings_to_add)
            self.index.add(embeddings_array)
            
            # Save database
            self.save_database()
            
            logger.info(f"Added {len(embeddings_to_add)} papers to vector database")
        
        return embedded_papers
    
    def search_similar_papers(self, query: str, k: int = 20, paper_type_filter: Optional[str] = None) -> List[EmbeddedPaper]:
        """
        Search for similar papers using vector similarity
        
        Args:
            query: Search query text
            k: Number of results to return
            paper_type_filter: Filter by paper type ('review', 'conference', 'journal')
            
        Returns:
            List of EmbeddedPaper objects ranked by similarity
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No papers in database")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search in FAISS index
            # Get more results for filtering if needed
            search_k = k * 3 if paper_type_filter else k
            scores, indices = self.index.search(query_embedding, min(search_k, self.index.ntotal))
            
            similar_papers = []
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= len(self.paper_ids):
                    continue
                    
                paper_id = self.paper_ids[idx]
                if paper_id not in self.papers_metadata:
                    continue
                
                metadata = self.papers_metadata[paper_id]
                
                # Apply paper type filter
                if paper_type_filter and metadata.get('paper_type') != paper_type_filter:
                    continue
                
                try:
                    # Ensure all required fields have default values
                    metadata_with_defaults = {
                        'paper_id': metadata.get('paper_id', paper_id),
                        'title': metadata.get('title', 'Unknown Title'),
                        'authors': metadata.get('authors', []),
                        'abstract': metadata.get('abstract', ''),
                        'journal': metadata.get('journal', 'Unknown'),
                        'publication_date': metadata.get('publication_date', 'Unknown'),
                        'citation_count': metadata.get('citation_count', 0),
                        'relevance_score': metadata.get('relevance_score', 0.0),
                        'confidence_score': metadata.get('confidence_score', 0.0),
                        'url': metadata.get('url', ''),
                        'doi': metadata.get('doi'),
                        'keywords': metadata.get('keywords', []),
                        'categories': metadata.get('categories', []),
                        'source': metadata.get('source', 'unknown'),
                        'gemini_reasoning': metadata.get('gemini_reasoning'),
                        'key_matches': metadata.get('key_matches', []),
                        'concerns': metadata.get('concerns', []),
                        'search_query': metadata.get('search_query', ''),
                        'session_id': metadata.get('session_id', ''),
                        'timestamp': metadata.get('timestamp', ''),
                        'embedding': None,
                        'similarity_score': float(score),
                        'paper_type': metadata.get('paper_type', 'unknown'),
                        'introduction': metadata.get('introduction'),
                        'conclusion': metadata.get('conclusion'),
                        'full_text': metadata.get('full_text'),
                        'pdf_url': metadata.get('pdf_url')
                    }
                    
                    # Create EmbeddedPaper object
                    embedded_paper = EmbeddedPaper(**metadata_with_defaults)
                    
                    similar_papers.append(embedded_paper)
                    
                    if len(similar_papers) >= k:
                        break
                        
                except Exception as e:
                    logger.error(f"Error creating EmbeddedPaper from metadata: {e}")
                    logger.error(f"Metadata keys: {list(metadata.keys())}")
                    continue
            
            logger.info(f"Found {len(similar_papers)} similar papers (filter: {paper_type_filter})")
            return similar_papers
            
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        if not self.papers_metadata:
            return {"total_papers": 0}
        
        # Count by paper type
        type_counts = {}
        for metadata in self.papers_metadata.values():
            paper_type = metadata.get('paper_type', 'unknown')
            type_counts[paper_type] = type_counts.get(paper_type, 0) + 1
        
        # Calculate average scores safely
        relevance_scores = []
        confidence_scores = []
        
        for metadata in self.papers_metadata.values():
            rel_score = metadata.get('relevance_score')
            conf_score = metadata.get('confidence_score')
            
            # Only include valid numeric scores
            if rel_score is not None and isinstance(rel_score, (int, float)):
                relevance_scores.append(float(rel_score))
            
            if conf_score is not None and isinstance(conf_score, (int, float)):
                confidence_scores.append(float(conf_score))
        
        return {
            "total_papers": len(self.papers_metadata),
            "papers_by_type": type_counts,
            "avg_relevance_score": np.mean(relevance_scores) if relevance_scores else 0.0,
            "avg_confidence_score": np.mean(confidence_scores) if confidence_scores else 0.0,
            "total_sessions": len(set(m.get('session_id') for m in self.papers_metadata.values() if m.get('session_id'))),
            "vector_index_size": self.index.ntotal if self.index else 0
        }
    
    def check_duplicate_dois(self, dois: List[str]) -> List[str]:
        """
        Check for duplicate DOIs in the database
        
        Args:
            dois: List of DOIs to check
            
        Returns:
            List of DOIs that already exist in database
        """
        existing_dois = []
        for metadata in self.papers_metadata.values():
            if metadata.get('doi'):
                existing_dois.append(metadata['doi'])
        
        duplicates = [doi for doi in dois if doi and doi in existing_dois]
        return duplicates

class EmbeddingAgent:
    """Main embedding agent for processing paper batches"""
    
    def __init__(self, db_path: str = "data/faiss_paper_embeddings"):
        self.vector_db = FAISSVectorDatabase(db_path)
        logger.info("Embedding Agent initialized")
    
    def process_paper_batch(self, papers: List[Dict[str, Any]], search_query: str, session_id: str) -> List[EmbeddedPaper]:
        """
        Process a batch of 24 papers and convert to embeddings
        
        Args:
            papers: List of paper dictionaries from literature_agent
            search_query: Original search query
            session_id: Search session identifier
            
        Returns:
            List of EmbeddedPaper objects with embeddings
        """
        logger.info(f"Processing batch of {len(papers)} papers for session {session_id}")
        
        # Filter out papers with duplicate DOIs
        unique_papers = []
        dois_to_check = [p.get('doi') for p in papers if p.get('doi')]
        existing_dois = self.vector_db.check_duplicate_dois(dois_to_check)
        
        for paper in papers:
            if paper.get('doi') and paper['doi'] in existing_dois:
                logger.info(f"Skipping duplicate DOI: {paper['doi']}")
                continue
            unique_papers.append(paper)
        
        logger.info(f"Processing {len(unique_papers)} unique papers (filtered {len(papers) - len(unique_papers)} duplicates)")
        
        # Add papers to vector database
        embedded_papers = self.vector_db.add_papers_batch(unique_papers, search_query, session_id)
        
        return embedded_papers
    
    def search_papers(self, query: str, k: int = 20, paper_type_filter: Optional[str] = None) -> List[EmbeddedPaper]:
        """
        Search for papers using vector similarity
        
        Args:
            query: Search query
            k: Number of results to return
            paper_type_filter: Filter by paper type
            
        Returns:
            List of similar papers ranked by relevance
        """
        return self.vector_db.search_similar_papers(query, k, paper_type_filter)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self.vector_db.get_database_stats()
    
    def get_stored_dois(self) -> List[str]:
        """Get all DOIs currently stored in the database"""
        dois = []
        for metadata in self.vector_db.papers_metadata.values():
            if metadata.get('doi'):
                dois.append(metadata['doi'])
        return dois
