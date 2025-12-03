🚀 LLM Observability Platform

A complete monitoring & analytics system for Large Language Models
built with FastAPI • Streamlit • PostgreSQL • Docker

🌟 Overview

The LLM Observability Platform provides real-time insights into the behavior and performance of LLMs.
It helps developers track prompts, responses, tokens, latency, errors, user sessions, model comparisons, and more — all through a beautiful and interactive dashboard.

This platform is perfect for developers who want visibility, debugging capabilities, and performance analytics for their LLM applications.

✨ Features
🔹 Real-Time LLM Monitoring

Track tokens in/out

Monitor latency per request

Capture model names, statuses & timestamps

Store every request in PostgreSQL

🔹 Interactive Playground

Enter prompts and test responses live

Choose models, temperature, and token limits

View latency & token usage instantly

🔹 Side-by-Side Model Comparison

Benchmark two LLMs with:

Response differences

Latency comparison

Token usage comparison

🔹 Logs Dashboard

Complete history of all requests

Prompt & response preview

Status (success/error)

Sorting & filtering

🔹 Analytics & Visual Insights

📈 Token Usage Trend

⚡ Latency Trend

❌ Error Trend

📊 Metrics Summary

🔔 Live Alerts

🔹 User Session Analytics

Find per-user insights:

Total requests

Total tokens consumed

Average latency

Most-used model

🔹 Feedback System

Users can rate responses and leave comments — all stored for analysis.

🐳 Docker Support

This system is fully containerized using Docker.

Run everything with:

docker-compose up --build


Docker ensures:

Portability

Easy deployment

Clean isolation

Zero setup issues

Containers include:

FastAPI Backend

Streamlit Frontend

PostgreSQL Database

🏗️ Tech Stack
Layer	Technology
Backend	FastAPI, LangChain, Groq API
Frontend	Streamlit
Database	PostgreSQL
Containerization	Docker
ORM	SQLAlchemy
Validation	Pydantic


🚀 How to Run the Project
1. Clone the Repository
git clone https://github.com/IshaVishwakarma/llm-observability.git
cd llm-observability

2. Add Your Environment Variables

Create a .env file:

GROQ_API_KEY=your_api_key_here


⚠️ Your .env file is NOT committed (thanks to .gitignore).

3. Run with Docker
docker-compose up --build

📍 Default Ports

Backend → http://localhost:9000

Frontend → http://localhost:8501

📁 Project Structure
llm-observability/
│── backend/
│   ├── main.py
│   ├── models.py
│   ├── crud.py
│   ├── callbacks.py
│   ├── database.py
│── frontend/
│   ├── app.py
│── postgres_data/
│── docker-compose.yml
│── requirements.txt
│── README.md

🙋‍♀️ Author

Isha Vishwakarma
Built with ❤️ using Python, FastAPI, Streamlit, Docker & PostgreSQL.
