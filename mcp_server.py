
#!/usr/bin/env python3
"""
Literature Discovery MCP Server - Gemini 2.5 Flash Native Edition

Advanced Model Context Protocol server for managing academic papers discovered
by the Gemini-powered Literature Discovery Agent. Features intelligent storage,
retrieval, analysis, and organization capabilities with FAISS vector database integration.
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union
from dataclasses import dataclass, asdict

import anyio
from mcp.server import Server
from mcp.server.models import InitializationOptions  
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
    CallToolResult,
    ListResourcesResult,
    ReadResourceResult,
)
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our embedding agent for FAISS integration
try:
    from embedding_agent import EmbeddingAgent, EmbeddedPaper
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logger.warning("Embedding agent not available. Vector search features disabled.")

# Enhanced data models for Gemini integration
class GeminiPaper(BaseModel):
    """Enhanced paper model with Gemini-specific analysis fields"""
    paper_id: str = Field(description="Unique paper identifier")
    title: str = Field(description="Paper title")
    authors: List[str] = Field(description="List of authors")
    abstract: str = Field(description="Paper abstract")
    publication_date: str = Field(description="Publication date")
    journal: str = Field(description="Journal or venue name")
    citation_count: int = Field(ge=0, description="Number of citations")
    impact_factor: Optional[float] = Field(default=None, description="Journal impact factor")
    url: str = Field(default="", description="Paper URL")
    doi: Optional[str] = Field(default=None, description="DOI identifier")
    keywords: List[str] = Field(default=[], description="Paper keywords")
    categories: List[str] = Field(default=[], description="Research categories")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Gemini-calculated relevance score")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in relevance assessment")
    selected: bool = Field(default=False, description="Whether paper is selected")
    source: str = Field(default="unknown", description="Source of the paper")
    gemini_reasoning: Optional[str] = Field(default=None, description="Gemini's reasoning for relevance")
    key_matches: List[str] = Field(default=[], description="Key matching elements found by Gemini")
    concerns: List[str] = Field(default=[], description="Any concerns identified by Gemini")
    session_id: Optional[str] = Field(default=None, description="Search session ID")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

class SearchSession(BaseModel):
    """Search session model with comprehensive tracking"""
    session_id: str = Field(description="Unique session identifier")
    query: str = Field(description="Original search query")
    filters: Dict[str, Any] = Field(default={}, description="Applied search filters")
    total_papers_found: int = Field(ge=0, description="Total papers found in session")
    papers_selected: int = Field(ge=0, description="Number of papers selected")
    avg_relevance_score: float = Field(ge=0.0, le=1.0, description="Average relevance score")
    search_duration_seconds: float = Field(ge=0.0, description="Search duration in seconds")
    gemini_model_used: str = Field(default="gemini-2.5-flash", description="Gemini model version")
    created_at: str = Field(description="Session creation timestamp")
    last_activity: str = Field(description="Last activity timestamp")

class PaperCollection(BaseModel):
    """Collection model for organizing papers"""
    collection_id: int = Field(description="Unique collection identifier")
    name: str = Field(description="Collection name")
    description: str = Field(default="", description="Collection description")
    color: str = Field(default="#2196F3", description="Collection color")
    paper_count: int = Field(ge=0, description="Number of papers in collection")
    created_at: str = Field(description="Creation timestamp")

class SearchFilters(BaseModel):
    """Comprehensive search filters for paper queries"""
    session_id: Optional[str] = Field(default=None, description="Filter by session")
    min_relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum relevance score")
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum confidence score")
    min_citations: int = Field(default=0, ge=0, description="Minimum citation count")
    year_start: Optional[int] = Field(default=None, ge=1900, le=2030, description="Start year filter")
    year_end: Optional[int] = Field(default=None, ge=1900, le=2030, description="End year filter")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to filter by")
    categories: Optional[List[str]] = Field(default=None, description="Categories to filter by")
    sources: Optional[List[str]] = Field(default=None, description="Sources to filter by")
    selected_only: bool = Field(default=False, description="Show only selected papers")
    collections: Optional[List[int]] = Field(default=None, description="Filter by collections")

class GeminiLiteratureDatabase:
    """Advanced database manager optimized for Gemini literature discovery with FAISS integration"""

    def __init__(self, db_path: str = "gemini_mcp_literature.db"):
        self.db_path = db_path
        self.init_database()
        
        # Initialize embedding agent if available
        if EMBEDDING_AVAILABLE:
            self.embedding_agent = EmbeddingAgent("mcp_faiss_embeddings")
            logger.info("FAISS vector database integration enabled")
        else:
            self.embedding_agent = None
            logger.info("FAISS vector database integration disabled")
            
        logger.info(f"Gemini Literature MCP Database initialized at {db_path}")

    def init_database(self):
        """Initialize comprehensive database schema for Gemini integration"""
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
            source TEXT DEFAULT 'unknown',
            gemini_reasoning TEXT,
            key_matches TEXT,
            concerns TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Enhanced search sessions table
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

        # Collections for paper organization
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#2196F3',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Paper-collection relationships
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

        # Gemini analysis tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT,
            query TEXT,
            relevance_score REAL,
            confidence_score REAL,
            reasoning TEXT,
            key_matches TEXT,
            concerns TEXT,
            model_version TEXT DEFAULT 'gemini-2.5-flash',
            analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (paper_id)
        )
        """)

        # Search analytics for performance tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            search_query TEXT,
            source TEXT,
            papers_found INTEGER,
            avg_relevance REAL,
            search_time_seconds REAL,
            gemini_processing_time REAL,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES search_sessions (session_id)
        )
        """)

        # Create optimized indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_papers_relevance ON papers(relevance_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_papers_confidence ON papers(confidence_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_papers_session ON papers(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_papers_selected ON papers(selected)",
            "CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_created ON search_sessions(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name)",
            "CREATE INDEX IF NOT EXISTS idx_gemini_analysis_paper ON gemini_analysis(paper_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_session ON search_analytics(session_id)"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        conn.commit()
        conn.close()

    def add_paper(self, paper_data: Dict[str, Any]) -> bool:
        """Add or update a paper with comprehensive data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate paper_id if not provided
            if 'paper_id' not in paper_data or not paper_data['paper_id']:
                paper_data['paper_id'] = str(uuid.uuid4())[:8]

            cursor.execute("""
            INSERT OR REPLACE INTO papers (
                paper_id, title, authors, abstract, publication_date, journal,
                citation_count, impact_factor, url, doi, keywords, categories,
                relevance_score, confidence_score, selected, source,
                gemini_reasoning, key_matches, concerns, session_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                paper_data.get('paper_id'),
                paper_data.get('title', ''),
                json.dumps(paper_data.get('authors', [])),
                paper_data.get('abstract', ''),
                paper_data.get('publication_date', ''),
                paper_data.get('journal', ''),
                paper_data.get('citation_count', 0),
                paper_data.get('impact_factor'),
                paper_data.get('url', ''),
                paper_data.get('doi'),
                json.dumps(paper_data.get('keywords', [])),
                json.dumps(paper_data.get('categories', [])),
                paper_data.get('relevance_score', 0.0),
                paper_data.get('confidence_score', 0.0),
                paper_data.get('selected', False),
                paper_data.get('source', 'unknown'),
                paper_data.get('gemini_reasoning'),
                json.dumps(paper_data.get('key_matches', [])),
                json.dumps(paper_data.get('concerns', [])),
                paper_data.get('session_id')
            ))

            # Add Gemini analysis record
            if paper_data.get('gemini_reasoning'):
                cursor.execute("""
                INSERT INTO gemini_analysis (
                    paper_id, query, relevance_score, confidence_score,
                    reasoning, key_matches, concerns, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper_data['paper_id'],
                    paper_data.get('query', ''),
                    paper_data.get('relevance_score', 0.0),
                    paper_data.get('confidence_score', 0.0),
                    paper_data.get('gemini_reasoning'),
                    json.dumps(paper_data.get('key_matches', [])),
                    json.dumps(paper_data.get('concerns', [])),
                    'gemini-2.5-flash'
                ))

            conn.commit()
            conn.close()

            logger.info(f"Added/updated paper: {paper_data.get('title', 'Unknown')}")
            return True

        except Exception as e:
            logger.error(f"Error adding paper: {e}")
            return False

    def search_papers(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Advanced paper search with comprehensive filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build dynamic query
            query = "SELECT * FROM papers WHERE 1=1"
            params = []

            if filters:
                if filters.get('session_id'):
                    query += " AND session_id = ?"
                    params.append(filters['session_id'])

                if filters.get('min_relevance', 0) > 0:
                    query += " AND relevance_score >= ?"
                    params.append(filters['min_relevance'])

                if filters.get('min_confidence', 0) > 0:
                    query += " AND confidence_score >= ?"
                    params.append(filters['min_confidence'])

                if filters.get('min_citations', 0) > 0:
                    query += " AND citation_count >= ?"
                    params.append(filters['min_citations'])

                if filters.get('year_start'):
                    query += " AND publication_date >= ?"
                    params.append(str(filters['year_start']))

                if filters.get('year_end'):
                    query += " AND publication_date <= ?"
                    params.append(str(filters['year_end']))

                if filters.get('selected_only', False):
                    query += " AND selected = 1"

                if filters.get('sources'):
                    source_placeholders = ','.join(['?' for _ in filters['sources']])
                    query += f" AND source IN ({source_placeholders})"
                    params.extend(filters['sources'])

                if filters.get('keywords'):
                    for keyword in filters['keywords']:
                        query += " AND (title LIKE ? OR abstract LIKE ? OR keywords LIKE ?)"
                        keyword_pattern = f"%{keyword}%"
                        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

            # Default ordering
            query += " ORDER BY relevance_score DESC, confidence_score DESC, citation_count DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            papers = []

            for row in rows:
                paper_dict = dict(zip(columns, row))

                # Parse JSON fields
                for json_field in ['authors', 'keywords', 'categories', 'key_matches', 'concerns']:
                    if paper_dict.get(json_field):
                        try:
                            paper_dict[json_field] = json.loads(paper_dict[json_field])
                        except json.JSONDecodeError:
                            paper_dict[json_field] = []
                    else:
                        paper_dict[json_field] = []

                papers.append(paper_dict)

            conn.close()
            logger.info(f"Found {len(papers)} papers matching filters")
            return papers

        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return []

    def get_session_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if session_id:
                # Specific session stats
                cursor.execute("SELECT * FROM search_sessions WHERE session_id = ?", (session_id,))
                session_data = cursor.fetchone()

                cursor.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    COUNT(CASE WHEN selected = 1 THEN 1 END) as selected_papers,
                    AVG(relevance_score) as avg_relevance,
                    AVG(confidence_score) as avg_confidence,
                    MAX(relevance_score) as max_relevance,
                    MIN(relevance_score) as min_relevance,
                    COUNT(DISTINCT source) as unique_sources
                FROM papers WHERE session_id = ?
                """, (session_id,))

                paper_stats = cursor.fetchone()

                if session_data and paper_stats:
                    columns = [desc[0] for desc in cursor.description]
                    paper_stats_dict = dict(zip(columns, paper_stats))

                    return {
                        'session_id': session_id,
                        'query': session_data[2],
                        'gemini_model': session_data[7],
                        **paper_stats_dict,
                        'created_at': session_data[8],
                        'last_activity': session_data[9]
                    }
            else:
                # Global statistics
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    COUNT(CASE WHEN selected = 1 THEN 1 END) as selected_papers,
                    AVG(relevance_score) as avg_relevance,
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(DISTINCT source) as unique_sources
                FROM papers
                """)

                global_stats = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]

                conn.close()
                return dict(zip(columns, global_stats))

            conn.close()
            return {}

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def create_collection(self, name: str, description: str = "", color: str = "#2196F3") -> Optional[int]:
        """Create a new paper collection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO collections (name, description, color) VALUES (?, ?, ?)",
                (name, description, color)
            )

            collection_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Created collection '{name}' with ID {collection_id}")
            return collection_id

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return None

    def add_paper_to_collection(self, paper_id: str, collection_id: int) -> bool:
        """Add a paper to a collection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT OR IGNORE INTO paper_collections (paper_id, collection_id) VALUES (?, ?)",
                (paper_id, collection_id)
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                logger.info(f"Added paper {paper_id} to collection {collection_id}")

            return success

        except Exception as e:
            logger.error(f"Error adding paper to collection: {e}")
            return False

    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections with paper counts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT c.*, COUNT(pc.paper_id) as paper_count
            FROM collections c
            LEFT JOIN paper_collections pc ON c.id = pc.collection_id
            GROUP BY c.id, c.name, c.description, c.color, c.created_at
            ORDER BY c.created_at DESC
            """)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            collections = [dict(zip(columns, row)) for row in rows]

            conn.close()
            return collections

        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []

# Initialize server and database
server = Server("gemini-literature-discovery")
database = GeminiLiteratureDatabase()

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources for the Gemini literature system"""
    resources = []

    # Database overview
    resources.append(
        Resource(
            uri="gemini-literature://database/overview",
            name="Database Overview",
            description="Comprehensive overview of the Gemini literature database",
            mimeType="application/json"
        )
    )

    # Session resources
    resources.append(
        Resource(
            uri="gemini-literature://sessions/active",
            name="Active Sessions",
            description="Currently active search sessions",
            mimeType="application/json"
        )
    )

    # Collections
    collections = database.get_collections()
    for collection in collections:
        resources.append(
            Resource(
                uri=f"gemini-literature://collection/{collection['id']}",
                name=f"Collection: {collection['name']}",
                description=f"{collection['description']} ({collection['paper_count']} papers)",
                mimeType="application/json"
            )
        )

    # Analytics
    resources.append(
        Resource(
            uri="gemini-literature://analytics/performance",
            name="Performance Analytics",
            description="Gemini 2.5 Flash performance analytics and insights",
            mimeType="application/json"
        )
    )

    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read specific resources from the Gemini literature system"""

    if uri == "gemini-literature://database/overview":
        stats = database.get_session_statistics()
        collections = database.get_collections()

        overview = {
            "database_type": "Gemini Literature Discovery Database",
            "gemini_model": "gemini-2.5-flash",
            "statistics": stats,
            "collections": len(collections),
            "database_path": database.db_path,
            "last_updated": datetime.now().isoformat()
        }

        return json.dumps(overview, indent=2)

    elif uri == "gemini-literature://sessions/active":
        # Get recent sessions (last 7 days)
        try:
            conn = sqlite3.connect(database.db_path)
            cursor = conn.cursor()

            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute(
                """SELECT * FROM search_sessions 
                   WHERE created_at >= ? 
                   ORDER BY last_activity DESC""",
                (week_ago,)
            )

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            sessions = [dict(zip(columns, row)) for row in rows]

            conn.close()

            return json.dumps({
                "active_sessions": sessions,
                "count": len(sessions),
                "period": "last_7_days"
            }, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    elif uri.startswith("gemini-literature://collection/"):
        collection_id = int(uri.split("/")[-1])

        papers = database.search_papers({"collections": [collection_id]})

        return json.dumps({
            "collection_id": collection_id,
            "papers": papers,
            "count": len(papers)
        }, indent=2, default=str)

    elif uri == "gemini-literature://analytics/performance":
        try:
            conn = sqlite3.connect(database.db_path)
            cursor = conn.cursor()

            # Performance analytics
            cursor.execute("""
            SELECT 
                AVG(search_time_seconds) as avg_search_time,
                AVG(gemini_processing_time) as avg_gemini_time,
                COUNT(*) as total_searches,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_searches
            FROM search_analytics
            WHERE timestamp >= datetime('now', '-30 days')
            """)

            perf_stats = cursor.fetchone()

            # Relevance distribution
            cursor.execute("""
            SELECT 
                AVG(relevance_score) as avg_relevance,
                AVG(confidence_score) as avg_confidence,
                COUNT(CASE WHEN relevance_score >= 0.8 THEN 1 END) as high_relevance_count,
                COUNT(CASE WHEN relevance_score >= 0.6 THEN 1 END) as medium_relevance_count
            FROM papers
            WHERE created_at >= datetime('now', '-30 days')
            """)

            relevance_stats = cursor.fetchone()

            conn.close()

            analytics = {
                "period": "last_30_days",
                "performance": {
                    "avg_search_time_seconds": perf_stats[0] or 0,
                    "avg_gemini_processing_time": perf_stats[1] or 0,
                    "total_searches": perf_stats[2] or 0,
                    "success_rate": (perf_stats[3] or 0) / max(perf_stats[2] or 1, 1)
                },
                "relevance_quality": {
                    "avg_relevance_score": relevance_stats[0] or 0,
                    "avg_confidence_score": relevance_stats[1] or 0,
                    "high_relevance_papers": relevance_stats[2] or 0,
                    "medium_relevance_papers": relevance_stats[3] or 0
                },
                "gemini_model": "gemini-2.5-flash"
            }

            return json.dumps(analytics, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    else:
        raise ValueError(f"Unknown resource URI: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available tools for the Gemini literature system"""
    return [
        Tool(
            name="add_paper",
            description="Add a new paper to the Gemini literature database with full analysis data",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Paper title"},
                    "authors": {"type": "array", "items": {"type": "string"}, "description": "List of authors"},
                    "abstract": {"type": "string", "description": "Paper abstract"},
                    "publication_date": {"type": "string", "description": "Publication date"},
                    "journal": {"type": "string", "description": "Journal name"},
                    "citation_count": {"type": "integer", "description": "Citation count", "default": 0},
                    "impact_factor": {"type": "number", "description": "Journal impact factor", "optional": True},
                    "url": {"type": "string", "description": "Paper URL", "default": ""},
                    "doi": {"type": "string", "description": "DOI identifier", "optional": True},
                    "keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords", "default": []},
                    "categories": {"type": "array", "items": {"type": "string"}, "description": "Categories", "default": []},
                    "relevance_score": {"type": "number", "description": "Gemini relevance score (0-1)", "default": 0.0},
                    "confidence_score": {"type": "number", "description": "Confidence score (0-1)", "default": 0.0},
                    "source": {"type": "string", "description": "Paper source", "default": "manual"},
                    "gemini_reasoning": {"type": "string", "description": "Gemini's reasoning", "optional": True},
                    "key_matches": {"type": "array", "items": {"type": "string"}, "description": "Key matches found", "default": []},
                    "concerns": {"type": "array", "items": {"type": "string"}, "description": "Concerns identified", "default": []},
                    "session_id": {"type": "string", "description": "Search session ID", "optional": True}
                },
                "required": ["title", "authors", "abstract", "publication_date", "journal"]
            }
        ),
        Tool(
            name="search_papers",
            description="Search papers with advanced Gemini-powered filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Filter by session ID", "optional": True},
                    "min_relevance": {"type": "number", "description": "Minimum relevance score", "default": 0.0},
                    "min_confidence": {"type": "number", "description": "Minimum confidence score", "default": 0.0},
                    "min_citations": {"type": "integer", "description": "Minimum citation count", "default": 0},
                    "year_start": {"type": "integer", "description": "Start year filter", "optional": True},
                    "year_end": {"type": "integer", "description": "End year filter", "optional": True},
                    "keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords to search for", "optional": True},
                    "categories": {"type": "array", "items": {"type": "string"}, "description": "Categories to filter by", "optional": True},
                    "sources": {"type": "array", "items": {"type": "string"}, "description": "Sources to filter by", "optional": True},
                    "selected_only": {"type": "boolean", "description": "Show only selected papers", "default": False},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 50}
                }
            }
        ),
        Tool(
            name="update_paper",
            description="Update an existing paper's information",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper ID to update"},
                    "updates": {"type": "object", "description": "Fields to update"}
                },
                "required": ["paper_id", "updates"]
            }
        ),
        Tool(
            name="create_collection",
            description="Create a new paper collection for organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Collection name"},
                    "description": {"type": "string", "description": "Collection description", "default": ""},
                    "color": {"type": "string", "description": "Collection color", "default": "#2196F3"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="add_to_collection",
            description="Add a paper to a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper ID"},
                    "collection_id": {"type": "integer", "description": "Collection ID"}
                },
                "required": ["paper_id", "collection_id"]
            }
        ),
        Tool(
            name="get_session_statistics",
            description="Get comprehensive statistics for a session or global stats",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID (optional for global stats)", "optional": True}
                }
            }
        ),
        Tool(
            name="analyze_gemini_performance",
            description="Analyze Gemini 2.5 Flash performance and accuracy",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to analyze", "default": 30},
                    "include_details": {"type": "boolean", "description": "Include detailed analysis", "default": False}
                }
            }
        ),
        Tool(
            name="get_collections",
            description="Get all collections with paper counts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="export_papers",
            description="Export papers in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "enum": ["json", "csv"], "description": "Export format", "default": "json"},
                    "filters": {"type": "object", "description": "Filters to apply", "optional": True},
                    "include_analysis": {"type": "boolean", "description": "Include Gemini analysis", "default": True}
                }
            }
        ),
        Tool(
            name="vector_search_papers",
            description="Search papers using FAISS vector similarity (if available)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for vector similarity"},
                    "k": {"type": "integer", "description": "Number of results to return", "default": 20},
                    "paper_type_filter": {"type": "string", "enum": ["review", "conference", "journal"], "description": "Filter by paper type", "optional": True}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_papers_to_vector_db",
            description="Add a batch of papers to the FAISS vector database",
            inputSchema={
                "type": "object",
                "properties": {
                    "papers": {"type": "array", "items": {"type": "object"}, "description": "List of paper objects to add"},
                    "session_id": {"type": "string", "description": "Session ID for tracking"},
                    "search_query": {"type": "string", "description": "Original search query"}
                },
                "required": ["papers", "session_id", "search_query"]
            }
        ),
        Tool(
            name="get_vector_database_stats",
            description="Get comprehensive statistics about the FAISS vector database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="execute_research_pipeline",
            description="Execute the full two-phase research pipeline (48 papers → top 20)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research query"},
                    "paper_type_preference": {"type": "string", "enum": ["review", "conference", "journal"], "description": "Preferred paper type", "optional": True},
                    "filters": {"type": "object", "description": "Advanced search filters", "optional": True}
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle all tool calls for the Gemini literature system"""
    try:
        if name == "add_paper":
            success = database.add_paper(arguments)
            return [TextContent(
                type="text",
                text=f"Paper {'added successfully' if success else 'failed to add'}: '{arguments.get('title', 'Unknown')}'"
            )]

        elif name == "search_papers":
            limit = arguments.pop('limit', 50)
            papers = database.search_papers(arguments)

            # Apply limit
            papers = papers[:limit]

            return [TextContent(
                type="text",
                text=f"Found {len(papers)} papers matching criteria:\n" + json.dumps({
                    "count": len(papers),
                    "papers": papers
                }, indent=2, default=str)
            )]

        elif name == "update_paper":
            paper_id = arguments["paper_id"]
            updates = arguments["updates"]

            # Implementation would go here
            return [TextContent(
                type="text",
                text=f"Update functionality for paper {paper_id} - to be implemented"
            )]

        elif name == "create_collection":
            collection_id = database.create_collection(
                arguments["name"],
                arguments.get("description", ""),
                arguments.get("color", "#2196F3")
            )

            return [TextContent(
                type="text",
                text=f"Created collection '{arguments['name']}' with ID {collection_id}" if collection_id else "Failed to create collection"
            )]

        elif name == "add_to_collection":
            success = database.add_paper_to_collection(
                arguments["paper_id"],
                arguments["collection_id"]
            )

            return [TextContent(
                type="text",
                text=f"Paper {arguments['paper_id']} {'added to' if success else 'failed to add to'} collection {arguments['collection_id']}"
            )]

        elif name == "get_session_statistics":
            stats = database.get_session_statistics(arguments.get("session_id"))

            return [TextContent(
                type="text",
                text=f"Session Statistics:\n" + json.dumps(stats, indent=2, default=str)
            )]

        elif name == "analyze_gemini_performance":
            days = arguments.get("days", 30)
            include_details = arguments.get("include_details", False)

            # Simplified performance analysis
            stats = database.get_session_statistics()

            analysis = {
                "period_days": days,
                "gemini_model": "gemini-2.5-flash",
                "overall_performance": stats,
                "analysis_timestamp": datetime.now().isoformat()
            }

            return [TextContent(
                type="text",
                text=f"Gemini 2.5 Flash Performance Analysis:\n" + json.dumps(analysis, indent=2, default=str)
            )]

        elif name == "get_collections":
            collections = database.get_collections()

            return [TextContent(
                type="text",
                text=f"Collections ({len(collections)} total):\n" + json.dumps(collections, indent=2, default=str)
            )]

        elif name == "export_papers":
            format_type = arguments.get("format", "json")
            filters = arguments.get("filters", {})
            include_analysis = arguments.get("include_analysis", True)

            papers = database.search_papers(filters)

            if format_type == "csv":
                # Convert to CSV format (simplified)
                export_text = "CSV export would be generated here"
            else:
                export_text = json.dumps({
                    "export_format": format_type,
                    "export_timestamp": datetime.now().isoformat(),
                    "include_gemini_analysis": include_analysis,
                    "paper_count": len(papers),
                    "papers": papers
                }, indent=2, default=str)

            return [TextContent(
                type="text",
                text=f"Export completed ({len(papers)} papers):\n{export_text}"
            )]

        elif name == "vector_search_papers":
            if not EMBEDDING_AVAILABLE or not database.embedding_agent:
                return [TextContent(
                    type="text",
                    text="Vector search not available: FAISS/embedding agent not initialized"
                )]

            query = arguments.get("query", "")
            k = arguments.get("k", 20)
            paper_type_filter = arguments.get("paper_type_filter")

            similar_papers = database.embedding_agent.search_papers(query, k, paper_type_filter)

            return [TextContent(
                type="text",
                text=f"Vector search results ({len(similar_papers)} papers):\n" + json.dumps([
                    {
                        "paper_id": p.paper_id,
                        "title": p.title,
                        "similarity_score": p.similarity_score,
                        "paper_type": p.paper_type,
                        "relevance_score": p.relevance_score,
                        "journal": p.journal
                    } for p in similar_papers
                ], indent=2)
            )]

        elif name == "add_papers_to_vector_db":
            if not EMBEDDING_AVAILABLE or not database.embedding_agent:
                return [TextContent(
                    type="text",
                    text="Vector database not available: FAISS/embedding agent not initialized"
                )]

            papers = arguments.get("papers", [])
            session_id = arguments.get("session_id", "")
            search_query = arguments.get("search_query", "")

            embedded_papers = database.embedding_agent.process_paper_batch(papers, search_query, session_id)

            return [TextContent(
                type="text",
                text=f"Added {len(embedded_papers)} papers to vector database for session {session_id}"
            )]

        elif name == "get_vector_database_stats":
            if not EMBEDDING_AVAILABLE or not database.embedding_agent:
                return [TextContent(
                    type="text",
                    text="Vector database not available: FAISS/embedding agent not initialized"
                )]

            stats = database.embedding_agent.get_statistics()

            return [TextContent(
                type="text",
                text=f"Vector Database Statistics:\n" + json.dumps(stats, indent=2)
            )]

        elif name == "execute_research_pipeline":
            if not EMBEDDING_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="Research pipeline not available: embedding components not initialized"
                )]

            from control_agent import ResearchPipeline, SearchFilters
            
            query = arguments.get("query", "")
            paper_type_preference = arguments.get("paper_type_preference")
            filters_dict = arguments.get("filters", {})
            
            # Create filters object
            filters = SearchFilters(**filters_dict) if filters_dict else None
            
            # Execute pipeline
            pipeline = ResearchPipeline()
            results = pipeline.execute_full_pipeline(query, filters, paper_type_preference)

            return [TextContent(
                type="text",
                text=f"Research Pipeline Results:\n" + json.dumps({
                    "session_id": results["session_id"],
                    "query": results["query"],
                    "total_unique_papers": results["total_unique_papers"],
                    "top_papers_count": len(results["top_papers"]),
                    "pipeline_duration": results["pipeline_duration"],
                    "statistics": results["statistics"]
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Tool call error for {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the Gemini Literature Discovery MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-literature-discovery",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    logger.info("Starting Gemini Literature Discovery MCP Server v2.0")
    asyncio.run(main())
