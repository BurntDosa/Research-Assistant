import streamlit as st
from typing import Callable

def render_literature_review_section(generate_callback: Callable):
    """Render the literature review section of the app"""
    st.markdown("""
    <div class="lit-review-section">
        <h2>Literature Review Generator</h2>
        <p>Generate a comprehensive literature review from your selected papers using our multi-agent system.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input("Research Topic", 
                            placeholder="Enter your research topic",
                            help="Provide a clear and specific research topic for the literature review")
        
    with col2:
        max_papers = st.number_input("Max Papers", 
                                   min_value=10, 
                                   max_value=50, 
                                   value=30,
                                   help="Maximum number of papers to include in the review")
    
    # Generate button
    if st.button("Generate Literature Review", 
                 disabled=st.session_state.generating_review,
                 help="Click to generate a literature review"):
        
        if not topic:
            st.warning("Please enter a research topic")
            return
            
        st.session_state.generating_review = True
        generate_callback(topic, max_papers)
    
    # Display the generated review
    if st.session_state.literature_review:
        st.markdown("### Generated Literature Review")
        st.markdown(st.session_state.literature_review)
        
        # Download button
        st.download_button(
            label="Download Review as Markdown",
            data=st.session_state.literature_review,
            file_name="literature_review.md",
            mime="text/markdown"
        )
