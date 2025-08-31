"""
Main application entry point for Shensistent Personal Assistant.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from .config import get_settings
from .agent import PersonalAssistant
from .models import PersonProfile

# Global variables
settings = get_settings()
personal_assistant: PersonalAssistant = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global personal_assistant
    
    # Startup
    logger.info("Starting Shensistent Personal Assistant...")
    
    try:
        # Initialize OpenAI client
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Initialize personal assistant
        personal_assistant = PersonalAssistant(openai_client)
        logger.info("Personal Assistant initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Shensistent Personal Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Shensistent Personal Assistant",
    description="A hyperpersonalized personal assistant agent that offers advice and guidance",
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class UserDataRequest(BaseModel):
    """Request model for user data collection."""
    usernames: Dict[str, str]  # e.g., {"github": "username", "linkedin": "username"}

class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str

class UpdateRequest(BaseModel):
    """Request model for updating profile data."""
    usernames: Dict[str, str]

# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Shensistent Personal Assistant",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/collect-data")
async def collect_user_data(request: UserDataRequest):
    """Collect comprehensive user data from all sources."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        profile = await personal_assistant.collect_user_data(request.usernames)
        
        return {
            "success": True,
            "message": f"Data collected successfully for {profile.person.name}",
            "profile_summary": {
                "name": profile.person.name,
                "username": profile.person.username,
                "total_repositories": len(profile.repositories),
                "total_articles": len(profile.articles),
                "total_skills": len(profile.skills),
                "total_social_posts": len(profile.social_posts)
            }
        }
        
    except Exception as e:
        logger.error(f"Error collecting user data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error collecting data: {str(e)}")

@app.post("/analyze-profile")
async def analyze_profile(request: UserDataRequest):
    """Analyze user profile and extract insights."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # First collect data
        profile = await personal_assistant.collect_user_data(request.usernames)
        
        # Then analyze
        analysis = await personal_assistant.analyze_user_profile(profile)
        
        return {
            "success": True,
            "message": f"Profile analyzed successfully for {profile.person.name}",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing profile: {str(e)}")

@app.post("/get-recommendations")
async def get_recommendations(request: UserDataRequest):
    """Get personalized recommendations."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # First collect data
        profile = await personal_assistant.collect_user_data(request.usernames)
        
        # Then generate recommendations
        recommendations = await personal_assistant.generate_recommendations(profile)
        
        return {
            "success": True,
            "message": f"Recommendations generated successfully for {profile.person.name}",
            "recommendations": [
                {
                    "id": rec.id,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "category": rec.category,
                    "action_items": rec.action_items,
                    "expected_outcome": rec.expected_outcome,
                    "deadline": rec.deadline.isoformat() if rec.deadline else None
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/daily-summary")
async def get_daily_summary(request: UserDataRequest):
    """Get daily summary and insights."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # First collect data
        profile = await personal_assistant.collect_user_data(request.usernames)
        
        # Then get daily summary
        summary = await personal_assistant.get_daily_summary(profile)
        
        return {
            "success": True,
            "message": f"Daily summary generated successfully for {profile.person.name}",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error generating daily summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating daily summary: {str(e)}")

@app.post("/ask-question")
async def ask_question(request: QuestionRequest, user_data: UserDataRequest):
    """Ask questions about the user based on their profile."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # First collect data
        profile = await personal_assistant.collect_user_data(user_data.usernames)
        
        # Then answer the question
        answer = await personal_assistant.answer_questions(profile, request.question)
        
        return {
            "success": True,
            "message": "Question answered successfully",
            "question": request.question,
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@app.post("/career-insights")
async def get_career_insights(request: UserDataRequest):
    """Get comprehensive career insights and analysis."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # First collect data
        profile = await personal_assistant.collect_user_data(request.usernames)
        
        # Then get career insights
        insights = await personal_assistant.get_career_insights(profile)
        
        return {
            "success": True,
            "message": f"Career insights generated successfully for {profile.person.name}",
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error generating career insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating career insights: {str(e)}")

@app.post("/update-profile")
async def update_profile(request: UpdateRequest):
    """Update user profile data from all sources."""
    try:
        if not personal_assistant:
            raise HTTPException(status_code=503, detail="Personal Assistant not initialized")
        
        # Update profile data
        updated_profile = await personal_assistant.update_profile_data(request.usernames)
        
        return {
            "success": True,
            "message": f"Profile updated successfully for {updated_profile.person.name}",
            "profile_summary": {
                "name": updated_profile.person.name,
                "username": updated_profile.person.username,
                "total_repositories": len(updated_profile.repositories),
                "total_articles": len(updated_profile.articles),
                "total_skills": len(updated_profile.skills),
                "total_social_posts": len(updated_profile.social_posts),
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

# CLI interface
def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Shensistent Personal Assistant")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        "logs/shensistent.log",
        rotation="1 day",
        retention="7 days",
        level=args.log_level.upper()
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level=args.log_level.upper()
    )
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
