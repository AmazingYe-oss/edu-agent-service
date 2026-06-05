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
│  Planner    │ → Teaching Director: Analyze intent, determine routing
└─────────────┘
    ↓ (Intent Routing)
┌─────────────────────────────────────────────────────────────────┐
│                                                             │
↓        ↓        ↓        ↓        ↓                     │
┌──────┐┌──────┐┌──────┐┌──────┐┌──────────────┐             │
│Learner││Quiz- ││Score ││Explain││  Chitchat    │             │
│(Tutor)││ler   ││r     ││er    ││ (Chat)       │             │
│     ││(Exam  ││(Judge)││(Tutor)││ +WebSearch   │             │
│     ││Maker) ││     ││     ││              │             │
└──────┘└──────┘└──────┘└──────┘└──────────────┘             │
│   ↓ (Teaching nodes go through review)   ↓ (Direct output)   │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────┐
│  Critic     │ → Teaching Director: Quality review (can reject and redo)
└─────────────┘
    ↓
┌─────────────┐
│Summarizer   │ → Summarizer: Generate final response
└─────────────┘
    ↓ (Sync response return)
    ↓ (Async background persistence)
┌─────────────────────────────────────────────────────────────────┐
│ BackgroundTasks → PostgreSQL + DashVector (Async persistence)│
└─────────────────────────────────────────────────────────────────┘
```

## Agent Roles

| Agent | Role | Responsibilities | Tools Used |
|-------|------|------------------|------------|
| Planner | Teaching Director | Intent recognition, task routing | None |
| Learner | Private Tutor | Knowledge explanation, concept teaching | RAG search, database |
| Quizzler | Exam Maker | Intelligent question generation | RAG search, database |
| Scorer | Judge | Automatic grading, score feedback | Database |
| Explainer | Tutor | Error analysis, knowledge consolidation | RAG search, database |
| Critic | Teaching Director | Content quality review | None |
| Summarizer | Assistant | Generate final teaching response | None |
| Chitchat | Chat Assistant | General conversation, web search | Web search (MCP) |

## Project Structure

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── chat.py                  # Chat API
│   ├── core/
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # Database connection
│   │   ├── dashclient.py            # DashVector client
│   │   └── llm.py                   # LLM initialization
│   ├── models/
│   │   ├── domain.py                # Database models
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   ├── nodes/
│   │   │   ├── planner.py           # Intent recognition and routing
│   │   │   ├── learner.py           # Knowledge explanation
│   │   │   ├── quizzler.py          # Intelligent question generation
│   │   │   ├── scorer.py            # Automatic grading
│   │   │   ├── explainer.py         # Error analysis
│   │   │   ├── critic.py            # Quality review
│   │   │   ├── summarizer.py        # Final response generation
│   │   │   └── chitchat.py          # General chat + Web search
│   │   ├── async_persistence.py     # Async persistence service
│   │   ├── graph.py                 # LangGraph workflow definition
│   │   └── state.py                 # State definition
│   ├── tools/
│   │   ├── database.py              # Database tools
│   │   ├── rag.py                   # RAG tools
│   │   ├── rag_search.py            # RAG search tools
│   │   └── web_search.py            # Web search tool (MCP)
│   └── main.py                      # Application entry point
├── frontend/
│   ├── pages/                       # Streamlit pages
│   ├── utils/                       # Utility functions
│   └── app.py                       # Frontend entry point
├── .github/workflows/
│   └── main.yml                     # CI/CD pipeline
├── .env.example                     # Environment variables example
├── Dockerfile                       # Docker image build
├── requirements.txt                 # Dependencies list
└── README_EN.md                     # Project documentation (English)
```

---

## Prerequisites

### Local Development

| Dependency | Version | Description |
|------------|---------|-------------|
| Python | 3.9+ | Runtime environment |
| PostgreSQL | 12+ | Conversation history, user data storage |
| DashVector | - | Alibaba Cloud vector database (RAG retrieval) |
| OpenAI-compatible LLM | - | GPT-4 or other compatible API |
| Alibaba Cloud Bailian API | - | Web search capability (optional) |

### CI/CD and Deployment

| Dependency | Description |
|------------|-------------|
| GitHub Repository | Code hosting and CI/CD trigger |
| Alibaba Cloud ACR | Image storage |
| Kubernetes Cluster | Application runtime |
| ArgoCD | GitOps continuous deployment |
| GitOps Config Repo | [edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops) |

---

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# LLM Configuration
OPENAI_API_KEY=your-llm-api-key
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4-turbo

# RAG API Configuration
RAG_API_BASE_URL=http://localhost:8000

# Database Configuration
POSTGRES_URL=postgresql://user:password@host:port/database

# Redis Configuration
REDIS_URL=redis://:password@host:port/0

