"""
News data collector for gathering articles and publications.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .base_collector import BaseCollector
from ..models import Person, Repository, SocialPost, Article, SourceType

class NewsCollector(BaseCollector):
    """Collector for news and article data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(SourceType.NEWS, config)
        self.api_key = config.get("news_api_key")
        self.api_base_url = "https://newsapi.org/v2"
        self.rate_limit_delay = 1.0
        
        if self.api_key:
            self.headers = {"X-API-Key": self.api_key}
        else:
            self.headers = {}
            logger.warning("News API key not provided - collector will not function")
    
    async def collect_person_info(self, username: str) -> Optional[Person]:
        """News API doesn't provide user profiles."""
        return None
    
    async def collect_repositories(self, username: str) -> List[Repository]:
        """News API doesn't provide repositories."""
        return []
    
    async def collect_social_posts(self, username: str, limit: int = 100) -> List[SocialPost]:
        """News API doesn't provide social posts."""
        return []
    
    async def collect_articles(self, username: str, limit: int = 50) -> List[Article]:
        """Collect articles mentioning the username or related to their field."""
        if not self.api_key:
            logger.warning("News API key required for data collection")
            return []
        
        logger.info(f"Collecting news articles for {username}")
        
        try:
            articles = []
            
            # Search for articles mentioning the username
            search_queries = [
                username,
                f'"{username}"',  # Exact match
                f"{username} developer",
                f"{username} programmer",
                f"{username} software engineer"
            ]
            
            for query in search_queries:
                try:
                    url = f"{self.api_base_url}/everything"
                    params = {
                        "q": query,
                        "sortBy": "publishedAt",
                        "language": "en",
                        "pageSize": min(limit // len(search_queries), 20),
                        "apiKey": self.api_key
                    }
                    
                    data = await self._make_request(url, self.headers, params)
                    
                    if data and "articles" in data:
                        for article_data in data["articles"]:
                            try:
                                # Skip if no content
                                if not article_data.get("content"):
                                    continue
                                
                                # Parse published date
                                published_at = datetime.now()
                                if article_data.get("publishedAt"):
                                    try:
                                        published_at = datetime.fromisoformat(
                                            article_data["publishedAt"].replace("Z", "+00:00")
                                        )
                                    except:
                                        pass
                                
                                # Create article object
                                article = Article(
                                    id=f"news_{article_data.get('url', '').replace('/', '_')}",
                                    title=article_data.get("title", ""),
                                    content=article_data.get("content", ""),
                                    summary=article_data.get("description", ""),
                                    author=article_data.get("author", "Unknown"),
                                    source_url=article_data.get("url", ""),
                                    source_type=SourceType.NEWS,
                                    published_at=published_at,
                                    tags=[],  # News API doesn't provide tags
                                    read_time=max(1, len(article_data.get("content", "")) // 500)
                                )
                                
                                articles.append(article)
                                
                                # Check if we've reached the limit
                                if len(articles) >= limit:
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"Error parsing news article: {str(e)}")
                                continue
                    
                    # Check if we've reached the limit
                    if len(articles) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error searching for query '{query}': {str(e)}")
                    continue
            
            logger.info(f"Collected {len(articles)} news articles for {username}")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting news articles for {username}: {str(e)}")
            return []
    
    async def collect_articles_by_topic(self, topics: List[str], limit: int = 50) -> List[Article]:
        """Collect articles by specific topics (useful for industry insights)."""
        if not self.api_key:
            logger.warning("News API key required for data collection")
            return []
        
        logger.info(f"Collecting news articles for topics: {topics}")
        
        try:
            articles = []
            
            for topic in topics:
                try:
                    url = f"{self.api_base_url}/everything"
                    params = {
                        "q": topic,
                        "sortBy": "publishedAt",
                        "language": "en",
                        "pageSize": min(limit // len(topics), 20),
                        "apiKey": self.api_key
                    }
                    
                    data = await self._make_request(url, self.headers, params)
                    
                    if data and "articles" in data:
                        for article_data in data["articles"]:
                            try:
                                # Skip if no content
                                if not article_data.get("content"):
                                    continue
                                
                                # Parse published date
                                published_at = datetime.now()
                                if article_data.get("publishedAt"):
                                    try:
                                        published_at = datetime.fromisoformat(
                                            article_data["publishedAt"].replace("Z", "+00:00")
                                        )
                                    except:
                                        pass
                                
                                # Create article object
                                article = Article(
                                    id=f"news_topic_{topic}_{article_data.get('url', '').replace('/', '_')}",
                                    title=article_data.get("title", ""),
                                    content=article_data.get("content", ""),
                                    summary=article_data.get("description", ""),
                                    author=article_data.get("author", "Unknown"),
                                    source_url=article_data.get("url", ""),
                                    source_type=SourceType.NEWS,
                                    published_at=published_at,
                                    tags=[topic],
                                    read_time=max(1, len(article_data.get("content", "")) // 500)
                                )
                                
                                articles.append(article)
                                
                                # Check if we've reached the limit
                                if len(articles) >= limit:
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"Error parsing topic article: {str(e)}")
                                continue
                    
                    # Check if we've reached the limit
                    if len(articles) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error searching for topic '{topic}': {str(e)}")
                    continue
            
            logger.info(f"Collected {len(articles)} topic articles for: {topics}")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting topic articles: {str(e)}")
            return []
    
    async def _make_request(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with rate limiting and parameter support."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"News API rate limited. Waiting {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(url, headers, params)
                else:
                    logger.warning(f"News API request failed with status {response.status}: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"News API request error for {url}: {str(e)}")
            return None
