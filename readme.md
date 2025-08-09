# 🤖 AI/NLP Job Matcher

An AI system that analyzes user career profiles and job postings to provide matching scores and detailed feedback.

## 🚀 Key Features

- **Profile Management**: Save and load user career information (JSON format)
- **Text Input**: Direct job posting text input for analysis
- **Matching Analysis**: Keyword-based + semantic similarity analysis
- **AI Feedback**: Detailed matching feedback using GPT API
- **Multilingual Support**: Handles both Korean and English job postings

## 🛠️ API Setup

You have two options to configure your OpenAI API key:

#### Option 1: Create api.py file (Recommended)
- Edit the `api.py` file and replace the placeholder with your actual API key
- Restart the Streamlit app

#### Option 2: Manual Input in Web Interface
- Enter your API key directly in the application interface when prompted

⚠️ **Warning**: Other configuration methods (environment variables, config files) are not supported.

#### Getting an API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new secret key and copy it

### Run Application
```bash
streamlit run app.py
```

## 📖 Usage

### 1. Profile Setup
- Create and save your career profile with skills, experience, and preferences.

### 2. Job Analysis
- Paste job posting text and click analyze for automatic matching.

### 3. View Results
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

## 🚧 Future Improvements

- [ ] User login system
- [ ] Resume upload functionality
- [ ] Recommended job posting list
- [ ] Company information search integration
- [ ] Support for more languages

---
**Project maintained by Hyebin Lim**