# Vector Database Configuration
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint

# Alibaba Cloud Bailian MCP WebSearch
DASHSCOPE_API_KEY=your-dashscope-api-key
```

### 3. Initialize Database

```bash
python create_tables.py
```

### 4. Start the Service

```bash
# Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Start frontend (new terminal)
cd frontend
streamlit run app.py
```

### 5. Access the Service

- Backend API Documentation: http://localhost:8080/docs
- Frontend Interface: http://localhost:8501

---

## Deployment

This project uses **GitHub Actions + Alibaba Cloud ACR + ArgoCD GitOps** automated deployment pipeline.

### Overall Flow

```
Code Push (main)
    ↓
GitHub Actions Triggered
    ↓
Build Docker Image
    ↓
Push to Alibaba Cloud ACR
    ↓
Update GitOps Repo Image Tag
    ↓
ArgoCD Detects Changes
    ↓
Auto-sync to Kubernetes Cluster
```

### Detailed Deployment Steps

#### Step 1: Install ArgoCD (if not already installed)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for ArgoCD to be ready:

```bash
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
```

#### Step 2: Configure GitHub Secrets

In the repository's **Settings → Secrets and variables → Actions → Repository secrets**, add:

| Secret Name | Description |
|-------------|-------------|
| `ACR_USERNAME` | Alibaba Cloud ACR login username |
| `ACR_PASSWORD` | Alibaba Cloud ACR login password |
| `GITOPS_TOKEN` | GitHub PAT (requires `repo` permission for cross-repo push) |

> ACR_REGISTRY, ACR_NAMESPACE, ACR_REPO are hardcoded in the workflow file, no additional configuration needed.

#### Step 3: Push Code to Trigger CI

```bash
git add .
git commit -m "your commit message"
git push origin main
```

GitHub Actions will automatically:
1. Checkout code
2. Build Docker image
3. Login to Alibaba Cloud ACR
4. Push image (Tag: 8-char commit SHA + branch name)
5. Update GitOps repo `kustomization.yaml` image tag

#### Step 4: Deploy ArgoCD Application

Apply ArgoCD configuration in Kubernetes cluster:

```bash
kubectl apply -f https://raw.githubusercontent.com/AmazingYe-oss/edu-agent-service-gitops/main/argocd/application.yaml
```

Or via ArgoCD CLI:

```bash
argocd app create edu-agent-service \
  --repo https://github.com/AmazingYe-oss/edu-agent-service-gitops.git \
  --path base \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace edu-agent-service-dev \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

ArgoCD will automatically:
- Monitor the GitOps repo's `base/` directory
- Auto-sync when image tag changes
- Create namespace `edu-agent-service-dev`
- Deploy Deployment, Service, Ingress and other resources

#### Step 5: Verify Deployment

```bash
# Check Pod status
kubectl get pods -n edu-agent-service-dev

# Check Service
kubectl get svc -n edu-agent-service-dev

# Check Ingress
kubectl get ingress -n edu-agent-service-dev

# Check ArgoCD sync status
argocd app get edu-agent-service
```

#### Step 6: Access the Service

After deployment, access the service via Ingress domain or port forwarding:

```bash
# Port forward (for development/debugging)
kubectl port-forward svc/edu-agent-service 8080:80 -n edu-agent-service-dev

# Check Ingress address
kubectl get ingress -n edu-agent-service-dev
```

---

## CI/CD Configuration

### GitHub Actions Workflow

File location: `.github/workflows/main.yml`

**Triggers:**
- Push to `main`, `master`, `release/*` branches
- Manual trigger (workflow_dispatch)

**Image Tag Strategy:**
- `<8-char commit SHA>`: Unique identifier per build
- `<branch name>`: Branch-level identifier
- `latest`: Only for main/master branches

**Image Address Format:**
```
crpi-he7mqvhihpnvi08o.cn-shanghai.personal.cr.aliyuncs.com/edu-agent-project/edu-agent-service:<tag>
```

### GitOps Configuration Repo

Config repo: [edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops)

CI pipeline automatically updates the image tag in `base/kustomization.yaml`. ArgoCD detects changes and auto-syncs to the cluster.

### GitOps Config Repo Structure

```
edu-agent-service-gitops/
├── argocd/
│   └── application.yaml        # ArgoCD Application manifest
└── base/
    ├── development.yaml        # Deployment + Service
    ├── ingress.yaml            # Ingress configuration
    └── kustomization.yaml      # Kustomize main config (image tag auto-updated by CI)
```

For more details, see: [edu-agent-service-gitops README](https://github.com/AmazingYe-oss/edu-agent-service-gitops)

---

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

---

## Contributing

Issues and Pull Requests are welcome!

## License

This project is licensed under the MIT License.
