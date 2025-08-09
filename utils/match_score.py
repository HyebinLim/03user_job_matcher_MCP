import re
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from utils.mcp_schema import UserContext
from openai import OpenAI

class JobMatcher:
    def __init__(self, api_key: Optional[str] = None):
        """매칭 점수 계산을 위한 클래스 초기화"""
        # 임베딩 모델 로드 (한국어 지원)
        try:
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except:
            # 모델 로드 실패시 기본값 설정
            self.model = None
            print("Warning: Sentence transformer model could not be loaded")
        
        # OpenAI client 초기화 (Additional Notes AI 분석용)
        self.openai_client = None
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                print("[DEBUG] OpenAI client initialized for additional notes analysis")
            except Exception as e:
                print(f"[DEBUG] Failed to initialize OpenAI client: {e}")
                self.openai_client = None
    
    def calculate_keyword_score(self, user_context: UserContext, job_text: str) -> Dict[str, float]:
        """키워드 규칙 기반 점수 계산"""
        job_lower = job_text.lower()
        scores = {}
        
        # 1. 기술 스택 매칭 (25% 가중치)
        skill_matches = []
        all_user_skills = []
        
        # Skills와 Programming Languages를 모두 합쳐서 기술 스택으로 취급
        if user_context.skills:
            all_user_skills.extend(user_context.skills)
        if user_context.programming_languages:
            all_user_skills.extend(user_context.programming_languages)
        
        # 강화된 키워드 매칭 - 여러 표기법과 유사어 고려
        for skill in all_user_skills:
            skill_lower = skill.lower()
            
            # 기본 매칭
            if skill_lower in job_lower:
                skill_matches.append(skill)
            else:
                # 확장된 키워드 매칭 (유사어, 다른 표기법)
                skill_variations = self._get_skill_variations(skill_lower)
                for variation in skill_variations:
                    if variation in job_lower:
                        skill_matches.append(skill)
                        break
        
        skill_score = len(skill_matches) / len(all_user_skills) if all_user_skills else 0
        scores['skill_match'] = skill_score * 0.25
        
        print(f"[DEBUG] All user skills: {all_user_skills}")
        print(f"[DEBUG] Skill matches found: {skill_matches}")
        print(f"[DEBUG] Skill match rate: {skill_score} ({len(skill_matches)}/{len(all_user_skills)})")
        
        # 2. 직무/역할 매칭 (30% 가중치) - AI 기반으로 개선
        role_score = self._calculate_role_match_score(user_context, job_text)
        scores['role_match'] = role_score * 0.3
        
        # 3. 경력 요구사항 체크 (15% 가중치)
        # 경력 요구사항 패턴 찾기 (예: "3+ years", "5년 이상" 등)
        experience_patterns = [
            r'(\d+)\+?\s*years?',  # 3+ years, 5 years
            r'(\d+)년\s*이상',     # 3년 이상
            r'(\d+)년\s*경력',     # 3년 경력
        ]
        
        required_years = 0
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_lower)
            if matches:
                required_years = max(int(match) for match in matches)
                break
        
        if required_years == 0:
            experience_score = 0.5  # 경력 요구사항이 명시되지 않은 경우 중간 점수
        else:
            # 전체 경력 계산 (산업별 경력 합계)
            total_experience = sum(user_context.experience_by_industry.values()) if user_context.experience_by_industry else 0
            experience_score = min(1.0, total_experience / required_years)
        
        scores['experience_match'] = experience_score * 0.15
        
        # 4. 언어 요구사항 체크 (10% 가중치)
        language_score = 0
        for lang, level in user_context.languages.items():
            if lang.lower() in job_lower or level.lower() in job_lower:
                language_score = 1.0
                break
        
        scores['language_requirement'] = language_score * 0.1
        
        # 5. 교육/학위 매칭 (10% 가중치)
        education_score = 0
        education_keywords = [
            user_context.education_level.lower() if user_context.education_level else "",
            user_context.major.lower() if user_context.major else "",
            user_context.university.lower() if user_context.university else ""
        ]
        
        for edu_keyword in education_keywords:
            if edu_keyword and edu_keyword in job_lower:
                education_score = 1.0
                break
        
        # 일반적인 학위 키워드도 체크
        degree_keywords = ['bachelor', 'master', 'phd', '학사', '석사', '박사', '대학교', '대학원']
        if not education_score:
            for keyword in degree_keywords:
                if keyword in job_lower:
                    if user_context.education_level and any(deg in user_context.education_level.lower() for deg in ['bachelor', 'master', 'phd', '학사', '석사', '박사']):
                        education_score = 0.7
                        break
        
        scores['education_match'] = education_score * 0.1
        
        # 6. Additional Notes 기반 AI 매칭 (10% 가중치)
        additional_score = self._calculate_additional_notes_score(user_context, job_text)
        scores['additional_notes_match'] = additional_score * 0.1
        
        return scores
    
    def _get_skill_variations(self, skill_lower: str) -> List[str]:
        """스킬의 다양한 표기법과 유사어를 반환"""
        variations = set()
        
        # 공통 매핑 사전
        skill_mapping = {
            # 프로그래밍 언어
            'python': ['파이썬', 'python3', 'python2'],
            'javascript': ['js', '자바스크립트', 'java script', 'ecmascript'],
            'java': ['자바'],
            'sql': ['에스큐엘', 'structured query language', 'sequel'],
            'r': ['r language', 'r programming'],
            'c++': ['cpp', 'c plus plus', 'cplusplus'],
            'c#': ['csharp', 'c sharp'],
            'golang': ['go', 'go language'],
            'php': ['php7', 'php8'],
            
            # AI/ML/Data 기술
            'rag': ['retrieval augmented generation', '검색 증강 생성', 'retrieval-augmented generation'],
            'mcp': ['model context protocol'],
            'llm': ['large language model', '대형 언어 모델', 'large language models'],
            'nlp': ['natural language processing', '자연어 처리', 'natural language'],
            'transformers': ['transformer', 'huggingface transformers', 'transformer models'],
            'pytorch': ['torch', 'pytorch framework'],
            'tensorflow': ['tf', 'tensor flow', 'tensorflow2'],
            'scikit-learn': ['sklearn', 'scikit learn', 'sci-kit learn'],
            'opencv': ['cv2', 'open cv', 'computer vision'],
            'pandas': ['pd', 'pandas dataframe'],
            'numpy': ['np', 'numerical python'],
            
            # 클라우드/인프라
            'aws': ['amazon web services', 'amazon aws'],
            'gcp': ['google cloud platform', 'google cloud'],
            'azure': ['microsoft azure', 'azure cloud'],
            'docker': ['containerization', '도커'],
            'kubernetes': ['k8s', 'k8', '쿠버네티스'],
            
            # 데이터베이스
            'mysql': ['my sql', 'mysql database'],
            'postgresql': ['postgres', 'postgre sql', 'postgresql database'],
            'mongodb': ['mongo db', 'mongo database'],
            'redis': ['redis database', 'redis cache'],
            
            # 도구/프레임워크
            'power bi': ['powerbi', '파워 BI', '파워비아이', 'microsoft power bi'],
            'excel': ['엑셀', 'microsoft excel', 'ms excel', 'excel spreadsheet'],
            'tableau': ['tableau desktop', 'tableau public'],
            'git': ['github', 'git version control', 'version control'],
            'react': ['reactjs', 'react.js', 'react framework'],
            'vue': ['vuejs', 'vue.js', 'vue framework'],
            'angular': ['angularjs', 'angular framework'],
            'node.js': ['nodejs', 'node js', 'node'],
            'django': ['django framework', 'django python'],
            'flask': ['flask framework', 'flask python'],
            'fastapi': ['fast api', 'fastapi framework'],
            
            # 기타
            'api': ['rest api', 'restful api', 'web api'],
            'html': ['html5', 'hypertext markup language'],
            'css': ['css3', 'cascading style sheets'],
            'json': ['javascript object notation'],
            'xml': ['extensible markup language'],
        }
        
        # 매핑에서 찾기
        if skill_lower in skill_mapping:
            variations.update(skill_mapping[skill_lower])
        
        # 역방향 매핑 (값에서 키 찾기)
        for key, values in skill_mapping.items():
            if skill_lower in values:
                variations.add(key)
                variations.update(values)
        
        # 기본 변형 패턴
        variations.add(skill_lower.replace(' ', ''))  # 공백 제거
        variations.add(skill_lower.replace('-', ''))  # 하이픈 제거
        variations.add(skill_lower.replace('_', ''))  # 언더스코어 제거
        variations.add(skill_lower.replace('.', ''))  # 점 제거
        
        # 원본 스킬 제거
        variations.discard(skill_lower)
        
        return list(variations)
    
    def _calculate_role_match_score(self, user_context: UserContext, job_text: str) -> float:
        """직무/역할 매칭 스코어 계산 (AI 기반 + 키워드 fallback)"""
        if not user_context.target_roles:
            return 0.0
        
        # AI가 있으면 AI 분석, 없으면 키워드 기반 fallback
        if self.openai_client:
            return self._ai_analyze_role_match(user_context.target_roles, job_text)
        else:
            return self._keyword_analyze_role_match(user_context.target_roles, job_text)
    
    def _ai_analyze_role_match(self, target_roles: List[str], job_text: str) -> float:
        """AI를 활용한 역할 매칭 분석"""
        try:
            prompt = f"""
사용자가 원하는 직무와 채용 공고의 직무 간 매칭도를 0-1 사이의 점수로 평가해주세요.

**사용자 희망 직무:**
{', '.join(target_roles)}

**채용 공고 (일부):**
{job_text[:1500]}

평가 기준:
1. 직무명이 정확히 일치하지 않아도 업무 내용이나 요구 역량이 유사한가?
2. 사용자가 원하는 직무의 핵심 업무와 공고의 업무가 얼마나 관련성이 있는가?
3. 커리어 발전 경로상 연관성이 있는가?

예: "NLP Engineer"와 "AI Research Scientist"는 높은 관련성
예: "Data Scientist"와 "Machine Learning Engineer"는 높은 관련성
예: "Frontend Developer"와 "Backend Developer"는 중간 관련성

응답 형식: 숫자만 반환 (예: 0.8)
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor. Analyze the relevance between user's target roles and job posting. Consider semantic similarity, not just exact keyword matches. Return only a number between 0 and 1."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # 숫자 추출
            import re
            numbers = re.findall(r'0?\.\d+|0|1', score_text)
            if numbers:
                score = float(numbers[0])
                score = max(0.0, min(1.0, score))  # 0-1 범위 강제
                print(f"[DEBUG] AI Role Match Score: {score}")
                return score
            else:
                print(f"[DEBUG] AI returned invalid role score: {score_text}")
                return self._keyword_analyze_role_match(target_roles, job_text)
                
        except Exception as e:
            print(f"[DEBUG] AI role analysis failed: {e}")
            return self._keyword_analyze_role_match(target_roles, job_text)
    
    def _keyword_analyze_role_match(self, target_roles: List[str], job_text: str) -> float:
        """키워드 기반 역할 매칭 (AI 없을 때 fallback)"""
        job_lower = job_text.lower()
        role_matches = []
        
        for role in target_roles:
            if role.lower() in job_lower:
                role_matches.append(role)
        
        role_score = len(role_matches) / len(target_roles) if target_roles else 0
        print(f"[DEBUG] Keyword Role Match Score: {role_score}")
        return role_score
    
    def _calculate_additional_notes_score(self, user_context: UserContext, job_text: str) -> float:
        """Additional Notes AI 기반 매칭 스코어 계산"""
        if not user_context.additional_notes or not user_context.additional_notes.strip():
            return 0.0
        
        # AI가 있으면 AI 분석, 없으면 키워드 기반 fallback
        if self.openai_client:
            return self._ai_analyze_additional_notes(user_context.additional_notes, job_text)
        else:
            return self._keyword_analyze_additional_notes(user_context.additional_notes, job_text)
    
    def _ai_analyze_additional_notes(self, additional_notes: str, job_text: str) -> float:
        """AI를 활용한 Additional Notes 분석"""
        try:
            prompt = f"""
