# Edu Multi-Agent Service

A multi-agent education system based on **LangGraph**, providing personalized intelligent tutoring services through the collaboration of multiple specialized AI Agents.

## Core Features

- **Multi-Agent Collaborative Architecture**: 8 specialized agents work together to accomplish teaching tasks
- **Intelligent Intent Recognition**: Automatically analyze student needs and route to the most suitable teaching node
- **RAG-Enhanced Generation**: Integrated vector database ensures knowledge explanation is based on authoritative textbooks
- **Personalized Learning**: Student profiles, error books, and knowledge mastery tracking
- **Quality Assurance Mechanism**: Critic Agent reviews content to ensure output quality
- **Dual-Layer Memory System**:
  - Short-term Memory: PostgreSQL Checkpointer automatically saves conversation history
  - Long-term Memory: DashVector vector database stores user profiles and learning records
- **Asynchronous Persistence**: Uses FastAPI BackgroundTasks for async data writing, improving response speed
- **General Chitchat Mode**: Support natural conversation for non-learning scenarios, direct output without review
- **Web Search**: Integrated Alibaba Cloud Bailian MCP WebSearch for real-time information queries

## System Architecture

```
User Input
    ↓
┌─────────────┐
│  Planner    │  ← Teaching Director: Analyze intent, determine routing
└─────────────┘
    ↓ (Intent Routing)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
↓         ↓         ↓         ↓         ↓                      │
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐              │
│Learner│ │Quiz- │ │Score │ │Explain│ │ Chitchat │              │
│(Tutor)│ │zler  │ │r     │ │er    │ │ (Chat)   │              │
│      │ │(Exam │ │(Judge)│ │(Tutor)│ │ +WebSearch│             │
│      │ │Maker)│ │      │ │      │ │          │              │
└──────┘ └──────┘ └──────┘ └──────┘ └──────────┘              │
│    ↓ (Teaching nodes go through review)   ↓ (Direct output)   │
└──────────────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│   Critic    │  ← Teaching Director: Quality review (can reject and redo)
└─────────────┘
    ↓
┌─────────────┐
│ Summarizer  │  ← Summarizer: Generate final response
└─────────────┘
    ↓ (Sync response return)
    ↓ (Async background persistence)
┌─────────────────────────────────────────────────────────────┐
│  BackgroundTasks → PostgreSQL + DashVector (Async persistence)│
└─────────────────────────────────────────────────────────────┘
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
| **Summarizer** | Summarizer | Integrate review results, generate final response | None |
| **Chitchat** | Chat Partner | General conversation with web search support | `web_search` (Alibaba Cloud Bailian MCP) |

## Memory System

### Short-term Memory (PostgreSQL Checkpointer)
- Uses LangGraph's `AsyncPostgresSaver` to automatically save conversation history
- Automatically restores context based on `thread_id` (i.e., `session_id`)
- Supports multi-turn conversation coherence

### Long-term Memory (DashVector)
- User profiles: learning preferences, knowledge level
- Learning records: learned knowledge points, error records
- Chitchat memories: user personal information (name, interests, etc.)

### Memory Saving Process
```
Conversation End
    ↓
Async Persistence Service (BackgroundTasks)
    ↓
┌─────────────────────────────────────────┐
│ 1. Noise Filtering: Intercept worthless │
│ 2. LLM Extraction: Extract factual      │
│ 3. Vectorization: text-embedding-v3     │
│    (1024 dimensions)                    │
│ 4. Storage: DashVector vector database  │
└─────────────────────────────────────────┘
```

## Web Search

Integrated Alibaba Cloud Bailian MCP WebSearch service for real-time information queries:

- **Weather**: What's the weather like in Shanghai today?
- **News**: Latest technology news
- **Real-time Info**: Stock prices, match results, etc.

### Configuration

Add to `.env`:
```env
DASHSCOPE_API_KEY=your-dashscope-api-key
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI + Uvicorn |
| AI Framework | LangChain + LangGraph |
| Large Language Model | OpenAI-compatible API |
| Vector Database | DashVector (Alibaba Cloud) |
| Relational Database | PostgreSQL (Alibaba Cloud RDS) |
| Short-term Memory | PostgreSQL Checkpointer |
| Web Search | Alibaba Cloud Bailian MCP WebSearch |
| Embedding | text-embedding-v3 (1024 dimensions) |
| ORM | SQLAlchemy 2.0 |
| Frontend | Streamlit |

## Project Structure

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # User authentication API
│   │       └── chat.py          # Chat API
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
│   │   │   ├── critic.py        # Quality review
│   │   │   ├── summarizer.py    # Final response generation
│   │   │   └── chitchat.py      # General chat + Web search
│   │   ├── async_persistence.py # Async persistence service
│   │   ├── graph.py             # LangGraph workflow definition
│   │   └── state.py             # State definition
│   ├── tools/
│   │   ├── database.py          # Database tools
│   │   ├── rag.py               # RAG tools
│   │   ├── rag_search.py        # RAG search tools
│   │   └── web_search.py        # Web search tool (MCP)
│   └── main.py                  # Application entry point
├── frontend/
│   ├── pages/                   # Streamlit pages
│   ├── utils/                   # Utility functions
│   └── app.py                   # Frontend entry point
├── .env.example                 # Environment variables example
├── requirements.txt             # Dependencies list
└── README_EN.md                 # Project documentation (English)
```

## Quick Start

### 1. Environment Preparation

Ensure Python 3.9+ is installed and prepare the following services:
- PostgreSQL database
- DashVector vector database (Alibaba Cloud)
- OpenAI-compatible LLM API
- Alibaba Cloud Bailian API Key (for web search)

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
XIAOMI_API_KEY=your-llm-api-key
XIAOMI_BASE_URL=https://api.openai.com/v1
XIAOMI_MODEL=gpt-4-turbo

# RAG API Configuration
RAG_API_BASE_URL=http://localhost:8000

# Database Configuration
POSTGRES_URL=postgresql://user:password@host:port/database

# Vector Database Configuration
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Alibaba Cloud Bailian MCP WebSearch
DASHSCOPE_API_KEY=your-dashscope-api-key
```

### 4. Initialize Database

```bash
python create_tables.py
```

### 5. Start the Service

```bash
# Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Start frontend (new terminal)
cd frontend
streamlit run app.py
```

### 6. Access the Service

- Backend API Documentation: http://localhost:8080/docs
- Frontend Interface: http://localhost:8501

## API Endpoints

### Chat Endpoint

**POST** `/api/v1/chat`

Request Body:
```json
{
  "message": "Please explain Newton's second law to me",
  "user_id": "user_123",
  "session_id": "sess_456"
}
```

Response: SSE streaming output

### Session Management

**GET** `/api/v1/sessions?user_id=user_123`

Get user's session list

## Workflow

1. **Intent Recognition**: Planner Agent analyzes user input, identifies intent (learn/quiz/score/explain/chitchat)
2. **Route Distribution**: Routes the request to the corresponding Agent based on intent
3. **Task Execution**:
   - Teaching intents (learn/quiz/score/explain) → Go through Critic review → Summarizer generates final response
   - Chitchat intent → Direct output without review, supports web search
4. **Quality Review**: Critic Agent reviews teaching content quality, can reject and redo (up to 2 times)
5. **Async Persistence**: After response is returned, BackgroundTasks asynchronously saves learning data to PostgreSQL and DashVector

## Contributing

Issues and Pull Requests are welcome!

## License

This project is licensed under the MIT License.
