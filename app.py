import streamlit as st
import os
import json
from utils.mcp_schema import UserContext, load_user_context, list_saved_contexts, save_user_context
from utils.extract_text import extract_text_from_url, extract_all_text
from utils.match_score import calculate_match_score
from utils.feedback import generate_job_feedback

# API 키 불러오기 (config.py 또는 api.py에서)
CONFIG_API_KEY = None
API_KEY_SOURCE = None

# 1. 개발자용 config.py 확인
try:
    from config import OPENAI_API_KEY
    if OPENAI_API_KEY and OPENAI_API_KEY != "여기에_본인의_API_키를_입력하세요":
        CONFIG_API_KEY = OPENAI_API_KEY
        API_KEY_SOURCE = "config.py (Developer)"
except ImportError:
    pass

# 2. 사용자용 api.py 확인 (config.py가 없거나 비어있을 때)
if not CONFIG_API_KEY:
    try:
        from api import OPENAI_API_KEY
        if OPENAI_API_KEY and OPENAI_API_KEY != "sk-proj-your_actual_api_key_here":
            CONFIG_API_KEY = OPENAI_API_KEY
            API_KEY_SOURCE = "api.py (User)"
    except ImportError:
        pass

# 3. Streamlit secrets 확인 (배포 환경용)
if not CONFIG_API_KEY:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            CONFIG_API_KEY = st.secrets["OPENAI_API_KEY"]
            API_KEY_SOURCE = "Streamlit Secrets"
    except Exception:
        pass