사용자의 추가 정보와 채용 공고 간의 매칭도를 0-1 사이의 점수로 평가해주세요.

**사용자 추가 정보:**
{additional_notes}

**채용 공고 (일부):**
{job_text[:1500]}

평가 기준:
1. 사용자의 관심사, 경험, 목표가 채용 공고의 요구사항이나 업무 내용과 얼마나 관련성이 있는가?
2. 사용자가 언급한 프로젝트, 기술, 경험이 해당 직무에 얼마나 적합한가?
3. 사용자의 커리어 목표나 관심 분야가 해당 회사/직무와 얼마나 일치하는가?

응답 형식: 숫자만 반환 (예: 0.7)
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor. Analyze the relevance between user's additional notes and job posting. Return only a number between 0 and 1."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # 숫자 추출
            import re
            numbers = re.findall(r'0?\.\d+|0|1', score_text)
            if numbers:
                score = float(numbers[0])
                score = max(0.0, min(1.0, score))  # 0-1 범위 강제
                print(f"[DEBUG] AI Additional Notes Score: {score}")
                return score
            else:
                print(f"[DEBUG] AI returned invalid score: {score_text}")
                return self._keyword_analyze_additional_notes(additional_notes, job_text)
                
        except Exception as e:
            print(f"[DEBUG] AI additional notes analysis failed: {e}")
            return self._keyword_analyze_additional_notes(additional_notes, job_text)
    
    def _keyword_analyze_additional_notes(self, additional_notes: str, job_text: str) -> float:
        """키워드 기반 Additional Notes 분석 (AI 없을 때 fallback)"""
        additional_notes_lower = additional_notes.lower()
        job_lower = job_text.lower()
        
        # Additional Notes의 키워드들을 공고와 비교
        notes_keywords = re.findall(r'\b\w+\b', additional_notes_lower)
        job_keywords = re.findall(r'\b\w+\b', job_lower)
        
        if notes_keywords and job_keywords:
            # 교집합 비율 계산
            common_keywords = set(notes_keywords) & set(job_keywords)
            additional_score = len(common_keywords) / len(set(notes_keywords)) if notes_keywords else 0
            additional_score = min(1.0, additional_score * 2)  # 가중치 적용
            print(f"[DEBUG] Keyword Additional Notes Score: {additional_score}")
            return additional_score
        
        return 0.0
    
    def calculate_embedding_similarity(self, user_context: UserContext, job_text: str) -> float:
        """임베딩 유사도 계산"""
        if not self.model:
            print("[DEBUG] Sentence transformer model not available, using keyword-based fallback")
            # 모델이 없으면 키워드 기반 유사도 계산
            return self._calculate_keyword_similarity_fallback(user_context, job_text)
        
        try:
            # 사용자 컨텍스트를 텍스트로 변환
            user_text = self._context_to_text(user_context)
            
            # 임베딩 계산
            user_embedding = self.model.encode([user_text])
            job_embedding = self.model.encode([job_text])
            
            # 코사인 유사도 계산
            similarity = np.dot(user_embedding[0], job_embedding[0]) / (
                np.linalg.norm(user_embedding[0]) * np.linalg.norm(job_embedding[0])
            )
            
            return float(similarity)
            
        except Exception as e:
            print(f"[DEBUG] Embedding similarity calculation failed: {e}")
            return self._calculate_keyword_similarity_fallback(user_context, job_text)
    
    def _calculate_keyword_similarity_fallback(self, user_context: UserContext, job_text: str) -> float:
        """임베딩 모델이 없을 때 키워드 기반 유사도 계산"""
        user_text = self._context_to_text(user_context)
        
        # 사용자 텍스트와 공고 텍스트를 단어 단위로 분리
        user_words = set(re.findall(r'\b\w+\b', user_text.lower()))
        job_words = set(re.findall(r'\b\w+\b', job_text.lower()))
        
        # 자카드 유사도 계산
        if not user_words or not job_words:
            return 0.0
        
        intersection = user_words & job_words
        union = user_words | job_words
        
        similarity = len(intersection) / len(union) if union else 0.0
        return min(1.0, similarity * 3)  # 0-1 범위로 정규화
    
    def _context_to_text(self, user_context: UserContext) -> str:
        """사용자 컨텍스트를 텍스트로 변환"""
        text_parts = []
        
        text_parts.append(f"Target roles: {', '.join(user_context.target_roles)}")
        
        # 경력 정보
        if user_context.experience_by_industry:
            experience_text = ", ".join([f"{industry}({years}년)" for industry, years in user_context.experience_by_industry.items()])
            text_parts.append(f"Experience: {experience_text}")
        
        text_parts.append(f"Skills: {', '.join(user_context.skills)}")
        
        if user_context.programming_languages:
            text_parts.append(f"Programming languages: {', '.join(user_context.programming_languages)}")
        
        text_parts.append(f"Languages: {', '.join([f'{lang}({level})' for lang, level in user_context.languages.items()])}")
        text_parts.append(f"Work preference: {', '.join(user_context.work_preference)}")
        
        if user_context.education_level:
            text_parts.append(f"Education: {user_context.education_level} in {user_context.major}")
        
        if user_context.projects:
            project_texts = []
            for project in user_context.projects:
                if isinstance(project, dict):
                    project_info = project.get('name', '')
                    if project.get('description'):
                        project_info += f": {project.get('description', '')}"
                    if project.get('tech_stack'):
                        project_info += f" (기술: {project.get('tech_stack', '')})"
                    if project.get('organization'):
                        project_info += f" @ {project.get('organization', '')}"
                    project_texts.append(project_info)
                else:
                    project_texts.append(str(project))
            text_parts.append(f"Projects: {', '.join(project_texts)}")
        
        if user_context.certifications:
            text_parts.append(f"Certifications: {', '.join(user_context.certifications)}")
        
        if user_context.location_preference:
            text_parts.append(f"Location preference: {', '.join(user_context.location_preference)}")
        
        if user_context.additional_notes:
            text_parts.append(f"Additional notes: {user_context.additional_notes}")
        
        return " ".join(text_parts)
    
    def calculate_overall_score(self, user_context: UserContext, job_text: str) -> Dict[str, any]:
        """전체 매칭 점수 계산"""
        # 키워드 기반 점수 계산
        keyword_scores = self.calculate_keyword_score(user_context, job_text)
        keyword_total = sum(keyword_scores.values())
        
        # 임베딩 유사도 계산
        embedding_similarity = self.calculate_embedding_similarity(user_context, job_text)
        
        # 최종 점수 계산 (키워드 70% + 임베딩 30%)
        final_score = (keyword_total * 0.7) + (embedding_similarity * 0.3)
        
        # 디버깅 정보 출력
        print(f"[DEBUG] Keyword scores: {keyword_scores}")
        print(f"[DEBUG] Keyword total: {keyword_total}")
        print(f"[DEBUG] Embedding similarity: {embedding_similarity}")
        print(f"[DEBUG] Final score: {final_score}")
        print(f"[DEBUG] Model loaded: {self.model is not None}")
        
        return {
            'overall_score': round(final_score * 100, 1),  # 백분율로 변환
            'keyword_score': round(keyword_total * 100, 1),
            'embedding_similarity': round(embedding_similarity * 100, 1),
            'detailed_scores': keyword_scores,
            'matched_skills': self._get_matched_skills(user_context, job_text),
            'missing_skills': self._get_missing_skills(user_context, job_text)
        }
    
    def _get_matched_skills(self, user_context: UserContext, job_text: str) -> List[str]:
        """매칭된 스킬 목록 반환 (강화된 키워드 매칭 사용)"""
        job_lower = job_text.lower()
        matched = []
        all_user_skills = []
        
        # 모든 스킬 통합
        if user_context.skills:
            all_user_skills.extend(user_context.skills)
        if user_context.programming_languages:
            all_user_skills.extend(user_context.programming_languages)
        
        # 강화된 키워드 매칭으로 매칭된 스킬 찾기
        for skill in all_user_skills:
            skill_lower = skill.lower()
            skill_matched = False
            
            # 기본 매칭
            if skill_lower in job_lower:
                matched.append(skill)
                skill_matched = True
            else:
                # 확장된 키워드 매칭
                skill_variations = self._get_skill_variations(skill_lower)
                for variation in skill_variations:
                    if variation in job_lower:
                        matched.append(skill)
                        skill_matched = True
                        break
        
        return matched
    
    def _get_missing_skills(self, user_context: UserContext, job_text: str) -> List[str]:
        """공고에서 요구하지만 사용자가 없는 스킬 목록"""
        # AI가 있으면 AI 분석, 없으면 키워드 기반 fallback
        if self.openai_client:
            return self._ai_analyze_missing_skills(user_context, job_text)
        else:
            return self._keyword_analyze_missing_skills(user_context, job_text)
    
    def _ai_analyze_missing_skills(self, user_context: UserContext, job_text: str) -> List[str]:
        """AI를 사용해서 부족한 스킬을 분석"""
        try:
            # 사용자 스킬 통합
            user_all_skills = []
            if user_context.skills:
                user_all_skills.extend(user_context.skills)
            if user_context.programming_languages:
                user_all_skills.extend(user_context.programming_languages)
            
            prompt = f"""
다음 채용 공고에서 요구하는 기술들 중에서 사용자가 보유하지 않은 기술들을 찾아주세요.

**사용자 보유 기술:**
{', '.join(user_all_skills) if user_all_skills else '없음'}

**채용 공고 (일부):**
{job_text[:1500]}

중요한 지침:
1. 채용 공고에서 명시적으로 요구하거나 언급된 기술들을 식별하세요
2. 사용자가 이미 보유한 기술은 절대 포함하지 마세요
3. 유사한 기술은 같은 것으로 취급하세요:
   - "RAG" = "Retrieval Augmented Generation" = "검색 증강 생성"
   - "MCP" = "Model Context Protocol" 
   - "Power BI" = "PowerBI" = "파워 BI"
   - "Excel" = "엑셀" = "Microsoft Excel"
   - "Python" = "파이썬"
   - "SQL" = "에스큐엘" = "Structured Query Language"
4. 대소문자나 표기법이 다른 경우도 같은 기술로 취급하세요
5. 사용자가 보유한 기술과 겹치는 것은 절대 "부족한 기술"로 분류하지 마세요

응답 형식: 콤마로 구분된 기술 이름만 반환 (예: Docker, Kubernetes, React)
사용자가 필요한 기술을 모두 보유했다면 "없음"이라고 반환하세요.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter. Analyze job postings to identify required skills that candidates lack. Be precise and avoid false positives."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            print(f"[DEBUG] AI missing skills analysis: {result}")
            
            if result.lower() in ['없음', 'none', 'no missing skills']:
                return []
            
            # 콤마로 분리하고 정리
            missing_skills = [skill.strip() for skill in result.split(',') if skill.strip()]
            missing_skills = missing_skills[:5]  # 최대 5개
            
            print(f"[DEBUG] AI identified missing skills: {missing_skills}")
            return missing_skills
            
        except Exception as e:
            print(f"[DEBUG] AI missing skills analysis failed: {e}")
            return self._keyword_analyze_missing_skills(user_context, job_text)
    
    def _keyword_analyze_missing_skills(self, user_context: UserContext, job_text: str) -> List[str]:
        """키워드 기반 부족한 스킬 분석 (강화된 키워드 매칭 사용)"""
        job_lower = job_text.lower()
        
        # 사용자의 모든 스킬 통합
        user_all_skills = []
        if user_context.skills:
            user_all_skills.extend(user_context.skills)
        if user_context.programming_languages:
            user_all_skills.extend(user_context.programming_languages)
        
        print(f"[DEBUG] User skills (keyword fallback): {user_all_skills}")
        
        # 핵심 기술들과 변형 확인
        core_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'R', 'TensorFlow', 'PyTorch', 
            'AWS', 'Docker', 'Kubernetes', 'React', 'Vue.js', 'Node.js', 
            'MongoDB', 'PostgreSQL', 'MySQL', 'RAG', 'MCP', 'Power BI', 'Excel'
        ]
        
        missing = []
        for skill in core_skills:
            skill_lower = skill.lower()
            
            # 공고에 이 스킬이 언급되어 있는지 확인
            skill_mentioned = False
            if skill_lower in job_lower:
                skill_mentioned = True
            else:
                # 변형 확인
                variations = self._get_skill_variations(skill_lower)
                for variation in variations:
                    if variation in job_lower:
                        skill_mentioned = True
                        break
            
            if skill_mentioned:
                # 사용자가 이 스킬을 보유하고 있는지 확인
                user_has_skill = False
                for user_skill in user_all_skills:
                    user_skill_lower = user_skill.lower()
                    if (user_skill_lower == skill_lower or 
                        skill_lower in self._get_skill_variations(user_skill_lower) or
                        user_skill_lower in self._get_skill_variations(skill_lower)):
                        user_has_skill = True
                        break
                
                if not user_has_skill:
                    missing.append(skill)
                    print(f"[DEBUG] Keyword missing skill found: {skill}")
        
        print(f"[DEBUG] Keyword final missing skills: {missing}")
        return missing[:5]

# 전역 인스턴스 (API 키 없이)
_global_matcher = JobMatcher()

def calculate_match_score(user_context: UserContext, job_text: str, api_key: Optional[str] = None) -> Dict[str, any]:
    """매칭 점수 계산 함수 (외부에서 호출용)"""
    if api_key:
        # API 키가 있으면 새로운 인스턴스 생성 (AI 분석 포함)
        matcher = JobMatcher(api_key=api_key)
        return matcher.calculate_overall_score(user_context, job_text)
    else:
        # API 키가 없으면 전역 인스턴스 사용 (키워드 기반)
        return _global_matcher.calculate_overall_score(user_context, job_text) 