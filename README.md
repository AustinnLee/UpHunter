# 🏹 UpHunter API - Intelligent Job Aggregator

## 📖 Overview
UpHunter is a production-grade API service that aggregates, cleans, and analyzes job data from Upwork.
It features **AI-powered recommendations (RAG)** and **real-time scraping capabilities**.

**Live Demo**: [https://uphunter-z1ez.onrender.com/docs](https://uphunter-z1ez.onrender.com/docs)

---

## ✨ Key Features
*   **🔎 Real-time Scraping**: Fetches latest jobs with stealth browser technology (bypassing Cloudflare).
*   **🤖 AI Analyst**: Integrated with LLM to provide personalized job recommendations.
*   **🔒 Security**: API Key authentication protected.
*   **📊 Data Warehouse**: PostgreSQL storage with automatic deduplication.

---

## 🚀 Quick Start

### 1. Installation
Ensure you have **Python 3.10+** and **uv** installed.

```bash
# Install dependencies
uv sync
```
### 2. Configuration
```ini
DB_USER=postgres
DB_PASSWORD=your_password
AI_API_KEY=sk-xxxx (SiliconFlow/OpenAI)
API_SECRET_KEY=my-secret-key
```
### 3. Run the Server
```bash
uv run uvicorn src.api.main:app --reload
```
The API will be available at `http://localhost:8000`
## 📚 API Documentation

| Method | Endpoint  |                 Description                  |
|:------:|:---------:|:--------------------------------------------:|
| `GET`  |  `/jobs`  |List all jobs (supports filtering by keyword) | 
| `POST` | `/crawl`  |      Trigger a background scraping task      |
| `POST` | `/chat`	  |     Ask AI for job advice (RAG enabled)      |
## 🛠️ Tech Stack
*   **Backend:** FastAPI, SQLAlchemy, Pydantic
*   **Database:** PostgreSQL, LanceDB (Vector)
*   **AI:** OpenAI SDK (SiliconFlow), Sentence-Transformers
*   **Scraping:** Selenium, Undetected-Chromedriver
## 📞 Support
For any issues, please contact: [Your Name]