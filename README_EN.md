# Edu Multi-Agent Service — Multi-Agent Education Tutoring System

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi_Agent-000000?logo=langchain)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Conversation_History-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Session_Cache-dc382d?logo=redis)
![DashVector](https://img.shields.io/badge/DashVector-Vector_Retrieval-00c4b4)
![CI/CD](https://img.shields.io/badge/CI-GitHub_Actions-green?logo=github-actions)
![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange?logo=argo)

## Project Overview

This project is a **Multi-Agent intelligent tutoring system** designed for education scenarios, built on **LangGraph** to orchestrate multi-agent collaborative workflows. Through 8 specialized AI Agents working together, it provides personalized intelligent tutoring services for students.

The system adopts a **FastAPI** microservice backend + **Streamlit** interactive frontend, integrates **DashVector** for RAG-enhanced vector retrieval, uses **PostgreSQL** to persist conversation history and user profiles, **Redis** for session caching and rate limiting, and achieves cloud-native delivery through **Docker + Kubernetes + GitHub Actions + ArgoCD GitOps**.

> Core Positioning: Delegate knowledge explanation, quiz generation, grading, and error analysis to multiple specialized AI Agents working collaboratively, achieving truly personalized intelligent teaching.

---

## System Architecture

```mermaid
flowchart TD
    User["User Input"]
    Planner["Planner Agent<br/>Teaching Director: Intent & Routing"]
    Learner["Learner Agent<br/>Private Tutor: Knowledge"]
    Quizzler["Quizzler Agent<br/>Exam Maker: Quiz Generation"]
    Scorer["Scorer Agent<br/>Judge: Auto Grading"]
    Explainer["Explainer Agent<br/>Tutor: Error Analysis"]
    Chitchat["Chitchat Agent<br/>Chat + Web Search"]
    Critic["Critic Agent<br/>Director: Quality Review"]
    Summarizer["Summarizer Agent<br/>Final Response"]
    Response["Return to User"]
    Persist["Async Persistence"]
    DB["PostgreSQL + DashVector"]

    User --> Planner
    Planner -->|"Learn/Quiz/Score/Explain"| Learner
    Planner -->|"Quiz"| Quizzler
    Planner -->|"Grade"| Scorer
    Planner -->|"Error Analysis"| Explainer
    Planner -->|"Chitchat"| Chitchat
    Learner --> Critic
    Quizzler --> Critic
    Scorer --> Critic
    Explainer --> Critic
    Critic -->|"Approved"| Summarizer
    Critic -->|"Reject & Redo"| Learner
    Chitchat -->|"Direct Output"| Response
    Summarizer --> Response
    Summarizer -.->|"BackgroundTasks"| Persist
    Persist -.-> DB
```

### Core Data Flow

1. User enters a question in the Streamlit frontend
2. FastAPI backend receives the request, **Planner Agent** analyzes intent and routes to the corresponding Agent
3. Teaching requests (learn/quiz/score/explain) are processed by specialized Agents, then reviewed by **Critic Agent**
4. After approval, **Summarizer Agent** generates the final response, returned via **SSE streaming output**
5. Chitchat requests are output directly, supporting **Alibaba Cloud Bailian MCP Web Search**
6. After response is returned, **BackgroundTasks** asynchronously writes learning data to PostgreSQL and DashVector

### RESTful API Architecture

The system uses RESTful API design with modular routing:
- `app/api/chat.py` — Chat endpoint (SSE streaming)
- `app/services/nodes/` — Agent node implementations
- `app/services/graph.py` — LangGraph workflow definition
- `app/models/` — Pydantic request/response models

---

## Key Features

### Multi-Agent Collaborative Architecture
- **LangGraph** orchestration framework: Planner → Specialized Agents → Critic → Summarizer complete workflow
- **8 Specialized Agents**: Planner, Learner, Quizzler, Scorer, Explainer, Critic, Summarizer, Chitchat
- **Intelligent Intent Recognition**: Automatically analyze student needs and route to the most suitable teaching node
- **Quality Assurance**: Critic Agent reviews teaching content, can reject and redo (up to 2 times)

### RAG-Enhanced Retrieval
- **DashVector** vector database: Semantic retrieval based on Alibaba Cloud DashVector
- **DashScope Embedding** (text-embedding-v3): Converts knowledge snippets into vectors
- Ensures knowledge explanation is based on authoritative textbooks, not model hallucinations

### Dual-Layer Memory System
- **Short-term Memory**: PostgreSQL Checkpointer automatically saves conversation history
- **Long-term Memory**: DashVector vector database stores user profiles and learning records
- **Asynchronous Persistence**: FastAPI BackgroundTasks for async data writing without blocking responses

### SSE Streaming Output
- Character-by-character typewriter effect via `astream_events`
- Frontend renders in real-time via SSE for smooth experience

### General Chitchat + Web Search
- Natural conversation for non-learning scenarios, direct output without Critic review
- Integrated **Alibaba Cloud Bailian MCP WebSearch** for real-time information queries

---

## Project Structure

```
edu-agent-service/
├── app/
│   ├── api/
│   │   └── chat.py                  # Chat API (SSE streaming)
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
│   ├── components/                  # Page components
│   ├── pages/                       # Streamlit pages
│   ├── utils/
│   │   ├── auth.py                  # Authentication utilities
│   │   └── api.py                   # API call utilities
│   └── app.py                       # Frontend entry point
├── .github/workflows/
│   └── main.yml                     # CI/CD pipeline
├── Dockerfile                       # Docker image build
├── docker-compose.yml               # Local container orchestration
├── requirements.txt                 # Python dependency manifest
├── .env.example                     # Environment variable template
└── .env                             # Actual environment variables (not committed to Git)
```

> Kubernetes GitOps configurations (Deployment, Ingress, Service, etc.) are maintained in the separate repository [edu-agent-service-gitops](https://github.com/AmazingYe-oss/edu-agent-service-gitops).

---

## Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/AmazingYe-oss/edu-agent-service.git
cd edu-agent-service
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with actual configurations:

```env
# LLM Configuration
XIAOMI_API_KEY=your-llm-api-key
XIAOMI_BASE_URL=https://api.openai.com/v1
XIAOMI_MODEL=mimo-v2.5-pro

# RAG API Configuration
RAG_API_BASE_URL=http://localhost:8000

# PostgreSQL Configuration
POSTGRES_URL=postgresql://user:password@host:port/database

# Redis Configuration
REDIS_URL=redis://:password@host:port/0

# DashVector Configuration
DASHVECTOR_API_KEY=your-api-key
DASHVECTOR_ENDPOINT=your-endpoint

# Embedding Configuration
EMBEDDING_API_KEY=your-embedding-key
EMBEDDING_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Alibaba Cloud Bailian MCP Web Search
DASHSCOPE_API_KEY=your-dashscope-key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python create_tables.py
```

### 5. Start the Service

```bash
# Start backend (Terminal 1)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Start frontend (Terminal 2)
cd frontend
streamlit run app.py
```

### 6. Access the Service

- Frontend Interface: http://localhost:8501
- Backend API Documentation: http://localhost:8080/docs

---

## Docker Compose Local Deployment

```bash
# One-click start backend + frontend
docker compose up --build -d

# View logs
docker logs edu_backend
docker logs edu_frontend
```

Service URLs:
- Frontend: http://localhost:8501
- Backend: http://localhost:8080/docs

---

## Cloud Native Delivery Workflow

The project adopts a Dual-Repository GitOps architecture, completely decoupling the business source code from the Kubernetes configuration repository.

```mermaid
flowchart LR
    Dev["Developer Push Code"]
    CI["GitHub Actions"]
    Build["Docker Build"]
    ACR["Aliyun ACR"]
    GitOps["GitOps Config Repo"]
    ArgoCD["ArgoCD"]
    K8s["Kubernetes Cluster"]
    Pod["Agent Service Pods"]

    Dev --> CI
    CI --> Build
    Build --> ACR
    CI --> GitOps
    GitOps --> ArgoCD
    ArgoCD --> K8s
    K8s --> Pod
```

The delivery pipeline workflow:

1. Developers push code to the business repository (main branch).
2. GitHub Actions automatically triggers the CI pipeline.
3. CI executes Docker image build.
4. Image is pushed to Alibaba Cloud ACR (tagged with both latest and commit SHA).
5. CI automatically updates the Image Tag in the GitOps configuration repository.
6. ArgoCD continuously monitors the GitOps repository for changes.
7. ArgoCD synchronizes the desired state to the Kubernetes cluster.
8. Kubernetes performs a rolling update to complete the deployment.

### Detailed Deployment Steps

#### Step 0: Create a Kubernetes Cluster

**Option 1: Docker Desktop (Recommended for local development)**

1. Open Docker Desktop → **Settings** → **Kubernetes**
2. Check **Enable Kubernetes** → **Apply & Restart**
3. Verify:

```bash
kubectl cluster-info
kubectl get nodes
```

**Option 2: minikube**

```bash
minikube start
kubectl cluster-info
```

**Option 3: Cloud-managed cluster (Production)**

- Alibaba Cloud ACK: https://www.aliyun.com/product/kubernetes
- Tencent Cloud TKE: https://cloud.tencent.com/product/tke
- Huawei Cloud CCE: https://www.huaweicloud.com/product/cce.html

#### Step 1: Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
```

#### Step 2: Configure GitHub Secrets

In the repository's **Settings → Secrets and variables → Actions → Repository secrets**, add:

| Secret Name | Description |
|-------------|-------------|
| `ACR_USERNAME` | Alibaba Cloud ACR login username |
| `ACR_PASSWORD` | Alibaba Cloud ACR login password |
| `GITOPS_TOKEN` | GitHub PAT (requires `repo` permission for cross-repo push) |

#### Step 3: Push Code to Trigger CI

```bash
git add .
git commit -m "your commit message"
git push origin main
```

#### Step 4: Create K8s Secret and ConfigMap

```bash
# Create Secret from .env file
kubectl create secret generic edu-agent-service-secret \
  --from-env-file=.env \
  -n edu-agent-service-dev

# Create ACR image pull credentials
kubectl create secret docker-registry acr-credentials \
  --docker-server=crpi-he7mqvhihpnvi08o.cn-shanghai.personal.cr.aliyuncs.com \
  --docker-username=YOUR_ACR_USERNAME \
  --docker-password=YOUR_ACR_PASSWORD \
  -n edu-agent-service-dev
```

#### Step 5: Deploy ArgoCD Application

```bash
kubectl apply -f https://raw.githubusercontent.com/AmazingYe-oss/edu-agent-service-gitops/main/argocd/application.yaml
```

#### Step 6: Verify Deployment

```bash
kubectl get pods -n edu-agent-service-dev
kubectl get svc -n edu-agent-service-dev
kubectl get ingress -n edu-agent-service-dev
```

#### Step 7: Access the Service

```bash
kubectl port-forward svc/edu-agent-service 8080:80 -n edu-agent-service-dev
# Access http://localhost:8080/docs
```

---

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

---

## FAQ

**Q: Backend startup reports `DASHVECTOR_API_KEY` not configured?**
A: Ensure `.env` file or K8s Secret correctly configures `DASHVECTOR_API_KEY` and `DASHVECTOR_ENDPOINT`.

**Q: PostgreSQL connection fails?**
A: Check `POSTGRES_URL` format: `postgresql://username:password@host:port/database`.

**Q: Redis connection fails?**
A: Check `REDIS_URL` format. For local development, start a Redis container: `docker run -d -p 6379:6379 redis`.

**Q: Backend Pod status is `ErrImagePull`?**
A: You need to create ACR image pull credentials. See Step 4 in deployment.

**Q: Backend Pod status is `CreateContainerConfigError`?**
A: Usually the Secret name is not `edu-agent-service-secret` or required environment variables are missing. Use `kubectl describe pod` to view Events.

**Q: Critic Agent reports JSON parsing error?**
A: LLM returned JSON with invalid escape characters. The system has built-in fault tolerance and will automatically degrade to pass.

---

## Use Cases

- **Personalized intelligent tutoring** (Multi-agent collaboration covering learn, practice, test, and evaluate)
- **Intelligent quiz generation & auto-grading** (RAG-based precise question generation)
- **Error analysis & knowledge consolidation** (Targeted analysis of weak areas)
- **Web search-enhanced general Q&A** (Real-time information queries)
- **Cloud-native AI application engineering practice**
- **AI application CI/CD & GitOps delivery demonstration**

---

## Author

**Weiye Zhu (AmazingYe)**
- Class of 2027, Data Science and Big Data Technology
- AWS Certified Solutions Architect - Professional
- Alibaba Cloud Large Model ACP Certified
- Looking for internship opportunities in **Cloud Computing / Cloud Native / DevOps / SRE / AI Engineering**. Feel free to connect!
