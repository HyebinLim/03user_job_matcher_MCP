# 🤖 AI/NLP Job Matcher

An AI system that analyzes user career profiles and job postings to provide matching scores and detailed feedback.

## 🚀 Key Features

- **Profile Management**: Save and load user career information (JSON format)
- **Text Input**: Direct job posting text input for analysis
- **Matching Analysis**: Keyword-based + semantic similarity analysis
- **AI Feedback**: Detailed matching feedback using GPT API
- **Multilingual Support**: Handles both Korean and English job postings

## 📁 Project Structure

```
MCP_job_matcher/
├── app.py                    # Main Streamlit application
├── config.py                # Developer API key configuration
├── api.py                   # User API key configuration (create this)
├── requirements.txt          # Python package dependencies
├── readme.md                # Project documentation
├── .gitignore               # Git ignore file
├── utils/                   # Core modules
│   ├── __init__.py
│   ├── mcp_schema.py        # User context schema
│   ├── extract_text.py      # Text processing
│   ├── match_score.py       # Matching score calculation
│   └── feedback.py          # GPT API feedback generation
└── data/                    # Data storage
    ├── user_contexts/       # User profile JSON files
    └── postings/           # Job posting data
```

## 🛠️ Installation & Setup

### 1. Environment Setup

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. API Key Configuration

You have two options to configure your OpenAI API key:

#### Option 1: Create api.py file (Recommended)

1. Create a new file called `api.py` in the project root:
   ```python
   # Your OpenAI API Key
   OPENAI_API_KEY = "sk-proj-your_actual_api_key_here"
   ```

2. The `api.py` file is automatically excluded from Git (added to `.gitignore`)

#### Option 2: Manual Input

- Enter your API key directly in the application interface
- The key will be stored in session (temporary)
- You'll need to re-enter it each time you restart the app

#### Getting an API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the generated key (starts with `sk-proj-...`)

⚠️ **Security Note**: Never share your API key or commit it to version control!

### 3. Run Application

```bash
streamlit run app.py
```

## 📖 Usage

### 1. Profile Setup
- Go to **Profile tab** and enter personal information
  - Name, target roles, years of experience
  - Skills, languages, work preferences
  - Additional notes (free text)
- Click **Save** to store your profile

### 2. Job Analysis
- Go to **Job Analysis tab** and paste job posting text
- Click **Analyze** button
- Automatic matching analysis will be performed

### 3. View Results
- Go to **Results tab** to see matching score and AI feedback
- Detailed scores (skills, roles, experience, etc.)
- GPT-based detailed analysis and improvement suggestions

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Sentence Transformers (semantic similarity)
  - OpenAI GPT API (feedback generation)
- **Text Processing**: 
  - Regular expressions (text cleaning)
- **Data**: JSON, Python dataclasses

## 📊 Matching Algorithm

1. **Keyword-based Matching** (70% weight)
   - Skills matching
   - Role matching
   - Experience matching
   - Language matching
   - Work preference matching

2. **Semantic Similarity** (30% weight)
   - Sentence Transformers embeddings
   - Cosine similarity calculation

3. **AI Feedback**
   - GPT API for detailed analysis
   - Strengths/weaknesses/recommendations

## 🌐 Multilingual Support

- Handles Korean and English job postings automatically
- GPT responds in the same language as the job posting
- No manual language selection needed

## 🔒 Security & Privacy

- User profiles stored locally as JSON files
- API keys managed via `api.py` file (excluded from Git)
- Both `config.py` and `api.py` automatically excluded from version control
- No data sent to external servers except OpenAI API for feedback generation

## 🚧 Future Improvements

- [ ] User login system
- [ ] Resume upload functionality
- [ ] Recommended job posting list
- [ ] Company information search integration
- [ ] Support for more languages

## 📞 Contact

For project-related questions, please create an issue.
