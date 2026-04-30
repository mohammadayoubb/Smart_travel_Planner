# Smart Travel Planner – AI Agent System

## Overview

This project is an AI-powered travel recommendation system that helps users find destinations based on their preferences such as budget, culture, food, weather, and activities.

The system uses a *multi-step agent pipeline* combining:
- Retrieval-Augmented Generation (RAG)
- Machine Learning classification
- External API integration
- Two Large Language Models (LLMs)

## Technologies Used

### Backend
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL + pgvector
- JWT Authentication
- Docker

### AI / ML
- OpenAI API
  - `gpt-4o-mini` (cheap model)
  - `gpt-4o` (final reasoning model)
  - `text-embedding-3-small` (RAG embeddings)
- Scikit-learn (ML classifier)

### Frontend
- React (Vite)
- Axios

## Features

### 1. RAG (Retrieval-Augmented Generation)
- Travel documents stored in PostgreSQL with pgvector
- Semantic similarity search retrieves relevant destinations

### 2. Machine Learning Classifier
- Predicts travel style (Budget, Luxury, Adventure, etc.)
- Uses engineered features (budget, weather, activities)

### 3. Multi-Tool AI Agent
The agent orchestrates:
- Query rewriting (LLM)
- RAG search
- ML classification
- Weather lookup
- Final reasoning (LLM)

### 4. Two-Model LLM Setup
- Cheap model → preprocessing (query rewrite)
- Strong model → final answer generation

### 5. Tool Logging (Agent Tracing)
All tool calls are logged in the database:

Each entry contains:
- tool name
- input
- output
- status
- timestamps

### 6. Authentication
- JWT-based authentication
- Users must login to use the agent

### 7. Docker Deployment
- Backend, frontend, and database fully containerized
- System runs using docker-compose

## Agent Workflow

Example request:
Pipeline:

1. Query rewritten by LLM
2. RAG retrieves relevant destinations
3. ML model predicts travel style
4. Weather API fetches conditions
5. Final LLM generates human-readable answer

## Testing

Basic validation tests implemented using pytest:

- Input validation for agent requests
- ML feature validation



