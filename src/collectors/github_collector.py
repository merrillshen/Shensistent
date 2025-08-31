"""
GitHub data collector for gathering repository and profile information.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger

from .base_collector import BaseCollector
from ..models import Person, Repository, SocialPost, Article, SourceType

class GitHubCollector(BaseCollector):
    """Collector for GitHub data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(SourceType.GITHUB, config)
        self.api_token = config.get("github_token")
        self.api_base_url = "https://api.github.com"
        self.rate_limit_delay = 0.1  # GitHub allows 5000 requests per hour for authenticated users
        
        if self.api_token:
            self.headers = {
                "Authorization": f"token {self.api_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        else:
            self.headers = {"Accept": "application/vnd.github.v3+json"}
    
    async def collect_person_info(self, username: str) -> Optional[Person]:
        """Collect GitHub user profile information."""
        url = f"{self.api_base_url}/users/{username}"
        
        try:
            data = await self._make_request(url, self.headers)
            if not data:
                return None
            
            # Parse GitHub user data
            person = Person(
                id=str(data.get("id", username)),
                name=data.get("name", username),
                username=data.get("login", username),
                email=data.get("email"),
                bio=data.get("bio"),
                location=data.get("location"),
                website=data.get("blog"),
                avatar_url=data.get("avatar_url"),
                created_at=datetime.fromisoformat(data.get("created_at", "").replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data.get("updated_at", "").replace("Z", "+00:00"))
            )
            
            logger.info(f"Collected GitHub profile for {username}")
            return person
            
        except Exception as e:
            logger.error(f"Error collecting GitHub profile for {username}: {str(e)}")
            return None
    
    async def collect_repositories(self, username: str) -> List[Repository]:
        """Collect GitHub repositories for a user."""
        repositories = []
        page = 1
        per_page = 100
        
        try:
            while True:
                url = f"{self.api_base_url}/users/{username}/repos?page={page}&per_page={per_page}&sort=updated"
                data = await self._make_request(url, self.headers)
                
                if not data or not isinstance(data, list):
                    break
                
                for repo_data in data:
                    try:
                        # Skip forked repositories unless they have significant activity
                        if repo_data.get("fork") and repo_data.get("forks_count", 0) < 5:
                            continue
                        
                        # Parse repository data
                        repo = Repository(
                            id=str(repo_data.get("id", "")),
                            name=repo_data.get("name", ""),
                            full_name=repo_data.get("full_name", ""),
                            description=repo_data.get("description"),
                            language=repo_data.get("language"),
                            stars=repo_data.get("stargazers_count", 0),
                            forks=repo_data.get("forks_count", 0),
                            topics=repo_data.get("topics", []),
                            created_at=datetime.fromisoformat(repo_data.get("created_at", "").replace("Z", "+00:00")),
                            updated_at=datetime.fromisoformat(repo_data.get("updated_at", "").replace("Z", "+00:00")),
                            source_type=SourceType.GITHUB
                        )
                        
                        repositories.append(repo)
                        
                        # Limit the number of repositories collected
                        if len(repositories) >= self.config.get("max_repositories", 100):
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error parsing repository {repo_data.get('name', '')}: {str(e)}")
                        continue
                
                if len(data) < per_page or len(repositories) >= self.config.get("max_repositories", 100):
                    break
                
                page += 1
            
            logger.info(f"Collected {len(repositories)} repositories for {username}")
            return repositories
            
        except Exception as e:
            logger.error(f"Error collecting repositories for {username}: {str(e)}")
            return repositories
    
    async def collect_social_posts(self, username: str, limit: int = 100) -> List[SocialPost]:
        """Collect GitHub activity as social posts."""
        # GitHub doesn't have traditional social posts, but we can collect recent activity
        posts = []
        
        try:
            # Get recent activity from public events
            url = f"{self.api_base_url}/users/{username}/events/public?per_page={limit}"
            data = await self._make_request(url, self.headers)
            
            if data and isinstance(data, list):
                for event in data[:limit]:
                    try:
                        # Create social post from GitHub event
                        post = self._create_post_from_event(event, username)
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Error parsing GitHub event: {str(e)}")
                        continue
            
            logger.info(f"Collected {len(posts)} GitHub activities for {username}")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting GitHub activities for {username}: {str(e)}")
            return posts
    
    async def collect_articles(self, username: str, limit: int = 50) -> List[Article]:
        """Collect articles from GitHub (README files, wikis, etc.)."""
        articles = []
        
        try:
            # Get repositories to check for README files and wikis
            repositories = await self.collect_repositories(username)
            
            for repo in repositories[:limit//2]:  # Limit repositories to check
                try:
                    # Check for README file
                    readme_url = f"{self.api_base_url}/repos/{username}/{repo.name}/readme"
                    readme_data = await self._make_request(readme_url, self.headers)
                    
                    if readme_data and readme_data.get("content"):
                        # Decode base64 content (GitHub stores content in base64)
                        import base64
                        content = base64.b64decode(readme_data["content"]).decode("utf-8")
                        
                        article = Article(
                            id=f"readme_{repo.id}",
                            title=f"README - {repo.name}",
                            content=content,
                            summary=content[:200] + "..." if len(content) > 200 else content,
                            author=username,
                            source_url=f"https://github.com/{username}/{repo.name}",
                            source_type=SourceType.GITHUB,
                            published_at=repo.updated_at,
                            tags=repo.topics,
                            read_time=max(1, len(content) // 500)  # Rough estimate: 500 chars per minute
                        )
                        
                        articles.append(article)
                        
                        if len(articles) >= limit:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error collecting README for {repo.name}: {str(e)}")
                    continue
            
            logger.info(f"Collected {len(articles)} articles from GitHub for {username}")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting articles from GitHub for {username}: {str(e)}")
            return articles
    
    def _create_post_from_event(self, event: Dict[str, Any], username: str) -> Optional[SocialPost]:
        """Create a social post from a GitHub event."""
        try:
            event_type = event.get("type", "")
            repo_name = event.get("repo", {}).get("name", "")
            created_at = datetime.fromisoformat(event.get("created_at", "").replace("Z", "+00:00"))
            
            # Create content based on event type
            if event_type == "PushEvent":
                commits = event.get("payload", {}).get("commits", [])
                if commits:
                    content = f"Pushed {len(commits)} commit(s) to {repo_name}"
                else:
                    content = f"Pushed to {repo_name}"
                    
            elif event_type == "CreateEvent":
                ref_type = event.get("payload", {}).get("ref_type", "")
                content = f"Created {ref_type} in {repo_name}"
                
            elif event_type == "ForkEvent":
                content = f"Forked {repo_name}"
                
            elif event_type == "WatchEvent":
                content = f"Starred {repo_name}"
                
            else:
                content = f"{event_type} in {repo_name}"
            
            return SocialPost(
                id=f"gh_{event.get('id', '')}",
                content=content,
                source_type=SourceType.GITHUB,
                author=username,
                created_at=created_at,
                url=f"https://github.com/{username}"
            )
            
        except Exception as e:
            logger.warning(f"Error creating post from GitHub event: {str(e)}")
            return None
