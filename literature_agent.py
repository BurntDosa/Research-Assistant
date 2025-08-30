
"""
Literature Discovery Agent - Gemini 2.5 Flash Native Implementation

This module implements a complete academic paper discovery system built specifically
for Google's Gemini 2.5 Flash model, with advanced search, validation, and storage capabilities.
"""

import os
import asyncio
import logging
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Gemini and LangChain imports
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Web scraping and academic APIs
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Data validation and processing
from pydantic import BaseModel, Field, validator
import numpy as np
from collections import Counter

# Async support
import aiohttp
import asyncio
from asyncio_throttle import Throttler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    """Enhanced data class for academic papers with Gemini-optimized structure"""
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    journal: str
    citation_count: int
    impact_factor: Optional[float] = None
    url: str = ""
    doi: Optional[str] = None
    keywords: List[str] = None
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    selected: bool = False
    paper_id: Optional[str] = None
    source: str = "unknown"
    categories: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.categories is None:
            self.categories = []
        if self.paper_id is None:
            self.paper_id = str(uuid.uuid4())[:8]

@dataclass
class ValidationResult:
    """Fallback validation result for failed Gemini calls"""
    relevance_score: float = 0.5
    confidence_score: float = 0.3
    reasoning: str = "Validation failed - fallback scoring"
    key_matches: List[str] = None
    concerns: List[str] = None
    
    def __post_init__(self):
        if self.key_matches is None:
            self.key_matches = []
        if self.concerns is None:
            self.concerns = []
    def __post_init__(self):
        if self.key_matches is None:
            self.key_matches = []
        if self.concerns is None:
            self.concerns = []
            self.paper_id = str(uuid.uuid4())[:8]

class RelevanceScore(BaseModel):
    """Pydantic model for structured relevance scoring from Gemini"""
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score between 0.0 and 1.0")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the assessment")
    reasoning: str = Field(description="Brief explanation of the scoring")
    key_matches: List[str] = Field(description="Key matching elements found")
    concerns: List[str] = Field(default=[], description="Any concerns about relevance")

class SearchFilters(BaseModel):
    """Comprehensive search filters with validation"""
    year_start: Optional[int] = Field(default=None, ge=1900, le=2030)
    year_end: Optional[int] = Field(default=None, ge=1900, le=2030)
    min_citations: int = Field(default=0, ge=0)
    max_citations: Optional[int] = Field(default=None, ge=0)
    include_preprints: bool = Field(default=True)
    journal_filter: Optional[List[str]] = Field(default=None)
    author_filter: Optional[List[str]] = Field(default=None)
    keyword_requirements: Optional[List[str]] = Field(default=None)
    exclude_keywords: Optional[List[str]] = Field(default=None)
    paper_type_filter: Optional[str] = Field(default=None, description="Filter by paper type: 'review', 'conference', or 'journal'")

    @validator('year_end')
    def validate_year_range(cls, v, values):
        if v is not None and 'year_start' in values and values['year_start'] is not None:
            if v < values['year_start']:
                raise ValueError('year_end must be >= year_start')
        return v
    
    @validator('paper_type_filter')
    def validate_paper_type(cls, v):
        if v is not None and v not in ['review', 'conference', 'journal']:
            raise ValueError('paper_type_filter must be one of: review, conference, journal')
        return v

