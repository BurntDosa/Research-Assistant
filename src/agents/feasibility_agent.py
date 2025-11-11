#!/usr/bin/env python3
"""
Feasibility Assessment Agent
Evaluates research feasibility based on available resources and provides recommendations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
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


class ResourceType(Enum):
    """Types of research resources"""
    COMPUTATIONAL = "computational"
    FUNDING = "funding"
    TIME = "time"
    PERSONNEL = "personnel"
    DATA = "data"
    EQUIPMENT = "equipment"
    EXPERTISE = "expertise"


class FeasibilityLevel(Enum):
    """Research feasibility levels"""
    HIGHLY_FEASIBLE = "Highly Feasible"
    FEASIBLE = "Feasible"
    MODERATELY_FEASIBLE = "Moderately Feasible"
    CHALLENGING = "Challenging"
    NOT_FEASIBLE = "Not Feasible"


class FeasibilityAssessmentAgent:
    """Assesses research feasibility based on available resources"""
    
    def __init__(self):
        """Initialize the Feasibility Assessment Agent"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Feasibility Assessment Agent initialized with Gemini 2.5 Flash")
    
    def assess_feasibility(
        self,
        research_topic: str,
        research_description: str,
        available_resources: Dict[str, Any],
        timeline_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Assess research feasibility based on available resources
        
        Args:
            research_topic: The research topic or title
            research_description: Detailed description of the research
            available_resources: Dictionary of available resources
            timeline_months: Proposed timeline in months
        
        Returns:
            Dictionary containing feasibility assessment and recommendations
        """
        try:
            logger.info(f"Assessing feasibility for: {research_topic}")
            
            # Perform rule-based assessment
            rule_based_assessment = self._rule_based_assessment(
                research_description,
                available_resources,
                timeline_months
            )
            
            # Perform AI-enhanced assessment
            ai_assessment = self._ai_enhanced_assessment(
                research_topic,
                research_description,
                available_resources,
                timeline_months,
                rule_based_assessment
            )
            
            # Combine assessments
            final_assessment = self._combine_assessments(
                rule_based_assessment,
                ai_assessment
            )
            
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'research_topic': research_topic,
                'timeline_months': timeline_months,
                **final_assessment
            }
            
            logger.info(f"Feasibility assessment complete: {final_assessment['overall_feasibility']}")
            return result
            
        except Exception as e:
            logger.error(f"Feasibility assessment failed: {e}")
            return {
                'success': False,
                'message': f'Assessment error: {str(e)}'
            }
    
    def _rule_based_assessment(
        self,
        research_description: str,
        available_resources: Dict[str, Any],
        timeline_months: Optional[int]
    ) -> Dict[str, Any]:
        """Perform rule-based feasibility checks"""
        
        checks = {
            'computational_check': self._check_computational_resources(available_resources),
            'funding_check': self._check_funding(available_resources),
            'time_check': self._check_time_resources(available_resources, timeline_months),
            'personnel_check': self._check_personnel(available_resources),
            'data_check': self._check_data_access(available_resources),
            'equipment_check': self._check_equipment(available_resources),
            'expertise_check': self._check_expertise(available_resources)
        }
        
        # Calculate overall score (0-100)
        passed_checks = sum(1 for check in checks.values() if check['status'] == 'sufficient')
        total_checks = len(checks)
        feasibility_score = (passed_checks / total_checks) * 100
        
        # Determine feasibility level
        if feasibility_score >= 85:
            level = FeasibilityLevel.HIGHLY_FEASIBLE
        elif feasibility_score >= 70:
            level = FeasibilityLevel.FEASIBLE
        elif feasibility_score >= 50:
            level = FeasibilityLevel.MODERATELY_FEASIBLE
        elif feasibility_score >= 30:
            level = FeasibilityLevel.CHALLENGING
        else:
            level = FeasibilityLevel.NOT_FEASIBLE
        
        return {
            'feasibility_score': feasibility_score,
            'feasibility_level': level.value,
            'resource_checks': checks,
            'critical_gaps': self._identify_critical_gaps(checks)
        }
    
    def _check_computational_resources(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check computational resource availability"""
        computational = resources.get('computational', {})
        
        has_gpu = computational.get('has_gpu', False)
        has_cloud = computational.get('has_cloud_access', False)
        cpu_cores = computational.get('cpu_cores', 0)
        ram_gb = computational.get('ram_gb', 0)
        
        # Rule-based evaluation
        if has_gpu or has_cloud:
            status = 'sufficient'
            message = "Adequate computational resources available"
        elif cpu_cores >= 8 and ram_gb >= 16:
            status = 'sufficient'
            message = "Sufficient CPU/RAM for moderate workloads"
        elif cpu_cores >= 4 and ram_gb >= 8:
            status = 'limited'
            message = "Limited computational resources, suitable for small-scale work"
        else:
            status = 'insufficient'
            message = "Insufficient computational resources"
        
        return {
            'status': status,
            'message': message,
            'details': computational
        }
    
    def _check_funding(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check funding availability"""
        funding = resources.get('funding', {})
        
        budget_inr = funding.get('budget_inr', 0)
        has_grant = funding.get('has_grant', False)
        funding_duration_months = funding.get('duration_months', 0)
        
        # INR thresholds (approximately 83 INR = 1 USD for reference)
        if has_grant and budget_inr >= 4150000:  # ~50k USD equivalent
            status = 'sufficient'
            message = f"Strong funding support (₹{budget_inr:,})"
        elif budget_inr >= 830000:  # ~10k USD equivalent
            status = 'sufficient'
            message = f"Adequate funding (₹{budget_inr:,})"
        elif budget_inr >= 415000:  # ~5k USD equivalent
            status = 'limited'
            message = f"Limited funding (₹{budget_inr:,}), plan carefully"
        else:
            status = 'insufficient'
            message = "Insufficient funding, seek additional sources"
        
        return {
            'status': status,
            'message': message,
            'details': funding
        }
    
    def _check_time_resources(self, resources: Dict[str, Any], timeline_months: Optional[int]) -> Dict[str, Any]:
        """Check time availability"""
        time_resources = resources.get('time', {})
        
        hours_per_week = time_resources.get('hours_per_week', 0)
        dedicated_percentage = time_resources.get('dedicated_percentage', 0)
        
        if not timeline_months:
            return {
                'status': 'unknown',
                'message': "No timeline specified",
                'details': time_resources
            }
        
        # Calculate total available hours
        total_weeks = timeline_months * 4.33
        total_hours = hours_per_week * total_weeks
        
        if hours_per_week >= 40 or dedicated_percentage >= 100:
            status = 'sufficient'
            message = f"Full-time dedication available ({total_hours:.0f} total hours)"
        elif hours_per_week >= 20 or dedicated_percentage >= 50:
            status = 'sufficient'
            message = f"Part-time dedication ({total_hours:.0f} total hours)"
        elif hours_per_week >= 10:
            status = 'limited'
            message = f"Limited time ({total_hours:.0f} total hours), may need extension"
        else:
            status = 'insufficient'
            message = "Insufficient time allocation"
        
        return {
            'status': status,
            'message': message,
            'details': {**time_resources, 'estimated_total_hours': total_hours}
        }
    
    def _check_personnel(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check personnel availability"""
        personnel = resources.get('personnel', {})
        
        team_size = personnel.get('team_size', 1)
        has_advisor = personnel.get('has_advisor', False)
        has_collaborators = personnel.get('has_collaborators', False)
        
        if team_size >= 3 and has_advisor:
            status = 'sufficient'
            message = f"Strong team support ({team_size} members)"
        elif team_size >= 2 or has_advisor:
            status = 'sufficient'
            message = "Adequate team support"
        elif has_collaborators:
            status = 'limited'
            message = "Limited team, collaborate actively"
        else:
            status = 'limited'
            message = "Solo work, consider seeking collaborators"
        
        return {
            'status': status,
            'message': message,
            'details': personnel
        }
    
    def _check_data_access(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check data availability"""
        data = resources.get('data', {})
        
        has_access = data.get('has_access', False)
        data_type = data.get('type', 'unknown')
        size_description = data.get('size', 'unknown')
        
        if has_access and data_type != 'unknown':
            status = 'sufficient'
            message = f"Data access confirmed ({data_type})"
        elif has_access:
            status = 'limited'
            message = "Data access available but needs verification"
        else:
            status = 'insufficient'
            message = "No data access, must acquire or generate data"
        
        return {
            'status': status,
            'message': message,
            'details': data
        }
    
    def _check_equipment(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check equipment availability"""
        equipment = resources.get('equipment', {})
        
        has_lab = equipment.get('has_lab_access', False)
        specialized_equipment = equipment.get('specialized_equipment', [])
        
        if has_lab and len(specialized_equipment) > 0:
            status = 'sufficient'
            message = f"Lab access with specialized equipment"
        elif has_lab:
            status = 'sufficient'
            message = "Lab access available"
        elif len(specialized_equipment) > 0:
            status = 'limited'
            message = "Some equipment available"
        else:
            status = 'limited'
            message = "No specialized equipment required or available"
        
        return {
            'status': status,
            'message': message,
            'details': equipment
        }
    
    def _check_expertise(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Check expertise and skills"""
        expertise = resources.get('expertise', {})
        
        skills = expertise.get('skills', [])
        experience_years = expertise.get('experience_years', 0)
        has_mentorship = expertise.get('has_mentorship', False)
        
        if experience_years >= 3 and len(skills) >= 3:
            status = 'sufficient'
            message = f"Strong expertise ({experience_years} years, {len(skills)} skills)"
        elif experience_years >= 1 or len(skills) >= 2:
            status = 'sufficient'
            message = "Adequate expertise, continue learning"
        elif has_mentorship:
            status = 'limited'
            message = "Limited expertise, leverage mentorship"
        else:
            status = 'limited'
            message = "Limited expertise, seek training/mentorship"
        
        return {
            'status': status,
            'message': message,
            'details': expertise
        }
    
    def _identify_critical_gaps(self, checks: Dict[str, Dict]) -> List[str]:
        """Identify critical resource gaps"""
        gaps = []
        
        for check_name, check_result in checks.items():
            if check_result['status'] == 'insufficient':
                resource_name = check_name.replace('_check', '').replace('_', ' ').title()
                gaps.append(f"{resource_name}: {check_result['message']}")
        
        return gaps
    
    def _ai_enhanced_assessment(
        self,
        research_topic: str,
        research_description: str,
        available_resources: Dict[str, Any],
        timeline_months: Optional[int],
        rule_based_assessment: Dict[str, Any]
    ) -> str:
        """Use AI to provide nuanced feasibility assessment"""
        try:
            prompt = f"""You are a research advisor evaluating project feasibility.

Research Topic: {research_topic}

Research Description:
{research_description}

Timeline: {timeline_months} months (if specified)

Available Resources:
{self._format_resources_for_prompt(available_resources)}

Rule-Based Assessment:
- Feasibility Score: {rule_based_assessment['feasibility_score']:.1f}/100
- Level: {rule_based_assessment['feasibility_level']}
- Critical Gaps: {', '.join(rule_based_assessment['critical_gaps']) if rule_based_assessment['critical_gaps'] else 'None'}

Provide a comprehensive feasibility assessment including:

1. **Overall Feasibility Judgment** (1-2 paragraphs)
   - Is this project feasible with current resources?
   - What are the main strengths and limitations?

2. **Critical Success Factors** (3-4 factors)
   - What must go right for this to succeed?

3. **Risk Assessment** (3-4 risks with mitigation strategies)
   - Technical risks
   - Resource risks
   - Timeline risks

4. **Resource Recommendations** (Specific, actionable)
   - What additional resources are needed?
   - How to acquire or substitute missing resources?
   - Priority order for resource acquisition

5. **Alternative Approaches** (2-3 alternatives if feasibility is low)
   - Scaled-down versions
   - Phased approaches
   - Collaborative strategies

6. **Go/No-Go Decision Recommendation**
   - Clear recommendation: Go, Go with modifications, or No-Go
   - Justification for recommendation

Format in clear markdown with headers and bullet points. Be honest and practical.
"""

            response = self.model.generate_content(prompt)
            assessment = response.text.strip()
            
            if not assessment or len(assessment) < 100:
                logger.warning("Received suspiciously short AI assessment")
                return "AI assessment unavailable"
            
            return assessment
            
        except Exception as e:
            logger.error(f"AI assessment failed: {e}")
            return f"AI assessment error: {str(e)}"
    
    def _format_resources_for_prompt(self, resources: Dict[str, Any]) -> str:
        """Format resources dictionary for AI prompt"""
        formatted = []
        
        for category, details in resources.items():
            if isinstance(details, dict):
                items = [f"  - {k}: {v}" for k, v in details.items()]
                formatted.append(f"{category.title()}:\n" + "\n".join(items))
            else:
                formatted.append(f"{category.title()}: {details}")
        
        return "\n\n".join(formatted)
    
    def _combine_assessments(
        self,
        rule_based: Dict[str, Any],
        ai_assessment: str
    ) -> Dict[str, Any]:
        """Combine rule-based and AI assessments"""
        return {
            'overall_feasibility': rule_based['feasibility_level'],
            'feasibility_score': rule_based['feasibility_score'],
            'resource_checks': rule_based['resource_checks'],
            'critical_gaps': rule_based['critical_gaps'],
            'detailed_assessment': ai_assessment,
            'recommendations_summary': self._extract_recommendations_summary(
                rule_based,
                ai_assessment
            )
        }
    
    def _extract_recommendations_summary(
        self,
        rule_based: Dict[str, Any],
        ai_assessment: str
    ) -> List[str]:
        """Extract key recommendations from assessments"""
        recommendations = []
        
        # Add recommendations for each insufficient resource
        for check_name, check_result in rule_based['resource_checks'].items():
            if check_result['status'] == 'insufficient':
                resource_name = check_name.replace('_check', '').replace('_', ' ').title()
                recommendations.append(f"Address {resource_name.lower()} gap: {check_result['message']}")
        
        # Add top-level recommendation based on score
        score = rule_based['feasibility_score']
        if score >= 70:
            recommendations.append("Project is feasible - proceed with planning")
        elif score >= 50:
            recommendations.append("Project is feasible with modifications - address critical gaps first")
        else:
            recommendations.append("Project faces significant challenges - consider alternative approaches")
        
        return recommendations


if __name__ == "__main__":
    # Example usage
    agent = FeasibilityAssessmentAgent()
    
    # Sample resource inventory
    resources = {
        'computational': {
            'has_gpu': True,
            'has_cloud_access': False,
            'cpu_cores': 8,
            'ram_gb': 32
        },
        'funding': {
            'budget_inr': 1245000,  # ~15k USD equivalent
            'has_grant': False,
            'duration_months': 12
        },
        'time': {
            'hours_per_week': 30,
            'dedicated_percentage': 75
        },
        'personnel': {
            'team_size': 2,
            'has_advisor': True,
            'has_collaborators': True
        },
        'data': {
            'has_access': True,
            'type': 'public_dataset',
            'size': 'large'
        },
        'equipment': {
            'has_lab_access': False,
            'specialized_equipment': []
        },
        'expertise': {
            'skills': ['machine learning', 'python', 'data analysis'],
            'experience_years': 2,
            'has_mentorship': True
        }
    }
    
    result = agent.assess_feasibility(
        research_topic="Deep Learning for Medical Image Analysis",
        research_description="Develop a CNN-based system for automated diagnosis from X-ray images",
        available_resources=resources,
        timeline_months=12
    )
    
    if result['success']:
        print(f"✅ Feasibility Assessment Complete!")
        print(f"Overall: {result['overall_feasibility']}")
        print(f"Score: {result['feasibility_score']:.1f}/100")
        print(f"\nCritical Gaps: {len(result['critical_gaps'])}")
    else:
        print(f"❌ Assessment Failed: {result['message']}")
