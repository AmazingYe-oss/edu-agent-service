# Edu Multi-Agent Service

A multi-agent education system based on **LangGraph**, providing personalized intelligent tutoring services through the collaboration of multiple specialized AI Agents.

## Core Features

- **Multi-Agent Collaborative Architecture**: 7 specialized agents work together to accomplish teaching tasks
- **Intelligent Intent Recognition**: Automatically analyze student needs and route to the most suitable teaching node
- **RAG-Enhanced Generation**: Integrated vector database ensures knowledge explanation is based on authoritative textbooks
- **Personalized Learning**: Student profiles, error books, and knowledge mastery tracking
- **Quality Assurance Mechanism**: Critic Agent reviews content to ensure output quality
- **Long-term Memory System**: Three-tier storage architecture with Redis + PostgreSQL + DashVector
- **Asynchronous Persistence**: Uses FastAPI BackgroundTasks for async data writing, improving response speed

## System Architecture

```
User Input
    ↓
┌─────────────┐
│  Planner    │  ← Teaching Director: Analyze intent, determine routing
└─────────────┘
    ↓ (Intent Routing)
┌─────────────────────────────────────────────────────┐
│                                                     │
↓         ↓         ↓         ↓                       │
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                  │
│Learner│ │Quiz- │ │Score │ │Explain│                 │
│(Tutor) │ │zler  │ │r     │ │er    │                  │
│      │ │(Exam │ │(Judge) │ │(Tutor) │                │
│      │ │Maker) │ │      │ │      │                  │
└──────┘ └──────┘ └──────┘ └──────┘                  │
│                                                     │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│   Critic    │  ← Teaching Director: Quality review (can reject and redo)
└─────────────┘
    ↓ (Sync response return)
    ↓ (Async background persistence)
┌─────────────────────────────────────┐
│  BackgroundTasks → PostgreSQL +     │
│  DashVector (Async data persistence)│
└─────────────────────────────────────┘
```

## Agent Roles

| Agent | Role | Responsibilities | Tools Used |
|-------|------|------------------|------------|
| **Planner** | Teaching Director | Analyze user intent, determine routing strategy | `get_user_profile_tool`, `search_user_memory_tool` |
| **Learner** | Gold Tutor | Explain knowledge points, provide learning guidance | `search_knowledge_base` |
| **Quizzler** | Exam Maker | Generate intelligent questions based on student weaknesses | `check_error_book_tool` |
| **Scorer** | Judge | Grade assignments, determine correctness | `search_knowledge_base` |
| **Explainer** | Senior Tutor | In-depth analysis of wrong answers, provide problem-solving approaches | `search_knowledge_base`, `check_error_book_tool` |
| **Critic** | Teaching Director | Review content quality, can reject and redo | Structured output |

## Tech Stack

- **Web Framework**: FastAPI + Uvicorn
- **AI Framework**: LangChain + LangGraph
- **Large Language Model**: OpenAI-compatible API (can switch to domestic models)
- **Vector Database**: DashVector (Alibaba Cloud)
- **Relational Database**: PostgreSQL (Alibaba Cloud RDS)
- **Cache/State Storage**: Redis (Alibaba Cloud)
- **ORM**: SQLAlchemy 2.0

## Project Structure

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── chat.py          # API route definitions
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection
│   │   ├── dashclient.py        # DashVector client
│   │   └── llm.py               # LLM initialization
│   ├── models/
│   │   ├── domain.py            # Database models
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── nodes/
│   │   │   ├── planner.py       # Intent recognition and routing
│   │   │   ├── learner.py       # Knowledge explanation
│   │   │   ├── quizzler.py      # Intelligent question generation
│   │   │   ├── scorer.py        # Automatic grading
│   │   │   ├── explainer.py     # Error analysis
│   │   │   └── critic.py        # Quality review
│   │   ├── async_persistence.py # Async persistence service
│   │   ├── graph.py             # LangGraph workflow definition
│   │   └── state.py             # State definition
│   ├── tools/
│   │   ├── database.py          # Database tools
│   │   ├── rag.py               # RAG tools
│   │   └── rag_search.py        # RAG search tools
│   └── main.py                  # Application entry point
├── .env.example                 # Environment variables example
├── requirements.txt             # Dependencies list
└── README_EN.md                 # Project documentation (English)
```

## Quick Start

### 1. Environment Preparation

Ensure Python 3.9+ is installed and prepare the following services:
- PostgreSQL database
- Redis service
- DashVector vector database (Alibaba Cloud)
- OpenAI-compatible LLM API

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the environment variables example file and fill in the actual configuration:

```bash
cp .env.example .env
```

Edit the `.env` file with the following configurations:

```env
# LLM Configuration
OPENAI_API_KEY="your-llm-api-key"
OPENAI_API_BASE="https://api.openai.com/v1"
LLM_MODEL_NAME="gpt-4-turbo"

# RAG API Configuration
RAG_API_BASE_URL="http://localhost:8000"

# Database Configuration
POSTGRES_URL="postgresql://user:password@host:port/database"
REDIS_URL="redis://:password@host:port/db"

# Vector Database Configuration
DASHVECTOR_API_KEY="your-api-key"
DASHVECTOR_ENDPOINT="your-endpoint"
```

### 4. Start the Service

```bash
# Development mode (auto-reload)
python -m app.main

# Or using uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 5. Access API Documentation

After startup, visit: http://localhost:8080/docs

## API Endpoints

### Chat Endpoint

**POST** `/api/v1/chat`

Request Body:
```json
{
  "message": "Please explain Newton's second law to me",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "Newton's second law states that...",
  "intent": "learn",
  "agent_used": "learner_node"
}
```

## Workflow

1. **Intent Recognition**: Planner Agent analyzes user input, identifies intent (learn/quiz/score/explain)
2. **Route Distribution**: Routes the request to the corresponding Agent based on intent
3. **Task Execution**: Target Agent executes the specific task, may call RAG or database tools
4. **Quality Review**: Critic Agent reviews output quality, can reject and redo (up to 2 times)
5. **Async Persistence**: After response is returned, BackgroundTasks asynchronously saves learning data to PostgreSQL and DashVector

## Data Models

### User Profile (UserProfile)
- `user_id`: Unique user identifier
- `knowledge_state`: JSONB format knowledge mastery
- `learning_style`: Learning style

### Error Book (ErrorBook)
- `user_id`: User ID
- `knowledge_point`: Knowledge point
- `question_content`: Question content
- `user_answer`: User's answer
- `ai_analysis`: AI analysis

## Configuration

All configurations are managed through environment variables. See `app/core/config.py` for details:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | LLM API key | `sk-xxx` |
| `OPENAI_API_BASE` | LLM API endpoint | `https://api.openai.com/v1` |
| `LLM_MODEL_NAME` | Model name | `gpt-4-turbo` |
| `RAG_API_BASE_URL` | RAG service URL | `http://localhost:8000` |
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://...` |
| `REDIS_URL` | Redis connection string | `redis://...` |
| `DASHVECTOR_API_KEY` | DashVector API key | - |
| `DASHVECTOR_ENDPOINT` | DashVector endpoint | - |

## Contributing

Issues and Pull Requests are welcome!

## License

This project is licensed under the MIT License.
