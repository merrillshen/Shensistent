"""
Base collector class for data collection from online sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
from loguru import logger

from ..models import Person, Repository, SocialPost, Article, SourceType

class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self, source_type: SourceType, config: Dict[str, Any]):
        self.source_type = source_type
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 1.0  # Default delay between requests
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def collect_person_info(self, username: str) -> Optional[Person]:
        """Collect basic person information."""
        pass
    
    @abstractmethod
    async def collect_repositories(self, username: str) -> List[Repository]:
        """Collect repositories/projects."""
        pass
    
    @abstractmethod
    async def collect_social_posts(self, username: str, limit: int = 100) -> List[SocialPost]:
        """Collect social media posts."""
        pass
    
    @abstractmethod
    async def collect_articles(self, username: str, limit: int = 50) -> List[Article]:
        """Collect articles and blog posts."""
        pass
    
    async def collect_all_data(self, username: str) -> Dict[str, Any]:
        """Collect all available data for a user."""
        logger.info(f"Starting data collection for {username} from {self.source_type.value}")
        
        try:
            # Collect person info
            person = await self.collect_person_info(username)
            if not person:
                logger.warning(f"Could not collect person info for {username}")
                return {}
            
            # Collect repositories
            repositories = await self.collect_repositories(username)
            logger.info(f"Collected {len(repositories)} repositories for {username}")
            
            # Collect social posts
            social_posts = await self.collect_social_posts(username)
            logger.info(f"Collected {len(social_posts)} social posts for {username}")
            
            # Collect articles
            articles = await self.collect_articles(username)
            logger.info(f"Collected {len(articles)} articles for {username}")
            
            return {
                "person": person,
                "repositories": repositories,
                "social_posts": social_posts,
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error collecting data for {username}: {str(e)}")
            return {}
    
    async def _make_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with rate limiting."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(url, headers)
                else:
                    logger.warning(f"Request failed with status {response.status}: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
    
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
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        
        return text.strip()
