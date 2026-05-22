# 🚀 RAG GenAI Platform using FastAPI, React, AWS & DevOps

A production-ready Retrieval-Augmented Generation (RAG) based Generative AI platform built using FastAPI, React, Docker, Kubernetes (EKS), Jenkins CI/CD, and AWS Cloud Services.

This project allows users to upload PDF documents, generate embeddings from document chunks, store vectors in a vector database, retrieve relevant chunks using semantic similarity search, and generate context-aware AI responses using Large Language Models (LLMs).

---

# 📌 Features

- ✅ PDF Upload & Processing
- ✅ Document Chunking
- ✅ Embedding Generation
- ✅ Semantic Search
- ✅ Vector Database Integration
- ✅ AI-Powered Question Answering
- ✅ FastAPI Backend
- ✅ React Frontend
- ✅ JWT Authentication
- ✅ Dockerized Architecture
- ✅ Kubernetes Deployment (EKS)
- ✅ Jenkins CI/CD Automation
- ✅ AWS Cloud Deployment
- ✅ Ansible Automation
- ✅ Monitoring with Prometheus & Grafana
- ✅ Secure Secret Management

---

# 🧠 What is RAG?

RAG (Retrieval-Augmented Generation) combines:

## 1️⃣ Retrieval
Relevant document chunks are retrieved using vector similarity search.

## 2️⃣ Generation
Retrieved context is sent to an LLM to generate accurate and context-aware responses.

This approach reduces hallucination and improves answer accuracy.

---

# 🏗️ System Architecture

```text
User
  ↓
React Frontend
  ↓
FastAPI Backend
  ↓
PDF Processing
  ↓
Text Chunking
  ↓
Embedding Generation
  ↓
Vector Database
  ↓
Semantic Search
  ↓
LLM (GPT / Bedrock / Llama)
  ↓
AI Generated Response
```

---

# ☁️ AWS Production Architecture

```text
Users
  ↓
Route53
  ↓
Application Load Balancer
  ↓
Amazon EKS Cluster
  ├── React Frontend Pods
  ├── FastAPI Backend Pods
  ├── PostgreSQL / pgvector
  ├── Prometheus
  └── Grafana
        ↓
Amazon S3
        ↓
OpenAI API / Amazon Bedrock
```

---

# 🛠️ Tech Stack

## Frontend
- React
- Vite
- Axios
- Tailwind CSS

## Backend
- FastAPI
- Python
- LangChain
- Sentence Transformers
- JWT Authentication

## AI / GenAI
- RAG Architecture
- Embeddings
- Semantic Search
- Prompt Engineering
- LLM Integration

## Vector Database
- FAISS
- PostgreSQL + pgvector

## DevOps
- Docker
- Kubernetes
- Jenkins
- Ansible
- GitHub Actions

## AWS Services
- EC2
- EKS
- ECR
- S3
- IAM
- VPC
- Route53
- ALB
- CloudWatch
- Secrets Manager

---

# 📂 Project Structure

```text
rag-genai-platform/
│
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── kubernetes/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   └── services/
│
├── ansible/
│   ├── inventory.ini
│   ├── deploy.yaml
│   └── roles/
│
├── jenkins/
│   └── Jenkinsfile
│
├── docker-compose.yml
└── README.md
```

---

# ⚙️ Local Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/rag-genai-platform.git

cd rag-genai-platform
```

---

## 2️⃣ Setup Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

---

## 3️⃣ Setup Frontend

```bash
cd frontend

npm install
```

Run frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

---

# 🐳 Docker Setup

## Build Backend Image

```bash
cd backend

docker build -t rag-backend .
```

---

## Build Frontend Image

```bash
cd frontend

docker build -t rag-frontend .
```

---

## Run using Docker Compose

```bash
docker-compose up --build
```

---

# ☸️ Kubernetes Deployment

## Create EKS Cluster

```bash
eksctl create cluster \
--name rag-genai-cluster \
--region ap-south-1 \
--nodegroup-name workers \
--node-type t3.medium \
--nodes 2
```

---

## Configure kubectl

```bash
aws eks update-kubeconfig \
--region ap-south-1 \
--name rag-genai-cluster
```

---

## Deploy Application

```bash
kubectl apply -f kubernetes/
```

Check pods:

```bash
kubectl get pods
```

---

# 🚀 CI/CD Pipeline using Jenkins

## Pipeline Flow

```text
GitHub Push
    ↓
Jenkins Trigger
    ↓
Build Docker Images
    ↓
Push Images to Amazon ECR
    ↓
Deploy to Amazon EKS
```

---

## Jenkinsfile Example

```groovy
pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo.git'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t rag-backend .'
            }
        }

        stage('Push to ECR') {
            steps {
                sh 'docker push IMAGE_URL'
            }
        }

        stage('Deploy') {
            steps {
                sh 'kubectl apply -f kubernetes/'
            }
        }
    }
}
```

---

# 📄 RAG Workflow

## Step 1 — Upload PDF

User uploads a document through frontend.

---

## Step 2 — Extract Text

Backend extracts text from uploaded PDFs.

---

## Step 3 — Chunking

Large document split into smaller chunks.

---

## Step 4 — Generate Embeddings

Embeddings generated using transformer models.

---

## Step 5 — Store Vectors

Vectors stored in vector database.

---

## Step 6 — User Query

User asks a question.

---

## Step 7 — Semantic Search

Relevant chunks retrieved using similarity search.

---

## Step 8 — Prompt Engineering

Retrieved chunks added into LLM prompt context.

---

## Step 9 — AI Response

LLM generates intelligent answer.

---

# 🔐 Security Features

- JWT Authentication
- Secure API Endpoints
- AWS Secrets Manager
- IAM Roles
- Kubernetes Secrets
- Environment Variables

---

# 📊 Monitoring

## Prometheus
- Metrics collection

## Grafana
- Dashboard visualization

## CloudWatch
- AWS logs and monitoring

---

# 👨‍💻 Author

Vishal Pande

---
