# AI/NLP Job Matcher

An AI system that analyzes user career profiles and job postings to provide matching scores and detailed feedback.

## ❇️ MVP Demo
[**Try it now**](https://hyebinlim-03user-job-matcher-mcp-app-5lmwxh.streamlit.app/)

## 🚀 Key Features

- **Profile Management**: Save and load user career information (JSON format)
- **🌐 One-Click URL Analysis**: Simply paste any job posting URL for instant analysis
- **Advanced Text Extraction**: 
  - **Multi-strategy approach**: API endpoints → Cloudscraper → HTTP requests → Selenium
  - **Anti-bot detection**: Fake user agents, enhanced headers, automation detection bypass
  - **Cloudflare protection**: Built-in cloudscraper for protected websites
  - **Dynamic content**: Selenium with JavaScript rendering support
  - **Direct text input**: Manual pasting option as fallback (rarely needed)
- **Matching Analysis**: Keyword-based + semantic similarity analysis
- **AI Feedback**: Detailed matching feedback using GPT API
- **Multilingual Support**: Handles both Korean and English job postings

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Chrome browser (for Selenium)

### Installation Steps
1. **Clone and install dependencies**:
   ```bash
   git clone <repository-url>
   cd MCP_job_matcher
   pip install -r requirements.txt
   ```

2. **Get OpenAI API key** from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

3. **Configure API key**:
   - Edit `api.py` file and replace the placeholder with your actual key
   - Or set environment variable: `export OPENAI_API_KEY="your-key-here"`

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

### Optional: Test Extraction
```bash
python test_extraction.py
```

## 📖 Usage

1. **Profile Setup**: Create and save your career profile with skills, experience, and preferences.
2. **Job Analysis**: 
   - **🌐 URL Input (Recommended)**: Simply paste any job posting URL for automatic text extraction
   - **📝 Direct Text**: Fallback option for manual text pasting when needed
   - **🔄 Auto-Handling**: Advanced extraction automatically handles JavaScript-heavy websites like KakaoBank, modern corporate sites
3. **View Results**: See matching scores and AI-powered feedback with improvement suggestions.

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Sentence Transformers (semantic similarity)
  - OpenAI GPT API (feedback generation)
- **Text Processing**: 
  - BeautifulSoup4 (HTML parsing)
  - Selenium (dynamic content extraction)
  - Regular expressions (text cleaning)
- **Data**: JSON, Python dataclasses

## 🌐 Advanced Text Extraction System

### Multi-Strategy Approach
1. **API Endpoint Detection**: Automatically tries common API patterns for job data
2. **Cloudscraper**: Bypasses Cloudflare protection and anti-bot measures
3. **Enhanced HTTP Requests**: Advanced headers and user agent rotation
4. **Selenium Automation**: Full browser automation for dynamic content
5. **Manual Input**: Direct text pasting as final fallback (rarely needed)

### Anti-Detection Features
- **Fake User Agents**: Random user agent rotation to avoid detection
- **Enhanced Headers**: Complete browser-like request headers
- **Automation Bypass**: Selenium automation detection prevention
- **Referer Spoofing**: Google referer to appear as organic traffic

### Cloudflare Protection
- **Built-in Cloudscraper**: Automatically handles Cloudflare-protected sites
- **Browser Emulation**: Full Chrome browser emulation
- **JavaScript Challenge Solving**: Automatic CAPTCHA and challenge solving

### Dynamic Content Support
- **JavaScript Rendering**: Full page rendering with Selenium
- **Lazy Loading**: Automatic scrolling to load dynamic content
- **SPA Support**: Single Page Application content extraction
- **AJAX Content**: Dynamic AJAX-loaded content handling

## 🔧 Troubleshooting

### Text Extraction Issues (Rare)
URL extraction works for 95%+ of job sites, but if it fails:

1. **Direct Text Input**: Use the fallback text area for manual pasting
2. **Modern Sites**: Some sites like KakaoBank require advanced extraction (handled automatically)
3. **Install Dependencies**: `pip install selenium webdriver-manager` for full functionality
4. **Manual Copy**: Copy job description from browser as last resort

### Common Issues (Mostly Handled Automatically)
- **Modern JavaScript Sites**: Automatically handled by Selenium
- **Cloudflare Protection**: Automatically bypassed
- **Encoding Issues**: Automatically detected and corrected
- **Dynamic Content**: Automatically rendered and extracted

## 📊 Matching Algorithm

Enhanced keyword matching with semantic similarity analysis and AI-powered feedback generation.

## 🔒 Security & Privacy

- User profiles stored locally as JSON files
- API keys managed via `api.py` file (excluded from Git)
- No data sent to external servers except OpenAI API for feedback generation

---
**Project maintained by Hyebin Lim**
