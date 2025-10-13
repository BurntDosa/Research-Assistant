#!/usr/bin/env python3
"""
Research Gap Analysis Agent
Identifies gaps in current literature and suggests potential research topics
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchGapAnalyzer:
    """Analyzes literature to identify research gaps and suggest new topics"""
    
    def __init__(self):
        """Initialize the Research Gap Analyzer with Gemini AI"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Research Gap Analyzer initialized with Gemini 2.5 Flash")
    
    def analyze_research_gaps(self, papers: List[Dict[str, Any]], original_query: str = "") -> Dict[str, Any]:
        """
        Analyze a collection of papers to identify research gaps
        
        Args:
            papers: List of paper dictionaries with metadata
            original_query: The original research query (optional)
        
        Returns:
            Dictionary containing identified gaps and research suggestions
        """
        try:
            if not papers or len(papers) == 0:
                return {
                    'success': False,
                    'message': 'No papers provided for gap analysis'
                }
            
            logger.info(f"Analyzing {len(papers)} papers for research gaps")
            
            # Prepare paper summaries for analysis
            paper_summaries = self._prepare_paper_summaries(papers[:20])  # Limit to 20 papers
            
            # Generate comprehensive gap analysis
            gaps_analysis = self._identify_gaps_with_ai(paper_summaries, original_query)
            
            if not gaps_analysis:
                return {
                    'success': False,
                    'message': 'Failed to generate gap analysis'
                }
            
            # Parse the analysis into structured format
            structured_gaps = self._structure_gap_analysis(gaps_analysis)
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'papers_analyzed': len(papers),
                'original_query': original_query,
                'raw_analysis': gaps_analysis,
                **structured_gaps
            }
            
            logger.info(f"Gap analysis complete: found {len(structured_gaps.get('identified_gaps', []))} gaps")
            return result
            
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {
                'success': False,
                'message': f'Gap analysis error: {str(e)}'
            }
    
    def _prepare_paper_summaries(self, papers: List[Dict[str, Any]]) -> str:
        """Prepare concise summaries of papers for AI analysis"""
        summaries = []
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            abstract = paper.get('abstract', '')
            year = paper.get('publication_date', 'Unknown')
            methods = paper.get('keywords', [])
            
            summary = f"""
Paper {i}:
Title: {title}
Year: {year}
Abstract: {abstract[:400] if abstract else 'No abstract available'}
Keywords/Methods: {', '.join(methods[:8]) if methods else 'Not specified'}
"""
            summaries.append(summary.strip())
        
        return "\n\n---\n\n".join(summaries)
    
    def _identify_gaps_with_ai(self, paper_summaries: str, original_query: str) -> str:
        """Use Gemini AI to identify research gaps"""
        try:
            prompt = f"""You are a research analyst specializing in identifying gaps in academic literature and suggesting novel research directions.

Original Research Area: {original_query if original_query else "General literature review"}

Current Literature Summary:
{paper_summaries}

Based on these papers, conduct a comprehensive gap analysis and provide:

1. **IDENTIFIED GAPS** (5-7 specific gaps):
   - List clear, specific gaps in the current research
   - For each gap, explain why it's important and what's missing
   - Focus on:
     * Methodological gaps (unexplored methods or approaches)
     * Empirical gaps (understudied populations, contexts, or scenarios)
     * Theoretical gaps (missing frameworks or conceptual models)
     * Temporal gaps (outdated research needing updates)
     * Cross-disciplinary gaps (lack of interdisciplinary approaches)

2. **PROMISING RESEARCH TOPICS** (8-10 specific topics):
   - Suggest concrete, actionable research questions or topics
   - Each topic should be:
     * Novel and original
     * Feasible for a researcher to pursue
     * Grounded in the identified gaps
     * Likely to make a meaningful contribution
   - Include brief rationale for each topic

3. **EMERGING TRENDS** (3-5 trends):
   - Identify patterns or emerging directions across the papers
   - Highlight areas gaining momentum but still underexplored

4. **METHODOLOGICAL OPPORTUNITIES** (3-4 suggestions):
   - Suggest new methods, tools, or approaches that could advance the field
   - Consider novel data sources, analytical techniques, or experimental designs

5. **INTERDISCIPLINARY CONNECTIONS** (2-3 connections):
   - Identify opportunities to bridge this research area with other fields
   - Suggest how cross-pollination could yield insights

Format your response in clear markdown with headers and bullet points. Be specific, actionable, and research-oriented.
"""

            response = self.model.generate_content(prompt)
            analysis = response.text.strip()
            
            if not analysis or len(analysis) < 100:
                logger.warning("Received suspiciously short gap analysis response")
                return None
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI gap identification failed: {e}")
            return None
    
    def _structure_gap_analysis(self, raw_analysis: str) -> Dict[str, Any]:
        """Parse the raw AI analysis into structured format"""
        try:
            # Extract sections using simple parsing
            sections = {
                'identified_gaps': [],
                'research_topics': [],
                'emerging_trends': [],
                'methodological_opportunities': [],
                'interdisciplinary_connections': []
            }
            
            current_section = None
            current_items = []
            
            lines = raw_analysis.split('\n')
            
            for line in lines:
                line_lower = line.lower().strip()
                
                # Detect section headers
                if 'identified gap' in line_lower or 'gaps in' in line_lower:
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = 'identified_gaps'
                    current_items = []
                elif 'research topic' in line_lower or 'promising topic' in line_lower or 'research question' in line_lower:
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = 'research_topics'
                    current_items = []
                elif 'emerging trend' in line_lower or 'current trend' in line_lower:
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = 'emerging_trends'
                    current_items = []
                elif 'methodological' in line_lower and 'opportunit' in line_lower:
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = 'methodological_opportunities'
                    current_items = []
                elif 'interdisciplinary' in line_lower or 'cross-disciplinary' in line_lower:
                    if current_section and current_items:
                        sections[current_section] = current_items
                    current_section = 'interdisciplinary_connections'
                    current_items = []
                # Extract bullet points and numbered items
                elif current_section:
                    # Check for bullet points, numbered items, or bold items
                    if (line.strip().startswith(('-', '*', '•')) or 
                        (len(line.strip()) > 0 and line.strip()[0].isdigit() and '.' in line[:5]) or
                        line.strip().startswith('**')):
                        # Clean the line
                        item = line.strip()
                        # Remove markdown formatting
                        item = item.lstrip('-*•0123456789. ')
                        item = item.replace('**', '')
                        if item and len(item) > 10:
                            current_items.append(item)
            
            # Add last section
            if current_section and current_items:
                sections[current_section] = current_items
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to structure gap analysis: {e}")
            return {
                'identified_gaps': [],
                'research_topics': [],
                'emerging_trends': [],
                'methodological_opportunities': [],
                'interdisciplinary_connections': []
            }
    
    def generate_research_proposal_outline(self, gap: str, papers: List[Dict[str, Any]]) -> str:
        """
        Generate a research proposal outline for a specific gap
        
        Args:
            gap: The identified research gap to address
            papers: Related papers for context
        
        Returns:
            A research proposal outline as markdown text
        """
        try:
            # Prepare relevant paper context
            paper_context = self._prepare_paper_summaries(papers[:10])
            
            prompt = f"""You are a research advisor helping to develop a research proposal.

Research Gap to Address:
{gap}

Context from Related Literature:
{paper_context}

Create a detailed research proposal outline that addresses this gap. Include:

1. **Research Title** (compelling and descriptive)

2. **Background & Motivation** (2-3 paragraphs)
   - Why is this gap important?
   - What are the implications of not addressing it?

3. **Research Questions** (3-4 specific questions)

4. **Proposed Methodology**
   - Research design
   - Data collection approach
   - Analysis methods
   - Expected challenges and solutions

5. **Expected Contributions**
   - Theoretical contributions
   - Practical implications
   - Novelty of the approach

6. **Timeline** (rough milestones)

7. **Required Resources**

Format in clear markdown. Be specific and actionable.
"""
            
            response = self.model.generate_content(prompt)
            outline = response.text.strip()
            
            logger.info("Generated research proposal outline")
            return outline
            
        except Exception as e:
            logger.error(f"Failed to generate proposal outline: {e}")
            return f"Error generating proposal outline: {str(e)}"


if __name__ == "__main__":
    # Example usage
    analyzer = ResearchGapAnalyzer()
    
    # Test with sample papers
    sample_papers = [
        {
            'title': 'Machine Learning in Healthcare: A Survey',
            'abstract': 'This paper surveys the application of machine learning techniques in healthcare...',
            'publication_date': '2023',
            'keywords': ['machine learning', 'healthcare', 'deep learning']
        },
        {
            'title': 'Deep Learning for Medical Image Analysis',
            'abstract': 'Deep learning has shown remarkable success in medical image analysis...',
            'publication_date': '2024',
            'keywords': ['deep learning', 'medical imaging', 'CNN']
        }
    ]
    
    result = analyzer.analyze_research_gaps(sample_papers, "machine learning in healthcare")
    
    if result['success']:
        print("✅ Gap Analysis Complete!")
        print(f"\nIdentified Gaps: {len(result['identified_gaps'])}")
        print(f"Research Topics: {len(result['research_topics'])}")
    else:
        print(f"❌ Analysis Failed: {result['message']}")
