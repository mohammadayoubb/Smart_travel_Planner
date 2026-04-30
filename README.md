# Smart Travel Planner – AI Agent System

## Overview

This project is an AI-powered travel recommendation system that helps users find destinations based on their preferences such as budget, culture, food, weather, and activities.

Instead of searching across multiple platforms, the system provides a *complete, structured recommendation in one step*.

The system is built as a *multi-step AI agent pipeline* combining:
- Retrieval-Augmented Generation (RAG)
- Machine Learning classification
- External API integration
- Multiple Large Language Models (LLMs)


## System Architecture

The system follows an end-to-end pipeline:

User Input → Processing → Data Retrieval → Decision Making → Final Recommendation

- The user provides a travel request
- The system processes and enriches the request
- Multiple components contribute to the final output
- A complete recommendation is generated


## Technologies Used

### Backend
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL + pgvector
- JWT Authentication
- Docker

### AI / ML
- OpenAI API
  - `gpt-4o-mini` → query processing (cheap model)
  - `gpt-4o` → final response (strong model)
  - `text-embedding-3-small` → RAG embeddings
- Scikit-learn (ML classifier)

### Frontend
- React (Vite)
- Axios


## Features

### 1. RAG (Retrieval-Augmented Generation)
- Travel documents stored in PostgreSQL using pgvector
- Semantic similarity search retrieves relevant destinations
- Improves factual accuracy and reduces hallucination


### 2. Machine Learning Classifier
- Predicts travel style:
  - Adventure
  - Budget
  - Culture
  - Luxury
- Uses engineered features such as:
  - budget indicators
  - keywords (hiking, beaches, museums)
  - travel intent


### 3. Multi-Tool AI Agent

The agent orchestrates multiple steps:

1. Query rewriting (LLM)
2. RAG retrieval
3. ML classification
4. Weather API call
5. Final response generation (LLM)


### 4. Two-Model LLM Strategy

| Model          | Role                | Reason                     |
|----------------|---------------------|----------------------------|
| gpt-4o-mini    | Query processing     | Fast and low cost          |
| gpt-4o         | Final recommendation | Higher reasoning quality   |

This approach reduces cost while maintaining high-quality output.


### 5. Tool Logging (Agent Tracing)

All tool calls are stored in the database:

Each log contains:
- tool name
- input
- output
- status
- timestamps

This enables:
- debugging
- traceability
- system monitoring


### 6. Authentication
- JWT-based authentication
- Users must log in to interact with the system


### 7. Docker Deployment
- Backend, frontend, and database containerized
- System runs using:

