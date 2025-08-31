# Shensistent - Hyperpersonalized Personal Assistant Agent

A comprehensive AI-powered personal assistant that acts as both a personal helper and professional representative, leveraging publicly available online information to provide personalized advice, career insights, and growth recommendations.

## 🌟 Features

### 🤖 **Personal Assistant Capabilities**
- **Daily Recommendations**: Personalized suggestions for personal and career growth
- **Skill Analysis**: Comprehensive assessment of technical skills and expertise
- **Career Insights**: Analysis of career trajectory and market positioning
- **Content Quality Assessment**: Evaluation of online presence and portfolio
- **Growth Opportunities**: Identification of areas for improvement and development

### 🔍 **Data Collection & Intelligence**
- **GitHub Integration**: Repository analysis, contribution patterns, and skill extraction
- **Social Media Monitoring**: Twitter activity, LinkedIn presence, and engagement metrics
- **News & Publications**: Articles, blog posts, and industry-related content
- **Professional Network**: Connection suggestions and networking opportunities
- **Market Intelligence**: Industry trends and competitive positioning

### 🌐 **Professional Representative**
- **Recruiter Interface**: AI-powered responses to potential employer inquiries
- **Portfolio Showcase**: Comprehensive presentation of skills and achievements
- **Career Wikipedia**: Detailed professional background and expertise
- **Opportunity Matching**: Job recommendations and career advancement suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Optional: GitHub, Twitter, LinkedIn, and News API credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Shensistent.git
cd Shensistent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Run the application**
```bash
# Start the FastAPI server
python -m src.main --reload

# Or run directly
uvicorn src.main:app --reload
```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here

# Optional - for enhanced data collection
GITHUB_TOKEN=your_github_token_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
LINKEDIN_USERNAME=your_linkedin_username
LINKEDIN_PASSWORD=your_linkedin_password
NEWS_API_KEY=your_news_api_key_here

# Application settings
DEBUG=false
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
UPDATE_FREQUENCY_HOURS=24
```

## 📖 Usage Examples

### 1. **Collect User Data**
```python
import asyncio
from src.agent import PersonalAssistant
from openai import AsyncOpenAI

async def main():
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key="your_api_key")
    
    # Initialize personal assistant
    assistant = PersonalAssistant(openai_client)
    
    # Collect data from multiple sources
    usernames = {
        "github": "your_github_username",
        "twitter": "your_twitter_username",
        "linkedin": "your_linkedin_username"
    }
    
    profile = await assistant.collect_user_data(usernames)
    print(f"Collected data for {profile.person.name}")
    print(f"Repositories: {len(profile.repositories)}")
    print(f"Skills: {len(profile.skills)}")

asyncio.run(main())
```

### 2. **Get Daily Recommendations**
```python
# Generate personalized recommendations
recommendations = await assistant.generate_recommendations(profile)

for rec in recommendations[:5]:
    print(f"📋 {rec.title}")
    print(f"   Priority: {rec.priority}")
    print(f"   Category: {rec.category}")
    print(f"   Actions: {', '.join(rec.action_items[:3])}")
    print()
```

### 3. **Analyze Career Insights**
```python
# Get comprehensive career analysis
insights = await assistant.get_career_insights(profile)

print(f"🎯 Career Stage: {insights['career_overview']['career_stage']}")
print(f"💻 Technical Score: {insights['technical_assessment']['technical_score']}")
print(f"📈 Market Position: {insights['market_positioning']['market_positioning_score']}")
```

### 4. **Ask Questions About the User**
```python
# Ask questions about the user's profile
question = "What are this person's strongest technical skills?"
answer = await assistant.answer_questions(profile, question)
print(f"Q: {question}")
print(f"A: {answer}")
```

## 🌐 API Endpoints

The system provides a comprehensive REST API:

### **Core Endpoints**
- `POST /collect-data` - Collect user data from all sources
- `POST /analyze-profile` - Analyze user profile and extract insights
- `POST /get-recommendations` - Generate personalized recommendations
- `POST /daily-summary` - Get daily summary and insights
- `POST /ask-question` - Ask questions about the user
- `POST /career-insights` - Get comprehensive career analysis
- `POST /update-profile` - Update profile data from all sources

### **Example API Request**
```bash
curl -X POST "http://localhost:8000/collect-data" \
     -H "Content-Type: application/json" \
     -d '{
       "usernames": {
         "github": "your_github_username",
         "twitter": "your_twitter_username"
       }
     }'
