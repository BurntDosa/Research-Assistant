"""
Literature Review Multi-Agent System

This module implements a multi-agent system for generating literature reviews
using a Manager Agent and a Writing Agent that collaborate through LangChain.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from langchain.agents import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .embedding_agent import EmbeddedPaper, FAISSVectorDatabase

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReviewSection:
    """Structure for a section in the literature review"""
    title: str
    content: str
    papers_cited: List[str]
    subsections: List['ReviewSection']
    feedback: Optional[str] = None

class ReviewOutline(BaseModel):
    """Structure for the complete review outline"""
    title: str = Field(description="Title of the literature review")
    sections: List[Dict] = Field(description="List of sections and subsections")
    key_themes: List[str] = Field(description="Key themes to be covered")
    target_length: int = Field(description="Target word count")

class ManagerAgent:
    """
    Agent responsible for maintaining review structure and providing oversight
    """
    def __init__(self, vector_db: FAISSVectorDatabase):
        self.vector_db = vector_db
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                         temperature=0.3)
        self.current_outline: Optional[ReviewOutline] = None
        
    def create_initial_outline(self, topic: str, papers: List[EmbeddedPaper]) -> ReviewOutline:
        """Generate initial review structure based on available papers"""
        papers_text = "\n".join([
            f"Title: {p.title}\nAbstract: {p.abstract}\nType: {p.paper_type}"
            for p in papers[:10]  # Use top 10 papers for outline
        ])
        
        prompt_messages = [
            SystemMessage(content="""You are an expert research paper organizer.
            Create a detailed outline for a literature review with clear sections.
            Focus on logical flow and comprehensive coverage of the topic.
            Provide a simple, clear structure."""),
            HumanMessage(content=f"""
            Topic: {topic}
            Available Papers:
            {papers_text}
            
            Create a structured outline with:
            1. A clear title for the literature review
            2. 4-6 main sections that logically cover the topic
            3. Key themes that should be addressed
            
            Keep the response concise and well-structured.
            """)
        ]
        
        # Get response and create outline manually
        response = self.llm.invoke(prompt_messages)
        
        # Create a simple outline structure based on the response
        self.current_outline = ReviewOutline(
            title=f"Literature Review: {topic}",
            sections=[
                {"title": "Introduction", "subsections": []},
                {"title": "Methodology", "subsections": []},
                {"title": "Current State of Research", "subsections": []},
                {"title": "Key Findings and Trends", "subsections": []},
                {"title": "Future Directions", "subsections": []},
                {"title": "Conclusion", "subsections": []}
            ],
            key_themes=[topic, "current research", "methodologies", "applications"],
            target_length=2000
        )
        return self.current_outline

    def validate_section(self, section_content: str, cited_papers: List[str]) -> Dict[str, Any]:
        """Validate section content matches outline and uses correct citations"""
        if not self.current_outline:
            raise ValueError("No outline created. Call create_initial_outline first.")
        
        prompt_messages = [
            SystemMessage(content="""You are a research paper validator.
            Check if the section content follows the outline and uses citations properly.
            Identify any issues with structure, flow, or citation usage."""),
            HumanMessage(content=f"""
            Current Outline: {self.current_outline.dict()}
            Section Content: {section_content}
            Papers Cited: {cited_papers}
            
            Validate:
            1. Content follows outline
            2. All citations are from provided papers
            3. Proper academic style
            4. Logical flow
            """)
        ]
        
        response = self.llm.invoke(prompt_messages)
        # Parse validation results
        validation_result = {
            'needs_revision': False,
            'feedback': '',
            'structural_issues': [],
            'citation_issues': []
        }
        
        # Process validation response
        validation_text = response.content.lower()
        if any(issue in validation_text for issue in ['revise', 'fix', 'error', 'problem']):
            validation_result['needs_revision'] = True
            validation_result['feedback'] = response.content
        
        return validation_result

    def suggest_revisions(self, section: ReviewSection) -> Dict[str, Any]:
        """Suggest specific revisions for a section"""
        prompt_messages = [
            SystemMessage(content="""You are a research paper revision expert.
            Suggest specific improvements while maintaining academic integrity."""),
            HumanMessage(content=f"""
            Section Title: {section.title}
            Current Content: {section.content}
            Papers Cited: {section.papers_cited}
            Previous Feedback: {section.feedback}
            
            Provide specific revision suggestions for:
            1. Structure and flow
            2. Citation usage
            3. Academic language
            4. Content depth
            """)
        ]
        
        response = self.llm.invoke(prompt_messages)
        return {
            'suggestions': response.content,
            'priority': 'high' if 'urgent' in response.content.lower() else 'medium'
        }

class WritingAgent:
    """
    Agent responsible for writing review content following manager's outline
    """
    def __init__(self, vector_db: FAISSVectorDatabase):
        self.vector_db = vector_db
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                         temperature=0.7)
        self.citation_style = "APA"
        
    def write_section(self, section_title: str, 
                     relevant_papers: List[EmbeddedPaper],
                     previous_sections: List[str]) -> ReviewSection:
        """Generate content for a specific section using provided papers"""
        papers_text = "\n".join([
            f"Title: {p.title}\nAbstract: {p.abstract}\nAuthors: {', '.join(p.authors)}"
            for p in relevant_papers
        ])
        
        context = "\n".join(previous_sections[-2:]) if previous_sections else ""
        
        prompt_messages = [
            SystemMessage(content=f"""You are an academic writing expert.
            Write a coherent section of a literature review using only the provided papers.
            Use {self.citation_style} citation style and maintain academic tone."""),
            HumanMessage(content=f"""
            Section Title: {section_title}
            Available Papers:
            {papers_text}
            
            Previous Context:
            {context}
            
            Write a comprehensive section that:
            1. Synthesizes the papers' findings
            2. Uses proper citations
            3. Maintains flow with previous sections
            4. Identifies key themes and gaps
            5. Uses appropriate transition phrases
            """)
        ]
        
        response = self.llm.invoke(prompt_messages)
        
        # Extract citations from content
        cited_papers = [
            p.paper_id for p in relevant_papers
            if p.title.lower() in response.content.lower()
        ]
        
        return ReviewSection(
            title=section_title,
            content=response.content,
            papers_cited=cited_papers,
            subsections=[]
        )
    
    def revise_section(self, section: ReviewSection, feedback: Dict[str, Any]) -> ReviewSection:
        """Revise a section based on manager's feedback"""
        prompt_messages = [
            SystemMessage(content="""You are an academic revision expert.
            Revise the section based on provided feedback while maintaining academic integrity."""),
            HumanMessage(content=f"""
            Original Section: {section.content}
            Feedback: {feedback['suggestions']}
            Priority: {feedback['priority']}
            
            Revise the section to:
            1. Address all feedback points
            2. Maintain citation accuracy
            3. Improve flow and clarity
            4. Enhance academic style
            """)
        ]
        
        response = self.llm.invoke(prompt_messages)
        
        section.content = response.content
        section.feedback = feedback['suggestions']
        return section

