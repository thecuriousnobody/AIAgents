# Personal Assistant Agent System

A sophisticated multi-agent system built with CrewAI for managing Rajeev's four project lanes through conversational AI.

## 🎯 Overview

This system uses 3 specialized CrewAI agents to process speech input and execute real-world actions:

1. **Personal Assistant (Gatekeeper)** - Conversational refinement and understanding
2. **Research & Classification Specialist** - Deep research and lane classification  
3. **Execution Agent** - Real-world actions (calendar, checklists, etc.)

## 📂 Project Lanes

The system manages four distinct project areas:

- **🎙️ Podcasting** - Content creation, episodes, publishing
- **🏢 Distillery Lab** - Accelerator and consulting work
- **🤖 Podcast Bots AI** - Startup development and growth
- **📝 Miscellaneous** - General collaborations and projects

## 🏗️ Architecture

### Agent Flow
```
Speech Input → Personal Assistant → Research & Classification → Execution → Actions
```

### Features
- ✅ **Real-time streaming responses**
- ✅ **Multi-agent coordination** 
- ✅ **Project lane classification**
- ✅ **Unique work ID generation**
- ✅ **Structured output with Pydantic models**
- ✅ **Session tracking and logging**
- 🔄 **Whisper integration** (planned)
- 🔄 **Calendar API integration** (planned)
- 🔄 **FastAPI streaming endpoints** (planned)

## 🚀 Quick Start

### 1. Installation
```bash
# Navigate to the personal assistant directory
cd personalAssistantAgent

# Install dependencies (if not already installed)
pip install crewai crewai-tools langchain-anthropic
```

### 2. Configuration
Make sure your `config.py` file has the required API keys:
```python
ANTHROPIC_API_KEY = "your-api-key"
SERPER_API_KEY = "your-serper-key"  # Optional for research
```

### 3. Run Tests
```bash
# Basic functionality test
python test_assistant.py

# Or run the main system directly
python personal_assistant_system.py
```

### 4. Streaming Interface
```bash
# Try the real-time streaming interface
python streaming_assistant.py
```

## 📁 File Structure

```
personalAssistantAgent/
├── personal_assistant_system.py    # Main 3-agent system
├── streaming_assistant.py          # Real-time streaming interface
├── assistant_config.py            # Configuration settings
├── test_assistant.py              # Test scripts and demos
├── README.md                       # This file
└── sessions/                       # Session logs (auto-created)
    └── session_*.txt
```

## 🔧 Usage Examples

### Basic Text Input
```python
from personal_assistant_system import PersonalAssistantWorkflow

workflow = PersonalAssistantWorkflow()
result = workflow.process_speech_input("I finished recording podcast episode 45")
```

### Streaming Interface
```python
from streaming_assistant import StreamingPersonalAssistant

assistant = StreamingPersonalAssistant()
async for message in assistant.process_speech_stream("Schedule a mentor call"):
    print(f"{message.agent}: {message.content}")
```

### Interactive Console
```bash
python test_assistant.py
# Choose option 3 for interactive streaming console
```

## 🧪 Test Cases

The system includes several test cases for different project lanes:

1. **Podcasting**: "I just finished recording episode 45 and need to schedule editing"
2. **Distillery Lab**: "Had a mentor session about AI architecture"
3. **Podcast Bots AI**: "Need to update the feature roadmap based on user feedback"
4. **Miscellaneous**: "Working on a personal blockchain learning project"

## 🔄 Development Roadmap

### Phase 1: Foundation ✅
- [x] Multi-agent CrewAI system
- [x] Project lane classification
- [x] Streaming responses
- [x] Pydantic data models
- [x] Session tracking

### Phase 2: Integration 🔄
- [ ] Whisper speech-to-text integration
- [ ] FastAPI streaming endpoints
- [ ] Frontend React component integration
- [ ] Real calendar API integration

### Phase 3: Advanced Features 📋
- [ ] User confirmation workflows
- [ ] Tool integration framework
- [ ] Learning from user corrections
- [ ] Advanced conversation memory

## 🛠️ Technical Details

### CrewAI Configuration
- **Version**: CrewAI 0.140.0
- **LLM**: Claude Sonnet (Anthropic)
- **Process**: Sequential with reasoning
- **Tools**: Serper search integration

### Data Models
```python
class WorkItem(BaseModel):
    work_id: str
    lane: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    actions_needed: List[str]
    calendar_events: List[str]
```

### Streaming Implementation
- Real-time message streaming using async generators
- FastAPI-compatible Server-Sent Events
- Background processing with thread safety
- Structured message types for different agent states

## 🎯 Next Steps

1. **Test the current system** with various inputs
2. **Add Whisper integration** for real speech-to-text
3. **Build FastAPI endpoints** for frontend integration
4. **Create React components** for the voice interface
5. **Add real tool integrations** (Calendar, Notion, etc.)

## 📝 Notes

This is a **prototyping exercise** - we're discovering and building together! The system is designed to be:

- **Modular** - Easy to add new agents and tools
- **Extensible** - Ready for additional integrations
- **User-centric** - Focused on conversational refinement
- **Action-oriented** - Designed to execute real tasks

Feel free to experiment with different inputs and watch how the 3-agent system processes and refines your requests!

## 🔗 Integration Points

### Frontend Integration (Planned)
```typescript
// React component for voice interface
const response = await fetch('/api/assistant/stream', {
  method: 'POST',
  body: JSON.stringify({ speech: transcript })
});

// Handle streaming responses
const reader = response.body.getReader();
// ... process streaming messages
```

### API Endpoints (Planned)
```python
# FastAPI streaming endpoint
@app.post("/api/assistant/stream")
async def stream_assistant_response(request: AssistantRequest):
    return StreamingResponse(assistant.stream_response(request.speech))
```

Ready to start prototyping! 🚀
