# 🤖 AI/NLP Job Matcher

An AI system that analyzes user career profiles and job postings to provide matching scores and detailed feedback.

## ❇️ MVP Demo
[**Try it now**](https://hyebinlim-03user-job-matcher-mcp-app-5lmwxh.streamlit.app/)

## 🚀 Key Features

- **Profile Management**: Save and load user career information (JSON format)
- **Text Input**: Direct job posting text input for analysis
- **Matching Analysis**: Keyword-based + semantic similarity analysis
- **AI Feedback**: Detailed matching feedback using GPT API
- **Multilingual Support**: Handles both Korean and English job postings

## 🛠️ API Setup

1. Get your OpenAI API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Edit `api.py` file and replace the placeholder with your actual key
3. Run: `streamlit run app.py`

## 📖 Usage

#### 1. Profile Setup
- Create and save your career profile with skills, experience, and preferences.

#### 2. Job Analysis
- Paste job posting text and click analyze for automatic matching.

#### 3. View Results
- See matching scores and AI-powered feedback with improvement suggestions.

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Sentence Transformers (semantic similarity)
  - OpenAI GPT API (feedback generation)
- **Text Processing**: 
  - Regular expressions (text cleaning)
- **Data**: JSON, Python dataclasses

## 📊 Matching Algorithm

Enhanced keyword matching with semantic similarity analysis and AI-powered feedback generation.

## 🔒 Security & Privacy

- User profiles stored locally as JSON files
- API keys managed via `api.py` file (excluded from Git)
- No data sent to external servers except OpenAI API for feedback generation

---
**Project maintained by Hyebin Lim**