class LiteratureReviewCoordinator:
    """
    Coordinates interaction between Manager and Writing agents
    """
    def __init__(self, vector_db_path: str = "data/faiss_paper_embeddings", vector_db=None):
        try:
            if vector_db is not None:
                self.vector_db = vector_db
            else:
                self.vector_db = FAISSVectorDatabase(vector_db_path)
            
            # Initialize LLM directly for simplified approach
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
            logger.info("Literature Review Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Literature Review Coordinator: {e}")
            raise
        
    def generate_review(self, topic: str, max_papers: int = 30) -> str:
        """
        Generate complete literature review through simplified agent collaboration
        """
        logger.info(f"Starting literature review generation for topic: {topic}")
        
        try:
            # 1. Get relevant papers
            papers = self.vector_db.search_similar_papers(topic, k=max_papers)
            logger.info(f"Found {len(papers)} relevant papers")
            
            if not papers:
                return f"# Literature Review: {topic}\n\nNo relevant papers found in the database. Please save some papers first before generating a literature review."
            
            # 2. Create a comprehensive literature review in one go
            papers_text = "\n\n".join([
                f"**Paper {i+1}:** {p.title}\n"
                f"**Authors:** {', '.join(p.authors) if p.authors else 'Unknown'}\n"
                f"**Journal:** {p.journal}\n"
                f"**Abstract:** {p.abstract}\n"
                f"**Type:** {p.paper_type}\n"
                f"**Relevance Score:** {p.relevance_score:.2f}"
                for i, p in enumerate(papers[:15])  # Use top 15 papers
            ])
            
            prompt_messages = [
                SystemMessage(content=f"""You are an expert academic writer specializing in literature reviews.
                Create a comprehensive, well-structured literature review on the topic: {topic}
                
                Structure your review with:
                1. Title and Abstract
                2. Introduction
                3. Current State of Research
                4. Key Methodologies and Approaches
                5. Findings and Trends
                6. Gaps and Future Directions
                7. Conclusion
                8. References
                
                Write in formal academic style with proper citations."""),
                HumanMessage(content=f"""
                Topic: {topic}
                
                Available Research Papers:
                {papers_text}
                
                Generate a comprehensive literature review (2000-3000 words) that:
                - Synthesizes the key findings from these papers
                - Identifies major themes and trends
                - Discusses methodological approaches
                - Highlights research gaps
                - Suggests future research directions
                - Uses proper academic formatting
                
                Make sure to reference the papers by their titles in your review.
                """)
            ]
            
            logger.info("Generating comprehensive literature review...")
            response = self.llm.invoke(prompt_messages)
            
            # Return the generated review
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating literature review: {e}")
            return f"# Literature Review Generation Error\n\nFailed to generate literature review for topic '{topic}': {str(e)}\n\nPlease try again or check your saved papers."
    
    
    
    def _generate_abstract(self, sections: List[ReviewSection]) -> str:
        """Generate an abstract for the complete review"""
        content_summary = "\n".join([
            f"Section {i+1}: {section.title}\n{section.content[:200]}..."
            for i, section in enumerate(sections)
        ])
        
        prompt_messages = [
            SystemMessage(content="""You are an academic abstract writer.
            Create a concise abstract that summarizes the entire literature review."""),
            HumanMessage(content=f"""
            Review Content:
            {content_summary}
            
            Create a 250-word abstract that:
            1. Summarizes the main themes
            2. Highlights key findings
            3. Indicates the review's scope
            4. Follows academic abstract structure
            """)
        ]
        
        response = self.llm.invoke(prompt_messages)
        return response.content