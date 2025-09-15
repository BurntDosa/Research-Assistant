"""
Modern Research Discovery Hub - Enhanced Gradio Frontend
Built for Google Gemini 2.5 Flash with FAISS Vector Database

Beautiful, intuitive interface for iterative research discovery using Gradio
Based on the excellent Streamlit interface with improved paper selection
"""
import gradio as gr
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import components
from src.agents.literature_agent import SearchFilters
from src.agents.embedding_agent import EmbeddingAgent
from src.agents.control_agent import EnhancedResearchPipeline
from src.agents.literature_review_agents import LiteratureReviewCoordinator

class EnhancedGradioResearchApp:
    """Enhanced Gradio application for research discovery with individual paper selection"""
    
    def __init__(self):
        self.pipeline = None
        self.pipeline_results = None
        self.search_iterations = 0
        self.augmented_queries = []
        self.original_query = ""
        self.literature_review = None
        self.generating_review = False
        self.current_papers = []  # Store current papers for selection
        
    def clean_database(self):
        """Clean out the vector database to start fresh"""
        try:
            import os
            import glob
            
            # Remove FAISS database files
            db_patterns = [
                "faiss_paper_embeddings*",
                "*.index",
                "*_metadata.pkl"
            ]
            
            files_removed = 0
            for pattern in db_patterns:
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                        print(f"🗑️ Removed database file: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Could not remove {file_path}: {e}")
            
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
    
    def execute_search(self, query: str, paper_type: str, year_start: int, year_end: int, 
                      min_citations: int, progress=gr.Progress()):
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
        
        try:
            progress(0.2, desc="Searching academic databases...")
            
            # Execute search
            results = self.pipeline.execute_initial_search(
                query=query,
                filters=filters
            )
            
            progress(1.0, desc="Search completed!")
            
            # Store results
            self.pipeline_results = results
            self.original_query = query
            self.search_iterations = 1
            self.augmented_queries = []
            
            # Store current papers for selection
            self.current_papers = results.get('top_papers', [])
            
            # Format results for display
            papers_found = results.get('papers_found', 0)
            top_papers = len(results.get('top_papers', []))
            duration = results.get('pipeline_duration', 0)
            
            status_msg = f"🎉 **Search Complete!**\n\n"
            status_msg += f"📊 **Found:** {papers_found} relevant papers in {duration:.1f}s\n"
            status_msg += f"🏆 **Showing:** Top {top_papers} most relevant papers\n"
            status_msg += f"🔍 **Query:** {query}\n\n"
            status_msg += f"📋 **Next Steps:** Review papers below and select interesting ones for further actions"
            
            # Create papers display and selection components
            papers_display = self.format_papers_for_display(results.get('top_papers', []))
            
            # Create individual paper selection checkboxes
            paper_checkboxes = self.create_paper_checkboxes(results.get('top_papers', []))
            
            return (
                status_msg,
                papers_display,
                *paper_checkboxes,  # Unpack the checkboxes
                gr.update(visible=True),  # Make selection interface visible
                gr.update(visible=True),  # Make action buttons visible
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
            
            display_text += f"### {i}. {title}\n\n"
            display_text += f"**Type:** {type_badges.get(inferred_type, type_badges['journal'])}  \n"
            display_text += f"**Journal:** {journal}  \n"
            display_text += f"**Date:** {publication_date}  \n"
            display_text += f"**Citations:** {citation_count}  \n"
            display_text += f"**Relevance:** {relevance_score:.3f}  \n"
            
            if similarity_score:
                display_text += f"**Similarity:** {similarity_score:.3f}  \n"
            
            display_text += f"**Source:** {source}  \n"
            
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
                else:
                    title = getattr(paper, 'title', 'Unknown Title')
                    paper_type = getattr(paper, 'paper_type', 'unknown')
                    relevance_score = getattr(paper, 'relevance_score', 0)
                    journal = getattr(paper, 'journal', 'Unknown')
                    publication_date = getattr(paper, 'publication_date', 'Unknown')
                    citation_count = getattr(paper, 'citation_count', 0)
                
                # Infer paper type
                inferred_type = self._infer_paper_type(paper_type, title, journal)
                
                # Type emoji
                type_emoji = {'review': '📋', 'conference': '🎯', 'journal': '📖', 'unknown': '❓'}
                
                # Create compact label for checkbox
                title_short = title[:60] + '...' if len(title) > 60 else title
                label = f"{type_emoji.get(inferred_type, '📖')} **{title_short}**"
                info = f"Relevance: {relevance_score:.2f} | Citations: {citation_count} | {journal} ({publication_date})"
                
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
            gr.update(visible=False),  # Hide action buttons
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
        """Create the enhanced Gradio interface"""
        
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
            
            # Header
            gr.HTML("""
            <div class="main-header">
                <h1>🔬 Research Discovery Hub</h1>
                <p>Enhanced AI-Powered Literature Discovery with Individual Paper Selection</p>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 25px; display: inline-block; margin-top: 1rem;">
                    🚀 Smart Search • 📊 Quality Filtering • 🔄 Iterative Discovery • 📋 Individual Selection
                </div>
            </div>
            """)
            
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
            
            # About Tab  
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## 🚀 Enhanced Research Discovery Hub
                
                This advanced research pipeline combines **Google Gemini 2.5 Flash** with **FAISS vector database** 
                and **individual paper selection** for precise research discovery.
                
                ### ⭐ New Features
                - **📋 Individual Paper Selection** - Select specific papers with checkboxes
                - **🔄 Select All Toggle** - Quickly select/deselect all papers
                - **📊 Enhanced Paper Display** - Detailed paper information with relevance scores
                - **🎯 Smart Paper Classification** - Automatic paper type inference
                - **⚡ Improved Performance** - Faster search and better results display
                
                ### 🎯 How It Works
                1. **🔍 Smart Search** - Find papers from multiple academic sources
                2. **✅ Quality Filtering** - AI-powered relevance scoring (0.7+ threshold)
                3. **🏆 Top Results** - See the most relevant papers first
                4. **📋 Individual Selection** - Choose specific papers with checkboxes
                5. **🔄 Iterative Discovery** - Use selected papers to find more related research
                6. **💾 Save & Collect** - Build your personal research collection
                
                ### ✨ Key Features
                - **🧠 AI-Powered** - Gemini 2.5 Flash for intelligent paper validation
                - **🔍 Multi-Source** - Google Scholar, arXiv, CrossRef, OpenAlex
                - **📊 Smart Ranking** - FAISS-powered semantic similarity
                - **📋 Precise Selection** - Individual checkboxes for each paper
                - **🔄 Iterative** - Build comprehensive collections through multiple searches
                - **💾 Personal Collection** - Save and organize your research
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
                
                ### 🎨 Interface Improvements
                - **Better Layout** - Organized sections with clear visual separation
                - **Enhanced Status** - Detailed progress and result information  
                - **Smart Checkboxes** - Only show checkboxes for available papers
                - **Improved Typography** - Better readability and visual hierarchy
                - **Responsive Design** - Works well on different screen sizes
                """)
            
            # Event handlers
            search_btn.click(
                fn=self.execute_search,
                inputs=[query_input, paper_type, year_start, year_end, min_citations],
                outputs=[
                    status_output, 
                    papers_output,
                    *paper_checkboxes,
                    selection_interface,
                    action_buttons,
                    save_status
                ]
            )
            
            # Update action button visibility when selection interface becomes visible
            selection_interface.change(
                fn=lambda visible: [gr.update(visible=visible)] * 3,
                inputs=[selection_interface],
                outputs=[augment_btn, save_btn, save_all_btn]
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
    
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main()
