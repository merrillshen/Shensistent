"""
Recommendation Engine for generating personalized recommendations and suggestions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

from ..models import (
    PersonProfile, Recommendation, Connection, JobOpportunity, 
    Skill, Repository, Article, SourceType
)

class RecommendationEngine:
    """Engine for generating personalized recommendations."""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        
    async def generate_daily_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate daily recommendations for personal and career growth."""
        logger.info(f"Generating daily recommendations for {profile.person.name}")
        
        try:
            recommendations = []
            
            # Generate skill development recommendations
            skill_recs = await self._generate_skill_recommendations(profile)
            recommendations.extend(skill_recs)
            
            # Generate content creation recommendations
            content_recs = await self._generate_content_recommendations(profile)
            recommendations.extend(content_recs)
            
            # Generate networking recommendations
            networking_recs = await self._generate_networking_recommendations(profile)
            recommendations.extend(networking_recs)
            
            # Generate career advancement recommendations
            career_recs = await self._generate_career_recommendations(profile)
            recommendations.extend(career_recs)
            
            # Generate learning recommendations
            learning_recs = await self._generate_learning_recommendations(profile)
            recommendations.extend(learning_recs)
            
            # Prioritize recommendations
            prioritized_recs = self._prioritize_recommendations(recommendations)
            
            logger.info(f"Generated {len(prioritized_recs)} daily recommendations for {profile.person.name}")
            return prioritized_recs[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error generating daily recommendations for {profile.person.name}: {str(e)}")
            return []
    
    async def _generate_skill_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate skill development recommendations."""
        recommendations = []
        
        try:
            # Analyze current skills
            current_skills = {skill.name.lower(): skill for skill in profile.skills}
            
            # Define skill development paths
            skill_paths = {
                "python": ["django", "flask", "fastapi", "pandas", "numpy", "machine learning"],
                "javascript": ["react", "vue", "angular", "node.js", "typescript", "next.js"],
                "java": ["spring", "hibernate", "maven", "gradle", "android development"],
                "devops": ["docker", "kubernetes", "aws", "azure", "terraform", "jenkins"],
                "data_science": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow"]
            }
            
            for skill_name, skill in current_skills.items():
                if skill.proficiency_level in ["beginner", "intermediate"]:
                    # Find related skills to develop
                    for path_name, related_skills in skill_paths.items():
                        if skill_name in path_name or any(s in skill_name for s in path_name.split("_")):
                            for related_skill in related_skills:
                                if related_skill.lower() not in current_skills:
                                    recommendations.append(Recommendation(
                                        id=f"skill_{skill_name}_{related_skill}",
                                        category="skill_development",
                                        title=f"Develop {related_skill.title()} Skills",
                                        description=f"Build on your {skill_name} knowledge to learn {related_skill}",
                                        priority="high" if skill.proficiency_level == "intermediate" else "medium",
                                        action_items=[
                                            f"Complete {related_skill} tutorials",
                                            f"Build a small project using {related_skill}",
                                            f"Practice {related_skill} concepts daily"
                                        ],
                                        expected_outcome=f"Proficiency in {related_skill} and expanded skill set",
                                        deadline=datetime.now() + timedelta(days=30)
                                    ))
                                    break
            
            # Add general skill improvement recommendations
            beginner_skills = [skill for skill in current_skills.values() if skill.proficiency_level == "beginner"]
            if beginner_skills:
                recommendations.append(Recommendation(
                    id="skill_general_improvement",
                    category="skill_development",
                    title="Advance Beginner Skills",
                    description=f"Focus on advancing {len(beginner_skills)} beginner-level skills to intermediate",
                    priority="high",
                    action_items=[
                        "Complete advanced tutorials for each skill",
                        "Build portfolio projects",
                        "Seek mentorship or join study groups"
                    ],
                    expected_outcome="Improved technical capabilities and career prospects",
                    deadline=datetime.now() + timedelta(days=60)
                ))
            
        except Exception as e:
            logger.error(f"Error generating skill recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_content_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate content creation recommendations."""
        recommendations = []
        
        try:
            # Analyze current content
            total_articles = len(profile.articles)
            total_repos = len(profile.repositories)
            
            # Content creation recommendations
            if total_articles < 5:
                recommendations.append(Recommendation(
                    id="content_creation_articles",
                    category="content_creation",
                    title="Increase Technical Writing",
                    description="Create more technical articles and blog posts to establish thought leadership",
                    priority="medium",
                    action_items=[
                        "Write about recent projects and learnings",
                        "Create tutorials for common problems",
                        "Share insights from your work experience",
                        "Aim for 1-2 articles per month"
                    ],
                    expected_outcome="Improved online presence and professional reputation",
                    deadline=datetime.now() + timedelta(days=90)
                ))
            
            if total_repos < 10:
                recommendations.append(Recommendation(
                    id="content_creation_projects",
                    category="content_creation",
                    title="Build More Portfolio Projects",
                    description="Create additional projects to showcase your skills and creativity",
                    priority="medium",
                    action_items=[
                        "Identify gaps in your portfolio",
                        "Build projects using trending technologies",
                        "Focus on projects that solve real problems",
                        "Document projects thoroughly with README files"
                    ],
                    expected_outcome="Stronger portfolio and increased visibility",
                    deadline=datetime.now() + timedelta(days=120)
                ))
            
            # Content improvement recommendations
            low_star_repos = [repo for repo in profile.repositories if repo.stars < 5]
            if low_star_repos:
                recommendations.append(Recommendation(
                    id="content_improvement_repos",
                    category="content_improvement",
                    title="Improve Low-Performing Repositories",
                    description=f"Enhance {len(low_star_repos)} repositories to increase engagement",
                    priority="low",
                    action_items=[
                        "Update README files with better documentation",
                        "Add screenshots and demos",
                        "Improve code quality and structure",
                        "Add tests and CI/CD pipelines"
                    ],
                    expected_outcome="Increased repository visibility and potential collaborations",
                    deadline=datetime.now() + timedelta(days=60)
                ))
            
        except Exception as e:
            logger.error(f"Error generating content recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_networking_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate networking and connection recommendations."""
        recommendations = []
        
        try:
            # Analyze current networking activity
            social_posts = len(profile.social_posts)
            recent_activity = len([post for post in profile.social_posts 
                                 if (datetime.now() - post.created_at).days <= 30])
            
            # Social engagement recommendations
            if social_posts < 50:
                recommendations.append(Recommendation(
                    id="networking_social_engagement",
                    category="networking",
                    title="Increase Social Media Engagement",
                    description="Post more frequently on professional platforms to improve visibility",
                    priority="low",
                    action_items=[
                        "Share daily work updates and learnings",
                        "Engage with industry leaders' content",
                        "Participate in relevant discussions",
                        "Aim for 2-3 posts per week"
                    ],
                    expected_outcome="Better professional networking and increased visibility",
                    deadline=datetime.now() + timedelta(days=90)
                ))
            
            if recent_activity < 10:
                recommendations.append(Recommendation(
                    id="networking_recent_activity",
                    category="networking",
                    title="Maintain Consistent Social Activity",
                    description="Ensure regular posting to maintain professional presence",
                    priority="medium",
                    action_items=[
                        "Schedule regular posting times",
                        "Create content calendar",
                        "Engage with community discussions",
                        "Share industry insights and trends"
                    ],
                    expected_outcome="Consistent professional presence and community engagement",
                    deadline=datetime.now() + timedelta(days=30)
                ))
            
            # Professional connection recommendations
            recommendations.append(Recommendation(
                id="networking_connections",
                category="networking",
                title="Expand Professional Network",
                description="Connect with professionals in your field and related industries",
                priority="medium",
                action_items=[
                    "Identify key professionals in your field",
                    "Send personalized connection requests",
                    "Attend industry events and conferences",
                    "Join professional groups and communities"
                ],
                expected_outcome="Expanded professional network and career opportunities",
                deadline=datetime.now() + timedelta(days=60)
            ))
            
        except Exception as e:
            logger.error(f"Error generating networking recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_career_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate career advancement recommendations."""
        recommendations = []
        
        try:
            # Analyze career trajectory
            experiences = profile.experiences
            current_role = next((exp for exp in experiences if exp.current), None)
            
            if current_role:
                # Career progression recommendations
                role_duration = (datetime.now() - current_role.start_date).days
                
                if role_duration > 730:  # More than 2 years
                    recommendations.append(Recommendation(
                        id="career_progression",
                        category="career_advancement",
                        title="Consider Career Progression",
                        description="You've been in your current role for over 2 years - consider next steps",
                        priority="medium",
                        action_items=[
                            "Assess your career goals and aspirations",
                            "Identify skills needed for next level",
                            "Discuss growth opportunities with your manager",
                            "Update your resume and LinkedIn profile"
                        ],
                        expected_outcome="Clear career path and potential advancement",
                        deadline=datetime.now() + timedelta(days=90)
                    ))
                
                # Skill alignment recommendations
                role_skills = set(current_role.skills_used)
                profile_skills = {skill.name.lower() for skill in profile.skills}
                
                missing_role_skills = [skill for skill in role_skills if skill.lower() not in profile_skills]
                if missing_role_skills:
                    recommendations.append(Recommendation(
                        id="career_skill_alignment",
                        category="career_advancement",
                        title="Align Skills with Current Role",
                        description=f"Develop missing skills: {', '.join(missing_role_skills)}",
                        priority="high",
                        action_items=[
                            f"Learn {', '.join(missing_role_skills)}",
                            "Take relevant courses or certifications",
                            "Practice skills in current projects",
                            "Seek mentorship from experienced colleagues"
                        ],
                        expected_outcome="Better performance in current role and career growth",
                        deadline=datetime.now() + timedelta(days=60)
                    ))
            
            # Industry trend recommendations
            recommendations.append(Recommendation(
                id="career_industry_trends",
                category="career_advancement",
                title="Stay Updated with Industry Trends",
                description="Keep abreast of emerging technologies and industry developments",
                priority="low",
                action_items=[
                    "Follow industry leaders and publications",
                    "Attend webinars and conferences",
                    "Join professional associations",
                    "Read industry reports and whitepapers"
                ],
                expected_outcome="Enhanced industry knowledge and competitive advantage",
                deadline=datetime.now() + timedelta(days=120)
            ))
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {str(e)}")
        
        return recommendations
    
    async def _generate_learning_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate learning and education recommendations."""
        recommendations = []
        
        try:
            # Analyze current education and skills
            education_level = len(profile.education)
            advanced_skills = [skill for skill in profile.skills if skill.proficiency_level in ["advanced", "expert"]]
            
            # Certification recommendations
            if len(advanced_skills) < 3:
                recommendations.append(Recommendation(
                    id="learning_certifications",
                    category="learning",
                    title="Pursue Professional Certifications",
                    description="Obtain certifications in your key skill areas to validate expertise",
                    priority="medium",
                    action_items=[
                        "Identify relevant certifications for your field",
                        "Research certification requirements and costs",
                        "Create study plan and timeline",
                        "Practice with mock exams and projects"
                    ],
                    expected_outcome="Professional validation and increased marketability",
                    deadline=datetime.now() + timedelta(days=180)
                ))
            
            # Continuous learning recommendations
            recommendations.append(Recommendation(
                id="learning_continuous",
                category="learning",
                title="Establish Continuous Learning Routine",
                description="Develop a habit of continuous learning and skill development",
                priority="medium",
                action_items=[
                    "Allocate 2-3 hours per week for learning",
                    "Subscribe to technical newsletters and podcasts",
                    "Join online learning platforms",
                    "Participate in coding challenges and hackathons"
                ],
                expected_outcome="Continuous skill improvement and career growth",
                deadline=datetime.now() + timedelta(days=30)
            ))
            
            # Specialized training recommendations
            if any(skill.name.lower() in ["machine learning", "ai", "data science"] for skill in profile.skills):
                recommendations.append(Recommendation(
                    id="learning_specialized_ai",
                    category="learning",
                    title="Advanced AI/ML Training",
                    description="Enhance your AI/ML expertise with advanced training",
                    priority="high",
                    action_items=[
                        "Take advanced ML courses",
                        "Work on real-world AI projects",
                        "Join AI research communities",
                        "Attend AI conferences and workshops"
                    ],
                    expected_outcome="Expert-level AI/ML capabilities and career advancement",
                    deadline=datetime.now() + timedelta(days=120)
                ))
            
        except Exception as e:
            logger.error(f"Error generating learning recommendations: {str(e)}")
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize recommendations based on importance and urgency."""
        try:
            # Define priority weights
            priority_weights = {
                "high": 3,
                "medium": 2,
                "low": 1
            }
            
            # Calculate scores for each recommendation
            scored_recs = []
            for rec in recommendations:
                # Base score from priority
                score = priority_weights.get(rec.priority, 1)
                
                # Bonus for urgent deadlines
                if rec.deadline:
                    days_until_deadline = (rec.deadline - datetime.now()).days
                    if days_until_deadline <= 7:
                        score += 2
                    elif days_until_deadline <= 30:
                        score += 1
                
                # Bonus for high-impact categories
                if rec.category in ["skill_development", "career_advancement"]:
                    score += 1
                
                scored_recs.append((rec, score))
            
            # Sort by score (highest first)
            scored_recs.sort(key=lambda x: x[1], reverse=True)
            
            # Return sorted recommendations
            return [rec for rec, score in scored_recs]
            
        except Exception as e:
            logger.error(f"Error prioritizing recommendations: {str(e)}")
            return recommendations
    
    async def generate_connection_suggestions(self, profile: PersonProfile) -> List[Connection]:
        """Generate professional connection suggestions."""
        # This would typically integrate with LinkedIn API
        # For now, return empty list
        return []
    
    async def generate_job_opportunities(self, profile: PersonProfile) -> List[JobOpportunity]:
        """Generate job opportunity suggestions."""
        # This would typically integrate with job boards and career sites
        # For now, return empty list
        return []
