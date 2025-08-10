#!/usr/bin/env python3
"""
KakaoBank Recruitment Page Analysis
Tests different extraction methods on the KakaoBank page
"""

import requests
from bs4 import BeautifulSoup
import streamlit as st

def analyze_kakaobank_page():
    """카카오뱅크 채용 페이지 분석"""
    
    url = "https://recruit.kakaobank.com/jobs/213948"
    
    print("🔍 카카오뱅크 채용 페이지 분석")
    print("=" * 50)
    
    # 1. 기본 HTTP 요청
    print("\n1. 기본 HTTP 요청 테스트")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        print(f"Encoding: {response.encoding}")
        
        # HTML 구조 분석
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 제목 확인
        title = soup.find('title')
        print(f"Title: {title.get_text() if title else 'No title'}")
        
        # 메타 태그 확인
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        print(f"Meta Description: {meta_desc.get('content') if meta_desc else 'No meta description'}")
        
        # 주요 콘텐츠 영역 확인
        content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.job-description', '.job-content', '.description', '.details',
            '[role="main"]', '.container', '.wrapper', '.job-detail',
            '.recruit-content', '.job-info', '.position-detail'
        ]
        
        print("\n콘텐츠 영역 검색:")
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ {selector}: {len(elements)}개 요소 발견")
                for i, elem in enumerate(elements[:2]):  # 처음 2개만
                    text = elem.get_text().strip()[:100]
                    print(f"   {i+1}. {text}...")
            else:
                print(f"❌ {selector}: 요소 없음")
        
        # JavaScript 파일 확인
        scripts = soup.find_all('script')
        print(f"\nJavaScript 파일: {len(scripts)}개")
        for script in scripts[:5]:  # 처음 5개만
            src = script.get('src', '')
            if src:
                print(f"  - {src}")
        
        # 전체 텍스트 길이
        full_text = soup.get_text()
        print(f"\n전체 텍스트 길이: {len(full_text)} 문자")
        print(f"텍스트 미리보기: {full_text[:200]}...")
        
        # 동적 콘텐츠 지표
        dynamic_indicators = [
            'loading', 'spinner', 'skeleton', 'placeholder',
            'data-react', 'data-vue', 'ng-', 'v-',
            'window.__INITIAL_STATE__', 'window.__PRELOADED_STATE__'
        ]
        
        print("\n동적 콘텐츠 지표:")
        for indicator in dynamic_indicators:
            if indicator in str(response.content):
                print(f"✅ {indicator}: 발견됨")
            else:
                print(f"❌ {indicator}: 없음")
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
    
    # 2. API 엔드포인트 시도
    print("\n2. API 엔드포인트 테스트")
    try:
        api_patterns = [
            "https://recruit.kakaobank.com/api/jobs/213948",
            "https://recruit.kakaobank.com/api/recruit/213948",
            "https://recruit.kakaobank.com/api/positions/213948",
        ]
        
        for api_url in api_patterns:
            try:
                response = requests.get(api_url, headers=headers, timeout=5)
                print(f"{api_url}: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ 성공! 응답 길이: {len(response.content)}")
                    print(f"  응답 미리보기: {response.text[:200]}...")
            except Exception as e:
                print(f"{api_url}: ❌ {str(e)}")
                
    except Exception as e:
        print(f"❌ API 테스트 오류: {str(e)}")

if __name__ == "__main__":
    analyze_kakaobank_page()