class GeminiLiteratureDatabase:
    """Advanced database manager optimized for Gemini-powered literature discovery"""

    def __init__(self, db_path: str = "gemini_literature_discovery.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize comprehensive database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced papers table with Gemini-specific fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            publication_date TEXT,
            journal TEXT,
            citation_count INTEGER DEFAULT 0,
            impact_factor REAL,
            url TEXT,
            doi TEXT,
            keywords TEXT,
            categories TEXT,
            relevance_score REAL DEFAULT 0.0,
            confidence_score REAL DEFAULT 0.0,
            selected BOOLEAN DEFAULT FALSE,
            search_session TEXT,
            source TEXT DEFAULT 'unknown',
            gemini_reasoning TEXT,
            key_matches TEXT,
            concerns TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Search sessions with detailed tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            query TEXT NOT NULL,
            filters TEXT,
            total_papers_found INTEGER DEFAULT 0,
            papers_selected INTEGER DEFAULT 0,
            avg_relevance_score REAL DEFAULT 0.0,
            search_duration_seconds REAL DEFAULT 0.0,
            gemini_model_used TEXT DEFAULT 'gemini-2.5-flash',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Paper collections for organization
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#2196F3',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Many-to-many relationship for paper collections
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_collections (
            paper_id TEXT,
            collection_id INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
            FOREIGN KEY (collection_id) REFERENCES collections (id),
            PRIMARY KEY (paper_id, collection_id)
        )
        """)

        # Search analytics for improving performance
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            search_query TEXT,
            source TEXT,
            papers_found INTEGER,
            avg_relevance REAL,
            search_time_seconds REAL,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (session_id)
        )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_relevance ON papers(relevance_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_session ON papers(search_session)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_selected ON papers(selected)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON search_sessions(created_at DESC)")

        conn.commit()
        conn.close()
        logger.info(f"Gemini Literature Database initialized at {self.db_path}")

    def save_paper(self, paper: Paper, session_id: str, gemini_analysis: Optional[Dict[str, Any]] = None) -> bool:
        """Save paper with comprehensive Gemini analysis data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
            INSERT OR REPLACE INTO papers (
                paper_id, title, authors, abstract, publication_date, journal,
                citation_count, impact_factor, url, doi, keywords, categories,
                relevance_score, confidence_score, selected, search_session, source,
                gemini_reasoning, key_matches, concerns, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                paper.paper_id, paper.title, json.dumps(paper.authors), paper.abstract,
                paper.publication_date, paper.journal, paper.citation_count, paper.impact_factor,
                paper.url, paper.doi, json.dumps(paper.keywords), json.dumps(paper.categories),
                paper.relevance_score, paper.confidence_score, paper.selected, session_id, paper.source,
                gemini_analysis.get('reasoning', '') if gemini_analysis else '',
                json.dumps(gemini_analysis.get('key_matches', [])) if gemini_analysis else '[]',
                json.dumps(gemini_analysis.get('concerns', [])) if gemini_analysis else '[]'
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error saving paper {paper.paper_id}: {e}")
            return False

    def get_papers(self, session_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Paper]:
        """Retrieve papers with advanced filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM papers WHERE 1=1"
        params = []

        if session_id:
            query += " AND search_session = ?"
            params.append(session_id)

        if filters:
            if filters.get('min_relevance', 0) > 0:
                query += " AND relevance_score >= ?"
                params.append(filters['min_relevance'])

            if filters.get('selected_only', False):
                query += " AND selected = 1"

        query += " ORDER BY relevance_score DESC, citation_count DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        papers = []
        for row in rows:
            paper = Paper(
                paper_id=row[1],
                title=row[2],
                authors=json.loads(row[3]) if row[3] else [],
                abstract=row[4],
                publication_date=row[5],
                journal=row[6],
                citation_count=row[7],
                impact_factor=row[8],
                url=row[9],
                doi=row[10],
                keywords=json.loads(row[11]) if row[11] else [],
                categories=json.loads(row[12]) if row[12] else [],
                relevance_score=row[13] if row[13] is not None else 0.0,
                confidence_score=row[14] if row[14] is not None else 0.0,
                selected=bool(row[15]),
                source=row[17]
            )
            papers.append(paper)

        return papers

    def update_session_stats(self, session_id: str, total_papers: int, selected_papers: int, avg_relevance: float, duration: float):
        """Update session statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE search_sessions 
        SET total_papers_found = ?, papers_selected = ?, avg_relevance_score = ?, 
            search_duration_seconds = ?, last_activity = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """, (total_papers, selected_papers, avg_relevance, duration, session_id))

        conn.commit()
        conn.close()

class GeminiPaperScraper:
    """Advanced paper scraper with intelligent source selection and parallel processing"""

    def __init__(self, max_concurrent_requests: int = 5):
        self.max_concurrent_requests = max_concurrent_requests
        self.throttler = Throttler(rate_limit=10, period=1.0)  # 10 requests per second
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_semantic_scholar(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Search using Semantic Scholar API - high-quality CS/AI papers"""
        papers = []
        
        try:
            logger.info(f"Searching Semantic Scholar for: {query}")
            
            # Semantic Scholar API endpoint
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            
            # Build query parameters
            params = {
                'query': query,
                'limit': min(max_results * 2, 100),  # API limit is 100
                'fields': 'paperId,title,abstract,authors,year,citationCount,venue,url,externalIds,fieldsOfStudy'
            }
            
            # Add year filter if specified
            if filters.year_start or filters.year_end:
                year_filter = f"{filters.year_start or 1900}-{filters.year_end or 2030}"
                params['year'] = year_filter
            
            # Proper headers for Semantic Scholar
            headers = {
                'User-Agent': 'ResearchAssistant/1.0 (https://github.com/BurntDosa/Research-Assistant; mailto:gagan.bangaragiri@gmail.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Semantic Scholar rate limit hit, waiting...")
                time.sleep(10)
                response = requests.get(url, params=params, headers=headers, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            for paper_data in data.get('data', []):
                try:
                    # Extract paper information
                    title = paper_data.get('title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                        
                    abstract = paper_data.get('abstract', '')
                    authors = [author.get('name', '') for author in paper_data.get('authors', [])]
                    year = paper_data.get('year')
                    citation_count = paper_data.get('citationCount', 0) or 0
                    venue = paper_data.get('venue', 'Unknown')
                    url = paper_data.get('url', '')
                    
                    # Apply filters
                    if filters.min_citations and citation_count < filters.min_citations:
                        logger.debug(f"Skipping S2 paper '{title[:50]}' - citations {citation_count} < min {filters.min_citations}")
                        continue
                    if filters.max_citations and citation_count > filters.max_citations:
                        continue
                    
                    # Check keyword filters
                    full_text = f"{title} {abstract}".lower()
                    if filters.keyword_requirements:
                        if not any(req.lower() in full_text for req in filters.keyword_requirements):
                            continue
                    if filters.exclude_keywords:
                        if any(excl.lower() in full_text for excl in filters.exclude_keywords):
                            continue
                    
                    # Generate keywords and categories
                    keywords = self._extract_advanced_keywords(title + ' ' + abstract)
                    categories = paper_data.get('fieldsOfStudy', []) or ['Computer Science']
                    
                    # Get DOI if available
                    doi = ''
                    external_ids = paper_data.get('externalIds', {})
                    if external_ids and 'DOI' in external_ids:
                        doi = external_ids['DOI']
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract or 'No abstract available',
                        publication_date=str(year) if year else 'Unknown',
                        journal=venue,
                        citation_count=citation_count,
                        url=url,
                        doi=doi,
                        keywords=keywords,
                        categories=categories,
                        source='semantic_scholar'
                    )
                    
                    papers.append(paper)
                    
                    if len(papers) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing Semantic Scholar paper: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers from Semantic Scholar")
            
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
        
        return papers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_crossref(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Search using CrossRef API - comprehensive academic papers"""
        papers = []
        
        try:
            logger.info(f"Searching CrossRef for: {query}")
            
            # CrossRef API endpoint
            url = "https://api.crossref.org/works"
            
            # Build query parameters - CrossRef uses different query format
            params = {
                'query.bibliographic': query,  # Use bibliographic query for better results
                'rows': min(max_results * 2, 1000),  # CrossRef allows up to 1000
                'sort': 'relevance',
                'select': 'title,author,abstract,published,container-title,DOI,URL,is-referenced-by-count,subject,type'
            }
            
            # Add filters
            filters_list = []
            if filters.year_start:
                filters_list.append(f"from-pub-date:{filters.year_start}")
            if filters.year_end:
                filters_list.append(f"until-pub-date:{filters.year_end}")
            
            if filters_list:
                params['filter'] = ','.join(filters_list)
            
            # Proper headers for CrossRef
            headers = {
                'User-Agent': 'ResearchAssistant/1.0 (mailto:research@example.com)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('message', {}).get('items', []):
                try:
                    # Extract paper information
                    title_list = item.get('title', [])
                    if not title_list:
                        continue
                    title = title_list[0] if isinstance(title_list, list) else str(title_list)
                    
                    if not title or title == 'Unknown Title':
                        continue
                    
                    abstract = item.get('abstract', 'No abstract available')
                    
                    # Extract authors
                    authors = []
                    for author in item.get('author', []):
                        given = author.get('given', '')
                        family = author.get('family', '')
                        full_name = f"{given} {family}".strip()
                        if full_name:
                            authors.append(full_name)
                    
                    # Extract publication year
                    year = None
                    published = item.get('published', {})
                    if published.get('date-parts') and published['date-parts']:
                        try:
                            year = published['date-parts'][0][0]
                        except (IndexError, TypeError):
                            pass
                    
                    citation_count = item.get('is-referenced-by-count', 0) or 0
                    
                    # Extract venue
                    container_title = item.get('container-title', [])
                    venue = container_title[0] if container_title else 'Unknown'
                    
                    doi = item.get('DOI', '')
                    url = item.get('URL', '')
                    
                    # Apply citation filters
                    if filters.min_citations and citation_count < filters.min_citations:
                        logger.debug(f"Skipping CrossRef paper '{title[:50]}' - citations {citation_count} < min {filters.min_citations}")
                        continue
                    if filters.max_citations and citation_count > filters.max_citations:
                        continue
                    
                    # Check keyword filters
                    full_text = f"{title} {abstract}".lower()
                    if filters.keyword_requirements:
                        if not any(req.lower() in full_text for req in filters.keyword_requirements):
                            continue
                    if filters.exclude_keywords:
                        if any(excl.lower() in full_text for excl in filters.exclude_keywords):
                            continue
                    
                    # Generate keywords and categories
                    keywords = self._extract_advanced_keywords(title + ' ' + abstract)
                    categories = item.get('subject', []) or ['Academic']
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        publication_date=str(year) if year else 'Unknown',
                        journal=venue,
                        citation_count=citation_count,
                        url=url,
                        doi=doi,
                        keywords=keywords,
                        categories=categories,
                        source='crossref'
                    )
                    
                    papers.append(paper)
                    
                    if len(papers) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing CrossRef paper: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers from CrossRef")
            
        except Exception as e:
            logger.error(f"CrossRef search failed: {e}")
        
        return papers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_openalex(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Search using OpenAlex API - comprehensive open academic database"""
        papers = []
        
        try:
            logger.info(f"Searching OpenAlex for: {query}")
            
            # OpenAlex API endpoint
            url = "https://api.openalex.org/works"
            
            # Build query parameters - simplified approach
            params = {
                'search': query,
                'per_page': min(max_results * 2, 100),  # More conservative limit
                'sort': 'cited_by_count:desc',
                'mailto': 'gagan.bangaragiri@gmail.com'  # Polite pool for better performance
            }
            
            # Add year filter if specified
            if filters.year_start or filters.year_end:
                year_start = filters.year_start or 2000
                year_end = filters.year_end or 2030
                params['filter'] = f'publication_year:{year_start}-{year_end}'
            
            # Simple headers - OpenAlex doesn't require complex headers
            headers = {
                'User-Agent': 'ResearchAssistant/1.0 (mailto:gagan.bangaragiri@gmail.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            # Handle OpenAlex specific errors
            if response.status_code == 403:
                logger.warning("OpenAlex access forbidden - may need API key or better headers")
                return papers
            
            response.raise_for_status()
            data = response.json()
            
            for work in data.get('results', []):
                try:
                    # Extract paper information
                    title = work.get('title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Reconstruct abstract from inverted index
                    abstract = self._reconstruct_abstract_from_inverted_index(work.get('abstract_inverted_index'))
                    
                    # Extract authors
                    authors = []
                    for authorship in work.get('authorships', []):
                        author = authorship.get('author', {})
                        display_name = author.get('display_name', '')
                        if display_name:
                            authors.append(display_name)
                    
                    year = work.get('publication_year')
                    citation_count = work.get('cited_by_count', 0) or 0
                    
                    # Extract venue info
                    venue = 'Unknown'
                    primary_location = work.get('primary_location', {})
                    if primary_location and primary_location.get('source'):
                        venue = primary_location['source'].get('display_name', 'Unknown')
                    
                    doi = work.get('doi', '')
                    if doi and doi.startswith('https://doi.org/'):
                        doi = doi.replace('https://doi.org/', '')
                    
                    url = work.get('id', '')  # OpenAlex ID as URL
                    
                    # Apply citation filters
                    if filters.min_citations and citation_count < filters.min_citations:
                        logger.debug(f"Skipping OpenAlex paper '{title[:50]}' - citations {citation_count} < min {filters.min_citations}")
                        continue
                    if filters.max_citations and citation_count > filters.max_citations:
                        continue
                    
                    # Check keyword filters
                    full_text = f"{title} {abstract}".lower()
                    if filters.keyword_requirements:
                        if not any(req.lower() in full_text for req in filters.keyword_requirements):
                            continue
                    if filters.exclude_keywords:
                        if any(excl.lower() in full_text for excl in filters.exclude_keywords):
                            continue
                    
                    # Generate keywords and extract categories
                    keywords = self._extract_advanced_keywords(title + ' ' + abstract)
                    categories = []
                    for concept in work.get('concepts', []):
                        if concept.get('score', 0) > 0.3:  # Only high-confidence concepts
                            categories.append(concept.get('display_name', ''))
                    categories = categories[:5] or ['Academic']
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract or 'No abstract available',
                        publication_date=str(year) if year else 'Unknown',
                        journal=venue,
                        citation_count=citation_count,
                        url=url,
                        doi=doi,
                        keywords=keywords,
                        categories=categories,
                        source='openalex'
                    )
                    
                    papers.append(paper)
                    
                    if len(papers) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing OpenAlex paper: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers from OpenAlex")
            
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
        
        return papers
    
    def _reconstruct_abstract_from_inverted_index(self, inverted_index: Optional[Dict]) -> str:
        """Reconstruct abstract text from OpenAlex inverted index format"""
        if not inverted_index:
            return ""
        
        try:
            # Create a list to hold words in their correct positions
            max_position = 0
            for positions in inverted_index.values():
                if positions:
                    max_position = max(max_position, max(positions))
            
            words = [''] * (max_position + 1)
            
            # Place words in their correct positions
            for word, positions in inverted_index.items():
                for pos in positions:
                    if pos < len(words):
                        words[pos] = word
            
            # Join words and clean up
            abstract = ' '.join(words).strip()
            # Limit length to avoid very long abstracts
            if len(abstract) > 1000:
                abstract = abstract[:1000] + '...'
            
            return abstract
            
        except Exception:
            return ""

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_arxiv_api(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Simple arXiv API search as fallback"""
        papers = []
        
        try:
            logger.info(f"Searching arXiv API for: {query}")
            
            # arXiv API endpoint
            url = "http://export.arxiv.org/api/query"
            
            # Build query
            search_query = f"all:{query}"
            if filters.year_start:
                # arXiv uses submittedDate format
                start_date = f"{filters.year_start}0101"
                end_date = f"{filters.year_end or 2030}1231"
                search_query += f" AND submittedDate:[{start_date} TO {end_date}]"
            
            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': min(max_results * 2, 50),  # Conservative limit
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            for entry in root.findall('atom:entry', namespaces):
                try:
                    # Extract basic information
                    title_elem = entry.find('atom:title', namespaces)
                    title = title_elem.text.strip() if title_elem is not None else 'Unknown Title'
                    if not title or title == 'Unknown Title':
                        continue
                    
                    summary_elem = entry.find('atom:summary', namespaces)
                    abstract = summary_elem.text.strip() if summary_elem is not None else 'No abstract available'
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall('atom:author', namespaces):
                        name_elem = author.find('atom:name', namespaces)
                        if name_elem is not None:
                            authors.append(name_elem.text.strip())
                    
                    # Extract publication date
                    published_elem = entry.find('atom:published', namespaces)
                    year = 'Unknown'
                    if published_elem is not None:
                        try:
                            from datetime import datetime
                            pub_date = datetime.strptime(published_elem.text[:10], '%Y-%m-%d')
                            year = str(pub_date.year)
                        except:
                            pass
                    
                    # Extract arXiv ID and create URL
                    id_elem = entry.find('atom:id', namespaces)
                    arxiv_url = id_elem.text if id_elem is not None else ''
                    
                    # Extract DOI if available
                    doi = ''
                    doi_elem = entry.find('arxiv:doi', namespaces)
                    if doi_elem is not None:
                        doi = doi_elem.text
                    
                    # arXiv papers typically have 0 citations initially
                    citation_count = 0
                    
                    # Apply citation filters (arXiv papers usually have low citations)
                    if filters.min_citations and citation_count < filters.min_citations:
                        continue
                    
                    # Check keyword filters
                    full_text = f"{title} {abstract}".lower()
                    if filters.keyword_requirements:
                        if not any(req.lower() in full_text for req in filters.keyword_requirements):
                            continue
                    if filters.exclude_keywords:
                        if any(excl.lower() in full_text for excl in filters.exclude_keywords):
                            continue
                    
                    # Generate keywords
                    keywords = self._extract_advanced_keywords(title + ' ' + abstract)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        publication_date=year,
                        journal='arXiv',
                        citation_count=citation_count,
                        url=arxiv_url,
                        doi=doi,
                        keywords=keywords,
                        categories=['Computer Science'],
                        source='arxiv'
                    )
                    
                    papers.append(paper)
                    
                    if len(papers) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing arXiv paper: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers from arXiv")
            
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
        
        return papers

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_google_scholar_serpapi(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Search Google Scholar using SerpAPI - reliable alternative to scraping"""
        papers = []
        
        try:
            # Import SerpAPI
            from serpapi import GoogleSearch
            import os
            
            # Get API key from environment
            serpapi_key = os.getenv('SERPAPI_KEY')
            if not serpapi_key:
                logger.warning("SerpAPI key not found in environment variables")
                return papers
            
            logger.info(f"Searching Google Scholar via SerpAPI for: {query}")
            
            # Build search parameters following SerpAPI Google Scholar best practices
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": serpapi_key,
                "num": min(max_results * 2, 20),  # SerpAPI has limits
                "start": 0,
                "hl": "en",  # Language
                "as_sdt": "0,5"  # Include patents and citations
            }
            
            # Add year filter if specified
            if filters.year_start or filters.year_end:
                params["as_ylo"] = filters.year_start or 1900
                params["as_yhi"] = filters.year_end or 2030
            
            # Execute search with error handling
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
            except Exception as e:
                logger.error(f"SerpAPI request failed: {e}")
                return papers
            
            # Check for errors
            if "error" in results:
                logger.error(f"SerpAPI error: {results['error']}")
                return papers
            
            # Process organic results
            for result in results.get("organic_results", []):
                try:
                    title = result.get("title", "Unknown Title")
                    if not title or title == "Unknown Title":
                        continue
                    
                    # Extract snippet as abstract
                    abstract = result.get("snippet", "No abstract available")
                    
                    # Extract publication info
                    publication_info = result.get("publication_info", {})
                    authors = []
                    if "authors" in publication_info:
                        for author in publication_info["authors"]:
                            if isinstance(author, dict) and "name" in author:
                                authors.append(author["name"])
                            elif isinstance(author, str):
                                authors.append(author)
                    
                    # Extract year
                    year = "Unknown"
                    if "summary" in publication_info:
                        summary = publication_info["summary"]
                        # Try to extract year from summary (e.g., "2023 - Nature")
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', summary)
                        if year_match:
                            year = year_match.group()
                    
                    # Extract citation count from multiple possible locations
                    citation_count = 0
                    
                    # Method 1: inline_links.cited_by.total
                    inline_links = result.get("inline_links", {})
                    if "cited_by" in inline_links:
                        cited_by = inline_links["cited_by"]
                        if isinstance(cited_by, dict) and "total" in cited_by:
                            citation_count = cited_by["total"]
                        elif isinstance(cited_by, dict) and "link" in cited_by:
                            # Sometimes citation count is in the link text
                            link_text = cited_by.get("link", "")
                            import re
                            cite_match = re.search(r'Cited by (\d+)', link_text)
                            if cite_match:
                                citation_count = int(cite_match.group(1))
                    
                    # Method 2: result_id for more detailed lookup (if needed)
                    if citation_count == 0 and "result_id" in result:
                        # Could implement additional lookup here if needed
                        pass
                    
                    # Extract venue/journal
                    venue = publication_info.get("summary", "Unknown").split(" - ")[-1] if publication_info.get("summary") else "Unknown"
                    
                    # Get URL
                    url = result.get("link", "")
                    
                    # Apply citation filters
                    if filters.min_citations and citation_count < filters.min_citations:
                        continue
                    
                    # Check keyword filters
                    full_text = f"{title} {abstract}".lower()
                    if filters.keyword_requirements:
                        if not any(req.lower() in full_text for req in filters.keyword_requirements):
                            continue
                    if filters.exclude_keywords:
                        if any(excl.lower() in full_text for excl in filters.exclude_keywords):
                            continue
                    
                    # Generate keywords
                    keywords = self._extract_advanced_keywords(title + ' ' + abstract)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        publication_date=year,
                        journal=venue,
                        citation_count=citation_count,
                        url=url,
                        doi="",  # SerpAPI doesn't always provide DOI
                        keywords=keywords,
                        categories=self._classify_paper_categories(title, abstract, venue),
                        source='google_scholar_serpapi'
                    )
                    
                    papers.append(paper)
                    
                    if len(papers) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing Google Scholar result: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers from Google Scholar (SerpAPI)")
            
        except ImportError:
            logger.error("SerpAPI library not installed. Run: pip install google-search-results")
        except Exception as e:
            logger.error(f"Google Scholar SerpAPI search failed: {e}")
        
        return papers

    def search_google_scholar(self, query: str, filters: SearchFilters, max_results: int = 15) -> List[Paper]:
        """Deprecated: Google Scholar scraping is unreliable. Use SerpAPI version instead."""
        logger.warning("Google Scholar scraping is deprecated. Using SerpAPI version instead.")
        return self.search_google_scholar_serpapi(query, filters, max_results)

    def _extract_advanced_keywords(self, text: str, max_keywords: int = 15) -> List[str]:
        """Advanced keyword extraction with NLP-like processing"""
        import re
        from collections import Counter

        # Enhanced stop words for academic content
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'we', 'they', 'them', 'their', 'our', 'your', 'his', 'her', 'its', 'study',
            'research', 'paper', 'article', 'analysis', 'approach', 'method', 'results', 'conclusion'
        }

        # Extract words and phrases
        text = text.lower()

        # Find potential compound terms (2-3 words)
        compound_terms = re.findall(r'\b(?:[a-z]+(?:[\s-][a-z]+){1,2})\b', text)
        single_words = re.findall(r'\b[a-z]{3,}\b', text)

        # Filter and count
        filtered_compounds = [term for term in compound_terms if len(term) > 5 and not any(sw in term for sw in stop_words)]
        filtered_singles = [word for word in single_words if word not in stop_words and len(word) > 3]

        # Combine and prioritize
        all_terms = filtered_compounds + filtered_singles
        term_counts = Counter(all_terms)

        # Return top keywords, prioritizing compound terms
        keywords = []
        for term, count in term_counts.most_common(max_keywords * 2):
            if len(keywords) < max_keywords:
                if ' ' in term or '-' in term:  # Compound terms
                    keywords.append(term)
                elif len(keywords) < max_keywords // 2:  # Fill with single words if space
                    keywords.append(term)

        return keywords[:max_keywords]

    def _classify_paper_categories(self, title: str, abstract: str, journal: str) -> List[str]:
        """Classify papers into research categories"""
        categories = []
        content = (title + ' ' + abstract + ' ' + journal).lower()

        # Define category keywords (simplified - could be enhanced with ML)
        category_keywords = {
            'machine_learning': ['machine learning', 'neural network', 'deep learning', 'artificial intelligence', 'ai'],
            'computer_vision': ['computer vision', 'image processing', 'object detection', 'image recognition', 'visual'],
            'nlp': ['natural language processing', 'nlp', 'text mining', 'language model', 'sentiment analysis'],
            'data_science': ['data science', 'data mining', 'big data', 'analytics', 'statistical'],
            'robotics': ['robot', 'robotics', 'autonomous', 'control system', 'sensor'],
            'cybersecurity': ['security', 'cybersecurity', 'encryption', 'privacy', 'authentication'],
            'software_engineering': ['software', 'programming', 'development', 'engineering', 'architecture'],
            'algorithms': ['algorithm', 'optimization', 'complexity', 'computational', 'mathematical'],
            'systems': ['system', 'distributed', 'network', 'database', 'cloud computing'],
            'theory': ['theoretical', 'formal', 'proof', 'mathematical', 'logic']
        }

        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                categories.append(category)

        return categories if categories else ['general']

class GeminiRelevanceValidator:
    """Advanced relevance validator using Gemini 2.5 Flash with structured output"""

    def __init__(self, gemini_api_key: str):
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)

        # Initialize Gemini 2.5 Flash model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.2,  # Lower temperature for more consistent scoring
            max_output_tokens=1024
        )

        # Create structured output parser
        self.parser = PydanticOutputParser(pydantic_object=RelevanceScore)

        # Ultra-simple validation prompt to ensure consistent responses
        self.validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """Rate paper relevance to query on scale 0.0-1.0. 

Format: Only return a number between 0.0 and 1.0, nothing else.

Examples:
- For perfect match: 0.9
- For good match: 0.7  
- For weak match: 0.3
- For no match: 0.1

For "transformers" focus on: transformer neural networks, attention, BERT, GPT."""),
            ("human", """Query: {query}
Title: {title}
Abstract: {abstract}

Score:""")
        ])

        logger.info("Gemini 2.5 Flash Relevance Validator initialized")

    async def validate_paper_async(self, paper: Paper, query: str, criteria: Dict[str, Any], semaphore: asyncio.Semaphore, progress_callback=None, paper_index=0, total_papers=0) -> RelevanceScore:
        """Asynchronously validate a paper's relevance using Gemini 2.5 Flash"""
        async with semaphore:
            try:
                # Add a 7-second delay to respect rate limits (free tier: 10 requests/minute)
                # This ensures ~8.5 requests per minute to stay well under the limit
                if progress_callback:
                    progress_callback(paper_index, total_papers, f"Analyzing paper {paper_index + 1}/{total_papers}: {paper.title[:50]}...")
                
                await asyncio.sleep(7.0)  # 7 seconds between requests
                
                # Prepare paper information for evaluation
                paper_info = {
                    'title': paper.title,
                    'authors': ', '.join(paper.authors[:5]) + ('...' if len(paper.authors) > 5 else ''),
                    'journal': paper.journal,
                    'publication_date': paper.publication_date,
                    'citation_count': paper.citation_count,
                    'abstract': paper.abstract[:800] + ('...' if len(paper.abstract) > 800 else ''),
                    'keywords': ', '.join(paper.keywords[:10]),
                    'categories': ', '.join(paper.categories)
                }

                # Create the prompt with ultra-simple format
                formatted_prompt = self.validation_prompt.format(
                    query=query,
                    title=paper.title,
                    abstract=paper.abstract[:600] + ('...' if len(paper.abstract) > 600 else '')
                )
                
                logger.debug(f"Formatted prompt for '{paper.title[:50]}': {formatted_prompt[:300]}...")

                # Get Gemini's assessment
                response = await asyncio.to_thread(self.llm.invoke, formatted_prompt)

                # Parse structured output with robust error handling
                try:
                    # Clean the response content
                    content = response.content.strip()
                    logger.debug(f"Raw Gemini response for '{paper.title[:50]}': '{content}'")
                    
                    # Log the complete response for debugging
                    if len(content) < 3:  # Only warn if extremely short (empty or single character)
                        logger.warning(f"Suspiciously short Gemini response: '{content}' for paper '{paper.title[:50]}'")
                    elif len(content) < 10 and not content.replace('.', '').isdigit():  # Warn if short and not a simple number
                        logger.warning(f"Potentially problematic Gemini response: '{content}' for paper '{paper.title[:50]}'")
                    else:
                        logger.debug(f"Gemini response length: {len(content)} chars for '{paper.title[:50]}'")
                    
                    # Ultra-simple parsing - expect just a number
                    parsed_score = None
                    
                    logger.debug(f"Raw Gemini response: '{content}'")
                    
                    # Clean content and try to extract a number
                    content_clean = content.strip()
                    
                    # Try direct float parsing
                    try:
                        parsed_score = float(content_clean)
                        if 0.0 <= parsed_score <= 1.0:
                            logger.debug(f"Successfully parsed score directly: {parsed_score}")
                        else:
                            parsed_score = None
                    except ValueError:
                        pass
                    
                    # Try extracting a decimal number from the response
                    if parsed_score is None:
                        import re
                        number_match = re.search(r'([0-9]*\.?[0-9]+)', content_clean)
                        if number_match:
                            try:
                                parsed_score = float(number_match.group(1))
                                if 0.0 <= parsed_score <= 1.0:
                                    logger.debug(f"Successfully extracted score with regex: {parsed_score}")
                                else:
                                    parsed_score = None
                            except ValueError:
                                pass
                    
                    if parsed_score is not None:
                        # Create RelevanceScore from simple score
                        relevance_assessment = RelevanceScore(
                            relevance_score=parsed_score,
                            confidence_score=0.8 if parsed_score > 0.3 else 0.5,
                            reasoning=f"AI analysis: relevance score {parsed_score:.2f}",
                            key_matches=[query.lower()],
                            concerns=[] if parsed_score > 0.5 else ["Lower confidence due to limited matches"]
                        )
                        logger.info(f"Successfully parsed Gemini response for '{paper.title[:50]}' - Score: {parsed_score}")
                        return relevance_assessment
                    else:
                        raise ValueError(f"Could not extract valid score from response: {content}")
                        
                except Exception as parse_error:
                    logger.warning(f"Failed to parse Gemini response: {parse_error}. Response: '{content}'. Using enhanced fallback.")
                    return self._fallback_scoring(paper, query, content)

            except Exception as e:
                logger.error(f"Error in Gemini validation for paper '{paper.title}': {e}")
                return self._fallback_scoring(paper, query, "")

    def _fallback_scoring(self, paper: Paper, query: str, gemini_response: str = "") -> RelevanceScore:
        """Enhanced fallback scoring method when Gemini parsing fails"""
        try:
            # Normalize and tokenize
            query_words = set(query.lower().split())
            title_words = set(paper.title.lower().split())
            abstract_words = set(paper.abstract.lower().split()[:100])  # First 100 words
            keyword_words = set(' '.join(paper.keywords).lower().split())
            
            # Enhanced keyword matching for ML/AI terms
            ml_keywords = {
                'transformer', 'transformers', 'attention', 'bert', 'gpt', 'neural', 'network',
                'deep', 'learning', 'machine', 'artificial', 'intelligence', 'nlp', 'language',
                'model', 'training', 'fine-tuning', 'pre-training', 'embedding', 'encoder',
                'decoder', 'self-attention', 'multi-head'
            }
            
            # Check for ML/AI context boost
            content_text = (paper.title + ' ' + paper.abstract + ' ' + ' '.join(paper.keywords)).lower()
            ml_context_boost = 0.0
            for ml_term in ml_keywords:
                if ml_term in content_text:
                    ml_context_boost += 0.1
            ml_context_boost = min(ml_context_boost, 0.3)  # Cap at 0.3

            # Calculate overlaps with improved weighting
            title_overlap = len(query_words.intersection(title_words)) / max(len(query_words), 1)
            abstract_overlap = len(query_words.intersection(abstract_words)) / max(len(query_words), 1)
            keyword_overlap = len(query_words.intersection(keyword_words)) / max(len(query_words), 1)

            # Enhanced scoring with ML context
            base_score = (title_overlap * 0.5 + abstract_overlap * 0.3 + keyword_overlap * 0.2)
            
            # Add ML context boost for relevant papers
            enhanced_score = base_score + ml_context_boost

            # Citation boost (smaller impact)
            citation_boost = min(0.1, paper.citation_count / 1000)

            final_score = min(enhanced_score + citation_boost, 1.0)
            
            # Ensure minimum reasonable score for papers with any relevance
            if final_score > 0.1:
                final_score = max(final_score, 0.4)  # Boost weak but relevant papers

            matched_terms = list(query_words.intersection(title_words.union(keyword_words)))
            confidence = 0.7 if matched_terms else 0.4

            return RelevanceScore(
                relevance_score=final_score,
                confidence_score=confidence,
                reasoning=f"Enhanced relevance analysis. Base text matching: {base_score:.2f}, ML context boost: {ml_context_boost:.2f}, final score: {final_score:.2f}",
                key_matches=matched_terms[:5],
                concerns=[] if final_score > 0.5 else ["Lower confidence due to limited direct matches"]
            )

        except Exception as e:
            logger.error(f"Fallback scoring failed: {e}")
            return RelevanceScore(
                relevance_score=0.6,  # More generous default
                confidence_score=0.3,
                reasoning="Emergency fallback with conservative relevance estimate",
                key_matches=[],
                concerns=["Multiple evaluation errors occurred"]
            )

