import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from utils.mcp_schema import UserContext

class FeedbackGenerator:
    def __init__(self, api_key: str = None):
        """피드백 생성기 초기화"""
        # OpenAI API 키 확인 (환경변수 또는 직접 전달된 키)
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # 환경변수에서 확인
            env_api_key = os.getenv('OPENAI_API_KEY')
            if env_api_key:
                self.client = OpenAI(api_key=env_api_key)
            else:
                self.client = None
                print("Warning: OpenAI API key not found. Feedback generation will be limited.")
    
    def generate_feedback(self, user_context: UserContext, job_text: str, 
                         match_score: Dict, job_title: str = "") -> Dict[str, str]:
        """GPT를 사용하여 매칭 피드백 생성"""
        
        if not self.client:
            return self._generate_basic_feedback(user_context, job_text, match_score, job_title)
        
        try:
            # 프롬프트 구성
            prompt = self._create_feedback_prompt(user_context, job_text, match_score, job_title)
            
            # GPT API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
  "role": "system",
  "content": "채용공고의 구체적 요구사항을 인용하여 사용자의 실제 보유 역량과 비교해 평가하고, 키워드나 기술 용어 없이, 이미 가진 역량은 부족하다고 하지 않으며, 제공된 키워드 분석 요약을 근거로 3~5개의 짧고 구체적인 실행계획을 제시하라."
}
,
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            feedback_text = response.choices[0].message.content
            
            # 피드백을 구조화된 형태로 파싱
            structured_feedback = self._parse_feedback(feedback_text, match_score)
            
            return structured_feedback
            
        except Exception as e:
            print(f"GPT API 호출 실패: {e}")
            return self._generate_basic_feedback(user_context, job_text, match_score, job_title)
    
    def _create_feedback_prompt(self, user_context: UserContext, job_text: str, 
                               match_score: Dict, job_title: str) -> str:
        """피드백 생성을 위한 프롬프트 생성"""
        
        # 키워드 매칭 결과로 사전 분석 요약 생성
        keyword_analysis = self._create_keyword_analysis_summary(match_score, job_text)
        
        prompt = f"""
다음 정보를 바탕으로 채용 공고와의 적합성에 대한 상세한 피드백을 제공해주세요.

**사용자 정보:**
- 이름: {user_context.name}
- 목표 직무: {', '.join(user_context.target_roles)}
- 경력: {', '.join([f'{industry}({years}년)' for industry, years in user_context.experience_by_industry.items()]) if user_context.experience_by_industry else '없음'}
- 주요 스킬: {', '.join(user_context.skills)}
- 프로그래밍 언어: {', '.join(user_context.programming_languages) if user_context.programming_languages else '없음'}
- 언어 능력: {', '.join([f'{lang}({level})' for lang, level in user_context.languages.items()])}
- 학위/전공: {user_context.education_level} {user_context.major if user_context.major else ''}
- 프로젝트: {self._format_projects(user_context.projects) if user_context.projects else '없음'}
- 자격증: {', '.join(user_context.certifications) if user_context.certifications else '없음'}
- 희망 지역: {', '.join(user_context.location_preference) if user_context.location_preference else '없음'}
- 근무 선호: {', '.join(user_context.work_preference)}
- 추가 정보: {user_context.additional_notes if user_context.additional_notes else '없음'}

**채용 공고:**
- 제목: {job_title if job_title else '제목 없음'}
- 내용: {job_text[:1500]}

**사전 분석 요약:**
{keyword_analysis}

**중요한 지침:**
1. 각 평가 항목은 반드시 채용 공고의 구체적인 요구조건과 직접 매칭해서 분석하세요
2. 사용자가 보유한 기술을 "부족하다"고 절대 표현하지 마세요
3. 기술적 용어(키워드 매칭, 임베딩 유사도, 매칭 스코어 등)는 절대 사용하지 마세요
4. Action Plan은 짧고 구체적인 행동 단계로만 제한하세요 (포괄적 조언 금지)

다음 형식으로 피드백을 제공해주세요:

**전체 평가:**
[채용 공고의 요구조건 대비 사용자 적합성을 구체적으로 평가]

**강점:**
[공고에서 요구하는 조건 중 사용자가 충족하는 부분들을 명시적으로]

**개선점:**
[공고에서 요구하는 조건 중 사용자가 보완해야 할 부분들을 구체적으로]

**추천사항:**
[지원 여부 판단과 준비 방안을 명확하게]

**Action Plan:**
[3-5개의 짧고 구체적인 실행 단계만. "공부하세요", "경험 쌓으세요" 같은 포괄적 조언 금지]

**매칭 근거:**
[공고 요구조건과 사용자 역량의 구체적인 대응 관계]
"""
        return prompt
    
    def _create_keyword_analysis_summary(self, match_score: Dict, job_text: str) -> str:
        """키워드 매칭 결과를 요약하여 GPT에게 전달할 사전 분석 생성"""
        
        # 상세 점수에서 주요 항목 추출
        detailed_scores = match_score.get('detailed_scores', {})
        skill_match = detailed_scores.get('skill_match', 0) * 100
        role_match = detailed_scores.get('role_match', 0) * 100
        experience_match = detailed_scores.get('experience_match', 0) * 100
        
        # 매칭된 스킬과 부족한 스킬
        matched_skills = match_score.get('matched_skills', [])
        missing_skills = match_score.get('missing_skills', [])
        
        # 공고에서 언급된 주요 기술들 추출 (간단한 키워드 기반)
        job_lower = job_text.lower()
        mentioned_techs = []
        tech_keywords = [
            'python', 'java', 'javascript', 'sql', 'r', 'tensorflow', 'pytorch', 
            'aws', 'docker', 'kubernetes', 'react', 'vue', 'node.js', 'mongodb', 
            'postgresql', 'mysql', 'rag', 'mcp', 'power bi', 'excel', 'tableau',
            'machine learning', 'deep learning', 'ai', 'nlp', 'data science'
        ]
        
        for tech in tech_keywords:
            if tech in job_lower:
                mentioned_techs.append(tech)
        
        analysis = f"""
◎ 기술 스킬 매칭: {skill_match:.1f}%
  - 매칭된 기술: {', '.join(matched_skills) if matched_skills else '없음'}
  - 추가 필요 기술: {', '.join(missing_skills) if missing_skills else '없음'}

◎ 직무 역할 매칭: {role_match:.1f}%

◎ 경험 매칭: {experience_match:.1f}%

◎ 공고에서 언급된 주요 기술:
  {', '.join(mentioned_techs) if mentioned_techs else '특별히 언급된 기술 없음'}

◎ 전체 적합도: {match_score.get('overall_score', 0)}%
"""
        return analysis.strip()
    
    def _format_projects(self, projects: List) -> str:
        """프로젝트 목록을 포맷팅"""
        if not projects:
            return "없음"
        
        formatted_projects = []
        for project in projects:
            if isinstance(project, dict):
                project_info = project.get('name', '')
                if project.get('description'):
                    project_info += f": {project.get('description', '')}"
                if project.get('tech_stack'):
                    project_info += f" (기술: {project.get('tech_stack', '')})"
                if project.get('organization'):
                    project_info += f" @ {project.get('organization', '')}"
                formatted_projects.append(project_info)
            else:
                formatted_projects.append(str(project))
        
        return ', '.join(formatted_projects)
    
    def _parse_feedback(self, feedback_text: str, match_score: Dict) -> Dict[str, str]:
        """GPT 응답을 구조화된 피드백으로 파싱"""
        
        # 기본 구조
        structured = {
            'overall_assessment': '',
            'strengths': '',
            'improvements': '',
            'recommendations': '',
            'action_plan': '',
            'matching_evidence': '',
            'raw_feedback': feedback_text
        }
        
        # 섹션별로 파싱 시도
        sections = feedback_text.split('**')
        current_section = None
        
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
                
            if '전체 평가' in section:
                current_section = 'overall_assessment'
            elif '강점' in section:
                current_section = 'strengths'
            elif '개선점' in section:
                current_section = 'improvements'
            elif '추천사항' in section:
                current_section = 'recommendations'
            elif 'Action Plan' in section or '액션 플랜' in section or '실행 계획' in section:
                current_section = 'action_plan'
            elif '매칭 근거' in section:
                current_section = 'matching_evidence'
            elif current_section and i > 0:
                # 이전 섹션의 내용
                structured[current_section] = section
        
        # 파싱이 실패한 경우 전체 텍스트를 전체 평가에 넣기
        if not any(structured.values()):
            structured['overall_assessment'] = feedback_text
        
        return structured
    
    def _generate_basic_feedback(self, user_context: UserContext, job_text: str, 
                                match_score: Dict, job_title: str) -> Dict[str, str]:
        """GPT API 없이 기본 피드백 생성"""
        
        overall_score = match_score['overall_score']
        matched_skills = match_score['matched_skills']
        missing_skills = match_score['missing_skills']
        
        # 전체 평가
        if overall_score >= 80:
            assessment = f"매우 높은 매칭도({overall_score}%)를 보여주고 있습니다. 이 공고는 귀하의 경력과 스킬셋과 매우 잘 맞습니다."
        elif overall_score >= 60:
            assessment = f"양호한 매칭도({overall_score}%)를 보여주고 있습니다. 지원을 고려해볼 만한 수준입니다."
        elif overall_score >= 40:
            assessment = f"보통 수준의 매칭도({overall_score}%)입니다. 일부 요구사항을 충족하지만 추가 준비가 필요합니다."
        else:
            assessment = f"낮은 매칭도({overall_score}%)를 보여주고 있습니다. 이 공고는 현재 스킬셋과 큰 차이가 있습니다."
        
        # 강점
        strengths = []
        if matched_skills:
            strengths.append(f"보유하신 다음 기술들이 이 직무에 잘 맞습니다: {', '.join(matched_skills)}")
        if match_score['keyword_score'] > 60:
            strengths.append("현재 보유하신 기술 스택이 공고 요구사항과 잘 일치합니다.")
        if match_score['embedding_similarity'] > 60:
            strengths.append("전반적인 업무 경험과 이 직무의 내용이 잘 맞습니다.")
        
        strengths_text = "\n".join(strengths) if strengths else "특별한 강점이 보이지 않습니다."
        
        # 개선점
        improvements = []
        if missing_skills:
            improvements.append(f"이 직무에서 요구하는 추가 기술들을 학습하면 도움이 될 것 같습니다: {', '.join(missing_skills)}")
        if match_score['keyword_score'] < 50:
            improvements.append("현재 보유 기술과 공고에서 요구하는 기술 간 차이가 있어 보입니다. 관련 기술 학습을 고려해보세요.")
        if match_score['embedding_similarity'] < 50:
            improvements.append("현재 경력과 이 직무의 업무 내용이 다소 다른 방향으로 보입니다. 해당 분야 경험을 쌓아보시는 것을 추천합니다.")
        
        improvements_text = "\n".join(improvements) if improvements else "특별한 개선점이 없습니다."
        
        # 추천사항
        if overall_score >= 70:
            recommendations = "지원을 적극 권장합니다. 현재 스킬셋으로 충분히 경쟁력이 있습니다."
        elif overall_score >= 50:
            recommendations = "지원을 고려해볼 수 있습니다. 부족한 부분을 보완하면 좋은 기회가 될 수 있습니다."
        else:
            recommendations = "현재 매칭도가 낮아 지원을 권장하지 않습니다. 관련 기술이나 경험을 더 쌓은 후 재검토를 권장합니다."
        
        # Action Plan 생성
        action_plan = []
        if overall_score >= 70:
            action_plan = ["지원서 및 포트폴리오 준비", "면접 예상 질문 연습", "회사 리서치 진행"]
        elif overall_score >= 50:
            if missing_skills:
                action_plan.append(f"{missing_skills[0]} 학습 시작")
            action_plan.extend(["관련 프로젝트 1개 완성", "포트폴리오 업데이트", "지원서 작성"])
        else:
            if missing_skills:
                action_plan.append(f"{missing_skills[0]} 기초 과정 수강")
            action_plan.extend(["관련 분야 경험 쌓기", "기본 스킬 강화", "6개월 후 재검토"])
        
        action_plan_text = "\n".join([f"{i+1}. {action}" for i, action in enumerate(action_plan)])
        
        return {
            'overall_assessment': assessment,
            'strengths': strengths_text,
            'improvements': improvements_text,
            'recommendations': recommendations,
            'action_plan': action_plan_text,
            'matching_evidence': f"기술 적합도: {match_score['keyword_score']}%, 경험 관련성: {match_score['embedding_similarity']}%",
            'raw_feedback': f"{assessment}\n\n강점:\n{strengths_text}\n\n개선점:\n{improvements_text}\n\n추천사항:\n{recommendations}\n\nAction Plan:\n{action_plan_text}"
        }

def generate_job_feedback(user_context: UserContext, job_text: str, 
                         match_score: Dict, job_title: str = "", api_key: str = None) -> Dict[str, str]:
    """피드백 생성 함수 (외부에서 호출용)"""
    # API 키가 제공되면 새로운 인스턴스 생성, 아니면 전역 인스턴스 사용
    if api_key:
        feedback_generator = FeedbackGenerator(api_key=api_key)
    else:
        # 전역 인스턴스 (환경변수 사용)
        if not hasattr(generate_job_feedback, '_global_generator'):
            generate_job_feedback._global_generator = FeedbackGenerator()
        feedback_generator = generate_job_feedback._global_generator
    
    return feedback_generator.generate_feedback(user_context, job_text, match_score, job_title) 