# Page configuration
st.set_page_config(
    page_title="AI/NLP Job Matcher",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for tighter spacing
st.markdown("""
<style>
hr {
    margin: 8px 0 !important;
    border: 1px solid #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# Main page
st.title("Quick match checker - You to the job")

# Usage guide (moved to top right after title)
st.markdown("""
### How to Use
<div style='font-size: 14px;'>
1. <strong>Select Profile</strong>: Choose a user profile from the sidebar<br>
2. <strong>Enter URL</strong>: Input the job posting URL<br>
3. <strong>Run Analysis</strong>: Click "Analyze Job Posting" button<br>
4. <strong>Review Results</strong>: Check the matching results and AI feedback
</div>
""", unsafe_allow_html=True)

# OpenAI API Key 관리
st.markdown("### OpenAI API Key")

# API 키가 설정되었는지 확인
if CONFIG_API_KEY:
    st.success("✅ API key has been ready to provide detailed feedback.")
    # 로드된 키를 세션에 저장
    st.session_state.openai_api_key = CONFIG_API_KEY
    
    # 간단한 안내 메시지
    st.markdown("<div style='font-size: 12px; color: #666;'>💡 You can also insert your API key in [api.py]</div>", unsafe_allow_html=True)
else:


    # Manual API key input fallback
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""

    api_key = st.text_input(
        "Your OpenAI API key",
        value=st.session_state.openai_api_key,
        type="password",
        placeholder="sk-...",
        help="Your OpenAI API key will be stored in session and used for AI feedback generation",
        key="openai_api_key_input"
    )

    # Save API key to session state
    if api_key != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key
        if api_key:
            st.success("API key saved! You can now use AI-powered feedback features.")
        else:
            st.warning("API key removed. AI feedback features will be disabled.")
    
    # API 파일 설정 안내
    if not st.session_state.get('openai_api_key'):
        with st.expander("or... you can insert your key in api.py"):
            st.markdown("""
            1. Edit `api.py` file and replace the placeholder with your actual key
            2. Restart the application
            """)

# 현재 사용 중인 API 키 확인
current_api_key = st.session_state.get('openai_api_key', '')
if current_api_key and not CONFIG_API_KEY:
    st.info(f"Using manually entered API key (starts with: {current_api_key[:12]}...)")
elif not current_api_key and not CONFIG_API_KEY:
    st.warning("⚠️ No API key configured. AI feedback features will be disabled.")

st.markdown("---")

# Initial Q&A form for first-time users (only show if no profiles exist)
saved_contexts = list_saved_contexts()
if not saved_contexts and not st.session_state.get('has_profile', False):
    st.info("Welcome! Please answer a few questions to create your profile.")
    
    with st.form("initial_profile_form"):
        name = st.text_input("Name", key="initial_name")
        
        target_roles_input = st.text_area(
            "Target Roles (separated by commas)",
            placeholder="e.g., NLP Engineer, AI Research Assistant, Data Scientist",
            height=80,
            key="initial_target_roles"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            current_position = st.text_input("Current Position", placeholder="e.g., AI Research Assistant", key="initial_current_position")
        with col2:
            current_role = st.text_input("Current Role", placeholder="e.g., NLP Engineer", key="initial_current_role")
        with col3:
            current_company = st.text_input("Current Company", placeholder="e.g., Tech University", key="initial_current_company")
        
        salary_expectation = st.text_input("Salary Expectation", placeholder="e.g., 80M-120M KRW", key="initial_salary")
        
        skills_input = st.text_area(
            "Key Skills (separated by commas)",
            placeholder="e.g., Python, Transformers, PyTorch, NLP, Deep Learning",
            height=80,
            key="initial_skills"
        )
        
        programming_languages_input = st.text_area(
            "Programming Languages (separated by commas)",
            placeholder="e.g., Python, JavaScript, SQL, R, Java, C++",
            height=80,
            key="initial_programming_languages"
        )
        col1, col2 = st.columns(2)
        with col1:
            korean_level = st.selectbox("Korean Level", ["Native", "Fluent", "Intermediate", "Basic"], key="initial_korean_level")
        with col2:
            english_level = st.selectbox("English Level", ["Native", "Fluent", "Intermediate", "Basic"], key="initial_english_level")
        
        col1, col2 = st.columns(2)
        with col1:
            education_level = st.selectbox("Highest Degree", ["High School", "Associate's", "Bachelor's", "Master's", "PhD", "Other"], key="initial_education_level")
        with col2:
            university = st.text_input("University", placeholder="e.g., Seoul National University", key="initial_university")
        
        major = st.text_input("Major", placeholder="e.g., Computer Science", key="initial_major")
        
        col1, col2 = st.columns(2)
        with col1:
            experience_years = st.number_input("Experience Years", min_value=0, max_value=50, value=0, key="initial_experience_years")
        with col2:
            experience_months = st.number_input("Experience Months", min_value=0, max_value=11, value=0, key="initial_experience_months")
        
        work_preference = st.multiselect(
            "Work Preference",
            ["Remote", "Hybrid", "On-site"],
            default=["Remote", "Hybrid"],
            key="initial_work_preference"
        )
        
        additional_notes = st.text_area(
            "Additional Notes (optional)",
            placeholder="e.g., Special achievements, interests, career goals, etc.",
            height=100,
            key="initial_additional_notes"
        )
        
        if st.form_submit_button("Create Profile", type="primary"):
            if name:
                # Process input values
                target_roles = [role.strip() for role in target_roles_input.split(',') if role.strip()]
                skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                programming_languages = [lang.strip() for lang in programming_languages_input.split(',') if lang.strip()]
                
                # Calculate total experience in years (including months)
                total_experience = experience_years + (experience_months / 12)
                
                # Create UserContext
                new_context = UserContext(
                    name=name,
                    target_roles=target_roles,
                    current_position=current_position,
                    current_role=current_role,
                    current_company=current_company,
                    salary_expectation=salary_expectation,
                    skills=skills,
                    programming_languages=programming_languages,
                    languages={"Korean": korean_level, "English": english_level},
                    work_preference=work_preference,
                    education_level=education_level,
                    major=major,
                    university=university,
                    experience_by_industry={"General": total_experience} if total_experience > 0 else {},
                    projects=[],
                    certifications=[],
                    location_preference=[],
                    additional_notes=additional_notes
                )
                
                # Save
                try:
                    save_user_context(new_context)
                    st.success(f"{name}'s profile has been successfully created!")
                    st.session_state.has_profile = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error occurred while creating profile: {e}")
            else:
                st.error("Name is a required field.")

# Sidebar - User profile selection
st.sidebar.title("Select Profile")

# Get saved profile lists
if saved_contexts:
    # Create display names (remove _context.json suffix and replace underscores with spaces)
    display_names = []
    filename_to_display = {}
    display_to_filename = {}
    
    for filename in saved_contexts:
        # Remove _context.json suffix and replace underscores with spaces
        display_name = filename.replace('_context.json', '').replace('_', ' ')
        display_names.append(display_name)
        filename_to_display[filename] = display_name
        display_to_filename[display_name] = filename
    
    selected_display = st.sidebar.selectbox(
        "You are...",
        ["Create New Profile"] + display_names
    )
    
    if selected_display != "Create New Profile":
        selected_profile = display_to_filename[selected_display]
        user_context = load_user_context(selected_profile)
        if user_context:
            st.sidebar.success(f"{user_context.name} currently is...")
            st.sidebar.markdown(f"<div style='font-size: 12px;'><strong>Roles</strong>: {', '.join(user_context.target_roles)}</div>", unsafe_allow_html=True)
            if user_context.current_position and user_context.current_company:
                st.sidebar.markdown(f"<div style='font-size: 12px;'><strong>Current</strong>: {user_context.current_position} @ {user_context.current_company}</div>", unsafe_allow_html=True)
            if user_context.experience_by_industry:
                experience_text = ", ".join([f"{industry}({years:.1f}y)" for industry, years in user_context.experience_by_industry.items()])
                st.sidebar.markdown(f"<div style='font-size: 12px;'><strong>Experience</strong>: {experience_text}</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("<div style='font-size: 12px;'><strong>Experience</strong>: None</div>", unsafe_allow_html=True)
            if user_context.salary_expectation:
                st.sidebar.markdown(f"<div style='font-size: 12px;'><strong>Salary Expectation</strong>: {user_context.salary_expectation}</div>", unsafe_allow_html=True)
            
            # Profile management buttons
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("Edit"):
                    st.session_state.edit_profile = True
                    st.session_state.editing_profile = user_context
            with col2:
                if st.button("Delete"):
                    st.session_state.show_delete_modal = True
                    st.session_state.deleting_profile = selected_profile
        else:
            st.sidebar.error("Failed to load profile")
            user_context = None
    else:
        user_context = None
        if st.sidebar.button("Create New Profile"):
            st.session_state.create_profile = True
else:
    st.sidebar.info("No saved profiles found.")
    if st.sidebar.button("Create First Profile"):
        st.session_state.create_profile = True
    user_context = None

# Delete confirmation modal
if st.session_state.get('show_delete_modal', False):
    # Create a modal-like experience using columns and containers
    st.markdown("---")
    
    # Modal overlay effect
    with st.container():
        st.markdown("""
        <style>
        .modal-overlay {
            background-color: rgba(0, 0, 0, 0.5);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000;
        }
        .modal-content {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            max-width: 500px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Modal content
        with st.container():
            st.markdown("### Delete Profile Confirmation")
            st.warning(f"Are you sure you want to delete '{st.session_state.deleting_profile}' profile?")
            st.info("This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Delete", type="primary", use_container_width=True):
                    try:
                        # Delete file
                        import os
                        data_dir = "data/user_contexts"
                        filepath = os.path.join(data_dir, st.session_state.deleting_profile)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            st.success("Profile has been deleted.")
                            st.session_state.show_delete_modal = False
                            st.session_state.deleting_profile = None
                            st.rerun()
                        else:
                            st.error("Profile file not found.")
                    except Exception as e:
                        st.error(f"Error occurred while deleting profile: {e}")
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_delete_modal = False
                    st.session_state.deleting_profile = None
                    st.rerun()

# Profile creation/editing form
if st.session_state.get('create_profile', False) or st.session_state.get('edit_profile', False):
    st.subheader("Create Profile" if st.session_state.get('create_profile') else "Edit Profile")
    
    editing_profile = st.session_state.get('editing_profile')
    
    # Load existing data in edit mode
    if editing_profile and 'user_languages' not in st.session_state:
        st.session_state.user_languages = editing_profile.languages.copy()
    if editing_profile and 'user_experience' not in st.session_state:
        st.session_state.user_experience = editing_profile.experience_by_industry.copy() if editing_profile.experience_by_industry else {}
    if editing_profile and 'user_projects' not in st.session_state:
        st.session_state.user_projects = editing_profile.projects.copy() if editing_profile.projects else []
    if editing_profile and 'user_certifications' not in st.session_state:
        st.session_state.user_certifications = editing_profile.certifications.copy() if editing_profile.certifications else []
    if editing_profile and 'user_locations' not in st.session_state:
        st.session_state.user_locations = editing_profile.location_preference.copy() if editing_profile.location_preference else []
    
    # Basic information input
    name = st.text_input("Name", value=editing_profile.name if editing_profile else "", key="profile_name")
    col1, col2, col3 = st.columns(3)
    with col1:
        current_position = st.text_input("Current Position", value=editing_profile.current_position if editing_profile else "", placeholder="e.g., AI Research Assistant", key="profile_current_position")
    with col2:
        current_role = st.text_input("Current Role", value=editing_profile.current_role if editing_profile and hasattr(editing_profile, 'current_role') else "", placeholder="e.g., NLP Engineer", key="profile_current_role")
    with col3:
        current_company = st.text_input("Current Company", value=editing_profile.current_company if editing_profile else "", placeholder="e.g., Tech University", key="profile_current_company")
    
    
    salary_expectation = st.text_input("Salary Expectation", value=editing_profile.salary_expectation if editing_profile else "", placeholder="e.g., 80M-120M KRW", key="profile_salary")
    
    target_roles_input = st.text_area(
        "Target Roles (separated by commas)",
        value=", ".join(editing_profile.target_roles) if editing_profile else "",
        height=80,
        key="profile_target_roles"
    )
    
    skills_input = st.text_area(
        "Skills (separated by commas)",
        value=", ".join(editing_profile.skills) if editing_profile else "",
        height=80,
        key="profile_skills"
    )
    
    programming_languages_input = st.text_area(
        "Programming Languages (separated by commas)",
        value=", ".join(editing_profile.programming_languages) if editing_profile else "",
        height=80,
        key="profile_programming_languages"
    )

    
    # Language proficiency (dynamic add/delete)
    # Language addition feature
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_language = st.selectbox("Language Proficiency", ["Korean", "English", "Japanese", "Chinese", "German", "French", "Spanish", "Other"], key="profile_new_language")
    with col2:
        language_level = st.selectbox("Level", ["Native", "Fluent", "Intermediate", "Basic"], key="profile_language_level")
    with col3:
        if st.button("Add Language", use_container_width=True, key="profile_add_language"):
            if 'user_languages' not in st.session_state:
                st.session_state.user_languages = {}
            if new_language not in st.session_state.user_languages:
                st.session_state.user_languages[new_language] = language_level
                st.rerun()
    
    # Display and delete existing languages
    if st.session_state.get('user_languages'):
        for lang, level in st.session_state.user_languages.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(lang)
            with col2:
                st.write(level)
            with col3:
                if st.button("Delete", key=f"del_lang_{lang}", use_container_width=True):
                    del st.session_state.user_languages[lang]
                    st.rerun()
    
    # Education/Major
    col1, col2 = st.columns(2)
    with col1:
        education_level = st.selectbox("Highest Education", ["High School", "Associate's", "Bachelor's", "Master's", "PhD", "Other"], key="profile_education_level")
    with col2:
        university = st.text_input("Graduated University", value=editing_profile.university if editing_profile else "", placeholder="e.g., Seoul National University", key="profile_university")
    
    major = st.text_input("Major", value=editing_profile.major if editing_profile else "", placeholder="e.g., Computer Science", key="profile_major")

    
    # Experience breakdown (dynamic add/delete) - Updated to include months
    st.markdown("**Experience**")
    
    # Experience addition feature
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
    with col1:
        new_industry = st.text_input("Industry/Field", placeholder="e.g., AI/NLP, Investment Banking, IT", key="profile_new_industry")
    with col2:
        new_role = st.text_input("Role", placeholder="e.g., NLP Engineer, Data Scientist", key="profile_new_role")
    with col3:
        industry_years = st.number_input("Years", min_value=0, max_value=50, value=0, key="profile_industry_years")
    with col4:
        industry_months = st.number_input("Months", min_value=0, max_value=11, value=0, key="profile_industry_months")
    with col5:
        if st.button("Add Experience", use_container_width=True, key="profile_add_experience"):
            if new_industry:
                if 'user_experience' not in st.session_state:
                    st.session_state.user_experience = {}
                # Combine industry and role for the key
                experience_key = f"{new_industry}" + (f" ({new_role})" if new_role else "")
                if experience_key not in st.session_state.user_experience:
                    total_experience = industry_years + (industry_months / 12)
                    st.session_state.user_experience[experience_key] = total_experience
                    st.rerun()
    
    # Display and delete existing experience
    if st.session_state.get('user_experience'):
        for industry, years in st.session_state.user_experience.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(industry)
            with col2:
                st.write(f"{years:.1f} years")
            with col3:
                if st.button("Delete", key=f"del_exp_{industry}", use_container_width=True):
                    del st.session_state.user_experience[industry]
                    st.rerun()
    
    # Project experience (dynamic add/delete)
    st.markdown("**Project Experience**")
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name", placeholder="e.g., Chatbot Development", key="profile_project_name")
        project_description = st.text_area("Project Description", placeholder="e.g., Developed AI chatbot system for customer service", key="profile_project_description")
    with col2:
        project_tech = st.text_input("Tech Stack", placeholder="e.g., Python, GPT, FastAPI", key="profile_project_tech")
        project_org = st.text_input("Organization", placeholder="e.g., ABC Startup", key="profile_project_org")
    
    if st.button("Add Project", use_container_width=True, key="profile_add_project"):
        if project_name:
            if 'user_projects' not in st.session_state:
                st.session_state.user_projects = []
            
            new_project = {
                "name": project_name,
                "description": project_description,
                "tech_stack": project_tech,
                "organization": project_org
            }
            
            # Duplicate check (by name)
            existing_names = [p.get("name", "") for p in st.session_state.user_projects]
            if project_name not in existing_names:
                st.session_state.user_projects.append(new_project)
                st.rerun()
    
    # Display and delete existing projects
    if st.session_state.get('user_projects'):
        st.write("**Current Projects:**")
        for i, project in enumerate(st.session_state.user_projects):
            with st.expander(f"{project.get('name', 'Project')}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Description**: {project.get('description', '')}")
                    st.write(f"**Tech Stack**: {project.get('tech_stack', '')}")
                    st.write(f"**Organization**: {project.get('organization', '')}")
                with col2:
                    if st.button("Delete", key=f"del_proj_{i}", use_container_width=True):
                        st.session_state.user_projects.pop(i)
                        st.rerun()
    
    # Certifications (dynamic add/delete)
    st.write("**Certifications**")
    
    # Certification addition feature
    col1, col2 = st.columns([3, 1])
    with col1:
        cert_name = st.text_input("Certification Name", placeholder="e.g., AWS Certified Solutions Architect", key="profile_cert_name")
    with col2:
        if st.button("Add Certification", use_container_width=True, key="profile_add_cert"):
            if cert_name:
                if 'user_certifications' not in st.session_state:
                    st.session_state.user_certifications = []
                if cert_name not in st.session_state.user_certifications:
                    st.session_state.user_certifications.append(cert_name)
                    st.rerun()
    
    # Display and delete existing certifications
    if st.session_state.get('user_certifications'):
        st.write("**Current Certifications:**")
        for i, cert in enumerate(st.session_state.user_certifications):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {cert}")
            with col2:
                if st.button("Delete", key=f"del_cert_{i}", use_container_width=True):
                    st.session_state.user_certifications.pop(i)
                    st.rerun()
    
    # Preferred work locations
    preferred_locations_input = st.text_input(
        "Preferred Work Locations (separated by commas)",
        value=", ".join(st.session_state.get('user_locations', [])) if st.session_state.get('user_locations') else "",
        placeholder="e.g., Seoul, New York, London",
        key="profile_preferred_locations"
    )
    
    # Update session state when input changes
    if preferred_locations_input:
        locations = [loc.strip() for loc in preferred_locations_input.split(',') if loc.strip()]
        st.session_state.user_locations = locations
    else:
        st.session_state.user_locations = []
    
    # Work preference
    work_preference = st.multiselect(
        "Work Preference",
        ["Remote", "Hybrid", "On-site"],
        default=editing_profile.work_preference if editing_profile else ["Remote", "Hybrid"],
        key="profile_work_preference"
    )
    

    
    # Additional notes
    additional_notes = st.text_area(
        "Additional Notes (optional)",
        value=editing_profile.additional_notes if editing_profile else "",
        placeholder="e.g., Special achievements, interests, career goals, etc.",
        height=100,
        key="profile_additional_notes"
    )
    
    # Final save/cancel buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Save", type="primary", use_container_width=True, key="profile_save"):
            # Process input values
            target_roles = [role.strip() for role in target_roles_input.split(',') if role.strip()]
            skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
            programming_languages = [lang.strip() for lang in programming_languages_input.split(',') if lang.strip()]
            
            # Create UserContext
            new_context = UserContext(
                name=name,
                target_roles=target_roles,
                current_position=current_position,
                current_role=current_role,
                current_company=current_company,
                salary_expectation=salary_expectation,
                skills=skills,
                programming_languages=programming_languages,
                languages=st.session_state.get('user_languages', {"Korean": "Native", "English": "Fluent"}),
                work_preference=work_preference,
                education_level=education_level,
                major=major,
                university=university,
                experience_by_industry=st.session_state.get('user_experience', {}),
                projects=st.session_state.get('user_projects', []),
                certifications=st.session_state.get('user_certifications', []),
                location_preference=st.session_state.get('user_locations', []),
                additional_notes=additional_notes
            )
            
            # Save
            try:
                save_user_context(new_context)
                st.success(f"{name}'s profile has been successfully saved!")
                st.session_state.create_profile = False
                st.session_state.edit_profile = False
                st.session_state.editing_profile = None
                # Clear session state
                for key in ['user_languages', 'user_experience', 'user_projects', 'user_certifications', 'user_locations']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            except Exception as e:
                st.error(f"Error occurred while saving profile: {e}")
    
    with col2:
        if st.button("Cancel", use_container_width=True, key="profile_cancel"):
            st.session_state.create_profile = False
            st.session_state.edit_profile = False
            st.session_state.editing_profile = None
            # Clear session state
            for key in ['user_languages', 'user_experience', 'user_projects', 'user_certifications', 'user_locations']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Input method selection
st.subheader("Job Posting Analysis")
input_method = st.radio(
    "입력 방법 선택",
    ["🌐 URL 입력", "📝 직접 텍스트 입력"],
    horizontal=True,
    help="URL 입력을 먼저 시도해보고, 실패하면 직접 텍스트 입력을 사용하세요."
)

# URL input
if input_method == "🌐 URL 입력":
    url = st.text_input(
        "Job Posting URL",
        placeholder="https://example.com/job-posting",
        label_visibility="collapsed",
        key="job_url_input"
    )
    direct_text = ""
    job_title_input = ""
else:
    # Direct text input option
    st.markdown("### 📝 직접 텍스트 입력")
    st.info("💡 **팁**: 채용 공고 내용을 브라우저에서 복사하여 아래에 붙여넣기하세요.")
    
    direct_text = st.text_area(
        "채용 공고 내용을 직접 입력하세요",
        placeholder="채용 공고의 전체 내용을 여기에 복사하여 붙여넣기하세요...",
        height=300,
        help="URL에서 텍스트 추출이 실패하거나 동적 콘텐츠인 경우 이 옵션을 사용하세요.",
        key="direct_text_input"
    )
    job_title_input = st.text_input(
        "채용 공고 제목 (선택사항)",
        placeholder="예: AI/NLP 엔지니어 채용",
        help="채용 공고의 제목을 입력하면 더 정확한 분석이 가능합니다.",
        key="job_title_input"
    )
    url = ""

job_text = ""
job_title = ""

# Process text input (URL or direct text)
if url or direct_text:
    if url:
        extracted_text, headings = extract_text_from_url(url)
        
        if extracted_text:
            job_text = extracted_text
            if headings:
                job_title = headings[0] if headings else "No Title"
        else:
            st.warning("⚠️ URL에서 텍스트를 추출할 수 없습니다. 직접 텍스트 입력을 사용해주세요.")
            job_text = ""
            job_title = ""
    
    elif direct_text:
        job_text = direct_text
        job_title = job_title_input if job_title_input else "직접 입력된 채용 공고"
    
    # Analyze if we have text and user profile
    if job_text and user_context:
        with st.spinner("Performing matching analysis..."):
            # Calculate matching score
            # API 키를 매칭 계산에도 전달 (Additional Notes AI 분석용)
            match_score = calculate_match_score(user_context, job_text, st.session_state.get('openai_api_key'))
            
            # Generate feedback with user's API key
            feedback = generate_job_feedback(user_context, job_text, match_score, job_title, st.session_state.get('openai_api_key'))
        
        st.subheader("Analysis Results")
        
        # Display overall matching score and assessment
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("<div style='margin-bottom: 0;'><strong>Overall Match Score</strong></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 24px; font-weight: bold; margin-top: 0;'>{match_score['overall_score']}%</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-bottom: 2px;'><strong>Overall Assessment</strong></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 14px; margin-top: 0;'>{feedback['overall_assessment']}</div>", unsafe_allow_html=True)
        
        # Display detailed analysis in one line with vertical bars
        detailed_items = []
        # 제외할 항목들
        excluded_keys = ['language_requirement', 'education_match', 'additional_notes_match']
        
        for key, value in match_score['detailed_scores'].items():
            if key not in excluded_keys:
                # Format key names (remove underscores and capitalize)
                formatted_key = key.replace('_', ' ').title()
                detailed_items.append(f"<strong>{formatted_key}</strong>: {value:.2f}%")
        
        st.markdown(f"<p style='margin: 8px 0 2px 0; font-size: 14px;'> {' | '.join(detailed_items)}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Strengths, improvements, and recommendations in single column
        st.markdown("<div style='margin-bottom: 2px;'><strong>Strengths</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 14px; margin-top: 0; margin-bottom: 8px;'>{feedback['strengths']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 2px;'><strong>Areas for Improvement</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 14px; margin-top: 0; margin-bottom: 8px;'>{feedback['improvements']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 2px;'><strong>Recommendations</strong></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 14px; margin-top: 0; margin-bottom: 8px;'>{feedback['recommendations']}</div>", unsafe_allow_html=True)
        
        # Action Plan 표시 (있는 경우)
        if feedback.get('action_plan'):
            st.markdown("<div style='margin-bottom: 2px;'><strong>Action Plan</strong></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 14px; margin-top: 0; margin-bottom: 8px;'>{feedback['action_plan']}</div>", unsafe_allow_html=True)
        
        # Show API key status
        if not st.session_state.get('openai_api_key'):
            st.info("💡 **Tip**: Enter your OpenAI API key above to get more detailed AI-powered feedback!")
    
    elif job_text and not user_context:
        st.warning("Please select a user profile from the sidebar for analysis.")
    
    elif not job_text:
        st.info("채용 공고 URL을 입력하거나 직접 텍스트를 입력해주세요.")

else:
    st.info("채용 공고 URL을 입력하거나 직접 텍스트를 입력해주세요.") 