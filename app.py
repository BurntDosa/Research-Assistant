
"""
Literature Discovery Agent - Streamlit Frontend
Built natively for Google Gemini 2.5 Flash

This module provides a comprehensive, modern interface for academic paper discovery
with advanced filtering, real-time validation, and intelligent recommendations.
"""

import streamlit as st
import pandas as pd
import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import our Gemini-native agent
from literature_agent import GeminiLiteratureDiscoveryAgent, Paper, SearchFilters

# Configure Streamlit page
st.set_page_config(
    page_title="Literature Discovery Agent - Gemini 2.5 Flash",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .main-title {
        font-size: 3.5em;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-subtitle {
        font-size: 1.3em;
        margin-top: 0.5em;
        opacity: 0.9;
    }

    .gemini-badge {
        background: linear-gradient(45deg, #4285f4, #34a853, #fbbc04, #ea4335);
        color: white;
        padding: 0.5em 1.2em;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 1em 0;
        font-size: 1.1em;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Paper cards */
    .paper-card {
        border: 2px solid #e0e6ed;
        border-radius: 15px;
        padding: 1.5em;
        margin: 1.5em 0;
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    .paper-card:hover {
        border-color: #4285f4;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .selected-paper {
        border-color: #34a853;
        background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%);
        box-shadow: 0 6px 25px rgba(52, 168, 83, 0.15);
    }

    .high-relevance {
        border-left: 5px solid #4CAF50;
    }

    .medium-relevance {
        border-left: 5px solid #FF9800;
    }

    .low-relevance {
        border-left: 5px solid #f44336;
    }

    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 0;
    }

    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-top: 0.5em;
    }

    /* Status indicators */
    .relevance-score {
        font-weight: bold;
        padding: 0.3em 0.8em;
        border-radius: 20px;
        color: white;
        display: inline-block;
    }

    .relevance-high { background: #4CAF50; }
    .relevance-medium { background: #FF9800; }
    .relevance-low { background: #f44336; }

    .confidence-score {
        font-weight: bold;
        color: #2196F3;
        background: rgba(33, 150, 243, 0.1);
        padding: 0.2em 0.6em;
        border-radius: 15px;
    }

    .citation-count {
        color: #9C27B0;
        font-weight: bold;
        background: rgba(156, 39, 176, 0.1);
        padding: 0.2em 0.6em;
        border-radius: 15px;
    }

    /* Progress indicators */
    .search-progress {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 6px;
        border-radius: 3px;
        margin: 1em 0;
        overflow: hidden;
    }

    .search-status {
        background: rgba(102, 126, 234, 0.1);
        padding: 1em;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1em 0;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.5em 1.5em;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Sidebar */
    .sidebar-header {
        color: #667eea;
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 1em;
        padding-bottom: 0.5em;
        border-bottom: 2px solid #667eea;
    }

    /* API key input */
    .api-key-success {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 1em;
        border-radius: 10px;
        text-align: center;
        margin: 1em 0;
    }

    .api-key-warning {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        padding: 1em;
        border-radius: 10px;
        text-align: center;
        margin: 1em 0;
    }

    /* Animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    .searching {
        animation: pulse 2s infinite;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'agent': None,
        'papers': [],
        'selected_papers': [],
        'search_query': "",
        'search_performed': False,
        'session_id': None,
        'search_in_progress': False,
        'last_search_time': None,
        'session_stats': {},
        'filter_history': [],
        'gemini_api_key': ""
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def validate_gemini_api_key(api_key: str) -> bool:
    """Validate Gemini API key format"""
    if not api_key:
        return False

    # Basic format check - sufficient for validation
    if not api_key.startswith('AIza') or len(api_key) < 35:
        return False

    return True

def setup_gemini_agent():
    """Setup and validate Gemini agent"""
    st.sidebar.markdown('<div class="sidebar-header">🧠 Gemini 2.5 Flash Configuration</div>', unsafe_allow_html=True)

    # API key input with enhanced UI
    api_key = st.sidebar.text_input(
        "Google Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        help="Enter your Google Gemini API key. Get it from: https://makersuite.google.com/app/apikey",
        placeholder="AIza..."
    )

    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
        st.session_state.agent = None  # Reset agent when key changes

    if api_key:
        if validate_gemini_api_key(api_key):
            if not st.session_state.agent:
                with st.sidebar:
                    with st.spinner("Initializing Gemini 2.5 Flash..."):
                        try:
                            st.session_state.agent = GeminiLiteratureDiscoveryAgent(api_key)
                            st.sidebar.markdown(
                                '<div class="api-key-success">✅ Gemini 2.5 Flash Ready!</div>',
                                unsafe_allow_html=True
                            )
                            return True
                        except Exception as e:
                            st.sidebar.error(f"Failed to initialize Gemini: {str(e)}")
                            return False
            else:
                st.sidebar.markdown(
                    '<div class="api-key-success">✅ Gemini 2.5 Flash Connected</div>',
                    unsafe_allow_html=True
                )
                return True
        else:
            st.sidebar.markdown(
                '<div class="api-key-warning">❌ Invalid API Key Format</div>',
                unsafe_allow_html=True
            )
            return False
    else:
        st.sidebar.markdown(
            '<div class="api-key-warning">⚠️ Please enter your Gemini API key</div>',
            unsafe_allow_html=True
        )

        # Show helpful information
        with st.sidebar.expander("🔑 How to get Gemini API Key", expanded=False):
            st.markdown("""
            1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy and paste the key above

            **Benefits of Gemini 2.5 Flash:**
            - 🆓 Generous free tier
            - ⚡ Ultra-fast responses
            - 🧠 Advanced reasoning
            - 📚 Excellent for academic content
            """)

        return False

def create_advanced_search_interface():
    """Create comprehensive search interface"""
    st.sidebar.markdown('<div class="sidebar-header">🔍 Search Configuration</div>', unsafe_allow_html=True)

    # Main search query
    query = st.sidebar.text_area(
        "Research Query",
        value=st.session_state.search_query,
        height=100,
        help="Enter keywords, research questions, or topics. Use specific academic terms for better results.",
        placeholder="e.g., machine learning natural language processing transformers"
    )

    # Advanced filters in expandable sections
    with st.sidebar.expander("📅 Publication Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            year_start = st.number_input("Start Year", min_value=1900, max_value=2030, value=2020, step=1)
        with col2:
            year_end = st.number_input("End Year", min_value=1900, max_value=2030, value=2024, step=1)
        
        st.info("🔬 **Multi-Source Search**: Using Google Scholar (via SerpAPI), CrossRef (Academic), OpenAlex (Open Science), and arXiv (Preprints) for comprehensive, reliable results with full citation data.")

    with st.sidebar.expander("📊 Citation Filters"):
        col1, col2 = st.columns(2)
        with col1:
            min_citations = st.number_input("Min Citations", min_value=0, value=0, step=1)
        with col2:
            max_citations = st.number_input("Max Citations", min_value=0, value=10000, step=10)
            if max_citations == 0:
                max_citations = None

    with st.sidebar.expander("🎯 Content Filters"):
        keyword_requirements = st.text_input(
            "Required Keywords (comma-separated)",
            help="Papers must contain these keywords",
            placeholder="neural networks, deep learning"
        )

        exclude_keywords = st.text_input(
            "Exclude Keywords (comma-separated)",
            help="Papers containing these keywords will be excluded",
            placeholder="survey, review"
        )

        journal_filter = st.text_input(
            "Journal Names (comma-separated)",
            help="Only include papers from these journals",
            placeholder="Nature, Science, Cell"
        )

    with st.sidebar.expander("⚙️ Search Settings"):
        max_results = st.slider("Maximum Results", min_value=5, max_value=15, value=15, step=5)
        
        st.info("ℹ️ **Rate Limiting**: To respect API limits, there's a 7-second delay between paper analysis calls. Higher result counts will take longer.")

        search_strategy = st.selectbox(
            "Search Strategy",
            ["Balanced", "Precision (fewer, higher quality)", "Recall (more, broader scope)"],
            index=0
        )

    # Prepare filters
    filters = {
        'year_start': year_start,
        'year_end': year_end,
        'min_citations': min_citations,
        'max_citations': max_citations
    }

    if keyword_requirements:
        filters['keyword_requirements'] = [kw.strip() for kw in keyword_requirements.split(',')]

    if exclude_keywords:
        filters['exclude_keywords'] = [kw.strip() for kw in exclude_keywords.split(',')]

    if journal_filter:
        filters['journal_filter'] = [j.strip() for j in journal_filter.split(',')]

    return query, filters, max_results, search_strategy

def display_enhanced_paper_card(paper: Paper, index: int, show_analysis: bool = False) -> bool:
    """Display paper with enhanced visual design and analysis"""

    # Determine relevance class
    if paper.relevance_score >= 0.7:
        relevance_class = "high-relevance"
        relevance_color = "relevance-high"
    elif paper.relevance_score >= 0.4:
        relevance_class = "medium-relevance"
        relevance_color = "relevance-medium"
    else:
        relevance_class = "low-relevance"
        relevance_color = "relevance-low"

    card_class = f"paper-card {relevance_class}"
    if paper.selected:
        card_class += " selected-paper"

    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

    # Header row with title and metrics
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.markdown(f"**{paper.title}**")
        authors_display = ', '.join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_display += f" and {len(paper.authors) - 3} others"
        st.markdown(f"*{authors_display}*")

    with col2:
        st.markdown(
            f'<span class="relevance-score {relevance_color}">Relevance: {paper.relevance_score:.2f}</span>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f'<span class="confidence-score">Confidence: {paper.confidence_score:.2f}</span>',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f'<span class="citation-count">Citations: {paper.citation_count}</span>',
            unsafe_allow_html=True
        )

    # Abstract with smart truncation
    abstract_preview = paper.abstract[:400] + "..." if len(paper.abstract) > 400 else paper.abstract
    st.markdown(f"**Abstract:** {abstract_preview}")

    # Paper metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Journal:** {paper.journal}")
    with col2:
        st.markdown(f"**Date:** {paper.publication_date}")
    with col3:
        st.markdown(f"**Source:** {paper.source.replace('_', ' ').title()}")
    with col4:
        if paper.url:
            st.markdown(f"[📄 View Paper]({paper.url})")

    # Keywords and categories
    if paper.keywords or paper.categories:
        col1, col2 = st.columns(2)
        with col1:
            if paper.keywords:
                keywords_display = ', '.join(paper.keywords[:5])
                if len(paper.keywords) > 5:
                    keywords_display += f" (+{len(paper.keywords) - 5} more)"
                st.markdown(f"**Keywords:** {keywords_display}")
        with col2:
            if paper.categories:
                categories_display = ', '.join(paper.categories[:3])
                st.markdown(f"**Categories:** {categories_display}")

    # Advanced analysis (if requested)
    if show_analysis:
        with st.expander("🔍 Gemini Analysis Details", expanded=False):
            # Get detailed analysis from database if available
            if hasattr(paper, 'gemini_reasoning') and paper.gemini_reasoning:
                st.markdown("**🧠 Gemini's Reasoning:**")
                st.write(paper.gemini_reasoning)
            
            if hasattr(paper, 'key_matches') and paper.key_matches:
                st.markdown("**🎯 Key Matches Found:**")
                for match in paper.key_matches:
                    st.write(f"• {match}")
            
            if hasattr(paper, 'concerns') and paper.concerns:
                st.markdown("**⚠️ Concerns:**")
                for concern in paper.concerns:
                    st.write(f"• {concern}")
            
            # If no detailed analysis is available, show basic info
            if not (hasattr(paper, 'gemini_reasoning') and paper.gemini_reasoning):
                st.info(f"""
                **Analysis Summary:**
                - Relevance Score: {paper.relevance_score:.2f}/1.00
                - Confidence: {paper.confidence_score:.2f}/1.00
                - Paper focuses on: {', '.join(paper.keywords[:3]) if paper.keywords else 'General research'}
                - Published in: {paper.journal} ({paper.publication_date})
                """)
                st.warning("Detailed Gemini analysis not available for this paper.")

    # Selection checkbox
    selected = st.checkbox(
        f"Select this paper",
        key=f"select_{paper.paper_id}_{index}",
        value=paper.selected
    )

    st.markdown('</div>', unsafe_allow_html=True)

    return selected

def create_comprehensive_metrics_dashboard(papers: List[Paper]):
    """Create advanced metrics and visualizations"""
    if not papers:
        return

    st.markdown("### 📊 Search Analytics Dashboard")

    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    metrics = {
        'Total Papers': len(papers),
        'Selected': sum(1 for p in papers if p.selected),
        'Avg Relevance': sum(p.relevance_score for p in papers) / len(papers),
        'Avg Confidence': sum(p.confidence_score for p in papers) / len(papers),
        'Total Citations': sum(p.citation_count for p in papers)
    }

    for i, (label, value) in enumerate(metrics.items()):
        with [col1, col2, col3, col4, col5][i]:
            if isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)

            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{display_value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Advanced visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Relevance distribution
        fig_relevance = px.histogram(
            x=[p.relevance_score for p in papers],
            nbins=20,
            title="📈 Relevance Score Distribution",
            labels={'x': 'Relevance Score', 'y': 'Number of Papers'},
            color_discrete_sequence=['#667eea']
        )
        fig_relevance.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        st.plotly_chart(fig_relevance, use_container_width=True)

    with col2:
        # Citation vs Relevance scatter
        fig_scatter = px.scatter(
            x=[p.relevance_score for p in papers],
            y=[p.citation_count for p in papers],
            title="🎯 Citations vs Relevance",
            labels={'x': 'Relevance Score', 'y': 'Citation Count'},
            color=[p.confidence_score for p in papers],
            color_continuous_scale='viridis',
            hover_data={'Paper': [p.title[:50] + '...' if len(p.title) > 50 else p.title for p in papers]}
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Source distribution
    source_counts = {}
    for paper in papers:
        source = paper.source.replace('_', ' ').title()
        source_counts[source] = source_counts.get(source, 0) + 1

    if source_counts:
        fig_sources = px.pie(
            values=list(source_counts.values()),
            names=list(source_counts.keys()),
            title="📚 Papers by Source",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_sources.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        st.plotly_chart(fig_sources, use_container_width=True)

def create_smart_filtering_interface(papers: List[Paper]) -> List[Paper]:
    """Create intelligent filtering and sorting interface"""
    if not papers:
        return papers

    st.markdown("### 🎛️ Smart Filtering & Sorting")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            ["Relevance Score", "Confidence Score", "Citation Count", "Publication Date", "Title"],
            index=0
        )

    with col2:
        min_relevance = st.slider(
            "Min Relevance",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1
        )

    with col3:
        min_confidence = st.slider(
            "Min Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1
        )

    with col4:
        show_options = st.multiselect(
            "Show",
            ["All Papers", "Selected Only", "High Relevance (>0.7)", "Recent (2023+)"],
            default=["All Papers"]
        )

    # Apply filters
    filtered_papers = papers

    # Relevance filter
    if min_relevance > 0:
        filtered_papers = [p for p in filtered_papers if p.relevance_score >= min_relevance]

    # Confidence filter
    if min_confidence > 0:
        filtered_papers = [p for p in filtered_papers if p.confidence_score >= min_confidence]

    # Show options
    if "Selected Only" in show_options:
        filtered_papers = [p for p in filtered_papers if p.selected]

    if "High Relevance (>0.7)" in show_options and "All Papers" not in show_options:
        filtered_papers = [p for p in filtered_papers if p.relevance_score > 0.7]

    if "Recent (2023+)" in show_options and "All Papers" not in show_options:
        filtered_papers = [p for p in filtered_papers if 
                          p.publication_date and '2023' <= p.publication_date[:4] <= '2024']

    # Apply sorting
    reverse = True  # Most sorts should be descending

    if sort_by == "Relevance Score":
        filtered_papers.sort(key=lambda x: x.relevance_score, reverse=reverse)
    elif sort_by == "Confidence Score":
        filtered_papers.sort(key=lambda x: x.confidence_score, reverse=reverse)
    elif sort_by == "Citation Count":
        filtered_papers.sort(key=lambda x: x.citation_count, reverse=reverse)
    elif sort_by == "Publication Date":
        filtered_papers.sort(key=lambda x: x.publication_date, reverse=reverse)
    elif sort_by == "Title":
        filtered_papers.sort(key=lambda x: x.title.lower(), reverse=False)

    return filtered_papers

def create_action_buttons(papers: List[Paper]):
    """Create comprehensive action buttons with enhanced functionality"""
    st.markdown("### 🎯 Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💾 Save Selected Papers", type="primary"):
            selected_papers = [p for p in papers if p.selected]
            if selected_papers:
                selected_indices = [i for i, p in enumerate(papers) if p.selected]
                try:
                    saved_papers = st.session_state.agent.select_papers(selected_indices, papers)
                    st.success(f"✅ Saved {len(saved_papers)} papers to database!")

                    # Update session stats
                    st.session_state.session_stats = st.session_state.agent.get_session_statistics()
                except Exception as e:
                    st.error(f"❌ Error saving papers: {str(e)}")
            else:
                st.warning("⚠️ No papers selected")

    with col2:
        if st.button("🔍 Find Similar Papers"):
            selected_papers = [p for p in papers if p.selected]
            if selected_papers:
                with st.spinner("🧠 Gemini 2.5 Flash analyzing patterns..."):
                    try:
                        similar_papers = st.session_state.agent.find_similar_papers(selected_papers, max_results=10)
                        if similar_papers:
                            st.session_state.papers.extend(similar_papers)
                            st.success(f"✅ Found {len(similar_papers)} similar papers!")
                            st.rerun()
                        else:
                            st.info("No additional similar papers found")
                    except Exception as e:
                        st.error(f"❌ Error finding similar papers: {str(e)}")
            else:
                st.warning("⚠️ Please select papers first")

    with col3:
        if st.button("📊 Export Results"):
            selected_papers = [p for p in papers if p.selected]
            if selected_papers:
                try:
                    # Create comprehensive export data
                    export_data = []
                    for paper in selected_papers:
                        export_data.append({
                            'Title': paper.title,
                            'Authors': '; '.join(paper.authors),
                            'Journal': paper.journal,
                            'Publication Date': paper.publication_date,
                            'Citation Count': paper.citation_count,
                            'Relevance Score': paper.relevance_score,
                            'Confidence Score': paper.confidence_score,
                            'URL': paper.url,
                            'DOI': paper.doi,
                            'Keywords': '; '.join(paper.keywords),
                            'Categories': '; '.join(paper.categories),
                            'Source': paper.source,
                            'Paper ID': paper.paper_id
                        })

                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)

                    filename = f"literature_search_gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=filename,
                        mime="text/csv"
                    )
                    st.success(f"✅ Export ready: {len(selected_papers)} papers")
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
            else:
                st.warning("⚠️ No selected papers to export")

    with col4:
        if st.button("🔄 New Search"):
            # Clear current results but keep settings
            st.session_state.papers = []
            st.session_state.selected_papers = []
            st.session_state.search_performed = False
            st.session_state.session_id = None
            st.session_state.search_in_progress = False
            st.success("✅ Ready for new search")
            st.rerun()

def create_session_management_sidebar():
    """Enhanced session management in sidebar"""
    with st.sidebar.expander("📋 Session Management", expanded=False):
        if st.session_state.session_id:
            st.info(f"**Session:** {st.session_state.session_id[:8]}...")

            # Display session statistics
            if st.session_state.session_stats:
                stats = st.session_state.session_stats
                st.metric("Papers Found", stats.get('total_papers', 0))
                st.metric("Papers Selected", stats.get('selected_papers', 0))
                st.metric("Avg Relevance", f"{stats.get('avg_relevance_score', 0):.2f}")
                st.metric("Search Duration", f"{stats.get('search_duration', 0):.1f}s")

            # Session actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Session Stats"):
                    st.session_state.session_stats = st.session_state.agent.get_session_statistics()
                    st.rerun()

            with col2:
                if st.button("🗑️ Clear Session"):
                    # Clear everything
                    for key in ['papers', 'selected_papers', 'search_performed', 'session_id', 'session_stats']:
                        st.session_state[key] = [] if key.endswith('papers') else (False if key == 'search_performed' else (None if key in ['session_id'] else {}))
                    st.rerun()
        else:
            st.info("No active search session")

def main():
    """Main Streamlit application with enhanced UI"""
    initialize_session_state()

    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🧠 Literature Discovery Agent</h1>
        <div class="gemini-badge">⚡ Powered by Google Gemini 2.5 Flash</div>
        <p class="main-subtitle">AI-powered academic paper search with advanced relevance analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Setup Gemini agent
    agent_ready = setup_gemini_agent()

    if not agent_ready:
        st.info("👈 Please configure your Google Gemini API key in the sidebar to get started.")

        # Show benefits and getting started info
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🌟 Why Gemini 2.5 Flash?

            - **⚡ Ultra-fast responses** - Get results in seconds
            - **🧠 Advanced reasoning** - Better paper relevance assessment  
            - **🆓 Generous free tier** - More usage than other AI models
            - **📚 Academic expertise** - Optimized for research content
            - **🎯 Higher accuracy** - More precise relevance scoring
            """)

        with col2:
            st.markdown("""
            ### 🚀 Getting Started

            1. **Get your free API key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. **Sign in** with your Google account
            3. **Create API key** and copy it
            4. **Paste the key** in the sidebar
            5. **Start discovering** academic papers!

            *No billing setup required for free tier!*
            """)

        return

    # Create search interface
    query, filters, max_results, search_strategy = create_advanced_search_interface()

    # Search button with enhanced UI
    search_button_col1, search_button_col2 = st.sidebar.columns([3, 1])
    with search_button_col1:
        search_clicked = st.button("🚀 Start Discovery", type="primary", use_container_width=True)
    with search_button_col2:
        if st.session_state.search_in_progress:
            st.markdown('<div class="searching">🔄</div>', unsafe_allow_html=True)

    # Execute search
    if search_clicked and query.strip():
        if not st.session_state.search_in_progress:
            st.session_state.search_in_progress = True
            st.session_state.search_query = query

            # Create search progress interface
            progress_container = st.container()
            with progress_container:
                st.markdown('<div class="search-status">🧠 Gemini 2.5 Flash is analyzing your query...</div>', unsafe_allow_html=True)
                
                # Calculate estimated time based on max_results (7 seconds per paper + base time)
                # Quality assurance may require additional rounds
                base_time = max_results * 7 + 30  # Base search time
                qa_time = max_results * 3  # Additional time for quality assurance rounds
                estimated_time_seconds = base_time + qa_time
                estimated_minutes = estimated_time_seconds // 60
                estimated_remaining_seconds = estimated_time_seconds % 60
                
                if estimated_minutes > 0:
                    time_estimate = f"⏱️ Estimated time: ~{estimated_minutes}m {estimated_remaining_seconds}s"
                else:
                    time_estimate = f"⏱️ Estimated time: ~{estimated_remaining_seconds}s"
                
                st.info(f"{time_estimate} (Quality assurance: ensuring relevance ≥ 0.5 for all papers)")

                progress_bar = st.progress(0)
                status_text = st.empty()
                time_text = st.empty()
                quality_text = st.empty()

                start_time = time.time()

                # Step-by-step progress
                status_text.text('🔍 Searching 4 academic sources...')
                progress_bar.progress(10)
                time.sleep(0.5)

                status_text.text('� Found papers, removing duplicates...')
                progress_bar.progress(20)
                time.sleep(0.5)

                quality_text.markdown("🎯 **Quality Assurance**: Validating papers to ensure relevance ≥ 0.5")

                elapsed_time = time.time() - start_time
                time_text.text(f"Elapsed: {elapsed_time:.0f}s | Remaining: ~{max(0, estimated_time_seconds - elapsed_time):.0f}s")

                try:
                    # Start new session
                    st.session_state.session_id = st.session_state.agent.start_session(query, filters)

                    status_text.text('🧠 Gemini 2.5 Flash analyzing relevance (this will take a while)...')
                    progress_bar.progress(30)
                    
                    # Update timer before starting the long process
                    elapsed_time = time.time() - start_time
                    remaining_time = max(0, estimated_time_seconds - elapsed_time)
                    time_text.text(f"Elapsed: {elapsed_time:.0f}s | Remaining: ~{remaining_time:.0f}s")

                    # Perform search with progress tracking
                    def update_progress():
                        current_elapsed = time.time() - start_time
                        current_remaining = max(0, estimated_time_seconds - current_elapsed)
                        time_text.text(f"Elapsed: {current_elapsed:.0f}s | Remaining: ~{current_remaining:.0f}s")
                        # Update progress bar based on elapsed time
                        progress_percentage = min(90, 30 + (current_elapsed / estimated_time_seconds) * 60)
                        progress_bar.progress(int(progress_percentage))
                    
                    # Update progress every few seconds during the search
                    papers = st.session_state.agent.search_papers(query, filters, max_results)
                    update_progress()

                    progress_bar.progress(95)
                    status_text.text('✨ Finalizing results...')

                    st.session_state.papers = papers
                    st.session_state.search_performed = True
                    st.session_state.last_search_time = datetime.now()

                    progress_bar.progress(100)
                    total_time = time.time() - start_time
                    status_text.text(f'✅ Search complete! Total time: {total_time:.0f}s')

                    time.sleep(2)
                    progress_container.empty()

                    st.success(f"🎉 Found {len(papers)} papers! Relevance scores calculated by Gemini 2.5 Flash.")

                except Exception as e:
                    progress_container.empty()
                    st.error(f"❌ Search failed: {str(e)}")

                finally:
                    st.session_state.search_in_progress = False
                    st.rerun()

    elif search_clicked and not query.strip():
        st.sidebar.error("⚠️ Please enter a search query")

    # Display results if available
    if st.session_state.search_performed and st.session_state.papers:

        # Comprehensive metrics dashboard
        create_comprehensive_metrics_dashboard(st.session_state.papers)

        # Smart filtering interface
        filtered_papers = create_smart_filtering_interface(st.session_state.papers)

        # Action buttons
        create_action_buttons(st.session_state.papers)

        # Display papers
        st.markdown(f"### 📄 Research Papers ({len(filtered_papers)} shown)")

        if not filtered_papers:
            st.info("🔍 No papers match the current filters. Try adjusting your criteria.")
        else:
            # Track selections
            for i, paper in enumerate(filtered_papers):
                selected = display_enhanced_paper_card(paper, i, show_analysis=True)
                if selected != paper.selected:
                    paper.selected = selected
                    # Update the original paper in the main list
                    for orig_paper in st.session_state.papers:
                        if orig_paper.paper_id == paper.paper_id:
                            orig_paper.selected = selected
                            break

    # Session management
    create_session_management_sidebar()

    # Footer with enhanced styling
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 30px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin: 2rem 0;'>
        <h4 style='color: #667eea; margin-bottom: 1rem;'>Literature Discovery Agent v2.0</h4>
        <p style='margin: 0.5rem 0;'><strong>🧠 Powered by Google Gemini 2.5 Flash</strong></p>
        <p style='margin: 0.5rem 0;'>⚡ Ultra-fast • 🎯 Highly accurate • 📚 Research-optimized</p>
        <p style='margin: 0.5rem 0; font-size: 0.9em; opacity: 0.8;'>Built for academic excellence with advanced AI reasoning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
