<p align="center">
  <img src="https://img.shields.io/badge/Built%20For-Nirmaan%20AI-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/NLP-SentenceTransformers-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Deployed%20On-Render-purple?style=for-the-badge" />
</p>

# 🎤 AI-Powered Spoken Communication Rubric Scorer

This project evaluates a student's spoken self-introduction transcript and produces:

- A **final communication score (0–100)**
- A detailed **breakdown by rubric category**
- Constructive **feedback for improvement**

It combines:

| Component | Method |
|----------|--------|
| Rule-based scoring | Keywords, flow, speech rate, filler words |
| NLP understanding | Semantic similarity (Sentence Transformers) |
| Grammar analysis | LanguageTool Python |
| Sentiment | VADER |
| Vocabulary quality | TTR lexical analysis |

---

## 🚀 Live Demo (Coming Soon)
🔗 _Deployment URL will appear here after Render deployment._

---

## 📦 Features

- ✔ Extracts meaningful communication metadata from transcript text  
- ✔ Detects name, age, family, hobbies, structure, and expression quality  
- ✔ Analysis based on rubric provided in Nirmaan assignment  
- ✔ Web UI to paste text and instantly evaluate  
- ✔ Backend built using FastAPI  
- ✔ Frontend uses HTML, JavaScript, TailwindCSS  
- ✔ JSON API response available  

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Semantic NLP | SentenceTransformers (MiniLM-L6-v2) |
| Grammar | LanguageTool Python |
| Sentiment | VADER |
| Deployment Ready For | Render / Railway / AWS Free Tier |

---

## 🚀 Local Installation

```bash
git clone https://github.com/Subhajitdas99/nirmaan-ai-rubric-scorer.git
cd nirmaan-ai-rubric-scorer
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
