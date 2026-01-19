# 🧠 MarketMind: Hybrid LLM System for Economic Sentiment Analysis

![Banner Image](https://i.ibb.co/HTwfMzSr/main-page.jpg)
> **🏆 WINNER - 1ST PLACE AWARD (Prize: 10,000 THB)**
> *High-Competency AI Workforce Development Project (PMU-B) x 42 Bangkok*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://4tuathb.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red)](https://streamlit.io/)

---

## Executive Summary

**MarketMind** is an AI-powered financial intelligence platform developed to solve the "Information Overload" crisis faced by retail investors. By leveraging a **Multi-Model Consensus Architecture**, MarketMind utilizes three distinct Large Language Models (LLMs) to analyze real-time financial news, eliminate emotional bias, and provide actionable investment strategies (Buy/Hold/Sell) with explained reasoning.

This project was developed as a Capstone Project for **42 Bangkok - KMITL** and secured the **1st Place Award** in the AI Competency Development Program.

---

## The Solution : Multi-Model Consensus

We moved beyond a single-AI approach. MarketMind implements an **Ensemble Learning** strategy, treating AI agents as a "Committee of Experts."

![Consensus Workflow](https://i.ibb.co/wFs6QCtz/solution.jpg)
### The "Committee" Members
1.  **Qwen-2.5** Specialized in financial terminology and CFA-level concepts.
2.  **Gemma-3** Specialized in chain-of-thought reasoning and logic.
3.  **Llama-3.1** Provides a broad market overview and context.

**The Result:** A final **Sentiment Analysis, Market Scoring, News Summary, Investment Suggestion** that is cross-verified, unbiased, and highly accurate.

---

## System Architecture & Workflow

Our end-to-end pipeline consists of four main layers:

1.  **Data Ingestion Layer :**
    * Real-time Web Scraping from major financial news outlets.
    * Incremental updates to ensure fresh data.
2.  **Data Processing Layer :**
    * **Cleaning:** Regex-based removal of HTML tags and noise.
    * **Indexing:** TF-IDF and Cosine Similarity to detect and remove duplicate news.
    * **Filtering:** Sector classification to route news to the correct analysis pipeline.
3.  **AI Analysis Layer (The Core) :**
    * Parallel processing by Qwen, Gemma, and Llama.
    * Generation of JSON-structured outputs (Sentiment, Rationale, Action).
    * Weighted Consensus Calculation.
4.  **Visualization Layer :**
    * Interactive Streamlit Dashboard.
    * Plotly-based visualizations (Treemaps, Gauge Charts).
![LLM](https://i.ibb.co/5XJ8smNK/llm-b.jpg)
---

## Key Features

### 1. Market Heatmap Dashboard
Visualize the entire market at a glance. Green indicates bullish sentiment; Red indicates bearish sentiment.
### 2. Sector Deep Dive
Click on any sector (e.g., Technology, Energy) to see granular details, historical sentiment trends, and specific news drivers.
### 3. AI Investment Strategy & Rationale
MarketMind doesn't just give a score; it explains **WHY**.
* **Action:** Buy / Hold / Sell
* **Rationale:** "Oil prices surged due to geopolitical tension, positively impacting the Energy sector..."

### 4. LLM Leaderboard
A transparent view of how each model performs against standard financial benchmarks (CFA, Financial PhraseBank).

---

## 🛠️ Technology Stack

| Category | Technologies Used |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Data Processing** | Pandas, NumPy, Scikit-learn (TF-IDF) |
| **AI / NLP** | Hugging Face Transformers, PyTorch |
| **LLMs** | Qwen-2.5-14B, Gemma-3-12B, Llama-3.1-8B |
| **Visualization** | Streamlit, Plotly Express, Plotly Graph Objects |
| **DevOps/Tools** | Git, VS Code |

---

## Performance Benchmarks

To ensure reliability, we benchmarked our selected models against industry standards:

| Benchmark | Domain | Best Performer | Score |
| :--- | :--- | :--- | :--- |
| **CFA Level 1** | Financial Knowledge | **Qwen-2.5** | **75.00%** |
| **Financial PhraseBank** | Sentiment Accuracy | **Qwen-2.5** | **81.34%** |
| **GSM8K** | Logic & Reasoning | **Gemma-3** | **78.77%** |

*Conclusion: No single model is perfect. Combining Qwen's financial knowledge with Gemma's logic yields the best results.*

---

## Future Roadmap

* **Data Expansion:** Integrate local Thai Stock Market (SET) and ASEAN regional news.
* **Subscription Model:** Tiered access (Free vs. Premium) to unlock advanced Multi-Model Consensus features.
* **Personalization:** User profiles to customize risk tolerance and preferred sectors.
* **Notification System:** Real-time Line/Telegram alerts when sentiment shifts significantly.

---

## The Team: 4TUATHB Industries

**Advisor:** Dr. Jirayu Petchhan

* **Natthawut Chai-uam**
* **Peerapol Srisawat**
* **Nawaporn Kiatveerachon**
* **Teerawisit Jinnarat**

---

## Acknowledgements

We would like to extend our gratitude to:
* **PMU-B (Program Management Unit for Human Resources & Institutional Development, Research and Innovation)** for the support and the award.
* **42 Bangkok & KMITL** for the learning platform and resources.

---

<p align="center">
  <a href="https://4tuathb.streamlit.app/">
    <img src="https://img.shields.io/badge/View_Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="View Demo"/>
  </a>
</p>
