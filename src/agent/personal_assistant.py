"""
Main Personal Assistant class that orchestrates all components.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from ..models import PersonProfile, Person, Recommendation, Connection, JobOpportunity
from ..collectors import GitHubCollector, LinkedInCollector, TwitterCollector, NewsCollector
from .intelligence_engine import IntelligenceEngine
from .recommendation_engine import RecommendationEngine
from ..config import get_settings

class PersonalAssistant:
    """Main personal assistant agent that orchestrates all functionality."""
    
    def __init__(self, openai_client):
        self.settings = get_settings()
        self.openai_client = openai_client
        
        # Initialize engines
        self.intelligence_engine = IntelligenceEngine(openai_client)
        self.recommendation_engine = RecommendationEngine(openai_client)
        
        # Initialize collectors
        self.collectors = {
            "github": GitHubCollector(self.settings.dict()),
            "linkedin": None,  # Will be initialized if credentials are available
            "twitter": None,   # Will be initialized if credentials are available
            "news": None       # Will be initialized if credentials are available
        }
        
        # Initialize if credentials are available
        self._initialize_collectors()
        
        logger.info("Personal Assistant initialized successfully")
    
    def _initialize_collectors(self):
        """Initialize collectors based on available credentials."""
        try:
            if self.settings.linkedin_username and self.settings.linkedin_password:
                self.collectors["linkedin"] = LinkedInCollector(self.settings.dict())
                logger.info("LinkedIn collector initialized")
            
            if self.settings.twitter_bearer_token:
                self.collectors["twitter"] = TwitterCollector(self.settings.dict())
                logger.info("Twitter collector initialized")
            
            if self.settings.news_api_key:
                self.collectors["news"] = NewsCollector(self.settings.dict())
                logger.info("News collector initialized")
                
        except Exception as e:
            logger.warning(f"Error initializing some collectors: {str(e)}")
    
    async def collect_user_data(self, usernames: Dict[str, str]) -> PersonProfile:
        """Collect comprehensive user data from all available sources."""
        logger.info(f"Starting data collection for user: {usernames}")
        
        try:
            all_data = {}
            
            # Collect data from each source
            for source, username in usernames.items():
                if source in self.collectors and self.collectors[source]:
                    try:
                        async with self.collectors[source] as collector:
                            data = await collector.collect_all_data(username)
                            all_data[source] = data
                            logger.info(f"Collected data from {source}")
                    except Exception as e:
                        logger.error(f"Error collecting data from {source}: {str(e)}")
                        all_data[source] = {}
                else:
                    logger.warning(f"Collector not available for {source}")
                    all_data[source] = {}
            
            # Merge and create comprehensive profile
            profile = await self._create_comprehensive_profile(all_data, usernames)
            
            logger.info(f"Completed data collection for user: {profile.person.name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error in data collection: {str(e)}")
            raise
    
    async def _create_comprehensive_profile(self, all_data: Dict[str, Any], usernames: Dict[str, str]) -> PersonProfile:
        """Create a comprehensive profile from collected data."""
        try:
            # Start with GitHub data as base
            github_data = all_data.get("github", {})
            
            if not github_data or "person" not in github_data:
                raise ValueError("GitHub data is required to create profile")
            
            # Create base person
            person = github_data["person"]
            
            # Merge repositories
            repositories = github_data.get("repositories", [])
            
            # Merge social posts
            social_posts = github_data.get("social_posts", [])
            
            # Merge articles
            articles = github_data.get("articles", [])
            
            # Add data from other sources
            for source, data in all_data.items():
                if source == "github":
                    continue
                
                if "social_posts" in data:
                    social_posts.extend(data["social_posts"])
                
                if "articles" in data:
                    articles.extend(data["articles"])
            
            # Create profile (skills, experiences, education will be populated later)
            profile = PersonProfile(
                person=person,
                repositories=repositories,
                social_posts=social_posts,
                articles=articles,
                skills=[],  # Will be extracted from repositories and content
                experiences=[],  # Will be extracted from LinkedIn or other sources
                education=[],    # Will be extracted from LinkedIn or other sources
                recommendations=[],
                connections=[],
                job_opportunities=[]
            )
            
            # Extract skills from repositories and content
            profile.skills = await self._extract_skills_from_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating comprehensive profile: {str(e)}")
            raise
    
    async def _extract_skills_from_profile(self, profile: PersonProfile) -> List[Any]:
        """Extract skills from repositories and content."""
        try:
            from ..models import Skill
            
            skills = {}
            
            # Extract skills from repositories
            for repo in profile.repositories:
                if repo.language:
                    lang = repo.language.lower()
                    if lang not in skills:
                        skills[lang] = {
                            "name": repo.language,
                            "category": "programming",
                            "proficiency_level": "intermediate",
                            "projects_count": 0,
                            "endorsements": 0
                        }
                    skills[lang]["projects_count"] += 1
                
                # Extract skills from topics
                for topic in repo.topics:
                    if topic.lower() not in skills:
                        skills[topic.lower()] = {
                            "name": topic,
                            "category": "technology",
                            "proficiency_level": "intermediate",
                            "projects_count": 0,
                            "endorsements": 0
                        }
                    skills[topic.lower()]["projects_count"] += 1
            
            # Extract skills from articles
            for article in profile.articles:
                # Extract skills from content and tags
                content_skills = self._extract_skills_from_text(article.content)
                for skill_name in content_skills:
                    if skill_name not in skills:
                        skills[skill_name] = {
                            "name": skill_name,
                            "category": "general",
                            "proficiency_level": "intermediate",
                            "projects_count": 0,
                            "endorsements": 0
                        }
                    skills[skill_name]["projects_count"] += 1
            
            # Convert to Skill objects
            skill_objects = []
            for skill_data in skills.values():
                skill = Skill(
                    id=f"skill_{skill_data['name'].lower().replace(' ', '_')}",
                    name=skill_data["name"],
                    category=skill_data["category"],
                    proficiency_level=skill_data["proficiency_level"],
                    projects_count=skill_data["projects_count"],
                    endorsements=skill_data["endorsements"]
                )
                skill_objects.append(skill)
            
            return skill_objects
            
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return []
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text content."""
        # This is a simple implementation - could be enhanced with NLP
        common_skills = [
            "python", "javascript", "java", "c++", "c#", "go", "rust", "swift",
            "react", "angular", "vue", "node.js", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "sql", "mongodb",
            "redis", "elasticsearch", "machine learning", "ai", "data science",
            "devops", "ci/cd", "git", "agile", "scrum"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    async def analyze_user_profile(self, profile: PersonProfile) -> Dict[str, Any]:
        """Analyze user profile and extract insights."""
        logger.info(f"Starting profile analysis for {profile.person.name}")
        
        try:
            analysis = await self.intelligence_engine.analyze_profile(profile)
            logger.info(f"Completed profile analysis for {profile.person.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing profile: {str(e)}")
            raise
    
    async def generate_recommendations(self, profile: PersonProfile) -> List[Recommendation]:
        """Generate personalized recommendations."""
        logger.info(f"Generating recommendations for {profile.person.name}")
        
        try:
            recommendations = await self.recommendation_engine.generate_daily_recommendations(profile)
            logger.info(f"Generated {len(recommendations)} recommendations for {profile.person.name}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    async def get_daily_summary(self, profile: PersonProfile) -> Dict[str, Any]:
        """Get daily summary and insights."""
        logger.info(f"Generating daily summary for {profile.person.name}")
        
        try:
            # Analyze profile
            analysis = await self.analyze_user_profile(profile)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(profile)
            
            # Create daily summary
            summary = {
                "date": datetime.now().isoformat(),
                "user": {
                    "name": profile.person.name,
                    "username": profile.person.username,
                    "current_status": "Active"
                },
                "overview": {
                    "total_repositories": len(profile.repositories),
                    "total_articles": len(profile.articles),
                    "total_skills": len(profile.skills),
                    "recent_activity": len([post for post in profile.social_posts 
                                          if (datetime.now() - post.created_at).days <= 7])
                },
                "key_insights": {
                    "technical_score": analysis.get("technical_expertise", {}).get("technical_score", 0),
                    "career_stage": analysis.get("career_trajectory", {}).get("career_stage", "Unknown"),
                    "online_presence_score": analysis.get("online_presence", {}).get("online_presence_score", 0),
                    "market_positioning_score": analysis.get("market_positioning", {}).get("market_positioning_score", 0)
                },
                "top_recommendations": [
                    {
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority,
                        "category": rec.category,
                        "action_items": rec.action_items[:3]  # Top 3 action items
                    }
                    for rec in recommendations[:5]  # Top 5 recommendations
                ],
                "growth_areas": analysis.get("skill_gaps", {}).get("priority_areas", []),
                "next_actions": [
                    "Review and prioritize recommendations",
                    "Schedule time for skill development",
                    "Update portfolio and online presence",
                    "Network with industry professionals"
                ]
            }
            
            logger.info(f"Generated daily summary for {profile.person.name}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}")
            raise
    
    async def answer_questions(self, profile: PersonProfile, question: str) -> str:
        """Answer questions about the user based on their profile."""
        logger.info(f"Answering question: {question}")
        
        try:
            # Create context from profile
            context = self._create_profile_context(profile)
            
            # Use OpenAI to answer the question
            response = await self.openai_client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a personal assistant for {profile.person.name}. "
                                 f"Use the following profile information to answer questions accurately and helpfully. "
                                 f"Always be professional and provide specific examples from their profile when possible."
                    },
                    {
                        "role": "user",
                        "content": f"Profile Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                temperature=self.settings.openai_temperature,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _create_profile_context(self, profile: PersonProfile) -> str:
        """Create a text context from the user's profile."""
        try:
            context_parts = []
            
            # Basic info
            context_parts.append(f"Name: {profile.person.name}")
            context_parts.append(f"Username: {profile.person.username}")
            if profile.person.bio:
                context_parts.append(f"Bio: {profile.person.bio}")
            if profile.person.location:
                context_parts.append(f"Location: {profile.person.location}")
            
            # Skills
            if profile.skills:
                skill_names = [skill.name for skill in profile.skills]
                context_parts.append(f"Skills: {', '.join(skill_names)}")
            
            # Repositories
            if profile.repositories:
                context_parts.append(f"Total Repositories: {len(profile.repositories)}")
                top_repos = sorted(profile.repositories, key=lambda x: x.stars, reverse=True)[:5]
                for repo in top_repos:
                    context_parts.append(f"Top Repository: {repo.name} ({repo.stars} stars, {repo.language})")
            
            # Articles
            if profile.articles:
                context_parts.append(f"Total Articles: {len(profile.articles)}")
                recent_articles = sorted(profile.articles, key=lambda x: x.published_at, reverse=True)[:3]
                for article in recent_articles:
                    context_parts.append(f"Recent Article: {article.title}")
            
            # Social activity
            if profile.social_posts:
                context_parts.append(f"Total Social Posts: {len(profile.social_posts)}")
                recent_posts = [post for post in profile.social_posts 
                              if (datetime.now() - post.created_at).days <= 30]
                context_parts.append(f"Recent Activity (30 days): {len(recent_posts)} posts")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error creating profile context: {str(e)}")
            return f"Basic profile information for {profile.person.name}"
    
    async def update_profile_data(self, usernames: Dict[str, str]) -> PersonProfile:
        """Update user profile data from all sources."""
        logger.info(f"Updating profile data for user: {usernames}")
        
        try:
            # Collect fresh data
            updated_profile = await self.collect_user_data(usernames)
            
            # Re-analyze and generate new recommendations
            await self.analyze_user_profile(updated_profile)
            await self.generate_recommendations(updated_profile)
            
            logger.info(f"Profile data updated successfully for {updated_profile.person.name}")
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error updating profile data: {str(e)}")
            raise
    
    async def get_career_insights(self, profile: PersonProfile) -> Dict[str, Any]:
        """Get comprehensive career insights and analysis."""
        logger.info(f"Generating career insights for {profile.person.name}")
        
        try:
            # Get full analysis
            analysis = await self.analyze_user_profile(profile)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(profile)
            
            # Create career insights
            career_insights = {
                "career_overview": analysis.get("career_trajectory", {}),
                "technical_assessment": analysis.get("technical_expertise", {}),
                "market_positioning": analysis.get("market_positioning", {}),
                "skill_analysis": analysis.get("skill_gaps", {}),
                "growth_opportunities": analysis.get("growth_opportunities", {}),
                "recommendations": [
                    {
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority,
                        "category": rec.category,
                        "action_items": rec.action_items,
                        "expected_outcome": rec.expected_outcome,
                        "deadline": rec.deadline.isoformat() if rec.deadline else None
                    }
                    for rec in recommendations
                ],
                "next_steps": [
                    "Prioritize high-impact recommendations",
                    "Create action plan with timelines",
                    "Track progress on skill development",
                    "Network with industry professionals",
                    "Update portfolio and online presence"
                ]
            }
            
            logger.info(f"Generated career insights for {profile.person.name}")
            return career_insights
            
        except Exception as e:
            logger.error(f"Error generating career insights: {str(e)}")
            raise
