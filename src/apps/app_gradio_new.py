"""
Modern Research Discovery Hub - Enhanced Gradio Frontend
Built for Google Gemini 2.5 Flash with FAISS Vector Database

Beautiful, intuitive interface for iterative research discovery using Gradio
Based on the excellent Streamlit interface with improved paper selection
"""
import gradio as gr
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import logging
import os
import re

# Import API Key Manager first
from src.utils.api_key_manager import APIKeyManager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Import components
from src.agents.literature_agent import SearchFilters
from src.agents.embedding_agent import EmbeddingAgent
from src.agents.control_agent import EnhancedResearchPipeline
from src.agents.literature_review_agents import LiteratureReviewCoordinator
from src.agents.pdf_parser import PDFPaperParser
from src.agents.research_gap_agent import ResearchGapAnalyzer
from src.agents.feasibility_agent import FeasibilityAssessmentAgent
from src.agents.latex_assistant import LaTeXWritingAssistant

class EnhancedGradioResearchApp:
    """Enhanced Gradio application for research discovery with individual paper selection"""
    
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.api_keys_configured = self.api_key_manager.has_all_required_keys()
        self.pipeline = None
        self.pipeline_results = None
        self.search_iterations = 0
        self.augmented_queries = []
        self.original_query = ""
        self.literature_review = None
        self.generating_review = False
        self.current_papers = []  # Store current papers for selection
        self.pdf_parser = PDFPaperParser()  # Initialize PDF parser
        self.uploaded_papers = []  # Store uploaded papers
        self.gap_analyzer = None  # Will be initialized when needed
        self.feasibility_agent = None  # Will be initialized when needed
        self.latex_assistant = None  # Will be initialized when needed
    
    # ========== API Key Management ==========
    
    def save_api_keys(
        self,
        gemini_key: str,
        serpapi_key: str,
        openai_key: str = ""
    ) -> Tuple[str, bool]:
        """
        Save user-provided API keys
        
        Returns:
            Tuple of (message: str, success: bool)
        """
        try:
            keys_dict = {
                'GEMINI_API_KEY': gemini_key,
                'SERPAPI_KEY': serpapi_key,
            }
            
            if openai_key and openai_key.strip():
                keys_dict['OPENAI_API_KEY'] = openai_key
            
            success, message = self.api_key_manager.save_keys(keys_dict)
            
            if success:
                self.api_keys_configured = True
                return f"✅ {message}", True
            else:
                return f"❌ {message}", False
                
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            return f"❌ Error saving API keys: {str(e)}", False
    
    def check_api_keys_status(self) -> str:
        """Check status of API keys"""
        if self.api_keys_configured:
            return "✅ API keys are configured. You can proceed to the Research Assistant."
        else:
            return "⚠️ API keys not configured. Please enter your API keys below."
    
    def get_api_key_instructions(self) -> str:
        """Get instructions for obtaining API keys"""
        instructions = "# 🔑 API Key Setup Instructions\n\n"
        instructions += "## Required API Keys\n\n"
        
        for key_name, key_info in self.api_key_manager.REQUIRED_KEYS.items():
            instructions += f"### {key_info['name']}\n"
            instructions += f"**Purpose:** {key_info['description']}\n\n"
            instructions += f"**Get your key:** [{key_info['get_url']}]({key_info['get_url']})\n\n"
            if key_info['validation_prefix']:
                instructions += f"**Format:** Should start with `{key_info['validation_prefix']}`\n\n"
            instructions += "---\n\n"
        
        instructions += "## Optional API Keys\n\n"
        for key_name, key_info in self.api_key_manager.OPTIONAL_KEYS.items():
            instructions += f"### {key_info['name']}\n"
            instructions += f"**Purpose:** {key_info['description']}\n\n"
            instructions += f"**Get your key:** [{key_info['get_url']}]({key_info['get_url']})\n\n"
            if key_info['validation_prefix']:
                instructions += f"**Format:** Should start with `{key_info['validation_prefix']}`\n\n"
            instructions += "---\n\n"
        
        return instructions
        
    def clean_database(self):
        """Clean out the vector database to start fresh"""
        try:
            import os
            
            # Specific FAISS database files used by the app
            db_files = [
                os.path.join(os.getcwd(), "data", "faiss_paper_embeddings.index"),
                os.path.join(os.getcwd(), "data", "faiss_paper_embeddings_metadata.pkl")
            ]
            
            files_removed = 0
            for file_path in db_files:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except Exception as e:
                        print(f"⚠️ Could not remove {file_path}: {e}")
            
            # Clear all paper lists
            self.uploaded_papers = []
            self.current_papers = []
            
            return f"🧹 Cleaned database - removed {files_removed} files"
        except Exception as e:
            return f"⚠️ Database cleanup warning: {str(e)}"
    
    def initialize_pipeline(self):
        """Initialize the research pipeline with fresh database"""
        try:
            # Clean database first
            cleanup_msg = self.clean_database()
            print(cleanup_msg)
            
            # Initialize fresh pipeline
            self.pipeline = EnhancedResearchPipeline()
            return "✅ Pipeline initialized successfully with clean database!"
        except Exception as e:
            return f"❌ Failed to initialize pipeline: {str(e)}"
    
    def process_uploaded_pdfs(self, files, progress=gr.Progress()) -> Tuple[str, None]:
        """Process uploaded PDF files and add them to the system"""
        if not files or len(files) == 0:
            return "⚠️ No files uploaded", None
        
        try:
            progress(0.1, desc="Initializing pipeline...")
            
            # Initialize pipeline if needed
            if not self.pipeline:
                init_result = self.initialize_pipeline()
                if "❌" in init_result:
                    return init_result, None
            
            progress(0.2, desc=f"Parsing {len(files)} PDF file(s)...")
            
            # Extract file paths from file objects
            pdf_paths = []
            for file in files:
                # Handle both string paths and file objects
                if isinstance(file, str):
                    pdf_paths.append(file)
                elif hasattr(file, 'name'):
                    pdf_paths.append(file.name)
                else:
                    # Try to get path attribute
                    pdf_paths.append(str(file))
            
            # Parse all uploaded PDFs
            parsed_papers = self.pdf_parser.parse_multiple_pdfs(pdf_paths)
            
            if not parsed_papers:
                return "❌ Failed to parse any PDF files. Please ensure they are valid research papers.", None
            
            progress(0.5, desc=f"Adding {len(parsed_papers)} papers to database...")
            
            # Add parsed papers to vector database
            embedded_papers = self.pipeline.embedding_agent.vector_db.add_papers_batch(
                papers=parsed_papers,
                search_query="user_uploaded_papers",
                session_id=f"{self.pipeline.session_id}_uploads"
            )
            
            # Store uploaded papers
            self.uploaded_papers.extend(parsed_papers)
            
            # Add to current papers for display
            self.current_papers.extend(parsed_papers)
            
            progress(1.0, desc="Upload complete!")
            
            # Create status message
            status_msg = f"✅ **Successfully uploaded {len(parsed_papers)} paper(s)!**\n\n"
            
            for i, paper in enumerate(parsed_papers, 1):
                title = paper.get('title', 'Unknown')[:80]
                authors = paper.get('authors', [])
                authors_str = ', '.join(authors[:2]) if authors else 'Unknown'
                status_msg += f"{i}. **{title}**\n   📝 Authors: {authors_str}\n\n"
            
            status_msg += f"\n💾 Papers saved to vector database and ready for search/review generation!"
            
            return status_msg, None
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Upload error details:\n{error_details}")
            return f"❌ Upload failed: {str(e)}", None
    
    def execute_search(self, query: str, paper_type: str, year_start: int, year_end: int, 
                      min_citations: int, search_sources: List[str], progress=gr.Progress()):
        """Execute the initial search and return results with individual paper selection"""
        if not query.strip():
            return self._create_empty_results("⚠️ Please enter a research query")
        
        # Initialize pipeline if needed
        if not self.pipeline:
            progress(0.1, desc="Initializing pipeline...")
            init_result = self.initialize_pipeline()
            if "❌" in init_result:
                return self._create_empty_results(init_result)
        
        # Create filters
        filters = SearchFilters(
            year_start=year_start,
            year_end=year_end,
            min_citations=min_citations,
            paper_type_filter=paper_type if paper_type != "All Types" else None
        )
        
        # Map UI names to database source names
        source_mapping = {
            "Google Scholar (SerpAPI)": "google_scholar_serpapi",
            "arXiv": "arxiv",
            "CrossRef": "crossref",
            "OpenAlex": "openalex"
        }
        
        # Convert selected sources to database names
        enabled_sources = [source_mapping[src] for src in search_sources if src in source_mapping]
        
        try:
            # Initialize results dictionary
            results = {'top_papers': [], 'papers_found': 0, 'pipeline_duration': 0}
            
            # Execute search only if sources are selected
            search_papers = []
            papers_found = 0
            duration = 0
            
            if enabled_sources:
                progress(0.2, desc=f"Searching {len(enabled_sources)} database(s)...")
                
                # Execute search with selected sources
                results = self.pipeline.execute_initial_search(
                    query=query,
                    filters=filters,
                    sources=enabled_sources  # Pass selected sources
                )
                
                search_papers = results.get('top_papers', [])
                papers_found = results.get('papers_found', 0)
                duration = results.get('pipeline_duration', 0)
                self.pipeline_results = results
            else:
                # No database sources selected
                progress(0.3, desc="Skipping database search (no sources selected)...")
                self.pipeline_results = results
            
            progress(0.7, desc="Checking uploaded papers for relevance...")
            
            # Also search FAISS for uploaded papers that match the query
            uploaded_matches = []
            if self.uploaded_papers:
                try:
                    # Search FAISS for papers similar to the query
                    similar_papers = self.pipeline.embedding_agent.search_papers(
                        query=query, 
                        k=10,  # Get top 10 similar papers
                        paper_type_filter=None
                    )
                    
                    # Filter for uploaded papers only (source = 'user_upload')
                    for paper in similar_papers:
                        if hasattr(paper, 'source') and paper.source == 'user_upload':
                            # Convert to dict format
                            paper_dict = {
                                'paper_id': paper.paper_id,
                                'title': paper.title,
                                'authors': paper.authors,
                                'abstract': paper.abstract,
                                'journal': paper.journal,
                                'publication_date': paper.publication_date,
                                'citation_count': paper.citation_count,
                                'relevance_score': paper.relevance_score,
                                'confidence_score': paper.confidence_score,
                                'url': paper.url,
                                'doi': paper.doi,
                                'keywords': paper.keywords,
                                'categories': paper.categories,
                                'source': paper.source,
                                'paper_type': paper.paper_type,
                                'similarity_score': paper.similarity_score,
                                'gemini_reasoning': getattr(paper, 'gemini_reasoning', ''),
                                'key_matches': getattr(paper, 'key_matches', []),
                                'concerns': getattr(paper, 'concerns', [])
                            }
                            uploaded_matches.append(paper_dict)
                except Exception as e:
                    print(f"⚠️ Could not search uploaded papers: {e}")
            
            progress(1.0, desc="Search completed!")
            
            # Combine search results with uploaded matches
            if enabled_sources and self.pipeline_results:
                search_papers = self.pipeline_results.get('top_papers', [])
            else:
                search_papers = []
            
            # Merge uploaded matches with search results (avoid duplicates by paper_id)
            seen_ids = {p.get('paper_id') if isinstance(p, dict) else getattr(p, 'paper_id', None) 
                       for p in search_papers}
            
            combined_papers = list(search_papers)  # Start with search results
            for uploaded in uploaded_matches:
                if uploaded['paper_id'] not in seen_ids:
                    combined_papers.append(uploaded)
            
            # Sort by relevance + similarity score
            combined_papers.sort(
                key=lambda p: (
                    (p.get('relevance_score', 0) if isinstance(p, dict) else getattr(p, 'relevance_score', 0)) +
                    (p.get('similarity_score', 0) if isinstance(p, dict) else getattr(p, 'similarity_score', 0))
                ),
                reverse=True
            )
            
            # Limit to top 20 papers
            combined_papers = combined_papers[:20]
            
            # Store results
            self.pipeline_results = results
            self.original_query = query
            self.search_iterations = 1
            self.augmented_queries = []
            
            # Store combined papers for selection
            self.current_papers = combined_papers
            
            # IMPORTANT: Store papers in pipeline for augmented search
            # This ensures uploaded papers are available for secondary search
            if combined_papers:
                self.pipeline.current_session_papers = combined_papers
                # Only extend all_found_papers if they're not already there
                for paper in combined_papers:
                    paper_id = paper.get('paper_id') if isinstance(paper, dict) else getattr(paper, 'paper_id', None)
                    existing_ids = [
                        p.get('paper_id') if isinstance(p, dict) else getattr(p, 'paper_id', None)
                        for p in self.pipeline.all_found_papers
                    ]
                    if paper_id not in existing_ids:
                        self.pipeline.all_found_papers.append(paper)
            
            # Format results for display
            papers_found = results.get('papers_found', 0) if enabled_sources else 0
            uploaded_count = len(uploaded_matches)
            top_papers = len(combined_papers)
            duration = results.get('pipeline_duration', 0) if enabled_sources else 0
            
            status_msg = f"🎉 **Search Complete!**\n\n"
            
            # Show which sources were searched
            if enabled_sources:
                source_names = [src.replace('_', ' ').title() for src in enabled_sources]
                status_msg += f"🌐 **Sources:** {', '.join(source_names)}\n"
                status_msg += f"📊 **Found:** {papers_found} relevant papers from databases in {duration:.1f}s\n"
            else:
                status_msg += f"🌐 **Sources:** None (searching only uploaded papers)\n"
                
            if uploaded_count > 0:
                status_msg += f"📤 **Uploaded Papers:** {uploaded_count} matching papers found in your uploads\n"
            
            status_msg += f"🏆 **Showing:** Top {top_papers} most relevant papers"
            
            if enabled_sources and uploaded_count > 0:
                status_msg += " (database + uploads)\n"
            elif enabled_sources:
                status_msg += " (from databases)\n"
            elif uploaded_count > 0:
                status_msg += " (from uploads)\n"
            else:
                status_msg += "\n"
                
            status_msg += f"🔍 **Query:** {query}\n\n"
            status_msg += f"📋 **Next Steps:** Review papers below and select interesting ones for further actions"
            
            # Create papers display and selection components
            papers_display = self.format_papers_for_display(combined_papers)
            
            # Create individual paper selection checkboxes
            paper_checkboxes = self.create_paper_checkboxes(combined_papers)
            
            return (
                status_msg,
                papers_display,
                *paper_checkboxes,  # Unpack the checkboxes
                gr.update(visible=True),  # Make selection interface visible
                gr.update(visible=True),  # Make action buttons container visible
                gr.update(visible=True),  # Make augment button visible
                gr.update(visible=True),  # Make save button visible
                gr.update(visible=True),  # Make save all button visible
                ""  # Clear any previous save status
            )
            
        except Exception as e:
            error_msg = f"❌ Search failed: {str(e)}"
            return self._create_empty_results(error_msg)
    
    def execute_secondary_search(self, *selected_papers, progress=gr.Progress()):
        """Execute secondary search using selected papers"""
        if not self.pipeline or not self.pipeline_results:
            return self._create_results_update("❌ No previous search results available", "")
        
        # Get selected paper indices
        selected_indices = []
        for i, is_selected in enumerate(selected_papers):
            if is_selected and i < len(self.current_papers):
                selected_indices.append(i)
        
        if not selected_indices:
            return self._create_results_update("⚠️ Please select at least one paper for augmented search", "")
        
        try:
            progress(0.1, desc="Executing augmented search...")
            
            # IMPORTANT: Ensure pipeline has access to current papers
            # This is especially important when using only uploaded papers (no database search)
            if not self.pipeline.current_session_papers and self.current_papers:
                # Pipeline doesn't have papers stored, so store them now
                self.pipeline.current_session_papers = self.current_papers
                self.pipeline.all_found_papers.extend(self.current_papers)
            
            results = self.pipeline.execute_secondary_search(
                selected_paper_indices=selected_indices,
                original_query=self.original_query
            )
            
            progress(1.0, desc="Augmented search completed!")
            
            if results.get('new_papers_found', 0) > 0:
                self.search_iterations += 1
                self.augmented_queries.append(results.get('augmented_query', ''))
                
                # Update the results
                if 'top_papers' in results:
                    self.pipeline_results['top_papers'] = results['top_papers']
                    self.pipeline_results['new_papers_found'] = results['new_papers_found']
                    self.current_papers = results['top_papers']
                
                selected_count = results.get('selected_papers_count', 0)
                new_count = results.get('new_relevant_papers_count', 0)
                total_available = results.get('total_available_papers', 0)
                papers_displayed = results.get('papers_displayed', 0)
                
                status_msg = f"🎉 **Augmented Search Completed!**\n\n"
                status_msg += f"🔄 **Iteration:** {self.search_iterations}\n"
                status_msg += f"📊 **Results:** {selected_count} selected + {new_count} new = {total_available} total\n"
                status_msg += f"🖥️ **Display:** Showing top {papers_displayed} papers\n"
                status_msg += f"🔍 **Augmented Query:** {results.get('augmented_query', '')}\n\n"
                status_msg += f"📋 **Next Steps:** Review updated results and select more papers if needed"
                
                papers_display = self.format_papers_for_display(results['top_papers'])
                
                # Create new paper selection checkboxes
                paper_checkboxes = self.create_paper_checkboxes(results.get('top_papers', []))
                
                return (
                    status_msg,
                    papers_display,
                    *paper_checkboxes,  # Unpack the new checkboxes
                    ""  # Clear save status
                )
            else:
                return self._create_results_update(
                    "⚠️ No new papers found with augmented keywords. Try selecting different papers.", 
                    ""
                )
                
        except Exception as e:
            return self._create_results_update(f"❌ Secondary search failed: {str(e)}", "")
    
    def save_papers(self, *selected_papers):
        """Save selected papers to database"""
        if not self.pipeline or not self.pipeline_results:
            return "❌ No papers available or pipeline not available"
        
        # Get selected paper indices
        selected_indices = []
        for i, is_selected in enumerate(selected_papers):
            if is_selected and i < len(self.current_papers):
                selected_indices.append(i)
        
        if not selected_indices:
            return "❌ Please select at least one paper to save"
        
        try:
            # Save papers
            result = self.pipeline.save_selected_papers(selected_indices)
            
            if result.get('success'):
                saved_count = len(selected_indices)
                return f"✅ **Successfully saved {saved_count} papers!** {result.get('message', '')}"
            else:
                return f"❌ **Failed to save papers:** {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ **Error saving papers:** {str(e)}"
    
    def save_all_papers(self):
        """Save all papers from current search results"""
        if not self.pipeline or not self.pipeline_results:
            return "❌ No papers available or pipeline not available"
        
        try:
            # Get all paper indices
            if not self.current_papers:
                return "❌ No papers found to save"
            
            selected_indices = list(range(len(self.current_papers)))
            
            # Save papers
            result = self.pipeline.save_selected_papers(selected_indices)
            
            if result.get('success'):
                saved_count = len(selected_indices)
                return f"✅ **Successfully saved all {saved_count} papers!** {result.get('message', '')}"
            else:
                return f"❌ **Failed to save papers:** {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ **Error saving papers:** {str(e)}"
    
    def select_all_papers(self, select_all_state):
        """Toggle all paper selections"""
        num_papers = len(self.current_papers)
        if num_papers == 0:
            return [gr.update() for _ in range(20)]  # Return unchanged updates
        
        # Return updates for all possible checkboxes (up to 20)
        updates = []
        for i in range(20):
            if i < num_papers:
                updates.append(gr.update(value=select_all_state))
            else:
                updates.append(gr.update())  # No change for unused checkboxes
        
        return updates
    
    def generate_literature_review(self, topic: str, max_papers: int, progress=gr.Progress()):
        """Generate literature review from saved papers"""
        if not topic.strip():
            return "⚠️ Please enter a research topic"
        
        if not self.pipeline:
            return "❌ Pipeline not available"
        
        try:
            progress(0.1, desc="Initializing literature review generation...")
            self.generating_review = True
            
            # Use the same vector database where papers were saved
            vector_db = self.pipeline.embedding_agent.vector_db
            coordinator = LiteratureReviewCoordinator(vector_db=vector_db)
            
            progress(0.3, desc="Analyzing saved papers...")
            
            # Generate literature review using the correct method name
            review = coordinator.generate_review(
                topic=topic,
                max_papers=max_papers
            )
            
            progress(1.0, desc="Literature review generated!")
            
            self.literature_review = review
            self.generating_review = False
            
            return review
            
        except Exception as e:
            self.generating_review = False
            return f"❌ Failed to generate literature review: {str(e)}"
    
    def analyze_research_gaps(self, progress=gr.Progress()):
        """Analyze current papers to identify research gaps and suggest topics"""
        if not self.current_papers or len(self.current_papers) == 0:
            return "⚠️ No papers available for gap analysis. Please conduct a search first."
        
        try:
            progress(0.1, desc="Initializing gap analysis...")
            
            # Initialize gap analyzer if not already done
            if not self.gap_analyzer:
                self.gap_analyzer = ResearchGapAnalyzer()
            
            progress(0.3, desc=f"Analyzing {len(self.current_papers)} papers...")
            
            # Perform gap analysis
            result = self.gap_analyzer.analyze_research_gaps(
                papers=self.current_papers,
                original_query=self.original_query
            )
            
            progress(0.9, desc="Formatting results...")
            
            if not result['success']:
                return f"❌ Gap analysis failed: {result.get('message', 'Unknown error')}"
            
            # Format the results nicely
            output = self._format_gap_analysis(result)
            
            progress(1.0, desc="Gap analysis complete!")
            
            return output
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Gap analysis error:\n{error_details}")
            return f"❌ Gap analysis error: {str(e)}"
    
    def _format_gap_analysis(self, result: Dict[str, Any]) -> str:
        """Format gap analysis results for display"""
        output = f"""# 🔬 Research Gap Analysis

**Analysis Date:** {result.get('timestamp', 'Unknown')}  
**Papers Analyzed:** {result.get('papers_analyzed', 0)}  
**Research Area:** {result.get('original_query', 'General')}

---

"""
        
        # Add raw analysis (which contains the structured markdown from AI)
        if result.get('raw_analysis'):
            output += result['raw_analysis']
            output += "\n\n---\n\n"
        
        # Add structured summaries
        gaps = result.get('identified_gaps', [])
        topics = result.get('research_topics', [])
        trends = result.get('emerging_trends', [])
        methods = result.get('methodological_opportunities', [])
        interdisciplinary = result.get('interdisciplinary_connections', [])
        
        if gaps:
            output += f"\n## 📊 Quick Summary\n\n"
            output += f"- **{len(gaps)}** research gaps identified\n"
            output += f"- **{len(topics)}** promising research topics suggested\n"
            output += f"- **{len(trends)}** emerging trends detected\n"
            output += f"- **{len(methods)}** methodological opportunities\n"
            output += f"- **{len(interdisciplinary)}** interdisciplinary connections\n"
        
        output += "\n\n---\n\n"
        output += "*💡 Tip: Use these insights to guide your next research direction or refine your literature search!*"
        
        return output
    
    def assess_feasibility(
        self,
        research_topic: str,
        research_description: str,
        timeline_months: int,
        # Computational resources
        has_gpu: bool,
        has_cloud: bool,
        cpu_cores: int,
        ram_gb: int,
        # Funding
        budget_usd: int,
        has_grant: bool,
        # Time
        hours_per_week: int,
        # Personnel
        team_size: int,
        has_advisor: bool,
        has_collaborators: bool,
        # Data
        has_data_access: bool,
        data_type: str,
        # Equipment
        has_lab: bool,
        # Expertise
        skills_list: str,
        experience_years: int,
        has_mentorship: bool,
        progress=gr.Progress()
    ):
        """Assess research feasibility based on user's resource inventory"""
        
        # Validate inputs
        if not research_topic or not research_topic.strip():
            return "⚠️ Please provide a research topic."
        
        if not research_description or not research_description.strip():
            return "⚠️ Please provide a research description."
        
        try:
            progress(0.1, desc="Preparing resource inventory...")
            
            # Parse skills list
            skills = [s.strip() for s in skills_list.split(',') if s.strip()]
            
            # Build resource inventory
            resources = {
                'computational': {
                    'has_gpu': has_gpu,
                    'has_cloud_access': has_cloud,
                    'cpu_cores': cpu_cores,
                    'ram_gb': ram_gb
                },
                'funding': {
                    'budget_usd': budget_usd,
                    'has_grant': has_grant,
                    'duration_months': timeline_months
                },
                'time': {
                    'hours_per_week': hours_per_week,
                    'dedicated_percentage': (hours_per_week / 40) * 100
                },
                'personnel': {
                    'team_size': team_size,
                    'has_advisor': has_advisor,
                    'has_collaborators': has_collaborators
                },
                'data': {
                    'has_access': has_data_access,
                    'type': data_type,
                    'size': 'unspecified'
                },
                'equipment': {
                    'has_lab_access': has_lab,
                    'specialized_equipment': []
                },
                'expertise': {
                    'skills': skills,
                    'experience_years': experience_years,
                    'has_mentorship': has_mentorship
                }
            }
            
            progress(0.3, desc="Initializing feasibility assessment...")
            
            # Initialize agent if needed
            if not self.feasibility_agent:
                self.feasibility_agent = FeasibilityAssessmentAgent()
            
            progress(0.5, desc="Performing rule-based assessment...")
            progress(0.7, desc="Analyzing with AI...")
            
            # Perform assessment
            result = self.feasibility_agent.assess_feasibility(
                research_topic=research_topic,
                research_description=research_description,
                available_resources=resources,
                timeline_months=timeline_months if timeline_months > 0 else None
            )
            
            progress(0.9, desc="Formatting results...")
            
            if not result['success']:
                return f"❌ Feasibility assessment failed: {result.get('message', 'Unknown error')}"
            
            # Format the results
            output = self._format_feasibility_assessment(result)
            
            progress(1.0, desc="Assessment complete!")
            
            return output
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Feasibility assessment error:\n{error_details}")
            return f"❌ Assessment error: {str(e)}"
    
    def _format_feasibility_assessment(self, result: Dict[str, Any]) -> str:
        """Format feasibility assessment results for display"""
        output = f"""# 🎯 Research Feasibility Assessment

**Assessment Date:** {result.get('timestamp', 'Unknown')}  
**Research Topic:** {result.get('research_topic', 'Unknown')}  
**Timeline:** {result.get('timeline_months', 'Not specified')} months

---

## 📊 Overall Assessment

**Feasibility Level:** {result.get('overall_feasibility', 'Unknown')}  
**Feasibility Score:** {result.get('feasibility_score', 0):.1f}/100

"""
        
        # Add resource check results
        checks = result.get('resource_checks', {})
        if checks:
            output += "\n## 🔍 Resource Analysis\n\n"
            
            # Group by status
            sufficient = []
            limited = []
            insufficient = []
            
            for check_name, check_result in checks.items():
                resource_name = check_name.replace('_check', '').replace('_', ' ').title()
                status = check_result.get('status', 'unknown')
                message = check_result.get('message', 'No details')
                
                if status == 'sufficient':
                    sufficient.append(f"- ✅ **{resource_name}**: {message}")
                elif status == 'limited':
                    limited.append(f"- ⚠️ **{resource_name}**: {message}")
                elif status == 'insufficient':
                    insufficient.append(f"- ❌ **{resource_name}**: {message}")
            
            if sufficient:
                output += "\n### ✅ Sufficient Resources\n\n" + "\n".join(sufficient) + "\n"
            if limited:
                output += "\n### ⚠️ Limited Resources\n\n" + "\n".join(limited) + "\n"
            if insufficient:
                output += "\n### ❌ Insufficient Resources\n\n" + "\n".join(insufficient) + "\n"
        
        # Add critical gaps
        gaps = result.get('critical_gaps', [])
        if gaps:
            output += "\n## 🚨 Critical Gaps\n\n"
            for gap in gaps:
                output += f"- {gap}\n"
        
        # Add detailed AI assessment
        if result.get('detailed_assessment'):
            output += "\n## 📋 Detailed Analysis\n\n"
            output += result['detailed_assessment']
            output += "\n"
        
        # Add recommendations summary
        recommendations = result.get('recommendations_summary', [])
        if recommendations:
            output += "\n## 💡 Key Recommendations\n\n"
            for rec in recommendations:
                output += f"- {rec}\n"
        
        output += "\n\n---\n\n"
        output += "*💡 Tip: Use this assessment to plan your research project and identify resources to acquire!*"
        
        return output
    
    def format_to_latex(
        self,
        template_name: str,
        title: str,
        authors_text: str,
        abstract: str,
        keywords_text: str,
        document_file: Optional[Any],
        introduction: str,
        related_work: str,
        methodology: str,
        results: str,
        conclusion: str,
        references_text: str,
        custom_template_file: Optional[Any] = None,
        image_files: Optional[List[Any]] = None,
        image_captions: str = "",
        image_sections: str = "",
        progress=gr.Progress()
    ):
        """Format research content into LaTeX document"""
        
        # Validate inputs
        if not title or not title.strip():
            return "⚠️ Please provide a paper title.", None, None
        
        if not abstract or not abstract.strip():
            return "⚠️ Please provide an abstract.", None, None
        
        try:
            progress(0.1, desc="Initializing LaTeX assistant...")
            
            # Initialize assistant if needed
            if not self.latex_assistant:
                self.latex_assistant = LaTeXWritingAssistant()
            
            progress(0.2, desc="Preparing document structure...")
            
            # Parse authors
            authors = [a.strip() for a in authors_text.split(',') if a.strip()]
            if not authors:
                authors = ["Anonymous"]
            
            # Parse keywords
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Check if document file is uploaded
            if document_file is not None:
                progress(0.3, desc="Extracting content from uploaded document...")
                sections = self._extract_sections_from_document(document_file)
                if not sections:
                    return "⚠️ Failed to extract content from uploaded document. Please try manual input.", None, None
            else:
                # Build sections dictionary from manual input
                sections = {}
                if introduction and introduction.strip():
                    sections["Introduction"] = introduction
                if related_work and related_work.strip():
                    sections["Related Work"] = related_work
                if methodology and methodology.strip():
                    sections["Methodology"] = methodology
            if results and results.strip():
                sections["Results"] = results
            if conclusion and conclusion.strip():
                sections["Conclusion"] = conclusion
            
            if not sections:
                return "⚠️ Please provide at least one section content.", None, None
            
            # Parse references
            references = []
            if references_text and references_text.strip():
                references = [r.strip() for r in references_text.split('\n') if r.strip()]
            
            progress(0.4, desc="Processing images...")
            
            # Process images with metadata
            images = []
            if image_files:
                # Parse captions and sections
                caption_list = [c.strip() for c in image_captions.split('\n') if c.strip()] if image_captions else []
                section_list = [s.strip() for s in image_sections.split('\n') if s.strip()] if image_sections else []
                
                for i, img_file in enumerate(image_files):
                    if img_file is not None:
                        # Get caption (or generate default)
                        if i < len(caption_list):
                            raw_caption = caption_list[i]
                        else:
                            raw_caption = f'Figure {i+1}: [Add caption here]'
                        
                        # Get section placement (or default to end)
                        if i < len(section_list):
                            section = section_list[i]
                        else:
                            section = "Results"  # Default section
                        
                        # Extract figure number from caption if it exists
                        fig_num_match = re.match(r'[Ff]ig(?:ure)?\s+(\d+):\s*(.+)', raw_caption)
                        if fig_num_match:
                            fig_num = fig_num_match.group(1)
                            # Remove "Figure X:" or "Fig X:" from caption to avoid redundancy
                            # LaTeX will automatically add "Figure X:" via \caption{}
                            caption = fig_num_match.group(2).strip()
                            label = f'fig:{fig_num}'
                        else:
                            # No figure number found, use as-is
                            caption = raw_caption
                            label = f'fig:{i+1}'
                        
                        images.append({
                            'path': img_file.name if hasattr(img_file, 'name') else img_file,
                            'filename': f'figure_{i+1}{Path(img_file.name).suffix if hasattr(img_file, "name") else ".png"}',
                            'caption': caption,
                            'label': label,
                            'section': section,
                            'width': '0.8\\textwidth'
                        })
            
            progress(0.6, desc="Generating LaTeX code with AI...")
            
            # Handle custom template
            custom_template = None
            if custom_template_file is not None:
                try:
                    with open(custom_template_file.name if hasattr(custom_template_file, 'name') else custom_template_file, 'r', encoding='utf-8') as f:
                        custom_template = f.read()
                except Exception as e:
                    logger.warning(f"Failed to read custom template: {e}")
            
            # Format document
            result = self.latex_assistant.format_document(
                content="",  # Not used, sections provided separately
                template_name=template_name,
                title=title,
                authors=authors,
                abstract=abstract,
                keywords=keywords,
                sections=sections,
                references=references,
                images=images if images else None,
                tables=None,  # Future enhancement
                equations=None,  # Future enhancement
                custom_template=custom_template
            )
            
            progress(0.9, desc="Finalizing output...")
            
            if not result['success']:
                return f"❌ LaTeX formatting failed: {result.get('message', 'Unknown error')}", None, None
            
            # Format output message
            output = self._format_latex_result(result)
            
            progress(1.0, desc="LaTeX generation complete!")
            
            # Return: (status message, main tex file, zip file)
            return output, result['main_file'], result['zip_file']
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"LaTeX formatting error:\n{error_details}")
            return f"❌ LaTeX formatting error: {str(e)}", None, None
    
    def _format_latex_result(self, result: Dict[str, Any]) -> str:
        """Format LaTeX generation result for display"""
        output = f"""# ✅ LaTeX Document Generated Successfully!

**Template Used:** {result.get('template_used', 'Unknown')}  
**Generated:** {result.get('timestamp', 'Unknown')}

---

## 📁 Output Files

**Main LaTeX File:** `{Path(result['main_file']).name}`  
**Project Directory:** `{Path(result['project_dir']).name}`  
**ZIP Archive:** `{Path(result['zip_file']).name}` ⬇️ (Download below)

---

## 📊 Document Statistics

- **Sections:** {len(result.get('sections', []))}
- **Images Processed:** {result.get('images_processed', 0)}
- **Tables Included:** {result.get('tables_processed', 0)}

---

## 📝 What's Included

Your LaTeX project contains:

1. **Main `.tex` File** - Complete, compilable LaTeX document
2. **`references.bib`** - Bibliography file
3. **`figures/` Directory** - All images properly formatted
4. **`README.md`** - Compilation instructions
5. **`compile.sh`** - Bash script for easy compilation

---

## 🚀 How to Compile

### Option 1: Using pdflatex
```bash
pdflatex {Path(result['main_file']).stem}.tex
bibtex {Path(result['main_file']).stem}
pdflatex {Path(result['main_file']).stem}.tex
pdflatex {Path(result['main_file']).stem}.tex
```

### Option 2: Using the script
```bash
chmod +x compile.sh
./compile.sh
```

### Option 3: Using latexmk (recommended)
```bash
latexmk -pdf {Path(result['main_file']).stem}.tex
```

---

## 💡 Next Steps

1. **Download** the ZIP file below
2. **Extract** to your local directory
3. **Compile** using one of the methods above
4. **Edit** the .tex file as needed
5. **Submit** to your target journal/conference!

---

*📥 Download the complete LaTeX project using the download button below.*
"""
        
        return output
    
    def generate_overleaf_instructions(self, zip_file_path: str) -> str:
        """
        Generate simple instructions for Overleaf usage (no upload)
        
        Args:
            zip_file_path: Path to the ZIP file
        
        Returns:
            Instructions message string
        """
        if not zip_file_path or not Path(zip_file_path).exists():
            return "⚠️ ZIP file not available"
        
        message = """
## ✅ LaTeX Project Generated!

Your LaTeX project has been created and is ready to download.

### 📥 Next Steps:

**1. Download the ZIP file** using the download button above

**2. To use with Overleaf:**
   - Go to [Overleaf](https://www.overleaf.com)
   - Click "New Project" → "Upload Project"
   - Upload the ZIP file you downloaded
   - Start editing!

**3. To compile locally:**
   - Extract the ZIP file
   - Run `pdflatex` followed by `bibtex` (see README.md in the ZIP)

---

**💡 The ZIP file contains:**
- Main `.tex` file with your document
- `references.bib` file with properly formatted citations
- `figures/` folder with your images
- `README.md` with compilation instructions
"""
        return message
    
    def _handle_latex_generation(self, zip_file) -> tuple:
        """Helper to show download files and instructions after LaTeX generation"""
        if not zip_file:
            return (
                gr.update(visible=False),  # tex file
                gr.update(visible=False),  # zip file  
                gr.update(visible=False, value="")  # instructions
            )
        
        # Generate simple instructions
        zip_path = zip_file.name if hasattr(zip_file, 'name') else str(zip_file)
        message = self.generate_overleaf_instructions(zip_path)
        
        return (
            gr.update(visible=True),  # Show tex file
            gr.update(visible=True),  # Show zip file
            gr.update(visible=True, value=message)  # Show instructions
        )
    
    def get_latex_templates_list(self) -> str:
        """Get formatted list of available LaTeX templates"""
        if not self.latex_assistant:
            self.latex_assistant = LaTeXWritingAssistant()
        
        templates = self.latex_assistant.get_available_templates()
        
        output = "# 📚 Available LaTeX Templates\n\n"
        
        # Group by type
        journals = [t for t in templates if t['type'] == 'journal']
        conferences = [t for t in templates if t['type'] == 'conference']
        preprints = [t for t in templates if t['type'] == 'preprint']
        
        if journals:
            output += "## 📰 Journal Templates\n\n"
            for t in journals:
                output += f"### {t['name']}\n"
                output += f"- **ID:** `{t['id']}`\n"
                output += f"- **Description:** {t['description']}\n"
                output += f"- **Document Class:** `{t['document_class']}`\n\n"
        
        if conferences:
            output += "## 🎤 Conference Templates\n\n"
            for t in conferences:
                output += f"### {t['name']}\n"
                output += f"- **ID:** `{t['id']}`\n"
                output += f"- **Description:** {t['description']}\n"
                output += f"- **Document Class:** `{t['document_class']}`\n\n"
        
        if preprints:
            output += "## 📄 Preprint Templates\n\n"
            for t in preprints:
                output += f"### {t['name']}\n"
                output += f"- **ID:** `{t['id']}`\n"
                output += f"- **Description:** {t['description']}\n"
                output += f"- **Document Class:** `{t['document_class']}`\n\n"
        
        return output
    
    def _extract_sections_from_document(self, document_file: Any) -> Dict[str, str]:
        """Extract sections from uploaded document using AI"""
        try:
            # Get file path
            file_path = document_file.name if hasattr(document_file, 'name') else document_file
            
            # Read document content based on file type
            content = ""
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.txt' or file_ext == '.md':
                # Plain text or Markdown
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            elif file_ext == '.pdf':
                # PDF - use PyMuPDF
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(file_path)
                    content = ""
                    for page in doc:
                        content += page.get_text()
                    doc.close()
                except Exception as e:
                    logger.error(f"Failed to extract PDF: {e}")
                    return {}
            
            elif file_ext in ['.doc', '.docx']:
                # Word document - use python-docx
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
                except Exception as e:
                    logger.error(f"Failed to extract DOCX: {e}")
                    # Try alternative method
                    try:
                        import subprocess
                        result = subprocess.run(['antiword', file_path], capture_output=True, text=True)
                        if result.returncode == 0:
                            content = result.stdout
                    except:
                        return {}
            
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return {}
            
            if not content or len(content.strip()) < 100:
                logger.warning("Extracted content too short")
                return {}
            
            # Use AI to intelligently extract sections
            sections = self._parse_sections_with_ai(content)
            return sections
            
        except Exception as e:
            logger.error(f"Failed to extract document content: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _parse_sections_with_ai(self, content: str) -> Dict[str, str]:
        """Use AI to parse document content into sections"""
        try:
            if not self.latex_assistant:
                self.latex_assistant = LaTeXWritingAssistant()
            
            prompt = f"""You are analyzing a research paper document. Extract and organize the content into standard academic sections.

**Document Content:**
{content[:8000]}  # Limit to avoid token limits

**Instructions:**
1. Identify the main sections in this document
2. Extract the content for each section
3. Return as a structured format

**Expected Sections** (include only if present in document):
- Introduction
- Related Work / Literature Review / Background
- Methodology / Methods / Approach
- Results / Experiments / Evaluation
- Discussion
- Conclusion / Conclusions
- Any other relevant sections

**Output Format:**
Return ONLY a JSON object with section names as keys and content as values:
{{
  "Introduction": "content here...",
  "Related Work": "content here...",
  "Methodology": "content here...",
  "Results": "content here...",
  "Conclusion": "content here..."
}}

If a section is not clearly present, omit it. Use the exact section names as they appear in the document (with proper capitalization).
DO NOT include abstract, references, or title - only body sections.
"""

            response = self.latex_assistant.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                sections_dict = json.loads(json_match.group())
                logger.info(f"Extracted {len(sections_dict)} sections from document")
                return sections_dict
            else:
                logger.warning("Could not parse AI response as JSON")
                return {}
                
        except Exception as e:
            logger.error(f"AI section parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def format_papers_for_display(self, papers: List) -> str:
        """Format papers for display in Gradio"""
        if not papers:
            return "No papers found."
        
        display_text = f"## 📊 Research Papers ({len(papers)} found)\n\n"
        
        for i, paper in enumerate(papers, 1):
            # Handle both dict and object formats
            if isinstance(paper, dict):
                title = paper.get('title', 'Unknown Title')
                paper_type = paper.get('paper_type', 'unknown')
                relevance_score = paper.get('relevance_score', 0)
                similarity_score = paper.get('similarity_score', 0)
                journal = paper.get('journal', 'Unknown')
                publication_date = paper.get('publication_date', 'Unknown')
                citation_count = paper.get('citation_count', 0)
                authors = paper.get('authors', [])
                abstract = paper.get('abstract', '')
                url = paper.get('url', '')
                doi = paper.get('doi', '')
                source = paper.get('source', 'Unknown')
            else:
                title = getattr(paper, 'title', 'Unknown Title')
                paper_type = getattr(paper, 'paper_type', 'unknown')
                relevance_score = getattr(paper, 'relevance_score', 0)
                similarity_score = getattr(paper, 'similarity_score', 0)
                journal = getattr(paper, 'journal', 'Unknown')
                publication_date = getattr(paper, 'publication_date', 'Unknown')
                citation_count = getattr(paper, 'citation_count', 0)
                authors = getattr(paper, 'authors', [])
                abstract = getattr(paper, 'abstract', '')
                url = getattr(paper, 'url', '')
                doi = getattr(paper, 'doi', '')
                source = getattr(paper, 'source', 'Unknown')
            
            # Infer paper type if unknown
            inferred_type = self._infer_paper_type(paper_type, title, journal)
            
            # Paper type badge
            type_badges = {
                'review': '📋 Review Paper',
                'conference': '🎯 Conference Paper', 
                'journal': '📖 Journal Article',
                'unknown': '❓ Unknown Type'
            }
            
            # Check if this is an uploaded paper
            is_uploaded = source == 'user_upload'
            upload_badge = " 📤 **YOUR UPLOAD**" if is_uploaded else ""
            
            display_text += f"### {i}. {title}{upload_badge}\n\n"
            display_text += f"**Type:** {type_badges.get(inferred_type, type_badges['journal'])}  \n"
            
            # Show source prominently for uploaded papers
            if is_uploaded:
                display_text += f"**Source:** 📤 User Upload (Your Paper)  \n"
            else:
                display_text += f"**Source:** {source}  \n"
            
            display_text += f"**Journal:** {journal}  \n"
            display_text += f"**Date:** {publication_date}  \n"
            display_text += f"**Citations:** {citation_count}  \n"
            display_text += f"**Relevance:** {relevance_score:.3f}  \n"
            
            if similarity_score and similarity_score > 0:
                display_text += f"**Similarity:** {similarity_score:.3f}  \n"
            
            if authors:
                authors_str = ', '.join(authors[:3]) + ('...' if len(authors) > 3 else '')
                display_text += f"**Authors:** {authors_str}  \n"
            
            if url:
                display_text += f"**Link:** [View Paper]({url})  \n"
                
            if doi:
                display_text += f"**DOI:** {doi}  \n"
            
            if abstract:
                abstract_preview = abstract[:300] + '...' if len(abstract) > 300 else abstract
                display_text += f"\n**Abstract:** {abstract_preview}  \n"
            
            display_text += "\n---\n\n"
        
        return display_text
    
    def create_paper_checkboxes(self, papers: List) -> List:
        """Create individual checkboxes for each paper (up to 20)"""
        checkboxes = []
        
        # Create up to 20 checkboxes
        for i in range(20):
            if i < len(papers):
                paper = papers[i]
                
                # Handle both dict and object formats
                if isinstance(paper, dict):
                    title = paper.get('title', 'Unknown Title')
                    paper_type = paper.get('paper_type', 'unknown')
                    relevance_score = paper.get('relevance_score', 0)
                    journal = paper.get('journal', 'Unknown')
                    publication_date = paper.get('publication_date', 'Unknown')
                    citation_count = paper.get('citation_count', 0)
                    source = paper.get('source', 'unknown')
                    similarity_score = paper.get('similarity_score', 0)
                else:
                    title = getattr(paper, 'title', 'Unknown Title')
                    paper_type = getattr(paper, 'paper_type', 'unknown')
                    relevance_score = getattr(paper, 'relevance_score', 0)
                    journal = getattr(paper, 'journal', 'Unknown')
                    publication_date = getattr(paper, 'publication_date', 'Unknown')
                    citation_count = getattr(paper, 'citation_count', 0)
                    source = getattr(paper, 'source', 'unknown')
                    similarity_score = getattr(paper, 'similarity_score', 0)
                
                # Infer paper type
                inferred_type = self._infer_paper_type(paper_type, title, journal)
                
                # Type emoji
                type_emoji = {'review': '📋', 'conference': '🎯', 'journal': '📖', 'unknown': '❓'}
                
                # Check if uploaded
                is_uploaded = source == 'user_upload'
                upload_emoji = "📤 " if is_uploaded else ""
                
                # Create compact label for checkbox
                title_short = title[:55] + '...' if len(title) > 55 else title
                label = f"{upload_emoji}{type_emoji.get(inferred_type, '📖')} **{title_short}**"
                
                # Build info line
                info_parts = [f"Relevance: {relevance_score:.2f}"]
                if similarity_score > 0:
                    info_parts.append(f"Similarity: {similarity_score:.2f}")
                info_parts.append(f"Citations: {citation_count}")
                if is_uploaded:
                    info_parts.append("📤 YOUR UPLOAD")
                else:
                    info_parts.append(f"{journal} ({publication_date})")
                
                info = " | ".join(info_parts)
                
                checkbox = gr.Checkbox(
                    label=label,
                    info=info,
                    value=False,
                    visible=True,
                    elem_id=f"paper_checkbox_{i}"
                )
            else:
                # Create invisible checkbox for unused slots
                checkbox = gr.Checkbox(
                    label="",
                    value=False,
                    visible=False,
                    elem_id=f"paper_checkbox_{i}"
                )
            
            checkboxes.append(checkbox)
        
        return checkboxes
    
    def _infer_paper_type(self, paper_type: str, title: str, journal: str) -> str:
        """Infer paper type from title and journal if not explicitly set"""
        if paper_type != 'unknown':
            return paper_type
            
        title_lower = title.lower()
        journal_lower = journal.lower()
        
        # Check for review indicators
        if any(word in title_lower for word in ['review', 'survey', 'overview', 'state of the art']):
            return 'review'
        elif any(word in journal_lower for word in ['conference', 'proceedings', 'workshop', 'symposium']) or \
             any(word in title_lower for word in ['conference', 'proceedings', 'workshop']):
            return 'conference'
        elif any(word in journal_lower for word in ['journal', 'transactions', 'letters', 'review']) or \
             any(word in title_lower for word in ['journal', 'article']):
            return 'journal'
        else:
            return 'unknown'
    
    def _create_empty_results(self, status_msg: str) -> Tuple:
        """Create empty results tuple for error cases"""
        empty_checkboxes = [gr.update(visible=False, value=False) for _ in range(20)]
        return (
            status_msg,
            "No papers to display.",
            *empty_checkboxes,
            gr.update(visible=False),  # Hide selection interface
            gr.update(visible=False),  # Hide action buttons container
            gr.update(visible=False),  # Hide augment button
            gr.update(visible=False),  # Hide save button
            gr.update(visible=False),  # Hide save all button
            ""  # Empty save status
        )
    
    def _create_results_update(self, status_msg: str, save_status: str) -> Tuple:
        """Create results update tuple maintaining current checkboxes"""
        maintain_checkboxes = [gr.update() for _ in range(20)]  # Maintain current state
        return (
            status_msg,
            gr.update(),  # Maintain current papers display
            *maintain_checkboxes,
            save_status
        )
    
    def create_interface(self):
        """Create the enhanced Gradio interface with API key configuration"""
        
        # Custom CSS for better styling
        css = """
        .gradio-container {
            max-width: 1400px !important;
        }
        .main-header {
            text-align: center;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .api-key-header {
            text-align: center;
            background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .paper-selection-area {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            background: #f9fafb;
        }
        .action-buttons {
            border: 2px solid #ddd6fe;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            background: #faf5ff;
        }
        .status-container {
            border: 2px solid #d1fae5;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            background: #ecfdf5;
        }
        """
        
        with gr.Blocks(css=css, title="Research Discovery Hub", theme=gr.themes.Soft()) as app:
            
            # Check if API keys are configured
            keys_configured = gr.State(self.api_keys_configured)
            
            # ========== API KEY CONFIGURATION SCREEN ==========
            with gr.Column(visible=not self.api_keys_configured) as api_key_screen:
                gr.HTML("""
                <div class="api-key-header">
                    <h1>🔑 API Key Configuration</h1>
                    <p>Welcome! Please configure your API keys to get started.</p>
                    <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 25px; display: inline-block; margin-top: 1rem;">
                        🔐 Secure • 💾 Locally Stored • 🚀 One-Time Setup
                    </div>
                </div>
                """)
                
                gr.Markdown("""
                ## Welcome to Research Discovery Hub! 🎉
                
                This application requires API keys to function. Your keys are:
                - ✅ **Stored locally** in a `.env` file
                - ✅ **Never sent anywhere** except to the respective API providers
                - ✅ **Under your control** - you own the keys and the costs
                
                ### Why do we need these?
                - **Gemini API**: Powers AI features (literature review, gap analysis, feasibility assessment, LaTeX generation)
                - **SerpAPI**: Enables Google Scholar search for academic papers
                
                ### First Time Setup (takes ~2 minutes)
                1. Click the links below to get your API keys
                2. Paste them into the fields below
                3. Click "Save & Continue"
                4. Start using the Research Assistant!
                """)
                
                # API Key Instructions
                with gr.Accordion("📖 How to Get API Keys", open=True):
                    api_instructions = gr.Markdown(self.get_api_key_instructions())
                
                # API Key Input Fields
                gr.Markdown("### 🔐 Enter Your API Keys")
                
                with gr.Group():
                    gr.Markdown("#### Required Keys")
                    
                    gemini_key_input = gr.Textbox(
                        label="🤖 Google Gemini API Key",
                        placeholder="AIza...",
                        type="password",
                        info="Get from: https://makersuite.google.com/app/apikey"
                    )
                    
                    serpapi_key_input = gr.Textbox(
                        label="🔍 SerpAPI Key",
                        placeholder="Your SerpAPI key",
                        type="password",
                        info="Get from: https://serpapi.com/manage-api-key"
                    )
                
                with gr.Group():
                    gr.Markdown("#### Optional Keys")
                    
                    openai_key_input = gr.Textbox(
                        label="🧠 OpenAI API Key (Optional)",
                        placeholder="sk-...",
                        type="password",
                        info="Get from: https://platform.openai.com/api-keys"
                    )
                
                # Save Button
                save_keys_btn = gr.Button("💾 Save & Continue", variant="primary", size="lg")
                api_status_output = gr.Markdown()
            
            # ========== MAIN APPLICATION SCREEN ==========
            with gr.Column(visible=self.api_keys_configured) as main_app_screen:
                # Header
                gr.HTML("""
                <div class="main-header">
                    <h1>🔬 Research Discovery Hub</h1>
                    <p>Enhanced AI-Powered Literature Discovery with Individual Paper Selection</p>
                    <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 25px; display: inline-block; margin-top: 1rem;">
                        🚀 Smart Search • 📊 Quality Filtering • 🔄 Iterative Discovery • 📋 Individual Selection • 📤 PDF Upload
                    </div>
                </div>
                """)
                
                # PDF Upload Section - NEW
                with gr.Accordion("📤 Upload Your Own Papers", open=False):
                    gr.Markdown("""
                    ### 📄 Upload Private Research Papers
                    Upload PDF files from your system to add them to your research collection. 
                    This is perfect for:
                    - 🔒 Private or unpublished papers
                    - 📚 Papers you already have saved locally
                    - 💼 Internal company research documents
                    - 📖 Papers from subscription journals you have access to
                    
                    The system will automatically extract title, authors, abstract, and content for analysis.
                    """)
                
                with gr.Row():
                    pdf_upload = gr.File(
                        label="📁 Select PDF Files",
                        file_count="multiple",
                        file_types=[".pdf"]
                    )
                
                upload_btn = gr.Button("📤 Upload & Parse Papers", variant="primary", size="lg")
                upload_status = gr.Markdown("")
            
            # Main interface
            with gr.Tab("🔍 Enhanced Search"):
                with gr.Row():
                    # Search Configuration (Left Column)
                    with gr.Column(scale=1):
                        gr.HTML('<div class="status-container">')
                        gr.Markdown("### 🔧 Search Configuration")
                        
                        query_input = gr.Textbox(
                            label="🔍 Research Topic",
                            placeholder="Describe your research question, topic, or area of interest...",
                            lines=4,
                            info="Be specific for better results. Example: 'machine learning applications in healthcare'"
                        )
                        
                        paper_type = gr.Dropdown(
                            label="📋 Paper Type",
                            choices=["All Types", "review", "conference", "journal"],
                            value="All Types",
                            info="Filter by paper type for focused results"
                        )
                        
                        with gr.Accordion("⚙️ Advanced Options", open=False):
                            search_sources = gr.CheckboxGroup(
                                label="🌐 Search Sources",
                                choices=[
                                    "Google Scholar (SerpAPI)",
                                    "arXiv",
                                    "CrossRef",
                                    "OpenAlex"
                                ],
                                value=["Google Scholar (SerpAPI)", "arXiv", "CrossRef", "OpenAlex"],
                                info="Select which databases to search (uncheck all to search only uploaded papers)"
                            )
                            
                            year_start = gr.Number(
                                label="📅 From Year",
                                value=2020,
                                minimum=1900,
                                maximum=2030,
                                info="Start year for publication range"
                            )
                            
                            year_end = gr.Number(
                                label="📅 To Year", 
                                value=2024,
                                minimum=1900,
                                maximum=2030,
                                info="End year for publication range"
                            )
                            
                            min_citations = gr.Number(
                                label="📈 Min Citations",
                                value=0,
                                minimum=0,
                                info="Minimum citation count filter"
                            )
                        
                        search_btn = gr.Button(
                            "🔍 Find Research Papers", 
                            variant="primary", 
                            size="lg"
                        )
                        
                        gr.HTML('</div>')
                    
                    # Results Display (Right Column)
                    with gr.Column(scale=2):
                        gr.HTML('<div class="status-container">')
                        gr.Markdown("### 📊 Search Results")
                        
                        status_output = gr.Markdown(
                            "Enter your research query and click **'Find Research Papers'** to start discovery."
                        )
                        
                        gr.HTML('</div>')
                        
                        papers_output = gr.Markdown("")
                
                # Paper Selection Interface
                with gr.Row():
                    with gr.Column():
                        selection_interface = gr.HTML(
                            '<div class="paper-selection-area"><h3>📋 Select Papers for Actions</h3><p>Choose papers below to save or use for augmented search:</p></div>',
                            visible=False
                        )
                        
                        # Select All checkbox
                        select_all_checkbox = gr.Checkbox(
                            label="📋 Select All Papers",
                            value=False,
                            visible=False
                        )
                        
                        # Individual paper checkboxes (up to 20 papers)
                        paper_checkboxes = []
                        for i in range(20):
                            checkbox = gr.Checkbox(
                                label=f"Paper {i+1}",
                                value=False,
                                visible=False,
                                elem_id=f"paper_checkbox_{i}"
                            )
                            paper_checkboxes.append(checkbox)
                
                # Action Buttons
                with gr.Row():
                    with gr.Column():
                        action_buttons = gr.HTML(
                            '<div class="action-buttons"><h3>🚀 Actions</h3></div>',
                            visible=False
                        )
                        
                        with gr.Row():
                            augment_btn = gr.Button(
                                "🔄 Find More Related Papers",
                                variant="secondary",
                                size="lg",
                                visible=False
                            )
                            
                            save_btn = gr.Button(
                                "💾 Save Selected Papers", 
                                variant="primary",
                                size="lg",
                                visible=False
                            )
                            
                            save_all_btn = gr.Button(
                                "💾 Save All Papers",
                                variant="secondary", 
                                size="lg",
                                visible=False
                            )
                        
                        save_status = gr.Markdown("")
            
            # Literature Review Tab
            with gr.Tab("📚 Literature Review"):
                gr.Markdown("### 📖 Generate Comprehensive Literature Review")
                gr.Markdown("Generate a comprehensive literature review from your saved papers using our multi-agent system.")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        review_topic = gr.Textbox(
                            label="🎯 Research Topic",
                            placeholder="Enter your research topic for the literature review",
                            lines=2,
                            info="Provide a clear and specific research topic"
                        )
                    
                    with gr.Column(scale=1):
                        max_papers = gr.Number(
                            label="📊 Max Papers",
                            value=30,
                            minimum=10,
                            maximum=50,
                            info="Maximum papers to include"
                        )
                
                generate_review_btn = gr.Button(
                    "📚 Generate Literature Review", 
                    variant="primary",
                    size="lg"
                )
                
                review_output = gr.Markdown("")
                
                gr.Markdown("💡 **Download**: Copy the generated review text above and save it as a .md file")
            
            # Research Gap Analysis Tab
            with gr.Tab("🔬 Gap Analysis"):
                gr.Markdown("### 🎯 Research Gap & Opportunity Identification")
                gr.Markdown("""
                Analyze your collected papers to identify:
                - **Research Gaps**: Unexplored areas in current literature
                - **Promising Topics**: Novel research directions
                - **Emerging Trends**: Patterns across recent work
                - **Methodological Opportunities**: New approaches to try
                - **Interdisciplinary Connections**: Cross-field opportunities
                
                This analysis uses AI to examine your papers and suggest where future research could make meaningful contributions.
                """)
                
                with gr.Row():
                    gap_analyze_btn = gr.Button(
                        "🔬 Analyze Research Gaps", 
                        variant="primary",
                        size="lg"
                    )
                
                gap_analysis_output = gr.Markdown("")
                
                gr.Markdown("""
                ---
                **💡 Tips for Using Gap Analysis:**
                - Conduct this analysis after finding 10-20 relevant papers
                - Use identified gaps to refine your search queries
                - Combine with literature review for comprehensive insights
                - Consider gaps as potential research project ideas
                """)
            
            # Feasibility Assessment Tab
            with gr.Tab("🎯 Feasibility Assessment"):
                gr.Markdown("### 📊 Research Project Feasibility Evaluation")
                gr.Markdown("""
                Assess whether your research idea is feasible with your available resources. 
                This tool provides:
                - **Resource Adequacy Check**: Rule-based evaluation of 7 resource categories
                - **Feasibility Score**: Quantitative assessment (0-100)
                - **AI Analysis**: Detailed recommendations and risk assessment
                - **Go/No-Go Recommendation**: Clear guidance on proceeding
                
                Fill in your resource inventory below to receive a comprehensive feasibility assessment.
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🔬 Research Details")
                        feas_topic = gr.Textbox(
                            label="Research Topic",
                            placeholder="e.g., Deep Learning for Medical Image Analysis",
                            lines=1
                        )
                        feas_description = gr.Textbox(
                            label="Research Description",
                            placeholder="Provide a detailed description of your research project...",
                            lines=5
                        )
                        feas_timeline = gr.Slider(
                            label="Timeline (months)",
                            minimum=0,
                            maximum=60,
                            value=12,
                            step=1
                        )
                        
                        gr.Markdown("#### 💻 Computational Resources")
                        feas_has_gpu = gr.Checkbox(label="Has GPU Access", value=False)
                        feas_has_cloud = gr.Checkbox(label="Has Cloud Computing Access", value=False)
                        with gr.Row():
                            feas_cpu_cores = gr.Slider(label="CPU Cores", minimum=1, maximum=64, value=8, step=1)
                            feas_ram_gb = gr.Slider(label="RAM (GB)", minimum=1, maximum=256, value=16, step=1)
                        
                        gr.Markdown("#### 💰 Funding")
                        feas_budget = gr.Number(label="Budget (USD)", value=0, precision=0)
                        feas_has_grant = gr.Checkbox(label="Has Research Grant", value=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### ⏰ Time Resources")
                        feas_hours_week = gr.Slider(
                            label="Available Hours per Week",
                            minimum=0,
                            maximum=80,
                            value=20,
                            step=1
                        )
                        
                        gr.Markdown("#### 👥 Personnel")
                        feas_team_size = gr.Slider(label="Team Size (including you)", minimum=1, maximum=20, value=1, step=1)
                        feas_has_advisor = gr.Checkbox(label="Has Advisor/Mentor", value=False)
                        feas_has_collaborators = gr.Checkbox(label="Has Collaborators", value=False)
                        
                        gr.Markdown("#### 📊 Data Access")
                        feas_has_data = gr.Checkbox(label="Has Data Access", value=False)
                        feas_data_type = gr.Textbox(
                            label="Data Type",
                            placeholder="e.g., public dataset, proprietary, needs collection",
                            value="unknown"
                        )
                        
                        gr.Markdown("#### 🔬 Equipment & Expertise")
                        feas_has_lab = gr.Checkbox(label="Has Lab Access", value=False)
                        feas_skills = gr.Textbox(
                            label="Skills (comma-separated)",
                            placeholder="e.g., python, machine learning, statistics",
                            lines=2
                        )
                        feas_experience = gr.Slider(label="Years of Experience", minimum=0, maximum=20, value=1, step=0.5)
                        feas_has_mentorship = gr.Checkbox(label="Has Access to Mentorship", value=False)
                
                with gr.Row():
                    feas_assess_btn = gr.Button(
                        "🎯 Assess Feasibility",
                        variant="primary",
                        size="lg"
                    )
                
                feas_output = gr.Markdown("")
                
                gr.Markdown("""
                ---
                **💡 Tips for Feasibility Assessment:**
                - Be honest about available resources - underestimating leads to project failure
                - The assessment considers 7 categories: Computational, Funding, Time, Personnel, Data, Equipment, Expertise
                - Use the recommendations to plan resource acquisition before starting
                - Consider the "Go with modifications" option for challenging projects
                - Reassess feasibility as your resources change
                """)
            
            # LaTeX Writing Assistant Tab
            with gr.Tab("📝 LaTeX Writer"):
                gr.Markdown("### ✍️ Academic LaTeX Document Formatter")
                gr.Markdown("""
                Format your research paper into publication-ready LaTeX code using academic templates.
                Supports major journals and conferences (IEEE, ACM, Springer, Elsevier, NeurIPS, CVPR, etc.)
                
                **Features:**
                - 8+ built-in academic templates (journals & conferences)
                - Custom template upload support
                - Automatic image handling and placement
                - Proper bibliography formatting
                - Compilable LaTeX project with instructions
                - ZIP download of complete project
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📋 Document Information")
                        latex_title = gr.Textbox(
                            label="Paper Title",
                            placeholder="Your Paper Title Here",
                            lines=1
                        )
                        latex_authors = gr.Textbox(
                            label="Authors (comma-separated)",
                            placeholder="John Doe, Jane Smith, et al.",
                            lines=2
                        )
                        latex_template = gr.Dropdown(
                            label="Template",
                            choices=[
                                ('IEEE Journal', 'ieee_journal'),
                                ('ACM Conference', 'acm_conference'),
                                ('Springer LNCS', 'springer_lncs'),
                                ('Elsevier Journal', 'elsevier'),
                                ('arXiv Preprint', 'arxiv'),
                                ('NeurIPS Conference', 'neurips'),
                                ('CVPR Conference', 'cvpr'),
                                ('AAAI Conference', 'aaai')
                            ],
                            value='ieee_journal'
                        )
                        latex_custom_template = gr.File(
                            label="Custom Template (optional .tex file)",
                            file_types=['.tex']
                        )
                        
                        gr.Markdown("#### 🖼️ Images & Figures")
                        gr.Markdown("""
                        **⚠️ Important:** When uploading a complete document, images are NOT parsed automatically.
                        You must upload images separately here with their metadata (figure number, caption, section).
                        """)
                        latex_images = gr.File(
                            label="Upload Images (Select multiple files at once)",
                            file_count="multiple",
                            file_types=['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.pdf', '.eps']
                        )
                        latex_image_captions = gr.Textbox(
                            label="Image Captions (one per line, in same order as uploaded images)",
                            placeholder="Figure 1: System Architecture\nFigure 2: Experimental Results\nFigure 3: Comparison Chart",
                            lines=4
                        )
                        latex_image_sections = gr.Textbox(
                            label="Place Images in Sections (one per line, e.g., 'Introduction', 'Results', 'Methodology')",
                            placeholder="Methodology\nResults\nResults",
                            lines=4
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📝 Abstract & Keywords")
                        latex_abstract = gr.Textbox(
                            label="Abstract",
                            placeholder="Write your abstract here...",
                            lines=5
                        )
                        latex_keywords = gr.Textbox(
                            label="Keywords (comma-separated)",
                            placeholder="machine learning, deep learning, computer vision",
                            lines=2
                        )
                        
                        gr.Markdown("#### 📚 References")
                        latex_references = gr.Textbox(
                            label="References (one per line)",
                            placeholder="LeCun et al. Deep Learning, Nature 2015\nKrizhevsky et al. ImageNet Classification, NIPS 2012",
                            lines=5
                        )
                
                gr.Markdown("#### 📄 Paper Content")
                gr.Markdown("""
                Choose one option: Either upload your complete document OR fill in the sections below.
                
                **Option 1: Upload Document** (Recommended for existing papers)
                - Upload a text file, Word document, or PDF with your complete paper
                - The AI will extract and structure the content automatically
                
                **Option 2: Manual Input** (For writing from scratch)
                - Fill in each section individually below
                """)
                
                latex_document_file = gr.File(
                    label="📤 Upload Complete Document (Optional) - TXT, DOCX, PDF, or Markdown",
                    file_types=['.txt', '.doc', '.docx', '.pdf', '.md']
                )
                
                gr.Markdown("**--- OR fill in sections manually ---**")
                
                with gr.Row():
                    with gr.Column():
                        latex_intro = gr.Textbox(
                            label="1. Introduction",
                            placeholder="Introduction content... (leave empty if using uploaded document)",
                            lines=8
                        )
                        latex_related = gr.Textbox(
                            label="2. Related Work",
                            placeholder="Related work content... (leave empty if using uploaded document)",
                            lines=8
                        )
                    
                    with gr.Column():
                        latex_methodology = gr.Textbox(
                            label="3. Methodology",
                            placeholder="Methodology content... (leave empty if using uploaded document)",
                            lines=8
                        )
                        latex_results = gr.Textbox(
                            label="4. Results",
                            placeholder="Results and discussion... (leave empty if using uploaded document)",
                            lines=8
                        )
                
                latex_conclusion = gr.Textbox(
                    label="5. Conclusion",
                    placeholder="Concluding remarks...",
                    lines=6
                )
                
                with gr.Row():
                    latex_generate_btn = gr.Button(
                        "📝 Generate LaTeX Document",
                        variant="primary",
                        size="lg"
                    )
                    latex_templates_btn = gr.Button(
                        "📚 View Available Templates",
                        variant="secondary"
                    )
                
                latex_output = gr.Markdown("")
                
                with gr.Row():
                    latex_tex_file = gr.File(label="📄 Main .tex File", visible=False)
                    latex_zip_file = gr.File(label="📦 Complete Project (ZIP)", visible=False)
                
                latex_instructions = gr.Markdown(visible=False)
                
                gr.Markdown("""
                ---
                **💡 Tips for LaTeX Generation:**
                - Fill in all required fields (title, authors, abstract, at least one section)
                - **Upload images with captions and section placement** - Images are NOT extracted from uploaded documents
                - For custom templates, upload a .tex file with your preferred style
                - The generated ZIP contains: .tex file, figures/, references.bib, compilation scripts
                - Download the ZIP and compile locally with pdflatex or latexmk
                - **Or click "Open in Overleaf"** to edit and compile online directly
                - Edit the .tex file to add equations, tables, or additional formatting
                
                **🎯 Supported Templates:**
                - IEEE Transactions (journal)
                - ACM Proceedings (conference)
                - Springer LNCS (conference)
                - Elsevier (journal)
                - NeurIPS, CVPR, AAAI (conferences)
                - arXiv (preprint)
                """)
            
            # About Tab  
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## 🚀 Enhanced Research Discovery Hub
                
                This advanced research pipeline combines **Google Gemini 2.5 Flash** with **FAISS vector database** 
                and **individual paper selection** for precise research discovery.
                
                ### ⭐ New Features
                - **� PDF Upload** - Upload your own research papers (private/local files)
                - **�📋 Individual Paper Selection** - Select specific papers with checkboxes
                - **🔄 Select All Toggle** - Quickly select/deselect all papers
                - **📊 Enhanced Paper Display** - Detailed paper information with relevance scores
                - **🎯 Smart Paper Classification** - Automatic paper type inference
                - **⚡ Improved Performance** - Faster search and better results display
                
                ### 🎯 How It Works
                1. **� Upload Papers (Optional)** - Add your private/local PDF papers
                2. **�🔍 Smart Search** - Find papers from multiple academic sources
                3. **✅ Quality Filtering** - AI-powered relevance scoring (0.7+ threshold)
                4. **🏆 Top Results** - See the most relevant papers first
                5. **📋 Individual Selection** - Choose specific papers with checkboxes
                6. **🔄 Iterative Discovery** - Use selected papers to find more related research
                7. **💾 Save & Collect** - Build your personal research collection
                8. **📚 Generate Reviews** - Create literature reviews from saved papers
                
                ### ✨ Key Features
                - **📤 PDF Upload** - Add private papers, unpublished work, or local files
                - **🧠 AI-Powered** - Gemini 2.5 Flash for intelligent paper validation
                - **🔍 Multi-Source** - Google Scholar, arXiv, CrossRef, OpenAlex
                - **📊 Smart Ranking** - FAISS-powered semantic similarity
                - **📋 Precise Selection** - Individual checkboxes for each paper
                - **🔄 Iterative** - Build comprehensive collections through multiple searches
                - **💾 Personal Collection** - Save and organize your research
                - **📚 Literature Reviews** - AI-generated comprehensive reviews
                - **🔬 Gap Analysis** - Identify unexplored research opportunities
                - **🎯 Feasibility Assessment** - Evaluate project viability with your resources
                - **⚡ Fast & Efficient** - Enhanced performance and user experience
                
                ### 🎛️ Getting Started
                1. **🔍 Enter your research query** in the search configuration
                2. **📋 Choose paper type** (optional, recommended: All Types)
                3. **⚙️ Configure advanced options** if needed
                4. **🚀 Click "Find Research Papers"** to start discovery
                5. **🏆 Review results** and use checkboxes to select interesting papers
                6. **🔄 Click "Find More Related Papers"** for augmented search
                7. **💾 Save selected papers** to build your collection
                8. **📚 Generate literature reviews** from your saved papers
                9. **🔬 Analyze research gaps** to find opportunities
                10. **🎯 Assess project feasibility** before starting research
                
                ### 🎨 Interface Improvements
                - **Better Layout** - Organized sections with clear visual separation
                - **Enhanced Status** - Detailed progress and result information  
                - **Smart Checkboxes** - Only show checkboxes for available papers
                - **Improved Typography** - Better readability and visual hierarchy
                - **Responsive Design** - Works well on different screen sizes
                """)
            
            # Event handlers
            
            # Upload handler
            upload_btn.click(
                fn=self.process_uploaded_pdfs,
                inputs=[pdf_upload],
                outputs=[upload_status, pdf_upload]
            )
            
            search_btn.click(
                fn=self.execute_search,
                inputs=[query_input, paper_type, year_start, year_end, min_citations, search_sources],
                outputs=[
                    status_output, 
                    papers_output,
                    *paper_checkboxes,
                    selection_interface,
                    action_buttons,
                    augment_btn,
                    save_btn,
                    save_all_btn,
                    save_status
                ]
            )
            
            # Select all functionality
            select_all_checkbox.change(
                fn=self.select_all_papers,
                inputs=[select_all_checkbox],
                outputs=paper_checkboxes
            )
            
            # Action button events
            augment_btn.click(
                fn=self.execute_secondary_search,
                inputs=paper_checkboxes,
                outputs=[
                    status_output,
                    papers_output,
                    *paper_checkboxes,
                    save_status
                ]
            )
            
            save_btn.click(
                fn=self.save_papers,
                inputs=paper_checkboxes,
                outputs=[save_status]
            )
            
            save_all_btn.click(
                fn=self.save_all_papers,
                inputs=[],
                outputs=[save_status]
            )
            
            # Literature review generation
            generate_review_btn.click(
                fn=self.generate_literature_review,
                inputs=[review_topic, max_papers],
                outputs=[review_output]
            )
            
            # Research gap analysis
            gap_analyze_btn.click(
                fn=self.analyze_research_gaps,
                inputs=[],
                outputs=[gap_analysis_output]
            )
            
            # Feasibility assessment
            feas_assess_btn.click(
                fn=self.assess_feasibility,
                inputs=[
                    feas_topic,
                    feas_description,
                    feas_timeline,
                    feas_has_gpu,
                    feas_has_cloud,
                    feas_cpu_cores,
                    feas_ram_gb,
                    feas_budget,
                    feas_has_grant,
                    feas_hours_week,
                    feas_team_size,
                    feas_has_advisor,
                    feas_has_collaborators,
                    feas_has_data,
                    feas_data_type,
                    feas_has_lab,
                    feas_skills,
                    feas_experience,
                    feas_has_mentorship
                ],
                outputs=[feas_output]
            )
            
            # LaTeX document generation
            latex_generate_btn.click(
                fn=self.format_to_latex,
                inputs=[
                    latex_template,
                    latex_title,
                    latex_authors,
                    latex_abstract,
                    latex_keywords,
                    latex_document_file,
                    latex_intro,
                    latex_related,
                    latex_methodology,
                    latex_results,
                    latex_conclusion,
                    latex_references,
                    latex_custom_template,
                    latex_images,
                    latex_image_captions,
                    latex_image_sections
                ],
                outputs=[latex_output, latex_tex_file, latex_zip_file]
            ).then(
                fn=lambda zip_file: self._handle_latex_generation(zip_file),
                inputs=[latex_zip_file],
                outputs=[latex_tex_file, latex_zip_file, latex_instructions]
            )
            
            # Show available templates
            latex_templates_btn.click(
                fn=self.get_latex_templates_list,
                inputs=[],
                outputs=[latex_output]
            )
            
            # ========== API KEY CONFIGURATION EVENT HANDLERS ==========
            
            def save_and_switch_screen(gemini_key, serpapi_key, openai_key):
                """Save API keys and switch to main screen"""
                message, success = self.save_api_keys(gemini_key, serpapi_key, openai_key)
                
                if success:
                    return (
                        message,  # Status message
                        gr.update(visible=False),  # Hide API key screen
                        gr.update(visible=True),   # Show main app screen
                        True  # Update keys_configured state
                    )
                else:
                    return (
                        message,  # Error message
                        gr.update(visible=True),   # Keep API key screen visible
                        gr.update(visible=False),  # Keep main app hidden
                        False  # Keep keys_configured as False
                    )
            
            save_keys_btn.click(
                fn=save_and_switch_screen,
                inputs=[gemini_key_input, serpapi_key_input, openai_key_input],
                outputs=[api_status_output, api_key_screen, main_app_screen, keys_configured]
            )
        
        return app

def main():
    """Main function to launch the enhanced Gradio app"""
    print("🚀 Starting Enhanced Research Discovery Hub...")
    
    app_instance = EnhancedGradioResearchApp()
    
    # Clean database on startup for fresh session
    cleanup_msg = app_instance.clean_database()
    print(cleanup_msg)
    
    app = app_instance.create_interface()
    
    print("✅ Interface created successfully!")
    
    # Launch the app with public link
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )

if __name__ == "__main__":
    main()
