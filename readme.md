# AI/NLP Job Matcher

An AI system that analyzes user career profiles and job postings to provide matching scores and detailed feedback.

## ❇️ MVP Demo
[**Try it now**](https://hyebinlim-03user-job-matcher-mcp-app-5lmwxh.streamlit.app/)

## 🚀 Key Features

- **Profile Management**: Save and load user career information (JSON format)
- **🌐 One-Click URL Analysis**: Simply paste any job posting URL for instant analysis
- **Matching Analysis**: Keyword-based + semantic similarity analysis
- **AI Feedback**: Detailed matching feedback using GPT API
- **Multilingual Support**: Handles both Korean and English job postings

## 🛠️ API Setup

1. **Get OpenAI API key** from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. **Configure API key**:
   - Edit `api.py` file and replace the placeholder with your actual key
   - Or set environment variable: `export OPENAI_API_KEY="your-key-here"`

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

1. **Profile Setup**: Create and save your career profile with skills, experience, and preferences.
2. **Job Analysis**: **🌐 URL Input**: Simply paste any job posting URL for automatic text extraction
3. **View Results**: See matching scores and AI-powered feedback with improvement suggestions.

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Sentence Transformers (semantic similarity)
  - OpenAI GPT API (feedback generation)
- **Text Processing**: Regular expressions (text cleaning)
- **Data**: JSON, Python dataclasses



## 📊 Matching Algorithm

Enhanced keyword matching with semantic similarity analysis and AI-powered feedback generation.

## 🔒 Security & Privacy

- User profiles stored locally as JSON files
- API keys managed via `api.py` file (excluded from Git)
- No data sent to external servers except OpenAI API for feedback generation

---
**Project maintained by Hyebin Lim**
