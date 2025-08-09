import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class UserContext:
    # Basic Information
    name: str
    target_roles: List[str]  # e.g., ["NLP Engineer", "AI Research Assistant"]
    skills: List[str]  # e.g., ["Python", "Transformers", "PyTorch"]
    programming_languages: List[str]  # e.g., ["Python", "JavaScript", "SQL"]
    languages: Dict[str, str]  # e.g., {"Korean": "Native", "English": "Fluent"}
    work_preference: List[str]  # e.g., ["Remote", "Hybrid", "On-site"]
    
    # Optional fields with default values
    email: str = ""
    current_position: str = ""
    current_role: str = ""  # 현재 직무
    current_company: str = ""
    education_level: str = ""  # e.g., "학사", "석사", "박사"
    major: str = ""
    university: str = ""  # e.g., "서울대학교", "연세대학교"
    graduation_year: int = 0
    experience_by_industry: Dict[str, int] = None  # e.g., {"AI/NLP": 2, "투자은행": 7} - 기존 호환성
    experience_details: List[Dict[str, any]] = None  # e.g., [{"industry": "AI/NLP", "role": "NLP Engineer", "years": 2.5}]
    projects: List[Dict[str, str]] = None  # e.g., [{"name": "챗봇 개발", "description": "...", "tech_stack": "...", "organization": "..."}]
    certifications: List[str] = None  # e.g., ["AWS Certified", "Google Cloud"]
    location_preference: List[str] = None  # e.g., ["서울", "뉴욕", "런던"]
    salary_expectation: str = ""  # e.g., "50M-70M KRW", "100K-150K USD"
    additional_notes: str = ""  # Free text field for additional information
    
    def __post_init__(self):
        # Initialize empty lists if None
        if self.programming_languages is None:
            self.programming_languages = []
        if self.location_preference is None:
            self.location_preference = []
        if self.projects is None:
            self.projects = []
        if self.certifications is None:
            self.certifications = []
        if self.experience_by_industry is None:
            self.experience_by_industry = {}
        if self.experience_details is None:
            self.experience_details = []

    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserContext':
        # 기존 데이터와의 호환성을 위한 처리
        processed_data = data.copy()
        
        # experience_years를 experience_by_industry로 변환
        if 'experience_years' in processed_data and 'experience_by_industry' not in processed_data:
            experience_years = processed_data.pop('experience_years')
            if experience_years > 0:
                processed_data['experience_by_industry'] = {"일반": experience_years}
            else:
                processed_data['experience_by_industry'] = {}
        
        # frameworks 필드가 있으면 제거 (새 스키마에서는 제거됨)
        if 'frameworks' in processed_data:
            processed_data.pop('frameworks')
        
        # extra_notes를 additional_notes로 변환 (새 스키마에서는 이름이 변경됨)
        if 'extra_notes' in processed_data and 'additional_notes' not in processed_data:
            processed_data['additional_notes'] = processed_data.pop('extra_notes')
        
        # 필수 필드가 없으면 기본값 설정
        if 'programming_languages' not in processed_data:
            processed_data['programming_languages'] = []
        
        if 'languages' not in processed_data:
            processed_data['languages'] = {"한국어": "Native", "영어": "Fluent"}
        
        if 'work_preference' not in processed_data:
            processed_data['work_preference'] = ["Remote", "Hybrid"]
        
        if 'projects' not in processed_data:
            processed_data['projects'] = []
        else:
            # 기존 문자열 리스트를 딕셔너리 리스트로 변환
            if processed_data['projects'] and isinstance(processed_data['projects'][0], str):
                processed_data['projects'] = [
                    {"name": project, "description": "", "tech_stack": "", "organization": ""} 
                    for project in processed_data['projects']
                ]
        
        if 'certifications' not in processed_data:
            processed_data['certifications'] = []
        
        if 'location_preference' not in processed_data:
            processed_data['location_preference'] = []
        
        if 'experience_by_industry' not in processed_data:
            processed_data['experience_by_industry'] = {}
        
        if 'university' not in processed_data:
            processed_data['university'] = ""
        
        if 'additional_notes' not in processed_data:
            processed_data['additional_notes'] = ""
        
        return cls(**processed_data)

def save_user_context(context: UserContext, filename: str = None) -> str:
    """사용자 context를 JSON 파일로 저장"""
    if filename is None:
        filename = f"{context.name.replace(' ', '_')}_context.json"
    
    data_dir = "data/user_contexts"
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
    
    return filepath

def load_user_context(filename: str) -> Optional[UserContext]:
    """JSON 파일에서 사용자 context 로드"""
    data_dir = "data/user_contexts"
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return UserContext.from_dict(data)

def list_saved_contexts() -> List[str]:
    """저장된 context 파일 목록 반환"""
    data_dir = "data/user_contexts"
    if not os.path.exists(data_dir):
        return []
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    return files

def get_default_context() -> UserContext:
    """기본 사용자 context 반환"""
    return UserContext(
        name="",
        target_roles=[],
        skills=[],
        programming_languages=[],
        languages={"한국어": "Native", "영어": "Fluent"},
        work_preference=["Remote", "Hybrid"]
    ) 