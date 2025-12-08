# Chennai Tech Intelligence Hub 🏙️🤖

A sophisticated multi-agent system for real-time monitoring and analysis of Chennai's IT ecosystem.

## 🎯 Project Vision

Monitor the entire Chennai tech landscape through AI agents that work together to provide real-time business intelligence about:

- **Job Market Dynamics**: Live tracking of hiring trends, salary ranges, and skill demands
- **Technology Adoption**: Which frameworks, languages, and tools are trending
- **Startup Ecosystem**: New companies, funding rounds, and growth patterns  
- **Community Activity**: Tech events, meetups, and developer engagement
- **Talent Movement**: Where professionals are moving and what roles are hot

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React Dashboard (Port 3000)               │
│  Real-time charts │ Job trends │ Salary data │ Tech stats   │
└─────────────────┬───────────────────────────────────────────┘
                  │ WebSocket + REST API
┌─────────────────▼───────────────────────────────────────────┐
│                FastAPI Backend (Port 8000)                  │
│    Agent Orchestrator │ Data Pipeline │ Real-time Updates   │
└─────────────────┬───────────────────────────────────────────┘
                  │ Agent Coordination
┌─────────────────▼───────────────────────────────────────────┐
│                     AI Agent Fleet                          │
│ Job Scout │ Salary Intel │ Tech Monitor │ Startup │ Community │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agent Fleet

### 1. Job Market Scout Agent
- **Role**: Real-time job posting analysis
- **Sources**: Naukri, LinkedIn, Indeed, company career pages
- **Intelligence**: Skill demand tracking, role distribution, hiring velocity
- **Output**: Job trends, company hiring patterns, skill gap analysis

### 2. Salary Intelligence Agent  
- **Role**: Compensation trend monitoring
- **Sources**: Glassdoor, PayScale, job postings, salary surveys
- **Intelligence**: Pay band analysis, experience-wise breakdown, company comparisons
- **Output**: Salary ranges, compensation trends, market rates

### 3. Tech Stack Monitor Agent
- **Role**: Technology adoption tracking
- **Sources**: GitHub Chennai repos, job requirements, tech blogs
- **Intelligence**: Framework popularity, language trends, tool adoption
- **Output**: Tech stack popularity, emerging technologies, skill evolution

### 4. Startup Ecosystem Agent
- **Role**: Company and funding intelligence
- **Sources**: Crunchbase, VCCEdge, startup directories, news
- **Intelligence**: New company registration, funding rounds, growth tracking
- **Output**: Startup activity, funding trends, company lifecycle analysis

### 5. Community Pulse Agent
- **Role**: Developer community monitoring  
- **Sources**: Meetup.com, tech events, conference listings, social media
- **Intelligence**: Event popularity, community engagement, knowledge trends
- **Output**: Event calendar, community activity, learning trends

## ⚡ Real-time Features

- **Live Dashboard**: Auto-updating charts and metrics
- **WebSocket Updates**: Real-time data streaming
- **Smart Alerts**: Trend changes and market shifts
- **Historical Analysis**: Long-term pattern recognition
- **Predictive Intelligence**: AI-powered forecasting

## 🛠️ Tech Stack

**Backend**: FastAPI + SQLAlchemy + Redis + Celery  
**Frontend**: React + TypeScript + Recharts + TailwindCSS
**AI/ML**: CrewAI + Anthropic Claude + Pandas + Scikit-learn
**Data**: PostgreSQL + Redis Cache + WebSocket  
**Infrastructure**: Docker + async processing

## 🚀 Quick Start

```bash
# Start the intelligence hub
./start_hub.sh

# Backend will be on: http://localhost:8000
# Frontend will be on: http://localhost:3000  
# Real-time dashboard with live Chennai tech data
```

## 📊 Dashboard Features

1. **Job Market Overview**: Live job postings, trending roles, skill demands
2. **Salary Intelligence**: Compensation ranges, pay trends, company rankings  
3. **Tech Ecosystem**: Popular technologies, framework adoption, tool trends
4. **Startup Activity**: New companies, funding activity, growth metrics
5. **Community Pulse**: Upcoming events, developer engagement, learning trends

## 🎯 Business Value

- **For Recruiters**: Real-time talent market intelligence
- **For Job Seekers**: Salary benchmarking and skill guidance  
- **For Companies**: Market positioning and competitive analysis
- **For Investors**: Startup ecosystem monitoring
- **For Developers**: Career planning and skill development

---

*Demonstrating advanced full-stack development with AI agent orchestration 🚀*