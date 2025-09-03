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

from embedding_agent import EmbeddedPaper, FAISSVectorDatabase

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
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro",
                                         temperature=0.3)
        self.current_outline: Optional[ReviewOutline] = None
        
    def create_initial_outline(self, topic: str, papers: List[EmbeddedPaper]) -> ReviewOutline:
        """Generate initial review structure based on available papers"""
        papers_text = "\n".join([
            f"Title: {p.title}\nAbstract: {p.abstract}\nType: {p.paper_type}"
            for p in papers[:10]  # Use top 10 papers for outline
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert research paper organizer.
            Create a detailed outline for a literature review with clear sections.
            Focus on logical flow and comprehensive coverage of the topic."""),
            HumanMessage(content=f"""
            Topic: {topic}
            Available Papers:
            {papers_text}
            
            Create a structured outline including:
            1. Overall title
            2. 4-6 main sections with subsections
            3. Key themes to cover
            4. Target length (words)
            """)
        ])
        
        # Parse response into ReviewOutline
        response = self.llm.invoke(prompt)
        parser = PydanticOutputParser(pydantic_object=ReviewOutline)
        self.current_outline = parser.parse(response.content)
        return self.current_outline

    def validate_section(self, section_content: str, cited_papers: List[str]) -> Dict[str, Any]:
        """Validate section content matches outline and uses correct citations"""
        if not self.current_outline:
            raise ValueError("No outline created. Call create_initial_outline first.")
        
        prompt = ChatPromptTemplate.from_messages([
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
        ])
        
        response = self.llm.invoke(prompt)
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
        prompt = ChatPromptTemplate.from_messages([
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
        ])
        
        response = self.llm.invoke(prompt)
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
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro",
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
        
        prompt = ChatPromptTemplate.from_messages([
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
        ])
        
        response = self.llm.invoke(prompt)
        
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
        prompt = ChatPromptTemplate.from_messages([
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
        ])
        
        response = self.llm.invoke(prompt)
        
        section.content = response.content
        section.feedback = feedback['suggestions']
        return section

class LiteratureReviewCoordinator:
    """
    Coordinates interaction between Manager and Writing agents
    """
    def __init__(self, vector_db_path: str = "faiss_paper_embeddings"):
        self.vector_db = FAISSVectorDatabase(vector_db_path)
        self.manager = ManagerAgent(self.vector_db)
        self.writer = WritingAgent(self.vector_db)
        
    def generate_review(self, topic: str, max_papers: int = 30) -> str:
        """
        Generate complete literature review through agent collaboration
        """
        logger.info(f"Starting literature review generation for topic: {topic}")
        
        # 1. Get relevant papers
        papers = self.vector_db.search_similar_papers(topic, k=max_papers)
        logger.info(f"Found {len(papers)} relevant papers")
        
        # 2. Create outline
        outline = self.manager.create_initial_outline(topic, papers)
        logger.info(f"Created outline with {len(outline.sections)} main sections")
        
        # 3. Generate each section
        full_review = []
        previous_sections = []
        
        for section in outline.sections:
            logger.info(f"Writing section: {section['title']}")
            
            # Get papers relevant to this section
            section_papers = self.vector_db.search_similar_papers(
                section['title'], k=10
            )
            
            # Write section
            written_section = self.writer.write_section(
                section['title'],
                section_papers,
                previous_sections
            )
            
            # Validate with manager
            validation = self.manager.validate_section(
                written_section.content,
                written_section.papers_cited
            )
            
            # Handle revisions if needed
            revision_count = 0
            max_revisions = 3
            
            while validation.get('needs_revision') and revision_count < max_revisions:
                logger.info(f"Revision needed for section: {section['title']}")
                revision_suggestions = self.manager.suggest_revisions(written_section)
                written_section = self.writer.revise_section(written_section, revision_suggestions)
                
                validation = self.manager.validate_section(
                    written_section.content,
                    written_section.papers_cited
                )
                revision_count += 1
            
            previous_sections.append(written_section.content)
            full_review.append(written_section)
            
        return self._format_review(full_review, outline.title)
    
    def _format_review(self, sections: List[ReviewSection], title: str) -> str:
        """Format the complete review with proper structure"""
        formatted_review = [
            f"# {title}\n\n",
            "## Abstract\n\n",
            self._generate_abstract(sections),
            "\n## Table of Contents\n\n"
        ]
        
        # Add table of contents
        for i, section in enumerate(sections, 1):
            formatted_review.append(f"{i}. {section.title}\n")
        
        formatted_review.append("\n")
        
        # Add section content
        for section in sections:
            formatted_review.extend([
                f"## {section.title}\n\n",
                f"{section.content}\n\n"
            ])
        
        return "".join(formatted_review)
    
    def _generate_abstract(self, sections: List[ReviewSection]) -> str:
        """Generate an abstract for the complete review"""
        content_summary = "\n".join([
            f"Section {i+1}: {section.title}\n{section.content[:200]}..."
            for i, section in enumerate(sections)
        ])
        
        prompt = ChatPromptTemplate.from_messages([
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
        ])
        
        response = self.llm.invoke(prompt)
        return response.content