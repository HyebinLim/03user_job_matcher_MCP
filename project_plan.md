1. 프로젝트 컨셉
사용자의 커리어를 토대로, 채용공고와의 적합도를 분석하여 매칭도 및 피드백을 제공하는 AI 시스템

2. 기능
MCP(Model Context Protocol): 사용자의 직무 맥락을 structured하게 정의(JSON or form 입력)
입력(input): 채용공고 URL(텍스트+이미지 포함)
처리: (1)텍스트 추출 -> (2)유사도 분석 -> (3)매칭도 및 피드백
출력(outpput): 매칭도(0~100%), 자연어 피드백, 매칭 근거 하이라이트
언어 지원: 한국어, 영어
인터페이스: Streamlit UI
API: GPT API로 매칭 결과 요약 생성

3. 프로젝트 폴더 구조
MCP_job_matcher
├───── app.py               # Streamlit 메인
├───── requirements.txt     # 필요 패키지
├───── readme.md            # 프로젝트 설명(for user)
├───── project_plan.md      # 프로젝트 설명(for myself - gitignore)
├───── .streamlit/          # 배포 설정
│   └─── config.toml
├───── utils/               # 핵심 모듈
│   └─── extract_text.py    # URL 또는 OCR(image) 텍스트 추출
│   └─── match_score.py     # 사용자 context와 채용공고 간 매칭 점수(유사도) 계산
│   └─── feedback.py        # GPT API로 피드백(매칭 근거 및 부족한 점) 생성
│   └─── mcp_schema.py      # 사용자 context 스키마
└───── data/
│   └─── user_contexts/     # user별 context 저장(json)
│   └─── postings/          # 채용 공고
└───── .gitignore

4. 매칭 알고리즘
(1) keyword rule
ex. 기술스택, 연차, 언어 등 점수화
(2) embedding similarity: cosine similarity(user context, posting)
(3) feedback: GPT prompt -> score & summary
---> 최종: 가중평균(1)(2) + GPT 피드백

5. User Interface
[Streamlit app URL] Streamlit 앱 실행
[Context 입력폼] 사용자 context form 입력 or 불러오기
[옵션 버튼] context 저장 or 수정 or 삭제
[URL 입력창] 채용 공고 URL 입력
[분석 버튼] 공고 텍스트 분석
[텍스트(+하이라이트) 표시] 매칭 결과 출력 (점수 + 피드백)

6. 사용자 Context
- 기본 정보 질문형 방식 + 선택적 자유 입력
- GPT는 공고 당 1회만 호출: 점수 + 피드백을 한 번에 받기 (multi-output prompt)
{
  "name": "Hyebin Lim",
  "target_roles": ["NLP Engineer", "AI Research Assistant"],
  "experience_years": 2,
  "skills": ["Python", "Transformers", "PyTorch", "LLM", "SQL"],
  "languages": {
    "Korean": "Native",
    "English": "Fluent"
  },
  "work_preference": ["Remote", "Hybrid"],
  "extra_notes": "금융 도메인에 대한 이해가 깊고, NLP 해외 석사 있음"
}

7. 추후 확장
(1) 사용자 로그인 기능
(2) 공고 텍스트 + google search(회사명/직무 키워드 추출 -> Google Custom Search API로 관련 정보 수집 (회사 + 직무) -> 요약 + 구조화)를 토대로 피드백
(2) 직접 찾아서 적합한 공고 보여주기
(3) 이력서 업로드 기능
(4) 다국어 GPT 응답(답변 언어 선택 가능 옵션)
(5) 추천 공고 리스트(매칭도 순 정렬)