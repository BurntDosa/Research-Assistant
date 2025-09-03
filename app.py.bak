"""
Modern Research Discovery Hub - Streamlit Frontend
Built for Google Gemini 2.5 Flash with FAISS Vector Database

Beautiful, intuitive interface for iterative research discovery
"""

import streamlit as st
import pandas as pd
import json
import os
import time
from typing import List, Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import enhanced control agent
from enhanced_control_agent import EnhancedResearchPipeline, UserSelectionDatabase
from literature_agent import SearchFilters
from embedding_agent import EmbeddingAgent

# Configure Streamlit page
st.set_page_config(
    page_title="Research Discovery Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS with beautiful design
st.markdown("""
<style>
    /* Modern color scheme and typography */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #4b5563;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --sidebar-bg: #f8fafc;
        --input-bg: #ffffff;
        --input-border: #d1d5db;
    }

    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }

    .main-title {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }

    .main-subtitle {
        font-size: 1.5rem;
        margin-top: 1rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }

    .pipeline-badge {
        background: linear-gradient(45deg, var(--accent-color), var(--success-color));
        color: white;
        padding: 0.8em 2em;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
        margin: 1.5rem 0;
        font-size: 1.1rem;
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.3);
        position: relative;
        z-index: 1;
    }

    /* Modern cards */
    .modern-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    }

    /* Paper cards with enhanced design - simplified to avoid conflicts */
    .paper-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }

    .paper-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-color: var(--primary-color);
    }

    /* Modern buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    /* Progress indicators */
    .progress-container {
        background: var(--bg-secondary);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--border-color);
    }

    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem;
    }

    .status-success {
        background: linear-gradient(135deg, var(--success-color), #059669);
        color: white;
    }

    .status-info {
        background: linear-gradient(135deg, var(--accent-color), #0891b2);
        color: white;
    }

    .status-warning {
        background: linear-gradient(135deg, var(--warning-color), #d97706);
        color: white;
    }

    /* Metrics with modern design */
    .metric-card {
        background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 0;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0;
    }

    /* Selection interface */
    .selection-interface {
        background: var(--bg-secondary);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--border-color);
    }

    /* Timeline styling */
    .timeline {
        background: var(--bg-secondary);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--border-color);
    }

    .timeline-item {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background: var(--bg-primary);
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
    }

    .timeline-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--primary-color);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-weight: bold;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .main-subtitle {
            font-size: 1.2rem;
        }
        
        .pipeline-badge {
            font-size: 1rem;
            padding: 0.6em 1.5em;
        }
    }
    
    /* Ensure all text is visible */
    .stMarkdown, .stText {
        color: #1f2937 !important;
    }
    
    /* Fix sidebar text */
    .css-1d391kg {
        color: #1f2937 !important;
    }
    
    /* Fix button text */
    .stButton > button {
        color: white !important;
    }
    
    /* Fix paper card text */
    .paper-card h3 {
        color: #1f2937 !important;
        margin-bottom: 0.5rem;
    }
    
    .paper-card p {
        color: #6b7280 !important;
        margin: 0;
    }
    
    /* Paper type badges */
    .paper-type-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .paper-type-review {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .paper-type-conference {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .paper-type-journal {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
    }
    
    .paper-type-unknown {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
    }
    
    /* Sidebar styling for better readability */
    .css-1d391kg {
        background: var(--sidebar-bg) !important;
    }
    
    /* Input field styling */
    .stTextArea > div > div > textarea {
        background-color: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.8;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > select {
        background-color: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        background-color: var(--input-bg) !important;
        border: 2px solid var(--input-border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px;
    }
    
    /* Ensure all text is visible */
    .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }
    
    /* Fix sidebar text */
    .css-1d391kg {
        color: var(--text-primary) !important;
    }
    
    /* Fix button text */
    .stButton > button {
        color: white !important;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        border: none !important;
    }
    
    /* Fix paper card text */
    .paper-card h3 {
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem;
    }
    
    .paper-card p {
        color: var(--text-secondary) !important;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'pipeline_results' not in st.session_state:
        st.session_state.pipeline_results = None
    if 'search_iterations' not in st.session_state:
        st.session_state.search_iterations = 0
    if 'augmented_queries' not in st.session_state:
        st.session_state.augmented_queries = []

def main():
    """Main Streamlit application with modern design"""
    initialize_session_state()
    
    # Modern Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🔬 Research Discovery Hub</h1>
        <p class="main-subtitle">AI-Powered Literature Discovery with Gemini 2.5 Flash</p>
        <div class="pipeline-badge">🚀 Smart Search • 📊 Quality Filtering • 🔄 Iterative Discovery</div>
    </div>
    """, unsafe_allow_html=True)

    # Modern Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: var(--primary-color); margin-bottom: 0;">🔧 Search Setup</h2>
            <p style="color: var(--text-primary); font-size: 0.9rem; font-weight: 500;">Configure your research discovery</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Research Query
        st.markdown("**🔍 Research Topic**", help="Enter your research query here")
        query = st.text_area(
            "What are you researching?",
            placeholder="Describe your research question, topic, or area of interest...",
            help="Be specific for better results. Example: 'machine learning applications in healthcare'",
            height=120
        )
        
        # Paper Type Preference
        st.markdown("**📋 Paper Type**", help="Choose the type of papers you want to find")
        paper_type_preference = st.selectbox(
            "Choose paper type:",
            options=[None, "review", "conference", "journal"],
            format_func=lambda x: {
                None: "🎯 All Types (recommended)",
                "review": "📚 Review Papers",
                "conference": "🎪 Conference Papers", 
                "journal": "📖 Journal Articles"
            }[x],
            help="Filter by paper type for focused results"
        )
        
        # Advanced Filters
        with st.expander("⚙️ Advanced Options", expanded=False):
            st.markdown("**📅 Publication Year**", help="Filter papers by publication year range")
            col1, col2 = st.columns(2)
            with col1:
                year_start = st.number_input("From", min_value=1900, max_value=2030, value=2020, help="Start year for publication range")
            with col2:
                year_end = st.number_input("To", min_value=1900, max_value=2030, value=2025, help="End year for publication range")
            
            st.markdown("**📈 Citation Count**", help="Filter papers by minimum citation count")
            min_citations = st.number_input("Minimum citations", min_value=0, value=0, help="Papers with at least this many citations")
            
            # Create filters object
            filters = SearchFilters(
                year_start=year_start,
                year_end=year_end,
                min_citations=min_citations,
                paper_type_filter=paper_type_preference
            )
        
        # Search Execution
        st.markdown("---")
        st.markdown("**🚀 Start Discovery**")
        
        if st.button("🔍 Find Research Papers", type="primary", disabled=not query.strip(), use_container_width=True):
            if query.strip():
                execute_initial_search(query, filters, paper_type_preference)

    # Main Content Area
    if st.session_state.pipeline_results:
        display_modern_results()
    else:
        display_modern_welcome()

def display_modern_welcome():
    """Display modern welcome screen with instructions"""
    
    st.markdown("""
    <div class="modern-card">
        <h2 style="text-align: center; color: var(--primary-color); margin-bottom: 2rem;">🚀 Welcome to Research Discovery Hub</h2>
        
        <p style="font-size: 1.1rem; line-height: 1.6; color: var(--text-primary);">
            This advanced research pipeline combines the power of <strong>Google Gemini 2.5 Flash</strong> with <strong>FAISS vector database</strong> 
            to deliver the most relevant academic papers for your research.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # How it works section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">🎯 How It Works</h3>
            <ol style="color: var(--text-primary); line-height: 1.8;">
                <li><strong>🔍 Smart Search</strong> - Find papers from multiple academic sources</li>
                <li><strong>✅ Quality Filtering</strong> - AI-powered relevance scoring (0.7+ threshold)</li>
                <li><strong>🏆 Top Results</strong> - See the most relevant papers first</li>
                <li><strong>📋 Paper Selection</strong> - Choose papers to save or enhance search</li>
                <li><strong>🔄 Iterative Discovery</strong> - Use found papers to find more related research</li>
                <li><strong>💾 Save & Collect</strong> - Build your personal research collection</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">✨ Key Features</h3>
            <ul style="color: var(--text-primary); line-height: 1.8;">
                <li><strong>🧠 AI-Powered</strong> - Gemini 2.5 Flash for intelligent paper validation</li>
                <li><strong>🔍 Multi-Source</strong> - Google Scholar, arXiv, CrossRef, OpenAlex</li>
                <li><strong>📊 Smart Ranking</strong> - FAISS-powered semantic similarity</li>
                <li><strong>🔄 Iterative</strong> - Build comprehensive collections through multiple searches</li>
                <li><strong>💾 Personal Collection</strong> - Save and organize your research</li>
                <li><strong>⚡ Fast & Efficient</strong> - Optimized for quick discovery</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("""
    <div class="modern-card">
        <h3 style="color: var(--primary-color); margin-bottom: 1rem;">🎛️ Getting Started</h3>
        <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border-left: 4px solid var(--primary-color);">
            <ol style="color: var(--text-primary); line-height: 2;">
                <li><strong>🔍 Enter your research query</strong> in the sidebar</li>
                <li><strong>📋 Choose paper type</strong> (optional, recommended: All Types)</li>
                <li><strong>⚙️ Configure advanced options</strong> if needed</li>
                <li><strong>🚀 Click "Find Research Papers"</strong> to start discovery</li>
                <li><strong>🏆 Review top results</strong> and select interesting papers</li>
                <li><strong>🔄 Use selected papers</strong> to find more related research</li>
                <li><strong>💾 Save papers</strong> to build your collection</li>
            </ol>
        </div>
        <p style="text-align: center; margin-top: 1.5rem; font-size: 1.1rem; color: var(--primary-color); font-weight: 600;">
            🎉 Ready to discover? Enter your research query in the sidebar and start exploring!
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_modern_results():
    """Display results with modern design"""
    results = st.session_state.pipeline_results
    
    # Modern metrics display
    st.markdown("""
    <div class="modern-card">
        <h2 style="color: var(--primary-color); margin-bottom: 1.5rem; text-align: center;">📊 Search Results</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics in modern cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results.get('papers_found', 0)}</div>
            <div class="metric-label">Papers Found</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results.get('total_unique_papers', 0)}</div>
            <div class="metric-label">Total Searched</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(results.get('top_papers', []))}</div>
            <div class="metric-label">Showing Top</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results.get('pipeline_duration', 0):.1f}s</div>
            <div class="metric-label">Search Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show search iteration info for secondary searches
    if hasattr(st.session_state, 'search_iterations') and st.session_state.search_iterations > 1:
        total_available = results.get('total_available_papers', 0)
        papers_displayed = results.get('papers_displayed', 0)
        
        if total_available > papers_displayed:
            st.info(f"🔄 **Search Iteration {st.session_state.search_iterations}** - Showing {papers_displayed} papers out of {total_available} available (selected papers from previous search + new relevant papers from augmented search)")
        else:
            st.success(f"🔄 **Search Iteration {st.session_state.search_iterations}** - Showing all {papers_displayed} available papers (selected papers from previous search + new relevant papers from augmented search)")
    
    # Display papers
    if results.get('top_papers'):
        st.markdown("---")
        st.markdown(f"## 🏆 Top {len(results.get('top_papers', []))} Most Relevant Papers")
        st.markdown("")
        
        display_modern_papers(results['top_papers'])
        
        # Paper selection interface
        st.markdown("---")
        st.markdown("## 📋 Select Papers for Actions")
        st.markdown("Choose papers to save to your collection or use for augmented search:")
        st.markdown("")
        
        # Individual checkboxes for each paper
        st.markdown("**Select Papers:**")
        
        # Add "Select All" toggle
        select_all = st.checkbox("📋 Select All Papers", key="select_all")
        
        selected_indices = []
        
        # Display checkboxes for each paper
        for i, paper in enumerate(results['top_papers']):
            if isinstance(paper, dict):
                paper_title = paper.get('title', 'Unknown Title')
                paper_type = paper.get('paper_type', 'unknown')
                citation_count = paper.get('citation_count', 0)
                relevance_score = paper.get('relevance_score', 0)
            else:
                paper_title = getattr(paper, 'title', 'Unknown Title')
                paper_type = getattr(paper, 'paper_type', 'unknown') 
                citation_count = getattr(paper, 'citation_count', 0)
                relevance_score = getattr(paper, 'relevance_score', 0)
            
            # Format display with paper info - improved readability
            type_emoji = {'review': '📋', 'conference': '🎯', 'journal': '📖', 'unknown': '📖'}
            paper_display = f"{type_emoji.get(paper_type, '📖')} **{paper_title[:80]}{'...' if len(paper_title) > 80 else ''}**"
            
            # Add metadata below the title
            source = paper.get('source', 'Unknown') if isinstance(paper, dict) else getattr(paper, 'source', 'Unknown')
            metadata = f"Relevance: {relevance_score:.2f} | Citations: {citation_count} | Source: {source}"
            
            checkbox_value = select_all or st.checkbox(
                paper_display,
                key=f"paper_{i}",
                value=select_all
            )
            
            # Show metadata for selected papers
            if checkbox_value:
                st.markdown(f"*{metadata}*", help="Paper metadata")
                selected_indices.append(i)
        
        if selected_indices or select_all:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Selected Papers", type="primary", help="Save selected papers to your personal collection", use_container_width=True):
                    if select_all:
                        selected_indices = list(range(len(results['top_papers'])))
                    save_selected_papers(selected_indices)
            
            with col2:
                if st.button("🔍 Find More Papers (Augmented)", type="secondary", help="Use selected papers to enhance search and find more related research", use_container_width=True):
                    if select_all:
                        selected_indices = list(range(len(results['top_papers'])))
                    execute_secondary_search(selected_indices)
            
            with col3:
                if st.button("💾 Save All Papers", help="Save all displayed papers to your collection", use_container_width=True):
                    all_indices = list(range(len(results['top_papers'])))
                    save_selected_papers(all_indices)
        else:
            st.info("💡 Select papers above to save them or use them to find more related research")
        
        # Search history timeline
        if hasattr(st.session_state, 'search_iterations') and st.session_state.search_iterations > 1:
            st.markdown("""
            <div class="timeline">
                <h3 style="color: var(--primary-color); margin-bottom: 1.5rem;">🔄 Search History</h3>
            </div>
            """, unsafe_allow_html=True)
            
            timeline_data = []
            timeline_data.append(f"**Iteration 1:** {st.session_state.original_query}")
            
            if hasattr(st.session_state, 'augmented_queries'):
                for i, query in enumerate(st.session_state.augmented_queries):
                    timeline_data.append(f"**Iteration {i+2}:** {query}")
            
            for i, item in enumerate(timeline_data):
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-icon">{i+1}</div>
                    <div>{item}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <span class="status-badge status-info">Total iterations: {st.session_state.search_iterations}</span>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No papers found. Try adjusting your search query or filters.")

def display_modern_papers(papers: List):
    """Display papers with modern formatting - improved layout"""
    
    for i, paper in enumerate(papers):
        # Handle both dict and object formats
        if isinstance(paper, dict):
            title = paper.get('title', 'Unknown Title')
            paper_type = paper.get('paper_type', 'unknown')
            similarity_score = paper.get('similarity_score', 0)
            relevance_score = paper.get('relevance_score', 0)
        else:
            title = getattr(paper, 'title', 'Unknown Title')
            paper_type = getattr(paper, 'paper_type', 'unknown')
            similarity_score = getattr(paper, 'similarity_score', 0)
            relevance_score = getattr(paper, 'relevance_score', 0)
        
        # Paper type badge with color coding - improved classification
        # Try to infer paper type from title and journal if not explicitly set
        inferred_type = paper_type
        if paper_type == 'unknown':
            title_lower = title.lower()
            journal_lower = journal.lower() if journal else ''
            
            # Check for review indicators
            if any(word in title_lower for word in ['review', 'survey', 'overview', 'state of the art']):
                inferred_type = 'review'
            # Check for conference indicators
            elif any(word in journal_lower for word in ['conference', 'proceedings', 'workshop', 'symposium']) or \
                 any(word in title_lower for word in ['conference', 'proceedings', 'workshop']):
                inferred_type = 'conference'
            # Check for journal indicators
            elif any(word in journal_lower for word in ['journal', 'transactions', 'letters', 'review']) or \
                 any(word in title_lower for word in ['journal', 'article']):
                inferred_type = 'journal'
            else:
                # Default to journal for academic papers
                inferred_type = 'journal'
        
        type_badges = {
            'review': '<span class="paper-type-badge paper-type-review">📋 Review Paper</span>',
            'conference': '<span class="paper-type-badge paper-type-conference">🎯 Conference Paper</span>', 
            'journal': '<span class="paper-type-badge paper-type-journal">📖 Journal Article</span>',
            'unknown': '<span class="paper-type-badge paper-type-unknown">❓ Unknown Type</span>'
        }
        
        # Create a clean paper card without CSS conflicts
        st.markdown("---")
        
        # Title and paper type
        st.markdown(f"### {i+1}. {title}")
        st.markdown(f'{type_badges.get(inferred_type, type_badges["journal"])}', unsafe_allow_html=True)
        
        # Similarity score badge
        if similarity_score:
            st.markdown(f'<div class="status-badge status-info">Similarity: {similarity_score:.3f}</div>', unsafe_allow_html=True)
        
        # Paper metadata in clean columns
        col1, col2, col3 = st.columns(3)
        
        # Get metadata based on format
        if isinstance(paper, dict):
            journal = paper.get('journal', 'Unknown')
            publication_date = paper.get('publication_date', 'Unknown')
            citation_count = paper.get('citation_count', 0)
            source = paper.get('source', 'Unknown')
            doi = paper.get('doi', '')
            url = paper.get('url', '')
            authors = paper.get('authors', [])
            abstract = paper.get('abstract', '')
        else:
            journal = getattr(paper, 'journal', 'Unknown')
            publication_date = getattr(paper, 'publication_date', 'Unknown')
            citation_count = getattr(paper, 'citation_count', 0)
            source = getattr(paper, 'source', 'Unknown')
            doi = getattr(paper, 'doi', '')
            url = getattr(paper, 'url', '')
            authors = getattr(paper, 'authors', [])
            abstract = getattr(paper, 'abstract', '')
        
        with col1:
            st.markdown(f"**Journal:** {journal}")
            st.markdown(f"**Date:** {publication_date}")
            st.markdown(f"**Citations:** {citation_count}")
        
        with col2:
            st.markdown(f"**Relevance:** {relevance_score:.3f}")
            st.markdown(f"**Source:** {source}")
            if doi:
                st.markdown(f"**DOI:** [{doi}](https://doi.org/{doi})")
        
        with col3:
            if url:
                st.markdown(f"[📄 View Paper]({url})")
        
        # Authors
        if authors:
            st.markdown(f"**Authors:** {', '.join(authors[:5])}{'...' if len(authors) > 5 else ''}")
        
        # Abstract
        if abstract:
            with st.expander("📄 Abstract"):
                st.write(abstract)
        
        st.markdown("---")

def execute_initial_search(query: str, filters: SearchFilters, paper_type_preference: Optional[str]):
    """Execute initial search with modern progress tracking"""
    
    # Initialize pipeline
    with st.spinner("🚀 Initializing Research Pipeline..."):
        try:
            st.session_state.pipeline = EnhancedResearchPipeline()
        except Exception as e:
            st.error(f"❌ Failed to initialize pipeline: {str(e)}")
            return
    
    # Modern progress tracking
    progress_container = st.container()
    with progress_container:
        st.markdown("""
        <div class="progress-container">
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">🔍 Search Progress</h3>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress
            progress_bar.progress(20)
            status_text.text("🔍 Searching academic databases...")
            
            # Execute initial search
            with st.spinner("🔍 Searching academic databases..."):
                results = st.session_state.pipeline.execute_initial_search(
                    query=query,
                    filters=filters
                )
            
            progress_bar.progress(100)
            status_text.text("✅ Search completed!")
            
            # Store results
            st.session_state.pipeline_results = results
            st.session_state.original_query = query
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Success message
            papers_found = results.get('papers_found', 0)
            top_papers = len(results.get('top_papers', []))
            duration = results.get('pipeline_duration', 0)
            
            if papers_found > 0:
                st.success(f"🎉 **Search complete!** Found {papers_found} relevant papers in {duration:.1f}s, showing top {top_papers}")
                st.info("💡 Select papers below to augment your search or save them to your collection")
            else:
                st.warning("⚠️ No papers found. Try adjusting your search query or filters.")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def execute_secondary_search(selected_indices: List[int]):
    """Execute secondary search using selected papers for keyword augmentation"""
    try:
        if not st.session_state.pipeline:
            st.error("❌ Pipeline not available")
            return
        
        if not hasattr(st.session_state, 'original_query'):
            st.error("❌ Original query not found")
            return
        
        # Initialize search iteration counter
        if not hasattr(st.session_state, 'search_iterations'):
            st.session_state.search_iterations = 1
        
        if not hasattr(st.session_state, 'augmented_queries'):
            st.session_state.augmented_queries = []
        
        # Progress indicators
        with st.spinner("🔍 Executing augmented search..."):
            results = st.session_state.pipeline.execute_secondary_search(
                selected_paper_indices=selected_indices,
                original_query=st.session_state.original_query
            )
        
        if results.get('new_papers_found', 0) > 0:
            st.session_state.search_iterations += 1
            st.session_state.augmented_queries.append(results.get('augmented_query', ''))
            
            # Update the results in session state
            if 'top_papers' in results:
                st.session_state.pipeline_results['top_papers'] = results['top_papers']
                st.session_state.pipeline_results['new_papers_found'] = results['new_papers_found']
                st.session_state.pipeline_results['selected_papers_count'] = results.get('selected_papers_count', 0)
                st.session_state.pipeline_results['new_relevant_papers_count'] = results.get('new_relevant_papers_count', 0)
                st.session_state.pipeline_results['total_available_papers'] = results.get('total_available_papers', 0)
                st.session_state.pipeline_results['papers_displayed'] = results.get('papers_displayed', 0)
            
            # Show success message with details
            selected_count = results.get('selected_papers_count', 0)
            new_count = results.get('new_relevant_papers_count', 0)
            total_available = results.get('total_available_papers', 0)
            papers_displayed = results.get('papers_displayed', 0)
            
            st.success(f"🎉 **Augmented search completed!**")
            st.info(f"📊 **Results:** {selected_count} selected papers from previous search + {new_count} new relevant papers = {total_available} total papers available")
            st.info(f"🖥️ **Display:** Showing top {papers_displayed} papers ranked by relevance")
            st.info(f"🔍 **Augmented query:** {results.get('augmented_query', '')}")
            
            st.rerun()
        else:
            st.warning("⚠️ No new papers found with augmented keywords. Try selecting different papers or refining your search.")
            
    except Exception as e:
        st.error(f"❌ Secondary search failed: {str(e)}")

def save_selected_papers(selected_indices: List[int]):
    """Save selected papers to user database"""
    try:
        if st.session_state.pipeline:
            result = st.session_state.pipeline.save_selected_papers(selected_indices)
            
            if result.get('success'):
                st.success(f"✅ {result.get('message')}")
            else:
                st.error(f"❌ {result.get('message')}")
        else:
            st.error("❌ Pipeline not available")
            
    except Exception as e:
        st.error(f"❌ Failed to save papers: {str(e)}")

if __name__ == "__main__":
    main()