```

## 🏗️ Architecture

### **Core Components**
```
src/
├── agent/                    # AI agent components
│   ├── personal_assistant.py    # Main orchestrator
│   ├── intelligence_engine.py   # Data analysis engine
│   └── recommendation_engine.py # Recommendation generator
├── collectors/              # Data collection modules
│   ├── base_collector.py       # Base collector class
│   ├── github_collector.py     # GitHub data collector
│   ├── linkedin_collector.py   # LinkedIn data collector
│   ├── twitter_collector.py    # Twitter data collector
│   └── news_collector.py       # News API collector
├── models.py                 # Data models and schemas
├── config.py                 # Configuration management
└── main.py                   # FastAPI application entry point
```

### **Data Flow**
1. **Data Collection**: Gather information from multiple online sources
2. **Profile Creation**: Merge and normalize collected data
3. **Intelligence Analysis**: Extract insights and patterns
4. **Recommendation Generation**: Create personalized suggestions
5. **API Response**: Provide structured data and insights

## 🔧 Development

### **Adding New Data Sources**
1. Create a new collector class inheriting from `BaseCollector`
2. Implement required abstract methods
3. Add configuration options in `config.py`
4. Register the collector in the main assistant

### **Extending Analysis Capabilities**
1. Add new analysis methods to `IntelligenceEngine`
2. Create corresponding recommendation logic in `RecommendationEngine`
3. Update data models as needed
4. Add new API endpoints

### **Running Tests**
```bash
pytest tests/ -v
```

## 📊 Data Sources

### **GitHub**
- User profile information
- Repository analysis (stars, forks, languages, topics)
- Contribution patterns and activity
- README files and documentation

### **Twitter**
- User profile and bio
- Tweet content and engagement metrics
- Hashtag analysis and content themes
- Activity patterns and frequency

### **LinkedIn**
- Professional profile information
- Work experience and education
- Skills and endorsements
- Network connections and recommendations

### **News & Publications**
- Articles mentioning the user
- Industry-related content
- Professional publications
- Blog posts and technical writing

## 🎯 Use Cases

### **For Individuals**
- **Career Development**: Track progress and identify growth opportunities
- **Skill Assessment**: Understand strengths and areas for improvement
- **Portfolio Enhancement**: Optimize online presence and content
- **Networking**: Identify valuable professional connections

### **For Recruiters**
- **Candidate Evaluation**: Comprehensive assessment of technical skills
- **Background Research**: Detailed professional history and achievements
- **Cultural Fit**: Understanding of interests and professional focus
- **Skill Verification**: Validation of claimed expertise

### **For Career Coaches**
- **Client Assessment**: Data-driven career analysis
- **Goal Setting**: Evidence-based career planning
- **Progress Tracking**: Measurable development metrics
- **Market Positioning**: Competitive analysis and positioning

## 🚧 Limitations & Considerations

### **Data Privacy**
- Only collects publicly available information
- Respects rate limits and terms of service
- No storage of sensitive personal data
- Configurable data retention policies

### **API Dependencies**
- Requires valid API keys for enhanced functionality
- Subject to third-party service availability
- Rate limiting may affect data collection speed
- Some sources require manual authentication

### **Accuracy**
- Analysis based on available public data
- May not reflect current private activities
- Recommendations are suggestions, not guarantees
- Regular updates recommended for best results

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Areas for Contribution**
- Additional data source collectors
- Enhanced analysis algorithms
- UI/UX improvements
- Documentation and examples
- Testing and quality assurance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- GitHub, Twitter, LinkedIn, and News APIs
- The open-source community for various dependencies
- Contributors and beta testers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Shensistent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Shensistent/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/Shensistent/wiki)

---

**Shensistent** - Your AI-powered personal and professional growth companion! 🚀
