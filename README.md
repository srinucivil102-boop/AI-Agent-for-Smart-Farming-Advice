# AI Agent for Smart Farming Advice

## 🌾 Overview
An IBM Granite-powered multi-agent AI system that provides comprehensive, personalized, and real-time smart farming advice.

**Problem Statement:** IBM Hackathon — Problem No. 14  
**Tech Stack:** IBM Granite 3.0 · IBM watsonx.ai · IBM Cloud · Python · Streamlit  
**Project ID:** `81bcc076-b2a6-4039-a511-842212629b94`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit Web Interface                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│             Multi-Agent Orchestrator                         │
│  (Query routing, context management, agent coordination)     │
└──────┬──────────┬──────────┬──────────┬─────────────────────┘
       │          │          │          │
  ┌────▼──┐  ┌───▼───┐  ┌──▼───┐  ┌──▼────────┐
  │ Crop  │  │Weather│  │Pest/ │  │ Market    │
  │Advisor│  │ &Irr  │  │Disease│  │ Insights  │
  │ (RAG) │  │ Agent │  │Agent │  │ Agent     │
  └───────┘  └───────┘  └──────┘  └───────────┘
       │
┌──────▼──────────────────────────┐
│  Agricultural Knowledge Base    │
│  (TF-IDF RAG + IBM Granite)     │
└─────────────────────────────────┘
       │
┌──────▼──────────────────────────┐
│    IBM Granite 3.0 (LLM)        │
│    via IBM watsonx.ai API       │
└─────────────────────────────────┘
```

## 🤖 Multi-Agent System

| Agent | Function | Tech |
|-------|----------|------|
| **Crop Advisory Agent** | RAG-based best practices, guidelines | TF-IDF + IBM Granite |
| **Weather & Irrigation Agent** | Real-time weather, ET₀ calc, irrigation schedule | OpenWeatherMap + Granite |
| **Pest & Disease Detection Agent** | Image analysis + symptom diagnosis | Vision AI + Granite |
| **Market Insights Agent** | MSP prices, profit forecast, schemes | Price Oracle + Granite |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials
The `config.env` file is pre-configured with IBM credentials:
```
IBM_API_KEY=KJkn9AATL29Wl3XQ12vHqb1DJD7gJr4sqWFKvOUr9Ld6
IBM_PROJECT_ID=81bcc076-b2a6-4039-a511-842212629b94
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### 3. Run Tests
```bash
python test_agents.py
```

### 4. Launch Application
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
├── app.py                          # Main Streamlit UI
├── config.py                       # IBM credentials & settings
├── granite_client.py               # IBM Granite LLM interface
├── requirements.txt                # Python dependencies
├── test_agents.py                  # System validation tests
├── agents/
│   ├── orchestrator.py             # Multi-agent coordinator
│   ├── weather_irrigation_agent.py # Weather & irrigation module
│   ├── pest_disease_agent.py       # Pest/disease detection
│   ├── advisory_agent.py           # Personalized crop advisory
│   └── market_agent.py             # Market intelligence
└── data/
    └── knowledge_base/
        ├── agricultural_knowledge.py  # 17+ knowledge documents
        └── rag_agent.py               # TF-IDF RAG system
```

---

## 🌟 Key Features

### 1. 🔍 Agricultural Knowledge Retrieval (RAG)
- 17+ curated knowledge documents covering crops, soil, pests, market
- TF-IDF vector retrieval with IBM Granite generation
- Real-time Q&A with source citation

### 2. 🌤️ Weather & Soil Insights
- Live weather data integration (OpenWeatherMap)
- ET₀ calculation using Penman-Monteith method
- Stage-wise crop water requirement (Kc × ET₀)
- Soil profile database (5 soil types)

### 3. 🐛 Pest & Disease Detection
- Image-based crop disease analysis using IBM Granite
- Symptom text-to-diagnosis with knowledge base matching
- Treatment recommendations with product names and doses
- Seasonal pest calendar generation

### 4. 🌱 Personalized Advisory
- Complete season plan generation
- Variety recommendations (30+ varieties across 8 crops)
- Fertilizer scheduling with NPK calculations
- Harvest timeline estimation

### 5. 💰 Market Intelligence
- MSP data for 20+ crops (2024-25)
- Mandi price range database
- Profit/ROI projections
- Government scheme eligibility checker

### 6. 🤖 Multi-Agent Collaboration
- Smart query routing (keyword + AI classification)
- Shared farmer profile context across all agents
- Comprehensive dashboard aggregating all agent data

---

## 🛠️ IBM Technology Stack

| Component | Usage |
|-----------|-------|
| **IBM Granite 3.0** (`ibm/granite-3-8b-instruct`) | Core LLM for all text generation |
| **IBM watsonx.ai** | API endpoint for model inference |
| **IBM Cloud IAM** | Authentication & token management |
| **IBM Cloud** | Infrastructure & deployment platform |

---

## 📊 Sample Queries

- *"What is the best fertilizer schedule for wheat on black soil?"*
- *"Should I irrigate my soybean crop today given current weather?"*
- *"My tomato leaves have brown spots with concentric rings. What disease is this?"*
- *"What is the current MSP for soybean and when should I sell?"*
- *"Generate a complete season plan for cotton farming in Maharashtra"*
- *"What government schemes are available for cotton farmers in Gujarat?"*

---

## 📝 License
Academic project submission — IBM AI Hackathon 2024
