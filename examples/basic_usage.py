#!/usr/bin/env python3
"""
Basic usage example for Shensistent Personal Assistant.

This script demonstrates how to:
1. Initialize the personal assistant
2. Collect user data from GitHub
3. Generate recommendations
4. Get career insights
5. Ask questions about the user

Requirements:
- OpenAI API key in environment variable OPENAI_API_KEY
- Optional: GitHub token in environment variable GITHUB_TOKEN
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import PersonalAssistant
from openai import AsyncOpenAI

async def main():
    """Main example function."""
    print("🚀 Shensistent Personal Assistant - Basic Usage Example")
    print("=" * 60)
    
    # Check for required environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key and try again")
        return
    
    # Initialize OpenAI client
    print("🔧 Initializing OpenAI client...")
    openai_client = AsyncOpenAI(api_key=openai_api_key)
    
    # Initialize personal assistant
    print("🤖 Initializing Personal Assistant...")
    try:
        assistant = PersonalAssistant(openai_client)
        print("✅ Personal Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing Personal Assistant: {e}")
        return
    
    # Example usernames (replace with actual usernames)
    usernames = {
        "github": "octocat",  # Replace with actual GitHub username
        # "twitter": "username",  # Uncomment and add Twitter username
        # "linkedin": "username", # Uncomment and add LinkedIn username
    }
    
    print(f"\n📊 Collecting data for usernames: {usernames}")
    print("-" * 40)
    
    try:
        # Collect user data
        profile = await assistant.collect_user_data(usernames)
        print(f"✅ Data collected successfully for {profile.person.name}")
        print(f"   📁 Repositories: {len(profile.repositories)}")
        print(f"   📝 Articles: {len(profile.articles)}")
        print(f"   🛠️  Skills: {len(profile.skills)}")
        print(f"   📱 Social Posts: {len(profile.social_posts)}")
        
    except Exception as e:
        print(f"❌ Error collecting data: {e}")
        print("This might be due to invalid usernames or API rate limits")
        return
    
    # Generate recommendations
    print(f"\n💡 Generating personalized recommendations...")
    print("-" * 40)
    
    try:
        recommendations = await assistant.generate_recommendations(profile)
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        # Show top 3 recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\n{i}. 📋 {rec.title}")
            print(f"   Priority: {rec.priority.upper()}")
            print(f"   Category: {rec.category}")
            print(f"   Description: {rec.description}")
            if rec.action_items:
                print(f"   Actions: {rec.action_items[0]}")  # Show first action item
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
    
    # Get career insights
    print(f"\n🎯 Analyzing career insights...")
    print("-" * 40)
    
    try:
        insights = await assistant.get_career_insights(profile)
        
        # Extract key insights
        career_overview = insights.get("career_overview", {})
        technical_assessment = insights.get("technical_assessment", {})
        market_positioning = insights.get("market_positioning", {})
        
        print(f"✅ Career analysis completed!")
        print(f"   🎯 Career Stage: {career_overview.get('career_stage', 'Unknown')}")
        print(f"   💻 Technical Score: {technical_assessment.get('technical_score', 0)}/100")
        print(f"   📈 Market Position: {market_positioning.get('market_positioning_score', 0)}/100")
        
        # Show growth opportunities
        growth_opps = insights.get("growth_opportunities", {})
        if growth_opps.get("opportunities"):
            print(f"   🌱 Growth Opportunities: {growth_opps['total_opportunities']}")
        
    except Exception as e:
        print(f"❌ Error analyzing career insights: {e}")
    
    # Ask questions about the user
    print(f"\n❓ Asking questions about the user...")
    print("-" * 40)
    
    questions = [
        "What are this person's strongest technical skills?",
        "What type of projects do they typically work on?",
        "What career advice would you give this person?",
    ]
    
    for i, question in enumerate(questions, 1):
        try:
            print(f"\nQ{i}: {question}")
            answer = await assistant.answer_questions(profile, question)
            print(f"A{i}: {answer}")
            
        except Exception as e:
            print(f"❌ Error answering question {i}: {e}")
    
    # Get daily summary
    print(f"\n📅 Generating daily summary...")
    print("-" * 40)
    
    try:
        summary = await assistant.get_daily_summary(profile)
        print(f"✅ Daily summary generated!")
        
        # Show key metrics
        overview = summary.get("overview", {})
        key_insights = summary.get("key_insights", {})
        
        print(f"   📊 Total Repositories: {overview.get('total_repositories', 0)}")
        print(f"   📝 Total Articles: {overview.get('total_articles', 0)}")
        print(f"   🛠️  Total Skills: {overview.get('total_skills', 0)}")
        print(f"   📱 Recent Activity: {overview.get('recent_activity', 0)} posts (7 days)")
        
        print(f"   💻 Technical Score: {key_insights.get('technical_score', 0)}/100")
        print(f"   🌐 Online Presence: {key_insights.get('online_presence_score', 0)}/100")
        
    except Exception as e:
        print(f"❌ Error generating daily summary: {e}")
    
    print(f"\n🎉 Example completed successfully!")
    print("=" * 60)
    print("💡 Tips:")
    print("   - Replace 'octocat' with actual GitHub usernames")
    print("   - Add Twitter and LinkedIn usernames for more comprehensive data")
    print("   - Set GITHUB_TOKEN for better rate limits and access")
    print("   - Check the API documentation for more endpoints")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
