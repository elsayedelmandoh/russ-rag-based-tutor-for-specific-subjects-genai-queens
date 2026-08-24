# Beauty E-Commerce RAG Chatbot 🛍️

[![github](https://img.shields.io/badge/GitHub-sentiment__sleuth-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/elsayedelmandoh/russ-rag-based-tutor-for-specific-subjects-genai-queens)
[![linkedin-post](https://img.shields.io/badge/LinkedIn%20Post-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/posts/elsayed-elmandoh-b5849a1b8_can-an-air-gapped-ai-tutor-answer-curriculum-activity-7438317665930067968-TdoF?utm_source=share&utm_medium=member_desktop&rcm=ACoAADKeEvQBHt4xOmwiQTXdmYQjiJS81WuE3sc)

<p align="center">
  <img src="docs/02_results/res1.png" alt="Sentiment Sleuth — pos results" width="45%">
  &nbsp; &nbsp;
  <img src="docs/02_results/res2.png" alt="Sentiment Sleuth — neg results" width="45%">
</p>

A production-ready RAG chatbot for beauty e-commerce websites.
Answers customer questions about products, orders, and shipping
in both Arabic and English.

## 📋 Project Overview
Built for a beauty products e-commerce client.
Connects to product catalog (Excel) via RAG pipeline
to provide accurate, real-time answers.

## ✨ Features
- RAG pipeline connected to 100+ product catalog
- Bilingual support (Arabic + English)
- Product info, pricing, orders & shipping answers
- Clean embeddable UI (one line of code to add to website)
- Real-time accurate responses from product data

## 🛠️ Tech Stack
- Python + Streamlit
- LangChain (RAG pipeline)
- Google Gemini API
- FAISS (vector database)
- Pandas (Excel processing)
- OpenAI Embeddings

## 📦 Installation
pip install -r requirements.txt

## ⚙️ Setup
1. Add your API key to .env:
   GOOGLE_API_KEY=your_key_here
2. Place your Excel file in /data folder
3. Run: streamlit run app.py

## 📁 Project Structure
├── app.py              # Main Streamlit app
├── rag_pipeline.py     # RAG logic
├── data_loader.py      # Excel processing
├── requirements.txt
└── README.md

## 💬 Usage
1. Upload your product Excel file
2. Ask questions in Arabic or English
3. Get instant accurate answers

## 📊 Results
- 100+ products indexed
- Bilingual (AR/EN) support
- Deployed on client website ✅

## 👤 Author
Elsayed Elmandoh
NLP Engineer | MSc AI @ Queen's University
github.com/elsayedelmandoh