class GeminiLiteratureDiscoveryAgent:
    """Main orchestrating agent for literature discovery using Gemini 2.5 Flash"""

    def __init__(self, gemini_api_key: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.gemini_api_key = gemini_api_key
        self.scraper = GeminiPaperScraper()
        self.validator = GeminiRelevanceValidator(gemini_api_key)
        self.database = GeminiLiteratureDatabase()
        self.session_id = None
        self.search_start_time = None
        
        # Set up semaphore for limiting concurrent Gemini calls
        if loop:
            self.gemini_semaphore = asyncio.Semaphore(3, loop=loop)  # 3 concurrent with delays
        else:
            self.gemini_semaphore = asyncio.Semaphore(3)  # 3 concurrent requests with 7-second delays

        logger.info("Gemini Literature Discovery Agent initialized with Gemini 2.5 Flash")

    def start_session(self, query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Start a new literature discovery session"""
        self.session_id = str(uuid.uuid4())
        self.search_start_time = time.time()

        # Validate and convert filters
        if filters:
            try:
                search_filters = SearchFilters(**filters)
                filters = search_filters.dict()
            except Exception as e:
                logger.warning(f"Invalid filters provided: {e}")
                filters = {}

        # Save session to database
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_sessions (session_id, query, filters, gemini_model_used) VALUES (?, ?, ?, ?)",
            (self.session_id, query, json.dumps(filters or {}), "gemini-2.5-flash")
        )
        conn.commit()
        conn.close()

        logger.info(f"Started session {self.session_id[:8]} with query: '{query}'")
        return self.session_id

    async def search_papers_async(self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 15) -> List[Paper]:
        """Asynchronously search for papers using multiple sources with Gemini validation"""
        if not filters:
            filters = {}

        try:
            search_filters = SearchFilters(**filters)
        except Exception as e:
            logger.warning(f"Invalid filters, using defaults: {e}")
            search_filters = SearchFilters()

        logger.info(f"Starting comprehensive paper search for: '{query}'")

        # Multi-source search with sequential execution - using reliable sources
        all_papers = []
        source_stats = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'failed_sources': []
        }
        
        # Execute searches sequentially with delays to be respectful to APIs
        sources = [
            ('google_scholar_serpapi', self.scraper.search_google_scholar_serpapi),
            ('crossref', self.scraper.search_crossref),
            ('openalex', self.scraper.search_openalex),
            ('arxiv', self.scraper.search_arxiv_api)
        ]
        
        for source_name, search_func in sources:
            source_stats['attempted'] += 1
            
            try:
                logger.info(f"Searching {source_name}...")
                
                # Add timeout mechanism for individual sources
                try:
                    # For very small max_results, use 1 paper per source
                    papers_per_source = 1 if max_results <= 4 else max_results // 4 + 3
                    papers = await asyncio.wait_for(
                        asyncio.to_thread(
                            search_func, 
                            query, search_filters, papers_per_source
                        ),
                        timeout=45.0  # 45 second timeout per source
                    )
                    
                    if papers:
                        all_papers.extend(papers)
                        source_stats['successful'] += 1
                        logger.info(f"{source_name}: found {len(papers)} papers")
                    else:
                        logger.warning(f"{source_name}: returned no papers")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"{source_name}: timed out after 45 seconds, skipping...")
                    source_stats['failed'] += 1
                    source_stats['failed_sources'].append(f"{source_name} (timeout)")
                    continue
                
                # Small delay between API calls to be respectful
                if source_name != 'arxiv':  # No delay after last source
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"{source_name} search failed: {e}")
                source_stats['failed'] += 1
                source_stats['failed_sources'].append(f"{source_name} (error)")
                continue

        # Log search statistics
        logger.info(f"Source search completed: {source_stats['successful']}/{source_stats['attempted']} sources successful")
        if source_stats['failed_sources']:
            logger.warning(f"Failed sources: {', '.join(source_stats['failed_sources'])}")
        
        # Check if we have any papers at all
        if not all_papers:
            logger.error("No papers found from any source - all sources failed")
            if source_stats['failed'] == source_stats['attempted']:
                logger.error("All sources failed - this might indicate API issues or network problems")
            return []

        # Remove duplicates intelligently
        unique_papers = self._advanced_deduplication(all_papers)
        logger.info(f"After deduplication: {len(unique_papers)} unique papers")

        # Pre-filter and pre-rank papers to reduce Gemini API calls
        # Sort by citation count and relevance indicators
        def paper_priority_score(paper):
            score = 0
            # Citation count weight (normalized to 0-1)
            score += min(paper.citation_count / 1000, 1.0) * 0.3
            
            # Title relevance (simple keyword matching)
            title_lower = paper.title.lower()
            query_lower = query.lower()
            query_words = set(query_lower.split())
            title_words = set(title_lower.split())
            title_overlap = len(query_words.intersection(title_words)) / max(len(query_words), 1)
            score += title_overlap * 0.5
            
            # Recent papers bonus
            try:
                year = int(paper.publication_date) if paper.publication_date.isdigit() else 2000
                if year >= 2020:
                    score += 0.2
            except:
                pass
                
            return score
        
        # Sort by priority and take top candidates for Gemini validation
        unique_papers.sort(key=paper_priority_score, reverse=True)
        papers_to_validate = unique_papers[:max_results]  # Only validate what we need
        
        logger.info(f"Pre-selected {len(papers_to_validate)} high-priority papers for Gemini validation")

        # Parallel validation with Gemini 2.5 Flash - with rate limiting
        logger.info("Starting Gemini 2.5 Flash validation...")
        
        # Add delay between validation calls to respect rate limits
        validation_results = []
        for i, paper in enumerate(papers_to_validate):
            try:
                result = await self.validator.validate_paper_async(
                    paper, query, filters, self.gemini_semaphore, 
                    progress_callback=None, paper_index=i, total_papers=len(papers_to_validate)
                )
                validation_results.append(result)
                
                # Rate limiting: wait between calls for free tier
                if i < len(papers_to_validate) - 1:  # Don't wait after last paper
                    await asyncio.sleep(7)  # 7 seconds = ~8 requests/minute (under 10/minute limit)
                    
            except Exception as e:
                logger.error(f"Validation failed for paper {i}: {e}")
                # Use fallback scoring
                validation_results.append(ValidationResult())

        # Quality Assurance System: Ensure we get 15 high-quality papers (relevance ≥ 0.5)
        min_relevance_threshold = 0.5
        target_high_quality_papers = max_results
        all_validated_papers = []
        processed_papers = set()  # Track which papers we've already validated
        
        # Multi-round validation to ensure quality
        validation_round = 1
        max_validation_rounds = 3
        
        while (len([p for p in all_validated_papers 
                   if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold]) < target_high_quality_papers 
               and validation_round <= max_validation_rounds 
               and len(processed_papers) < len(papers_to_validate)):
            
            logger.info(f"Quality assurance round {validation_round}: Need {target_high_quality_papers - len([p for p in all_validated_papers if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold])} more high-quality papers")
            
            # Determine how many papers to validate in this round
            current_high_quality = len([p for p in all_validated_papers 
                                      if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold])
            needed_papers = target_high_quality_papers - current_high_quality
            
            # Take more papers in early rounds to account for potential low relevance
            papers_this_round = min(
                needed_papers * 2 if validation_round == 1 else needed_papers + 5,  # Over-sample in first round
                len(papers_to_validate) - len(processed_papers)
            )
            
            # Get papers for this round (excluding already processed)
            papers_for_validation = []
            for paper in papers_to_validate:
                if paper.title not in processed_papers and len(papers_for_validation) < papers_this_round:
                    papers_for_validation.append(paper)
                    processed_papers.add(paper.title)
            
            if not papers_for_validation:
                logger.info("No more papers to validate")
                break
                
            logger.info(f"Round {validation_round}: Validating {len(papers_for_validation)} papers")

            # Validate papers with rate limiting
            validation_results = []
            for i, paper in enumerate(papers_for_validation):
                try:
                    result = await self.validator.validate_paper_async(
                        paper, query, filters, self.gemini_semaphore, 
                        progress_callback=None, paper_index=i, total_papers=len(papers_for_validation)
                    )
                    validation_results.append(result)
                    
                    # Rate limiting: wait between calls for free tier
                    if i < len(papers_for_validation) - 1:  # Don't wait after last paper
                        await asyncio.sleep(7)  # 7 seconds = ~8 requests/minute
                        
                except Exception as e:
                    logger.error(f"Validation failed for paper {i}: {e}")
                    # Use fallback scoring
                    validation_results.append(ValidationResult())

            # Process validation results for this round
            for paper, validation_result in zip(papers_for_validation, validation_results):
                if hasattr(validation_result, 'relevance_score'):
                    # Safely assign scores with None protection
                    paper.relevance_score = validation_result.relevance_score if validation_result.relevance_score is not None else 0.3
                    paper.confidence_score = validation_result.confidence_score if validation_result.confidence_score is not None else 0.2
                    paper.gemini_reasoning = getattr(validation_result, 'reasoning', 'No reasoning available')
                    paper.key_matches = getattr(validation_result, 'key_matches', [])
                    paper.concerns = getattr(validation_result, 'concerns', [])
                else:
                    # Fallback scoring
                    paper.relevance_score = 0.3  # Lower fallback to encourage more searching
                    paper.confidence_score = 0.2
                    paper.gemini_reasoning = "Validation failed - using fallback scoring"
                    paper.key_matches = []
                    paper.concerns = []
                
                all_validated_papers.append(paper)
                
                # Save to database
                self.database.save_paper(
                    paper, 
                    self.session_id, 
                    {
                        'reasoning': paper.gemini_reasoning,
                        'key_matches': paper.key_matches,
                        'concerns': paper.concerns
                    }
                )
            
            # Check quality after this round
            current_high_quality_papers = [p for p in all_validated_papers 
                                         if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold]
            logger.info(f"After round {validation_round}: {len(current_high_quality_papers)} high-quality papers (≥{min_relevance_threshold})")
            
            validation_round += 1

        # Final selection: prioritize high-quality papers (safely handling None values)
        high_quality_papers = [p for p in all_validated_papers 
                             if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold]
        remaining_slots = max(0, target_high_quality_papers - len(high_quality_papers))
        
        if remaining_slots > 0:
            # Fill remaining slots with best available papers (even if below threshold)
            lower_quality_papers = [p for p in all_validated_papers 
                                  if p.relevance_score is None or p.relevance_score < min_relevance_threshold]
            # Sort safely with None handling
            lower_quality_papers.sort(key=lambda x: x.relevance_score if x.relevance_score is not None else 0.0, 
                                    reverse=True)
            high_quality_papers.extend(lower_quality_papers[:remaining_slots])
            
        # Sort final results by relevance score (safely handling None values)
        def safe_sort_key(paper):
            relevance = paper.relevance_score if paper.relevance_score is not None else 0.0
            confidence = paper.confidence_score if paper.confidence_score is not None else 0.0
            citations = paper.citation_count if paper.citation_count is not None else 0
            return (relevance, confidence, citations)
            
        validated_papers = sorted(high_quality_papers[:target_high_quality_papers], 
                                key=safe_sort_key, 
                                reverse=True)
        
        logger.info(f"Final selection: {len(validated_papers)} papers, "
                   f"{len([p for p in validated_papers if p.relevance_score is not None and p.relevance_score >= min_relevance_threshold])} high-quality (≥{min_relevance_threshold})")

        # Update session statistics
        if validated_papers:
            # Safe calculation of average relevance score
            valid_scores = [p.relevance_score for p in validated_papers if p.relevance_score is not None]
            avg_relevance = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            search_duration = time.time() - self.search_start_time if self.search_start_time is not None else 0.0
            self.database.update_session_stats(
                self.session_id, len(validated_papers), 0, avg_relevance, search_duration
            )

        logger.info(f"Search complete: {len(validated_papers)} papers validated and ranked (avg relevance: {avg_relevance:.2f})")
        return validated_papers

    def search_papers(self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 15) -> List[Paper]:
        """Synchronous wrapper for async paper search"""
        try:
            return asyncio.run(self.search_papers_async(query, filters, max_results))
        except Exception as e:
            # Add detailed traceback for debugging
            import traceback
            logger.error(f"Error in search_papers: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return []

    def _advanced_deduplication(self, papers: List[Paper]) -> List[Paper]:
        """Advanced deduplication using multiple similarity metrics"""
        if not papers:
            return []

        unique_papers = []
        seen_signatures = set()

        for paper in papers:
            # Create multiple signatures for comparison
            title_signature = self._normalize_title(paper.title)
            doi_signature = paper.doi.lower() if paper.doi else None
            url_signature = paper.url.lower() if paper.url else None

            # Check for exact matches
            if doi_signature and doi_signature in seen_signatures:
                continue
            if url_signature and url_signature in seen_signatures:
                continue

            # Check for title similarity
            is_duplicate = False
            for existing_paper in unique_papers:
                if self._titles_are_similar(paper.title, existing_paper.title):
                    # Keep the paper with higher citation count or better source
                    if (paper.citation_count > existing_paper.citation_count or 
                        (paper.source == 'google_scholar' and existing_paper.source == 'arxiv')):
                        # Replace the existing paper
                        unique_papers.remove(existing_paper)
                        break
                    else:
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_papers.append(paper)
                seen_signatures.add(title_signature)
                if doi_signature:
                    seen_signatures.add(doi_signature)
                if url_signature:
                    seen_signatures.add(url_signature)

        return unique_papers

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        import re
        # Remove punctuation, convert to lowercase, remove extra spaces
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _titles_are_similar(self, title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles are similar using Jaccard similarity"""
        norm1 = set(self._normalize_title(title1).split())
        norm2 = set(self._normalize_title(title2).split())

        if not norm1 or not norm2:
            return False

        intersection = len(norm1.intersection(norm2))
        union = len(norm1.union(norm2))

        jaccard_similarity = intersection / union if union > 0 else 0
        return jaccard_similarity >= threshold

    def select_papers(self, paper_indices: List[int], papers: List[Paper]) -> List[Paper]:
        """Mark papers as selected and update database"""
        selected_papers = []

        for idx in paper_indices:
            if 0 <= idx < len(papers):
                paper = papers[idx]
                paper.selected = True
                self.database.save_paper(paper, self.session_id)
                selected_papers.append(paper)

        # Update session statistics
        if selected_papers:
            total_selected = len([p for p in papers if p.selected])
            # Safe calculation of average relevance score
            valid_scores = [p.relevance_score for p in papers if p.relevance_score is not None]
            avg_relevance = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            search_duration = time.time() - self.search_start_time if self.search_start_time else 0

            self.database.update_session_stats(
                self.session_id, len(papers), total_selected, avg_relevance, search_duration
            )

        logger.info(f"Selected {len(selected_papers)} papers")
        return selected_papers

    async def find_similar_papers_async(self, selected_papers: List[Paper], max_results: int = 10) -> List[Paper]:
        """Find papers similar to selected ones using advanced similarity analysis"""
        if not selected_papers:
            return []

        logger.info(f"Finding papers similar to {len(selected_papers)} selected papers")

        # Analyze selected papers for similarity patterns
        all_keywords = []
        all_categories = []
        all_authors = []

        for paper in selected_papers:
            all_keywords.extend(paper.keywords)
            all_categories.extend(paper.categories)
            all_authors.extend(paper.authors)

        # Find most common elements
        from collections import Counter
        top_keywords = [kw for kw, count in Counter(all_keywords).most_common(8)]
        top_categories = [cat for cat, count in Counter(all_categories).most_common(3)]
        top_authors = [auth for auth, count in Counter(all_authors).most_common(5)]

        # Generate sophisticated search queries
        similarity_queries = []

        # Keyword-based query
        if top_keywords:
            keyword_query = ' '.join(top_keywords[:5])
            similarity_queries.append(keyword_query)

        # Category-based query
        if top_categories:
            category_query = ' '.join(top_categories)
            similarity_queries.append(category_query)

        # Author-based queries
        for author in top_authors[:2]:
            similarity_queries.append(f'author:"{author}"')

        # Search with similarity queries
        all_similar_papers = []

        for query in similarity_queries[:3]:  # Limit to 3 queries to avoid API limits
            try:
                similar_papers = await self.search_papers_async(
                    query, 
                    {'include_preprints': True}, 
                    max_results // len(similarity_queries) + 2
                )
                all_similar_papers.extend(similar_papers)
            except Exception as e:
                logger.error(f"Similar paper search failed for query '{query}': {e}")

        # Remove duplicates and already selected papers
        unique_similar = self._advanced_deduplication(all_similar_papers)
        selected_ids = {p.paper_id for p in selected_papers}
        new_similar = [p for p in unique_similar if p.paper_id not in selected_ids]

        # Sort by relevance and return top results (safely handling None values)
        def safe_sort_key(paper):
            relevance = paper.relevance_score if paper.relevance_score is not None else 0.0
            confidence = paper.confidence_score if paper.confidence_score is not None else 0.0
            return (relevance, confidence)
        
        new_similar.sort(key=safe_sort_key, reverse=True)
        result = new_similar[:max_results]

        logger.info(f"Found {len(result)} similar papers")
        return result

    def find_similar_papers(self, selected_papers: List[Paper], max_results: int = 10) -> List[Paper]:
        """Synchronous wrapper for similar paper search"""
        return asyncio.run(self.find_similar_papers_async(selected_papers, max_results))

    def get_session_papers(self, include_unselected: bool = False) -> List[Paper]:
        """Get papers from current session"""
        filters = {} if include_unselected else {'selected_only': True}
        return self.database.get_papers(self.session_id, filters)

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        if not self.session_id:
            return {}

        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()

        # Get session info
        cursor.execute("SELECT * FROM search_sessions WHERE session_id = ?", (self.session_id,))
        session_data = cursor.fetchone()

        # Get paper statistics
        cursor.execute("""
        SELECT 
            COUNT(*) as total_papers,
            COUNT(CASE WHEN selected = 1 THEN 1 END) as selected_papers,
            AVG(relevance_score) as avg_relevance,
            AVG(confidence_score) as avg_confidence,
            MAX(relevance_score) as max_relevance,
            MIN(relevance_score) as min_relevance
        FROM papers WHERE search_session = ?
        """, (self.session_id,))

        paper_stats = cursor.fetchone()
        conn.close()

        if session_data and paper_stats:
            return {
                'session_id': self.session_id,
                'query': session_data[2],
                'total_papers': paper_stats[0],
                'selected_papers': paper_stats[1],
                'avg_relevance_score': round(paper_stats[2] or 0, 3),
                'avg_confidence_score': round(paper_stats[3] or 0, 3),
                'max_relevance_score': round(paper_stats[4] or 0, 3),
                'min_relevance_score': round(paper_stats[5] or 0, 3),
                'search_duration': session_data[6],
                'created_at': session_data[8]
            }

        return {}