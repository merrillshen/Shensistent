"""
Twitter data collector for gathering social media activity.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .base_collector import BaseCollector
from ..models import Person, Repository, SocialPost, Article, SourceType

class TwitterCollector(BaseCollector):
    """Collector for Twitter data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(SourceType.TWITTER, config)
        self.bearer_token = config.get("twitter_bearer_token")
        self.api_base_url = "https://api.twitter.com/2"
        self.rate_limit_delay = 1.0
        
        if self.bearer_token:
            self.headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {}
            logger.warning("Twitter bearer token not provided - collector will not function")
    
    async def collect_person_info(self, username: str) -> Optional[Person]:
        """Collect Twitter user profile information."""
        if not self.bearer_token:
            logger.warning("Twitter bearer token required for data collection")
            return None
        
        logger.info(f"Collecting Twitter profile for {username}")
        
        try:
            url = f"{self.api_base_url}/users/by/username/{username}"
            data = await self._make_request(url, self.headers)
            
            if not data or "data" not in data:
                logger.warning(f"No Twitter data found for {username}")
                return None
            
            user_data = data["data"]
            
            person = Person(
                id=str(user_data.get("id", username)),
                name=user_data.get("name", username),
                username=user_data.get("username", username),
                email=None,
                bio=user_data.get("description"),
                location=user_data.get("location"),
                website=user_data.get("url"),
                avatar_url=user_data.get("profile_image_url"),
                created_at=datetime.fromisoformat(user_data.get("created_at", "").replace("Z", "+00:00")),
                updated_at=datetime.now()
            )
            
            logger.info(f"Collected Twitter profile for {username}")
            return person
            
        except Exception as e:
            logger.error(f"Error collecting Twitter profile for {username}: {str(e)}")
            return None
    
    async def collect_repositories(self, username: str) -> List[Repository]:
        """Twitter doesn't have repositories."""
        return []
    
    async def collect_social_posts(self, username: str, limit: int = 100) -> List[SocialPost]:
        """Collect Twitter posts and tweets."""
        if not self.bearer_token:
            logger.warning("Twitter bearer token required for data collection")
            return []
        
        logger.info(f"Collecting Twitter posts for {username}")
        
        try:
            # First get user ID
            user_url = f"{self.api_base_url}/users/by/username/{username}"
            user_data = await self._make_request(user_url, self.headers)
            
            if not user_data or "data" not in user_data:
                return []
            
            user_id = user_data["data"]["id"]
            
            # Get user's tweets
            tweets_url = f"{self.api_base_url}/users/{user_id}/tweets"
            params = {
                "max_results": min(limit, 100),  # Twitter API limit
                "tweet.fields": "created_at,public_metrics,entities"
            }
            
            tweets_data = await self._make_request(tweets_url, self.headers, params)
            
            if not tweets_data or "data" not in tweets_data:
                return []
            
            posts = []
            for tweet in tweets_data["data"]:
                try:
                    # Extract hashtags
                    hashtags = []
                    if "entities" in tweet and "hashtags" in tweet["entities"]:
                        hashtags = [tag["tag"] for tag in tweet["entities"]["hashtags"]]
                    
                    # Get engagement metrics
                    metrics = tweet.get("public_metrics", {})
                    
                    post = SocialPost(
                        id=f"twitter_{tweet['id']}",
                        content=tweet["text"],
                        source_type=SourceType.TWITTER,
                        author=username,
                        created_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                        likes=metrics.get("like_count", 0),
                        shares=metrics.get("retweet_count", 0),
                        hashtags=hashtags,
                        url=f"https://twitter.com/{username}/status/{tweet['id']}"
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    logger.warning(f"Error parsing tweet {tweet.get('id', 'unknown')}: {str(e)}")
                    continue
            
            logger.info(f"Collected {len(posts)} Twitter posts for {username}")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting Twitter posts for {username}: {str(e)}")
            return []
    
    async def collect_articles(self, username: str, limit: int = 50) -> List[Article]:
        """Twitter doesn't have traditional articles."""
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
                    logger.warning(f"Twitter rate limited. Waiting {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(url, headers, params)
                else:
                    logger.warning(f"Twitter request failed with status {response.status}: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Twitter request error for {url}: {str(e)}")
            return None
