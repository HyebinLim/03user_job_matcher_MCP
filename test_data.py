"""
Test data generator for AI/NLP Job Matcher
"""
import json
import os
from utils.mcp_schema import UserContext, save_user_context

def create_sample_user_contexts():
    """Create sample user profiles"""
    
    # Sample 1: AI/NLP Engineer
    user1 = UserContext(
        name="Hyebin Lim",
        email="hyebin.lim@example.com",
        target_roles=["NLP Engineer", "AI Research Assistant", "Machine Learning Engineer"],
        current_position="AI Research Assistant",
        current_company="Tech University",
        skills=["Python", "Transformers", "PyTorch", "NLP", "Deep Learning"],
        programming_languages=["Python", "JavaScript", "SQL"],
        education_level="Master's",
        major="Computer Science",
        university="Stanford University",
        graduation_year=2022,
        languages={"Korean": "Native", "English": "Fluent"},
        work_preference=["Remote", "Hybrid"],
        location_preference=["Seoul", "San Francisco", "Remote"],
        salary_expectation="80M-120M KRW",
        experience_by_industry={"AI/NLP": 2, "Research": 1},
        projects=[
            {
                "name": "Korean Language Model",
                "description": "Developed a Korean BERT model for sentiment analysis",
                "tech_stack": "Python, PyTorch, Transformers",
                "organization": "Tech University"
            },
            {
                "name": "Chatbot System",
                "description": "Built an NLP-based customer service chatbot",
                "tech_stack": "Python, GPT, FastAPI",
                "organization": "ABC Startup"
            }
        ],
        certifications=["AWS Certified Developer"],
        additional_notes="Specialized in Korean NLP and multilingual models. Experience with large language models and transformer architectures."
    )
    
    # Sample 2: Data Scientist
    user2 = UserContext(
        name="Alex Chen",
        email="alex.chen@example.com",
        target_roles=["Data Scientist", "ML Engineer", "AI Engineer"],
        current_position="Data Scientist",
        current_company="Tech Corp",
        skills=["Python", "R", "SQL", "Machine Learning", "Statistics"],
        programming_languages=["Python", "R", "SQL", "Scala"],
        education_level="Master's",
        major="Data Science",
        university="MIT",
        graduation_year=2020,
        languages={"English": "Native", "Mandarin": "Fluent"},
        work_preference=["On-site", "Hybrid"],
        location_preference=["New York", "San Francisco", "Boston"],
        salary_expectation="120K-180K USD",
        experience_by_industry={"Data Science": 3, "E-commerce": 2},
        projects=[
            {
                "name": "Recommendation System",
                "description": "Built a recommendation engine for e-commerce platform",
                "tech_stack": "Python, Scikit-learn, Redis",
                "organization": "Tech Corp"
            }
        ],
        certifications=["Google Cloud Professional Data Engineer"],
        additional_notes="Expert in recommendation systems and A/B testing. Strong background in statistics and experimental design."
    )
    
    # Save sample contexts
    save_user_context(user1, "hyebin_lim_sample.json")
    save_user_context(user2, "alex_chen_sample.json")
    
    print("Sample user contexts created successfully!")
    return user1, user2

def create_sample_job_postings():
    """Create sample job posting texts"""
    
    job_postings = {
        "nlp_engineer_korean": """
        [Hiring] NLP Engineer (Entry/Experienced)
        
        Company: AI Startup
        Location: Gangnam-gu, Seoul (Hybrid)
        Salary: 40M - 60M KRW
        
        Main Responsibilities:
        - Develop and optimize Korean natural language processing models
        - Research and apply transformer-based language models
        - Build chatbot and text analysis systems
        
        Requirements:
        - Experience with Python, PyTorch, Transformers required
        - NLP project experience
        - Korean/English communication skills
        - Master's degree or higher (Computer Science, AI related major)
        
        Preferred Qualifications:
        - Korean language model development experience
        - Paper publication or open source contribution experience
        - Cloud environment experience (AWS, GCP)
        """,
        
        "data_scientist_english": """
        [Hiring] Senior Data Scientist
        
        Company: Tech Startup
        Location: San Francisco, CA (Hybrid)
        Salary: $120K - $180K
        
        About the Role:
        We are looking for a Senior Data Scientist to join our growing team. You will be responsible for developing machine learning models and data-driven solutions.
        
        Responsibilities:
        - Develop and deploy machine learning models
        - Design and implement A/B testing frameworks
        - Build recommendation systems and predictive models
        - Collaborate with engineering and product teams
        
        Requirements:
        - 3+ years of experience in data science or machine learning
        - Strong programming skills in Python, R, or SQL
        - Experience with ML frameworks (TensorFlow, PyTorch, Scikit-learn)
        - Master's degree in Computer Science, Statistics, or related field
        - Experience with big data technologies (Spark, Hadoop)
        
        Preferred Qualifications:
        - Experience with recommendation systems
        - Knowledge of deep learning and neural networks
        - Experience with cloud platforms (AWS, GCP)
        - Published research or open source contributions
        """,
        
        "ai_researcher": """
        [Recruiting] AI Research Engineer
        
        Company: Research Institute
        Location: Remote / Cambridge, MA
        Salary: $100K - $150K
        
        Position Overview:
        We are seeking an AI Research Engineer to work on cutting-edge natural language processing and machine learning projects.
        
        Key Responsibilities:
        - Research and implement state-of-the-art NLP models
        - Develop and optimize transformer-based architectures
        - Contribute to research papers and technical documentation
        - Collaborate with academic and industry partners
        
        Required Qualifications:
        - PhD in Computer Science, AI, or related field
        - Strong background in deep learning and NLP
        - Experience with PyTorch, TensorFlow, or similar frameworks
        - Published research in top-tier conferences (ACL, EMNLP, ICML, NeurIPS)
        - Programming skills in Python and C++
        
        Desired Skills:
        - Experience with large language models
        - Knowledge of multilingual NLP
        - Experience with distributed training
        - Open source contributions to AI/ML projects
        """
    }
    
    # Save sample job postings
    data_dir = "data/postings"
    os.makedirs(data_dir, exist_ok=True)
    
    for name, content in job_postings.items():
        filepath = os.path.join(data_dir, f"{name}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    print("Sample job postings created successfully!")
    return job_postings

def main():
    """Main test data generation function"""
    print("Creating test data for AI/NLP Job Matcher...")
    
    # Create sample user contexts
    user1, user2 = create_sample_user_contexts()
    
    # Create sample job postings
    job_postings = create_sample_job_postings()
    
    print("\n=== Test Data Summary ===")
    print(f"Created {2} sample user profiles:")
    print(f"- {user1.name}: {', '.join(user1.target_roles)}")
    print(f"- {user2.name}: {', '.join(user2.target_roles)}")
    
    print(f"\nCreated {len(job_postings)} sample job postings:")
    for name in job_postings.keys():
        print(f"- {name}")
    
    print("\n=== How to Test ===")
    print("1. Run the Streamlit app: streamlit run app.py")
    print("2. Load a sample profile from the sidebar")
    print("3. Copy and paste a sample job posting text")
    print("4. Click 'Analyze Job Posting' to test the matching")
    print("5. Check the results in the Results tab")

if __name__ == "__main__":
    main() 