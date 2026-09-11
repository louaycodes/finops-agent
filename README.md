# FinOps Agent - Multi-Agent AWS Cost Optimization System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=for-the-badge)

**English:** An autonomous multi-agent system designed for AWS cost analysis and optimization. Built with LangGraph, LLMs (Groq), and a full-stack architecture, it automatically discovers resources, detects anomalies, forecasts spending, and provides actionable FinOps recommendations through an interactive dashboard and a RAG-powered chatbot.

**Français :** Un système multi-agents autonome conçu pour l'analyse et l'optimisation des coûts AWS. Construit avec LangGraph, des LLMs (Groq) et une architecture full-stack, il découvre automatiquement les ressources, détecte les anomalies, prévoit les dépenses et fournit des recommandations FinOps via un tableau de bord interactif et un chatbot basé sur le RAG.

## Architecture

```text
AWS Account
    |
    v Resource Explorer v2 (auto-discovery)
Discovery Agent
    |
    v
Collector Agent (Cost Explorer + CloudWatch -> S3 Parquet)
    |
    v
Analyzer Agent (Groq LLM -> anomalies JSON -> S3)
    |
    v
Forecaster Agent (AWS get_cost_forecast -> S3)
    |
    v
Recommender Agent (Groq LLM -> recommendations JSON -> S3)
    |
    v
RAG Indexer (ChromaDB + sentence-transformers)
    |
    v
Flask API <- Angular Dashboard
```

### Components Description
- **Discovery Agent:** Interfaces with AWS Resource Explorer v2 to automatically catalog all resources across the AWS account.
- **Collector Agent:** Gathers usage and financial metrics using AWS Cost Explorer and CloudWatch, then archives the data in S3 using the Parquet format for optimized querying.
- **Analyzer Agent:** Leverages the Groq LLM to analyze historical data, detect spending anomalies, and output findings as JSON to S3.
- **Forecaster Agent:** Utilizes the native AWS get_cost_forecast API to project spending for the next 30 days and stores the results in S3.
- **Recommender Agent:** Processes analyzed data through the Groq LLM to generate actionable, natural-language FinOps recommendations, saved as JSON.
- **RAG Indexer:** Embeds the generated insights into a local vector database (ChromaDB) using sentence-transformers, enabling semantic search and a conversational interface.
- **Flask API:** Serves as the backend bridge, exposing endpoints for the RAG chatbot, reporting, and data retrieval.
- **Angular Dashboard:** The frontend user interface that presents interactive charts, recommendations, and the FinOps assistant chat.

## Features

- **Auto-Discovery:** Automatically maps all AWS resources using Resource Explorer v2.
- **Multi-Agent Orchestration:** A sophisticated LangGraph pipeline orchestrating 5 sequential agents.
- **Anomaly Detection:** AI-driven cost anomaly detection utilizing Groq LLM.
- **Native Forecasting:** 30-day cost predictions using the AWS Cost Explorer API.
- **Actionable Insights:** Natural language FinOps recommendations tailored to your infrastructure.
- **Interactive Chatbot:** RAG-powered conversational agent (ChromaDB + sentence-transformers) to interrogate your cost data.
- **Automated Alerts:** Slack notifications triggered automatically for High-severity anomalies.
- **Weekly Reporting:** Automated PDF report generation powered by ReportLab.
- **Visual Analytics:** Comprehensive Angular dashboard featuring interactive cost and usage graphs.
- **Production Ready:** Dockerized deployment on EC2 with the Angular frontend hosted on S3.
- **100% Pluggable:** Easily connect to any AWS account simply by updating the `config.yaml` file.

## Technical Stack

| Component | Technology | Role |
|-----------|------------|------|
| **Orchestration** | LangGraph | Manages the sequential multi-agent workflow |
| **LLM Inference** | Groq | Powers the intelligence behind anomalies and recommendations |
| **Vector DB** | ChromaDB | Stores and retrieves embeddings for the RAG chatbot |
| **Embeddings** | sentence-transformers | Converts textual reports into searchable vectors |
| **Cloud Provider**| AWS | Target infrastructure (EC2, RDS, S3, Lambda, Cost Explorer, CloudWatch, Resource Explorer, Athena, EventBridge) |
| **Backend API** | Flask (Python) | Exposes data and RAG features to the frontend |
| **Frontend UI** | Angular | Displays interactive dashboards and chatbot interface |
| **PDF Generation**| ReportLab | Generates weekly FinOps summary reports |
| **Deployment** | Docker | Containerizes the backend API for consistent deployment |

## Prerequisites

- Python 3.12+
- Node.js 18+ (for Angular)
- Docker
- AWS CLI (configured with appropriate credentials)
- An AWS Account with required services enabled (Cost Explorer, Resource Explorer v2)

## Installation & Launch

### Backend (Local)

```bash
cd finops-agent
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your_groq_api_key"
export SLACK_WEBHOOK_URL="your_slack_webhook_url"
python -m pipeline.main
```

### Flask API

```bash
cd finops-rag-api
python app.py
```

### Angular Dashboard

```bash
cd finops-dashboard
npm install
ng serve
```

### Docker

```bash
docker build -t finops-api -f finops-rag-api/Dockerfile .
docker run -p 5001:5001 --env-file .env finops-api
```

## Configuration

The system is highly configurable via the `config.yaml` file located in the `finops-agent` directory. This file dictates the target AWS account, operational thresholds, and scheduling preferences.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | API key required to access Groq LLM services |
| `SLACK_WEBHOOK_URL`| Webhook URL for sending automated high-severity anomaly alerts |
| `AWS_ACCESS_KEY_ID`| (Optional) If not relying on default AWS CLI profiles |
| `AWS_SECRET_ACCESS_KEY`| (Optional) If not relying on default AWS CLI profiles |

## AWS Deployment

- **Backend:** The Flask API and LangGraph pipeline are containerized via Docker, pushed to AWS ECR, and deployed on an EC2 instance.
- **Frontend:** The Angular dashboard is compiled (`ng build`) and hosted statically on an AWS S3 bucket configured for Website Hosting.
- **Pipeline Automation:** The agent orchestration is scheduled to run every 24 hours using AWS EventBridge triggering an AWS Lambda function.

### Production URLs

- **Frontend Dashboard:** `http://finops-dashboard-louay.s3-website.eu-north-1.amazonaws.com`
- **Backend API:** `http://16.170.203.207:5001`

## Project Structure

```text
.
|-- finops-agent/          # Python Pipeline (LangGraph agents)
|   |-- pipeline/          # Orchestration logic
|   |-- config.yaml        # Main configuration file
|   `-- requirements.txt   # Python dependencies for the agents
|
|-- finops-rag-api/        # Flask API (Backend)
|   |-- app.py             # Flask application entry point
|   `-- Dockerfile         # Docker configuration for the API
|
`-- finops-dashboard/      # Angular Dashboard (Frontend)
    |-- src/               # Angular source code
    |-- angular.json       # Angular configuration
    `-- package.json       # Node.js dependencies
```

## Author & Acknowledgments

**Author:** Louay Zorai  
**Academic Context:** ArcTIC 4th year student, ESPRIT School of Engineering  
**Company:** Altran Telnet Corporation  

Special thanks to the engineering teams at Altran Telnet Corporation and the faculty at ESPRIT for their continuous support throughout this internship project.
