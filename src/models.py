"""
Data models for Shensistent agent.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class SourceType(str, Enum):
    """Types of data sources."""
    GITHUB = "github"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    NEWS = "news"
    BLOG = "blog"
    PORTFOLIO = "portfolio"
    RESEARCH_PAPER = "research_paper"
    CONFERENCE = "conference"

class ContentType(str, Enum):
    """Types of content."""
    REPOSITORY = "repository"
    POST = "post"
    ARTICLE = "article"
    PROJECT = "project"
    SKILL = "skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"

class Person(BaseModel):
    """Person entity model."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Full name")
    username: str = Field(..., description="Primary username")
    email: Optional[str] = Field(None, description="Email address")
    bio: Optional[str] = Field(None, description="Biography")
    location: Optional[str] = Field(None, description="Location")
    website: Optional[str] = Field(None, description="Personal website")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Repository(BaseModel):
    """GitHub repository model."""
    id: str = Field(..., description="Repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name")
    description: Optional[str] = Field(None, description="Repository description")
    language: Optional[str] = Field(None, description="Primary programming language")
    stars: int = Field(default=0, description="Number of stars")
    forks: int = Field(default=0, description="Number of forks")
    topics: List[str] = Field(default=[], description="Repository topics")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: datetime = Field(..., description="Last update date")
    source_type: SourceType = Field(default=SourceType.GITHUB)

class SocialPost(BaseModel):
    """Social media post model."""
    id: str = Field(..., description="Post ID")
    content: str = Field(..., description="Post content")
    source_type: SourceType = Field(..., description="Source platform")
    author: str = Field(..., description="Author username")
    created_at: datetime = Field(..., description="Post creation date")
    likes: int = Field(default=0, description="Number of likes")
    shares: int = Field(default=0, description="Number of shares")
    hashtags: List[str] = Field(default=[], description="Hashtags used")
    url: Optional[str] = Field(None, description="Post URL")

class Article(BaseModel):
    """Article or blog post model."""
    id: str = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    author: str = Field(..., description="Author name")
    source_url: str = Field(..., description="Article URL")
    source_type: SourceType = Field(..., description="Source type")
    published_at: datetime = Field(..., description="Publication date")
    tags: List[str] = Field(default=[], description="Article tags")
    read_time: Optional[int] = Field(None, description="Estimated read time in minutes")

class Skill(BaseModel):
    """Skill or technology model."""
    id: str = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill name")
    category: str = Field(..., description="Skill category")
    proficiency_level: str = Field(..., description="Proficiency level")
    years_experience: Optional[int] = Field(None, description="Years of experience")
    projects_count: int = Field(default=0, description="Number of projects using this skill")
    endorsements: int = Field(default=0, description="Number of endorsements")
    last_used: Optional[datetime] = Field(None, description="Last time skill was used")

class Experience(BaseModel):
    """Work experience model."""
    id: str = Field(..., description="Experience ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Job description")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    current: bool = Field(default=False, description="Currently employed")
    skills_used: List[str] = Field(default=[], description="Skills used in this role")
    achievements: List[str] = Field(default=[], description="Key achievements")

class Education(BaseModel):
    """Education model."""
    id: str = Field(..., description="Education ID")
    degree: str = Field(..., description="Degree name")
    institution: str = Field(..., description="Institution name")
    field_of_study: str = Field(..., description="Field of study")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    gpa: Optional[float] = Field(None, description="GPA if applicable")
    description: Optional[str] = Field(None, description="Additional details")

class JobOpportunity(BaseModel):
    """Job opportunity model."""
    id: str = Field(..., description="Opportunity ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(default=[], description="Job requirements")
    location: str = Field(..., description="Job location")
    salary_range: Optional[str] = Field(None, description="Salary range")
    job_type: str = Field(..., description="Full-time, part-time, contract, etc.")
    posted_date: datetime = Field(..., description="Date posted")
    application_url: str = Field(..., description="Application URL")
    match_score: float = Field(..., description="Match score with person's profile")
    skills_match: List[str] = Field(default=[], description="Matching skills")

class Recommendation(BaseModel):
    """Personal recommendation model."""
    id: str = Field(..., description="Recommendation ID")
    category: str = Field(..., description="Recommendation category")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(..., description="High, medium, or low priority")
    action_items: List[str] = Field(default=[], description="Specific action items")
    expected_outcome: str = Field(..., description="Expected outcome")
    deadline: Optional[datetime] = Field(None, description="Recommended deadline")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Connection(BaseModel):
    """Professional connection suggestion model."""
    id: str = Field(..., description="Connection ID")
    name: str = Field(..., description="Person's name")
    title: str = Field(..., description="Professional title")
    company: str = Field(..., description="Company name")
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    connection_reason: str = Field(..., description="Why this connection would be valuable")
    mutual_interests: List[str] = Field(default=[], description="Shared interests or skills")
    connection_strength: float = Field(..., description="Connection strength score")
    suggested_message: str = Field(..., description="Suggested connection message")

class PersonProfile(BaseModel):
    """Complete person profile model."""
    person: Person
    repositories: List[Repository] = Field(default=[])
    social_posts: List[SocialPost] = Field(default=[])
    articles: List[Article] = Field(default=[])
    skills: List[Skill] = Field(default=[])
    experiences: List[Experience] = Field(default=[])
    education: List[Education] = Field(default=[])
    recommendations: List[Recommendation] = Field(default=[])
    connections: List[Connection] = Field(default=[])
    job_opportunities: List[JobOpportunity] = Field(default=[])
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
