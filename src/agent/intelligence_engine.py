"""
Intelligence Engine for analyzing collected data and extracting insights.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

from ..models import (
    PersonProfile, Person, Repository, SocialPost, Article, 
    Skill, Experience, Education, SourceType
)

class IntelligenceEngine:
    """Engine for analyzing data and extracting intelligence."""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        
    async def analyze_profile(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze a complete person profile and extract insights."""
        logger.info(f"Starting profile analysis for {profile.person.name}")
        
        try:
            analysis = {
                "technical_expertise": await self._analyze_technical_expertise(profile),
                "career_trajectory": await self._analyze_career_trajectory(profile),
                "online_presence": await self._analyze_online_presence(profile),
                "skill_gaps": await self._analyze_skill_gaps(profile),
                "growth_opportunities": await self._analyze_growth_opportunities(profile),
                "professional_network": await self._analyze_professional_network(profile),
                "content_quality": await self._analyze_content_quality(profile),
                "market_positioning": await self._analyze_market_positioning(profile)
            }
            
            logger.info(f"Completed profile analysis for {profile.person.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing profile for {profile.person.name}: {str(e)}")
            return {}
    
    async def _analyze_technical_expertise(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze technical expertise based on repositories and skills."""
        try:
            # Extract skills from repositories
            repo_skills = {}
            for repo in profile.repositories:
                if repo.language:
                    repo_skills[repo.language] = repo_skills.get(repo.language, 0) + 1
                
                # Extract skills from topics
                for topic in repo.topics:
                    repo_skills[topic] = repo_skills.get(topic, 0) + 1
            
            # Analyze skill proficiency
            skill_analysis = {}
            for skill in profile.skills:
                skill_analysis[skill.name] = {
                    "proficiency": skill.proficiency_level,
                    "experience_years": skill.years_experience,
                    "projects_count": skill.projects_count,
                    "endorsements": skill.endorsements
                }
            
            # Calculate overall technical score
            total_repos = len(profile.repositories)
            total_stars = sum(repo.stars for repo in profile.repositories)
            total_forks = sum(repo.forks for repo in profile.repositories)
            
            technical_score = min(100, (
                (total_repos * 10) + 
                (total_stars * 2) + 
                (total_forks * 3)
            ) // 10)
            
            return {
                "primary_languages": sorted(repo_skills.items(), key=lambda x: x[1], reverse=True)[:5],
                "skill_proficiency": skill_analysis,
                "repository_metrics": {
                    "total_repositories": total_repos,
                    "total_stars": total_stars,
                    "total_forks": total_forks,
                    "average_stars_per_repo": total_stars / total_repos if total_repos > 0 else 0
                },
                "technical_score": technical_score,
                "expertise_areas": list(repo_skills.keys())[:10]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical expertise: {str(e)}")
            return {}
    
    async def _analyze_career_trajectory(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze career trajectory and progression."""
        try:
            experiences = sorted(profile.experiences, key=lambda x: x.start_date)
            
            if not experiences:
                return {"career_stage": "Early Career", "progression": "Limited data"}
            
            # Analyze career progression
            current_role = next((exp for exp in experiences if exp.current), None)
            career_duration = (datetime.now() - experiences[0].start_date).days / 365.25
            
            # Determine career stage
            if career_duration < 2:
                career_stage = "Early Career"
            elif career_duration < 5:
                career_stage = "Mid Career"
            elif career_duration < 10:
                career_stage = "Senior Level"
            else:
                career_stage = "Expert Level"
            
            # Analyze role progression
            role_progression = []
            for i, exp in enumerate(experiences):
                if i > 0:
                    prev_exp = experiences[i-1]
                    progression = {
                        "from": prev_exp.title,
                        "to": exp.title,
                        "duration_days": (exp.start_date - prev_exp.end_date).days if prev_exp.end_date else 0,
                        "company_change": prev_exp.company != exp.company
                    }
                    role_progression.append(progression)
            
            return {
                "career_stage": career_stage,
                "career_duration_years": round(career_duration, 1),
                "current_role": current_role.title if current_role else None,
                "current_company": current_role.company if current_role else None,
                "role_progression": role_progression,
                "total_companies": len(set(exp.company for exp in experiences)),
                "average_role_duration_days": sum(
                    (exp.end_date - exp.start_date).days if exp.end_date else (datetime.now() - exp.start_date).days
                    for exp in experiences
                ) / len(experiences) if experiences else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing career trajectory: {str(e)}")
            return {}
    
    async def _analyze_online_presence(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze online presence and engagement."""
        try:
            # Analyze social media activity
            social_activity = {}
            for post in profile.social_posts:
                platform = post.source_type.value
                if platform not in social_activity:
                    social_activity[platform] = {
                        "total_posts": 0,
                        "total_likes": 0,
                        "total_shares": 0,
                        "recent_activity": 0
                    }
                
                social_activity[platform]["total_posts"] += 1
                social_activity[platform]["total_likes"] += post.likes
                social_activity[platform]["total_shares"] += post.shares
                
                # Check if post is recent (last 30 days)
                if (datetime.now() - post.created_at).days <= 30:
                    social_activity[platform]["recent_activity"] += 1
            
            # Calculate engagement metrics
            total_posts = sum(platform["total_posts"] for platform in social_activity.values())
            total_engagement = sum(
                platform["total_likes"] + platform["total_shares"] 
                for platform in social_activity.values()
            )
            
            engagement_rate = (total_engagement / total_posts) if total_posts > 0 else 0
            
            # Analyze content consistency
            recent_posts = [post for post in profile.social_posts 
                          if (datetime.now() - post.created_at).days <= 90]
            
            content_themes = {}
            for post in recent_posts:
                # Extract hashtags and common themes
                for hashtag in post.hashtags:
                    content_themes[hashtag] = content_themes.get(hashtag, 0) + 1
            
            return {
                "social_activity": social_activity,
                "total_posts": total_posts,
                "total_engagement": total_engagement,
                "engagement_rate": round(engagement_rate, 2),
                "recent_activity_90_days": len(recent_posts),
                "content_themes": sorted(content_themes.items(), key=lambda x: x[1], reverse=True)[:10],
                "platforms_active": len(social_activity),
                "online_presence_score": min(100, (total_posts * 2) + (engagement_rate * 10))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing online presence: {str(e)}")
            return {}
    
    async def _analyze_skill_gaps(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze skill gaps and areas for improvement."""
        try:
            # Get current skills
            current_skills = {skill.name.lower(): skill for skill in profile.skills}
            
            # Define in-demand skills by category
            in_demand_skills = {
                "programming": ["python", "javascript", "java", "go", "rust", "typescript"],
                "frontend": ["react", "vue", "angular", "next.js", "tailwind css"],
                "backend": ["node.js", "django", "flask", "spring", "fastapi"],
                "devops": ["docker", "kubernetes", "aws", "azure", "terraform"],
                "data": ["python", "sql", "pandas", "numpy", "machine learning", "ai"],
                "mobile": ["react native", "flutter", "swift", "kotlin"]
            }
            
            skill_gaps = {}
            for category, skills in in_demand_skills.items():
                missing_skills = []
                for skill in skills:
                    if skill not in current_skills:
                        missing_skills.append(skill)
                
                if missing_skills:
                    skill_gaps[category] = {
                        "missing_skills": missing_skills,
                        "priority": "high" if len(missing_skills) > 2 else "medium"
                    }
            
            # Analyze skill levels
            skill_levels = {}
            for skill_name, skill in current_skills.items():
                skill_levels[skill_name] = {
                    "proficiency": skill.proficiency_level,
                    "experience_years": skill.years_experience,
                    "needs_improvement": skill.proficiency_level in ["beginner", "intermediate"]
                }
            
            return {
                "skill_gaps": skill_gaps,
                "skill_levels": skill_levels,
                "total_skills": len(current_skills),
                "skills_needing_improvement": len([
                    skill for skill in current_skills.values() 
                    if skill.proficiency_level in ["beginner", "intermediate"]
                ]),
                "priority_areas": [
                    category for category, data in skill_gaps.items() 
                    if data["priority"] == "high"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {str(e)}")
            return {}
    
    async def _analyze_growth_opportunities(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze growth opportunities and next steps."""
        try:
            opportunities = []
            
            # Repository improvement opportunities
            low_star_repos = [repo for repo in profile.repositories if repo.stars < 5]
            if low_star_repos:
                opportunities.append({
                    "type": "repository_improvement",
                    "title": "Improve Low-Performing Repositories",
                    "description": f"Focus on {len(low_star_repos)} repositories with low engagement",
                    "priority": "medium",
                    "expected_outcome": "Increased visibility and potential collaborations"
                })
            
            # Skill development opportunities
            beginner_skills = [skill for skill in profile.skills if skill.proficiency_level == "beginner"]
            if beginner_skills:
                opportunities.append({
                    "type": "skill_development",
                    "title": "Advance Beginner Skills",
                    "description": f"Focus on advancing {len(beginner_skills)} beginner-level skills",
                    "priority": "high",
                    "expected_outcome": "Improved technical capabilities and career prospects"
                })
            
            # Content creation opportunities
            if len(profile.articles) < 5:
                opportunities.append({
                    "type": "content_creation",
                    "title": "Increase Content Creation",
                    "description": "Create more technical articles and blog posts",
                    "priority": "medium",
                    "expected_outcome": "Establish thought leadership and improve online presence"
                })
            
            # Networking opportunities
            if len(profile.social_posts) < 50:
                opportunities.append({
                    "type": "networking",
                    "title": "Increase Social Engagement",
                    "description": "Post more frequently on professional platforms",
                    "priority": "low",
                    "expected_outcome": "Better professional networking and visibility"
                })
            
            return {
                "total_opportunities": len(opportunities),
                "high_priority": len([opp for opp in opportunities if opp["priority"] == "high"]),
                "opportunities": opportunities
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth opportunities: {str(e)}")
            return {}
    
    async def _analyze_professional_network(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze professional network and connections."""
        try:
            # This would typically involve analyzing LinkedIn connections
            # For now, we'll analyze based on available data
            
            network_metrics = {
                "total_connections": 0,  # Would come from LinkedIn
                "industry_connections": {},  # Would analyze company industries
                "skill_based_connections": {},  # Would analyze mutual skills
                "geographic_distribution": {},  # Would analyze locations
                "network_strength": 0
            }
            
            # Analyze company connections from experience
            companies = set(exp.company for exp in profile.experiences)
            network_metrics["companies_worked_at"] = len(companies)
            
            # Analyze skill-based potential connections
            skill_connections = {}
            for skill in profile.skills:
                skill_connections[skill.name] = {
                    "endorsements": skill.endorsements,
                    "potential_connections": skill.endorsements * 2  # Rough estimate
                }
            
            network_metrics["skill_connections"] = skill_connections
            
            return network_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing professional network: {str(e)}")
            return {}
    
    async def _analyze_content_quality(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze the quality of content and contributions."""
        try:
            # Analyze repository quality
            repo_quality = {
                "high_quality": len([repo for repo in profile.repositories if repo.stars > 10]),
                "medium_quality": len([repo for repo in profile.repositories if 5 <= repo.stars <= 10]),
                "low_quality": len([repo for repo in profile.repositories if repo.stars < 5]),
                "total_repos": len(profile.repositories)
            }
            
            # Analyze article quality
            article_quality = {
                "total_articles": len(profile.articles),
                "average_read_time": sum(art.read_time or 0 for art in profile.articles) / len(profile.articles) if profile.articles else 0,
                "content_length": sum(len(art.content) for art in profile.articles),
                "tag_coverage": len(set(tag for art in profile.articles for tag in art.tags))
            }
            
            # Calculate overall content quality score
            content_score = min(100, (
                (repo_quality["high_quality"] * 20) +
                (repo_quality["medium_quality"] * 10) +
                (article_quality["total_articles"] * 5) +
                (article_quality["tag_coverage"] * 2)
            ))
            
            return {
                "repository_quality": repo_quality,
                "article_quality": article_quality,
                "content_quality_score": content_score,
                "quality_distribution": {
                    "excellent": repo_quality["high_quality"],
                    "good": repo_quality["medium_quality"],
                    "needs_improvement": repo_quality["low_quality"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content quality: {str(e)}")
            return {}
    
    async def _analyze_market_positioning(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze market positioning and competitive advantage."""
        try:
            # Analyze unique value proposition
            unique_skills = set()
            for skill in profile.skills:
                if skill.proficiency_level in ["expert", "advanced"]:
                    unique_skills.add(skill.name)
            
            # Analyze market demand for skills
            high_demand_skills = [
                "python", "javascript", "machine learning", "ai", "cloud computing",
                "data science", "devops", "cybersecurity"
            ]
            
            in_demand_expertise = len([skill for skill in unique_skills if skill.lower() in high_demand_skills])
            
            # Calculate market positioning score
            positioning_score = min(100, (
                len(unique_skills) * 10 +
                in_demand_expertise * 15 +
                len(profile.repositories) * 2 +
                len(profile.articles) * 3
            ))
            
            return {
                "unique_skills": list(unique_skills),
                "in_demand_expertise": in_demand_expertise,
                "market_positioning_score": positioning_score,
                "competitive_advantage": len(unique_skills) > 3,
                "market_alignment": "high" if in_demand_expertise > 2 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market positioning: {str(e)}")
            return {}
