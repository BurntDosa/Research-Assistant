#!/usr/bin/env python3
"""
Enhanced Control Agent - Updated with Optional Phase 2 and Performance Improvements
"""

import os
import time
import uuid
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from .literature_agent import GeminiLiteratureDiscoveryAgent, SearchFilters
from .embedding_agent import EmbeddedPaper, EmbeddingAgent

# Simple placeholder for user database
class UserSelectionDatabase:
    def __init__(self):
        pass

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    """Configuration constants for the enhanced pipeline"""
    INITIAL_PAPERS_PER_SOURCE = 5  # Find 5 papers from each source initially
    SECONDARY_PAPERS_PER_SOURCE = 3  # Find 3 papers from each source in secondary searches
    RELEVANCE_THRESHOLD = 0.7  # Minimum relevance score for papers
    TOP_DISPLAY_RESULTS = 10  # Show top 10 papers to user
    SIMILARITY_THRESHOLD = 0.7
    SECONDARY_DISPLAY_RESULTS = 20 # Show more papers in secondary search results

class EnhancedResearchPipeline:
    """Enhanced Research Pipeline with Iterative Search and Keyword Augmentation"""
    
    def __init__(self):
        """Initialize the enhanced research pipeline"""
        self.session_id = str(uuid.uuid4())[:8]
        self.stored_dois = set()
        self.stored_titles = set()
        self.all_found_papers = []  # Keep track of all papers found during session
        self.current_session_papers = []  # Papers from current search
        
        # Initialize agents
        self._init_agents()
        
        # Initialize user selection database
        self.user_db = UserSelectionDatabase()
        logger.info("Enhanced Research Pipeline initialized with session ID: %s", self.session_id)
    
    def _init_agents(self):
        """Initialize literature and embedding agents with error handling"""
        try:
            # Get API key
            gemini_api_key = os.getenv('GOOGLE_API_KEY')
            if not gemini_api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Initialize literature agent
            self.literature_agent = GeminiLiteratureDiscoveryAgent(gemini_api_key)
            
            # Initialize embedding agent
            self.embedding_agent = EmbeddingAgent()
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def execute_initial_search(self, query: str, filters: Optional[SearchFilters] = None, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute initial search for 1 paper per source, return top 10 most relevant (reduced for testing)"""
        start_time = time.time()
        
        logger.info("=== INITIAL SEARCH: Finding Papers ===")
        logger.info(f"Starting initial search for query: '{query}'")
        logger.info(f"Target: {PipelineConfig.INITIAL_PAPERS_PER_SOURCE} papers per source")
        if sources:
            logger.info(f"Using selected sources: {sources}")
        
        # Initialize results structure
        results = {
            'session_id': self.session_id,
            'query': query,
            'papers_found': 0,
            'top_papers': [],
            'total_unique_papers': 0,
            'pipeline_duration': 0,
            'statistics': {},
            'all_papers': []
        }
        
        try:
            # Search for papers with increased target per source
            found_papers = self._search_papers_per_source(query, filters, PipelineConfig.INITIAL_PAPERS_PER_SOURCE, sources)
            
            if not found_papers:
                logger.warning("No papers found in initial search")
                results['pipeline_duration'] = time.time() - start_time
                return results
            
            # Filter for relevance and get top papers
            relevant_papers = self._filter_relevant_papers(found_papers, PipelineConfig.RELEVANCE_THRESHOLD)
            
            # Rank by similarity and get top 10
            top_papers = self._rank_papers_by_similarity(query, None, relevant_papers)
            results['top_papers'] = top_papers[:PipelineConfig.TOP_DISPLAY_RESULTS]
            results['all_papers'] = relevant_papers
            results['papers_found'] = len(relevant_papers)
            results['total_unique_papers'] = len(found_papers)
            
            # Store in session
            self.current_session_papers = relevant_papers
            self.all_found_papers.extend(relevant_papers)
            
            # Calculate duration
            results['pipeline_duration'] = time.time() - start_time
            
            logger.info(f"Initial search completed in {results['pipeline_duration']:.2f} seconds")
            logger.info(f"Found {len(found_papers)} total papers, {len(relevant_papers)} relevant papers")
            logger.info(f"Returning top {len(results['top_papers'])} papers")
            
            return results
            
        except Exception as e:
            logger.error(f"Initial search failed: {e}")
            results['error'] = str(e)
            results['pipeline_duration'] = time.time() - start_time
            return results

    def execute_secondary_search(self, selected_paper_indices: List[int], original_query: str, filters: Optional[SearchFilters] = None) -> Dict[str, Any]:
        """Execute secondary search using selected papers to augment keywords"""
        start_time = time.time()
        
        logger.info("=== SECONDARY SEARCH: Augmented Keywords ===")
        logger.info(f"Using {len(selected_paper_indices)} selected papers to augment search")
        
        # Get selected papers for keyword augmentation
        selected_papers = [self.current_session_papers[i] for i in selected_paper_indices if i < len(self.current_session_papers)]
        
        if not selected_papers:
            logger.warning("No valid selected papers for secondary search")
            return {'error': 'No valid selected papers'}
        
        # Generate augmented query
        augmented_query = self._generate_augmented_query(original_query, selected_papers)
        logger.info(f"Augmented query: {augmented_query}")
        
        # Search with fewer papers per source
        found_papers = self._search_papers_per_source(augmented_query, filters, PipelineConfig.SECONDARY_PAPERS_PER_SOURCE)
        
        if found_papers:
            # Filter for relevance
            relevant_papers = self._filter_relevant_papers(found_papers, PipelineConfig.RELEVANCE_THRESHOLD)
            
            # Add to session papers
            self.current_session_papers.extend(relevant_papers)
            self.all_found_papers.extend(relevant_papers)
            
            # Create combined list: selected papers from first round + new relevant papers
            combined_papers = selected_papers + relevant_papers
            
            # Re-rank combined papers by relevance to original query
            top_papers = self._rank_papers_by_similarity(original_query, None, combined_papers)
            
            # For secondary searches, show more papers to give users a comprehensive view
            display_limit = min(PipelineConfig.SECONDARY_DISPLAY_RESULTS, len(top_papers))
            top_papers = top_papers[:display_limit]
            
            logger.info(f"Secondary search found {len(relevant_papers)} new relevant papers")
            logger.info(f"Combined with {len(selected_papers)} selected papers from first round")
            logger.info(f"Total papers available: {len(combined_papers)}, showing top {display_limit}")
            
            return {
                'session_id': self.session_id,
                'new_papers_found': len(relevant_papers),
                'top_papers': top_papers,
                'total_session_papers': len(self.current_session_papers),
                'pipeline_duration': time.time() - start_time,
                'augmented_query': augmented_query,
                'selected_papers_count': len(selected_papers),
                'new_relevant_papers_count': len(relevant_papers),
                'total_available_papers': len(combined_papers),
                'papers_displayed': len(top_papers)
            }
        else:
            logger.warning("No papers found in secondary search")
            return {
                'session_id': self.session_id,
                'new_papers_found': 0,
                'message': 'No new papers found with augmented keywords'
            }
    
    def execute_phase_two_additional(self, query: str, filters: Optional[SearchFilters] = None) -> Dict[str, Any]:
        """Execute Phase 2 to get additional papers"""
        start_time = time.time()
        
        logger.info("=== PHASE 2: Extended Discovery ===")
        logger.info(f"Starting Phase 2 search for additional papers")
        
        results = {
            'phase_2_papers': 0,
            'additional_papers': [],
            'duration': 0,
            'error': None
        }
        
        try:
            # Execute Phase 2
            phase2_papers = self._execute_phase_two_fast(query, filters)
            results['phase_2_papers'] = len(phase2_papers)
            
            if phase2_papers:
                # Rank new papers
                ranked_papers = self._rank_papers_by_similarity(query, None, phase2_papers)
                results['additional_papers'] = ranked_papers
                
            results['duration'] = time.time() - start_time
            logger.info(f"Phase 2 completed in {results['duration']:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"Phase 2 execution failed: {e}")
            results['error'] = str(e)
            results['duration'] = time.time() - start_time
            return results

    def save_selected_papers(self, selected_indices: List[int]) -> Dict[str, Any]:
        """Save selected papers to vector database for literature review"""
        try:
            selected_papers = [self.current_session_papers[i] for i in selected_indices if i < len(self.current_session_papers)]
            
            if not selected_papers:
                return {'success': False, 'message': 'No valid papers selected'}
            
            # Convert papers to dictionary format for the embedding agent
            papers_dict = []
            for paper in selected_papers:
                # Handle both dict and object formats
                if isinstance(paper, dict):
                    paper_dict = {
                        'title': paper.get('title', ''),
                        'abstract': paper.get('abstract', ''),
                        'authors': paper.get('authors', []),
                        'journal': paper.get('journal', ''),
                        'publication_date': paper.get('publication_date', ''),
                        'citation_count': paper.get('citation_count', 0),
                        'doi': paper.get('doi', ''),
                        'url': paper.get('url', ''),
                        'source': paper.get('source', ''),
                        'paper_type': paper.get('paper_type', 'unknown'),
                        'relevance_score': paper.get('relevance_score', 0.0)
                    }
                else:
                    paper_dict = {
                        'title': getattr(paper, 'title', ''),
                        'abstract': getattr(paper, 'abstract', ''),
                        'authors': getattr(paper, 'authors', []),
                        'journal': getattr(paper, 'journal', ''),
                        'publication_date': getattr(paper, 'publication_date', ''),
                        'citation_count': getattr(paper, 'citation_count', 0),
                        'doi': getattr(paper, 'doi', ''),
                        'url': getattr(paper, 'url', ''),
                        'source': getattr(paper, 'source', ''),
                        'paper_type': getattr(paper, 'paper_type', 'unknown'),
                        'relevance_score': getattr(paper, 'relevance_score', 0.0)
                    }
                papers_dict.append(paper_dict)
            
            # Save papers to the embedding agent's vector database
            try:
                embedded_papers = self.embedding_agent.vector_db.add_papers_batch(
                    papers=papers_dict,
                    search_query="user_selected_papers",
                    session_id=self.session_id
                )
                saved_count = len(embedded_papers)
                logger.info(f"Saved {saved_count} papers to vector database")
                
                if saved_count > 0:
                    return {
                        'success': True,
                        'papers_saved': saved_count,
                        'message': f'Successfully saved {saved_count} papers to your collection for literature review'
                    }
                else:
                    return {'success': False, 'message': 'No papers were successfully added to the database'}
                    
            except Exception as e:
                logger.error(f"Failed to add papers to vector database: {e}")
                return {'success': False, 'message': f'Failed to save papers to database: {str(e)}'}
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to save selected papers: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'success': False, 'message': f'Failed to save papers: {str(e)}'}

    def _search_papers_per_source(self, query: str, filters: Optional[SearchFilters], papers_per_source: int, sources: Optional[List[str]] = None) -> List[Any]:
        """Search for specific number of papers from each source"""
        logger.info(f"Searching for {papers_per_source} papers per source")
        
        # Pass max_results directly to ensure exactly papers_per_source from each source
        max_results = papers_per_source * 4  # 4 sources (with 1 per source = 4 total)
        
        found_papers = self.literature_agent.search_papers(
            query=query,
            filters=filters or SearchFilters(),
            max_results=max_results,
            sources=sources  # Pass selected sources
        )
        return found_papers

    def _filter_relevant_papers(self, papers: List[Any], threshold: float) -> List[Any]:
        """Filter papers based on relevance threshold"""
        relevant_papers = []
        
        for paper in papers:
            # Get relevance score from paper
            if isinstance(paper, dict):
                relevance = paper.get('relevance_score', 0)
            else:
                relevance = getattr(paper, 'relevance_score', 0)
            
            if relevance >= threshold:
                relevant_papers.append(paper)
        
        logger.info(f"Filtered {len(relevant_papers)} papers above {threshold} relevance threshold from {len(papers)} total")
        return relevant_papers

    def _generate_augmented_query(self, original_query: str, selected_papers: List[Any]) -> str:
        """Generate augmented query using AI to extract keywords and restructure the search query"""
        try:
            import google.generativeai as genai
            
            # Extract titles and abstracts from selected papers
            paper_summaries = []
            
            for i, paper in enumerate(selected_papers[:5], 1):  # Limit to first 5 papers
                if isinstance(paper, dict):
                    title = paper.get('title', '')
                    abstract = paper.get('abstract', '')
                else:
                    title = getattr(paper, 'title', '')
                    abstract = getattr(paper, 'abstract', '')
                
                if title:
                    summary = f"Paper {i}: {title}"
                    if abstract:
                        summary += f"\nAbstract: {abstract[:300]}"
                    paper_summaries.append(summary)
            
            if not paper_summaries:
                logger.warning("No paper content available for augmentation")
                return original_query
            
            # Use Gemini to intelligently extract keywords and restructure query
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found, falling back to simple augmentation")
                return self._simple_keyword_extraction(original_query, selected_papers)
            
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""You are a research assistant helping to improve a literature search query.

Original Search Query: "{original_query}"

Based on these relevant papers that were found:

{chr(10).join(paper_summaries)}

Task: Generate an improved, more specific search query that:
1. Extracts the most important technical keywords and concepts from these papers
2. Identifies specific methodologies, techniques, or domains mentioned
3. Restructures the query to be more precise and academic
4. Focuses on deeper, more specialized aspects of the topic
5. Uses terminology that would appear in related research papers

Requirements:
- Keep the query concise (max 15 words)
- Use technical/academic language
- Include 3-5 key concepts or methodologies from the papers
- Make it suitable for academic database searches
- Do NOT use generic words like "paper", "study", "research", "analysis"

Return ONLY the improved search query, nothing else."""

            response = model.generate_content(prompt)
            augmented_query = response.text.strip()
            
            # Remove quotes if present
            augmented_query = augmented_query.strip('"').strip("'")
            
            # Fallback if response is too long or empty
            if not augmented_query or len(augmented_query.split()) > 20:
                logger.warning("AI-generated query invalid, using fallback")
                return self._simple_keyword_extraction(original_query, selected_papers)
            
            logger.info(f"AI-augmented query: {augmented_query}")
            return augmented_query
            
        except Exception as e:
            logger.error(f"Failed to generate AI-augmented query: {e}")
            return self._simple_keyword_extraction(original_query, selected_papers)
    
    def _simple_keyword_extraction(self, original_query: str, selected_papers: List[Any]) -> str:
        """Fallback: Simple keyword extraction when AI is unavailable"""
        try:
            titles = []
            abstracts = []
            
            for paper in selected_papers:
                if isinstance(paper, dict):
                    title = paper.get('title', '')
                    abstract = paper.get('abstract', '')
                else:
                    title = getattr(paper, 'title', '')
                    abstract = getattr(paper, 'abstract', '')
                
                if title:
                    titles.append(title)
                if abstract:
                    abstracts.append(abstract[:200])
            
            # Extract key terms
            all_text = ' '.join(titles + abstracts).lower()
            
            import re
            words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text)
            
            # Filter out common words
            stop_words = {'abstract', 'paper', 'study', 'research', 'using', 'method', 
                         'approach', 'based', 'results', 'data', 'model', 'analysis'}
            
            word_freq = {}
            for word in words:
                if word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top frequent terms
            top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            key_terms = [term for term, freq in top_terms if freq > 1]
            
            if key_terms:
                augmented_query = f"{original_query} {' '.join(key_terms[:3])}"
            else:
                augmented_query = original_query
            
            logger.info(f"Simple keyword augmentation: {key_terms[:3]}")
            return augmented_query
            
        except Exception as e:
            logger.error(f"Simple keyword extraction failed: {e}")
            return original_query
    
    def _execute_phase_one_fast(self, query: str, filters: Optional[SearchFilters]) -> List[EmbeddedPaper]:
        """Execute Phase 1 with performance optimizations"""
        try:
            logger.info(f"Searching for {PipelineConfig.BATCH_SIZE} papers...")
            filters_dict = filters.model_dump() if filters else None
            
            # Use smaller batch for faster results
            try:
                logger.debug("About to call literature_agent.search_papers")
                papers_data = self.literature_agent.search_papers(
                    query=query,
                    max_results=PipelineConfig.BATCH_SIZE,
                    filters=filters_dict
                )
                logger.debug(f"Got {len(papers_data) if papers_data else 0} papers from literature_agent")
            except Exception as e:
                logger.error(f"Error in literature_agent.search_papers: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return []
            
            if not papers_data:
                logger.warning("No papers found in Phase 1")
                return []
            
            logger.info(f"Phase 1 found {len(papers_data)} papers")
            
            # Convert to dictionary format with error handling
            papers_dict = []
            for i, paper in enumerate(papers_data):
                try:
                    logger.debug(f"Converting paper {i+1}/{len(papers_data)}: {getattr(paper, 'title', 'No title')[:50]}")
                    paper_dict = self._paper_to_dict_safe(paper)
                    if paper_dict:
                        papers_dict.append(paper_dict)
                        logger.debug(f"Successfully converted paper {i+1}")
                    else:
                        logger.warning(f"Paper {i+1} conversion returned None")
                except Exception as e:
                    logger.warning(f"Failed to convert paper {i+1} to dict: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
            
            if not papers_dict:
                logger.warning("No valid papers after conversion")
                return []
            
            # Process with embedding agent
            logger.info("Converting papers to embeddings...")
            try:
                embedded_papers = self.embedding_agent.process_paper_batch(
                    papers_dict, query, f"{self.session_id}_phase1"
                )
                logger.debug(f"Embedding processing completed, got {len(embedded_papers)} embedded papers")
            except Exception as e:
                logger.error(f"Error in embedding processing: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return []
            
            # Update stored identifiers
            try:
                logger.debug("About to update stored identifiers")
                self._update_stored_identifiers(embedded_papers)
                logger.debug("Stored identifiers updated successfully")
            except Exception as e:
                logger.error(f"Error updating stored identifiers: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                # Continue anyway
            
            logger.info(f"Phase 1 completed: {len(embedded_papers)} papers processed")
            return embedded_papers
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def _execute_phase_two_fast(self, query: str, filters: Optional[SearchFilters]) -> List[EmbeddedPaper]:
        """Execute Phase 2 with duplicate prevention and performance optimizations"""
        try:
            logger.info(f"Searching for additional {PipelineConfig.BATCH_SIZE} papers...")
            filters_dict = filters.model_dump() if filters else None
            
            papers_data = self.literature_agent.search_papers(
                query=query,
                max_results=PipelineConfig.BATCH_SIZE * 2,  # Get more to account for duplicates
                filters=filters_dict
            )
            
            if not papers_data:
                logger.warning("No papers found in Phase 2")
                return []
            
            logger.info(f"Phase 2 found {len(papers_data)} papers before deduplication")
            
            # Filter duplicates
            unique_papers = self._filter_duplicates(papers_data)
            
            if not unique_papers:
                logger.warning("Phase 2: All papers were duplicates")
                return []
            
            # Limit to batch size
            unique_papers = unique_papers[:PipelineConfig.BATCH_SIZE]
            logger.info(f"Phase 2: {len(unique_papers)} unique papers after deduplication")
            
            # Convert to dictionary format with error handling
            papers_dict = []
            for paper in unique_papers:
                try:
                    paper_dict = self._paper_to_dict_safe(paper)
                    if paper_dict:
                        papers_dict.append(paper_dict)
                except Exception as e:
                    logger.warning(f"Failed to convert paper to dict: {e}")
                    continue
            
            if not papers_dict:
                logger.warning("No valid papers after conversion in Phase 2")
                return []
            
            # Process with embedding agent
            logger.info("Converting Phase 2 papers to embeddings...")
            embedded_papers = self.embedding_agent.process_paper_batch(
                papers_dict, query, f"{self.session_id}_phase2"
            )
            
            logger.info(f"Phase 2 completed: {len(embedded_papers)} papers processed")
            return embedded_papers
            
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            return []
    
    def safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def safe_str(self, value: Any, default: str = '') -> str:
        """Safely convert value to str"""
        if value is None:
            return default
        try:
            return str(value)
        except (ValueError, TypeError):
            return default

    def _paper_to_dict_safe(self, paper) -> Optional[Dict[str, Any]]:
        """Safely convert Paper object to dictionary with None handling"""
        try:
            # Helper function to safely convert numeric values
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
            
            def safe_str(value, default=''):
                if value is None:
                    return default
                return str(value)
            
            def safe_list(value, default=None):
                if default is None:
                    default = []
                if value is None:
                    return default
                if isinstance(value, list):
                    return value
                return [value] if value else default
            
            return {
                'paper_id': safe_str(getattr(paper, 'paper_id', '')),
                'title': safe_str(getattr(paper, 'title', '')),
                'authors': safe_list(getattr(paper, 'authors', [])),
                'abstract': safe_str(getattr(paper, 'abstract', '')),
                'journal': safe_str(getattr(paper, 'journal', '')),
                'publication_date': safe_str(getattr(paper, 'publication_date', '')),
                'citation_count': safe_int(getattr(paper, 'citation_count', 0)),
                'relevance_score': safe_float(getattr(paper, 'relevance_score', 0.0)),
                'confidence_score': safe_float(getattr(paper, 'confidence_score', 0.0)),
                'url': safe_str(getattr(paper, 'url', '')),
                'doi': safe_str(getattr(paper, 'doi', '')),
                'keywords': safe_list(getattr(paper, 'keywords', [])),
                'categories': safe_list(getattr(paper, 'categories', [])),
                'source': safe_str(getattr(paper, 'source', '')),
                'gemini_reasoning': safe_str(getattr(paper, 'gemini_reasoning', '')),
                'key_matches': safe_list(getattr(paper, 'key_matches', [])),
                'concerns': safe_list(getattr(paper, 'concerns', [])),
                'paper_type': safe_str(getattr(paper, 'paper_type', 'unknown'))
            }
        except Exception as e:
            logger.warning(f"Error converting paper to dict: {e}")
            return None
    
    def _filter_duplicates(self, papers) -> List:
        """Filter out duplicate papers based on DOI and title"""
        unique_papers = []
        
        for paper in papers:
            is_duplicate = False
            
            # Check DOI duplicates
            if hasattr(paper, 'doi') and paper.doi:
                if paper.doi in self.stored_dois:
                    is_duplicate = True
                else:
                    self.stored_dois.add(paper.doi)
            
            # Check title duplicates for papers without DOI
            if not is_duplicate and hasattr(paper, 'title') and paper.title:
                title_lower = paper.title.lower().strip()
                if title_lower in self.stored_titles:
                    is_duplicate = True
                else:
                    self.stored_titles.add(title_lower)
            
            if not is_duplicate:
                unique_papers.append(paper)
        
        return unique_papers
    
    def _update_stored_identifiers(self, papers: List[EmbeddedPaper]):
        """Update stored DOIs and titles"""
        for paper in papers:
            if hasattr(paper, 'doi') and paper.doi:
                self.stored_dois.add(paper.doi)
            if hasattr(paper, 'title') and paper.title:
                self.stored_titles.add(paper.title.lower().strip())
    
    def _rank_papers_by_similarity(self, query: str, paper_type_filter: Optional[str], 
                                 papers: List[EmbeddedPaper] = None) -> List[Dict[str, Any]]:
        """Rank papers by similarity score"""
        try:
            if papers:
                # Convert EmbeddedPaper objects to dictionary format with safe handling
                ranked_papers = []
                for paper in papers:
                    try:
                        # Check if already a dict
                        if isinstance(paper, dict):
                            # Already a dict, just ensure it has required fields
                            paper_dict = {
                                'paper_id': paper.get('paper_id', ''),
                                'title': paper.get('title', ''),
                                'authors': paper.get('authors', []),
                                'abstract': paper.get('abstract', ''),
                                'journal': paper.get('journal', 'Unknown'),
                                'publication_date': paper.get('publication_date', 'Unknown'),
                                'citation_count': paper.get('citation_count', 0),
                                'relevance_score': paper.get('relevance_score', 0.0),
                                'confidence_score': paper.get('confidence_score', 0.0),
                                'url': paper.get('url', ''),
                                'doi': paper.get('doi', ''),
                                'keywords': paper.get('keywords', []),
                                'categories': paper.get('categories', []),
                                'source': paper.get('source', 'unknown'),
                                'gemini_reasoning': paper.get('gemini_reasoning', ''),
                                'key_matches': paper.get('key_matches', []),
                                'concerns': paper.get('concerns', []),
                                'similarity_score': paper.get('similarity_score', 0.0),
                                'paper_type': paper.get('paper_type', 'unknown')
                            }
                        else:
                            # It's an object, use getattr
                            paper_dict = {
                                'paper_id': getattr(paper, 'paper_id', ''),
                                'title': getattr(paper, 'title', ''),
                                'authors': getattr(paper, 'authors', []),
                                'abstract': getattr(paper, 'abstract', ''),
                                'journal': getattr(paper, 'journal', 'Unknown'),
                                'publication_date': getattr(paper, 'publication_date', 'Unknown'),
                                'citation_count': self.safe_int(getattr(paper, 'citation_count', 0)),
                                'relevance_score': self.safe_float(getattr(paper, 'relevance_score', 0.0)),
                                'confidence_score': self.safe_float(getattr(paper, 'confidence_score', 0.0)),
                                'url': getattr(paper, 'url', ''),
                                'doi': getattr(paper, 'doi', ''),
                                'keywords': getattr(paper, 'keywords', []),
                                'categories': getattr(paper, 'categories', []),
                                'source': getattr(paper, 'source', 'unknown'),
                                'gemini_reasoning': getattr(paper, 'gemini_reasoning', ''),
                                'key_matches': getattr(paper, 'key_matches', []),
                                'concerns': getattr(paper, 'concerns', []),
                                'similarity_score': self.safe_float(getattr(paper, 'similarity_score', 0.0)),
                                'paper_type': getattr(paper, 'paper_type', 'unknown')
                            }
                        ranked_papers.append(paper_dict)
                    except Exception as e:
                        logger.warning(f"Error converting paper for ranking: {e}")
                        continue
                
                # Sort by relevance score + similarity score, with citation count as tiebreaker (safe)
                ranked_papers.sort(key=lambda x: (
                    self.safe_float(x.get('relevance_score', 0.0)) + 
                    self.safe_float(x.get('similarity_score', 0.0)),
                    self.safe_int(x.get('citation_count', 0))  # Higher citations for same relevance
                ), reverse=True)
                
            else:
                # Use papers from database
                ranked_papers = self.embedding_agent.search_similar_papers(
                    query=query,
                    k=PipelineConfig.TOP_RESULTS * 2,
                    paper_type_filter=paper_type_filter
                )
                # Convert to dict format
                ranked_papers = [self._paper_to_dict_safe(paper) for paper in ranked_papers]
                ranked_papers = [p for p in ranked_papers if p is not None]
            
            logger.info(f"Ranked {len(ranked_papers)} papers by similarity")
            return ranked_papers
            
        except Exception as e:
            logger.error(f"Ranking failed: {e}")
            return []
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'session_id': self.session_id,
            'stored_dois': len(self.stored_dois),
            'stored_titles': len(self.stored_titles),
            'embedding_stats': self.embedding_agent.get_statistics() if self.embedding_agent else {}
        }

# Backward compatibility
ResearchPipeline = EnhancedResearchPipeline
