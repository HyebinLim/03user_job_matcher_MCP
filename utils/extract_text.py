import re
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import streamlit as st

def clean_text(text: str) -> str:
    """텍스트 정리 및 전처리"""
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 특수 문자 정리 (한글, 영어, 숫자, 기본 문장부호만 유지)
    text = re.sub(r'[^\w\s가-힣.,!?;:()\-]', '', text)
    
    return text.strip()

def extract_text_from_url(url: str) -> Tuple[str, List[str]]:
    """URL에서 텍스트 추출"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 텍스트 추출
        text = soup.get_text()
        text = clean_text(text)
        
        # 제목 추출
        title = soup.find('title')
        title_text = title.get_text() if title else ""
        
        # 주요 헤딩 추출
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip()
            if heading_text:
                headings.append(heading_text)
        
        return text, headings
        
    except Exception as e:
        st.error(f"URL에서 텍스트를 추출하는 중 오류가 발생했습니다: {str(e)}")
        return "", []

def extract_all_text(job_text: str) -> str:
    """입력받은 텍스트를 정리하여 반환 (MVP 단계)"""
    return clean_text(job_text)

# 기존 URL 크롤링 함수들은 주석 처리 (향후 확장용)
"""
def extract_text_from_image(image_url: str) -> str:
    # 이미지 OCR 기능 (향후 확장용)
    pass
""" 