import re
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional
import streamlit as st
import time
import json
import urllib.parse
import random

def clean_text(text: str) -> str:
    """텍스트 정리 및 전처리"""
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 특수 문자 정리 (한글, 영어, 숫자, 기본 문장부호만 유지)
    text = re.sub(r'[^\w\s가-힣.,!?;:()\-]', '', text)
    
    return text.strip()

def get_robust_headers() -> dict:
    """더 강력한 헤더 설정"""
    try:
        from fake_useragent import UserAgent
        ua = UserAgent()
        user_agent = ua.random
    except:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.google.com/'
    }

def try_cloudscraper(url: str) -> Optional[Tuple[str, List[str]]]:
    """Cloudflare 보호 사이트를 위한 cloudscraper 시도"""
    try:
        import cloudscraper
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        response = scraper.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'iframe']):
                tag.decompose()
            
            # 텍스트 추출
            text_parts = []
            headings = []
            
            # 제목 추출
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                if title_text:
                    text_parts.append(f"제목: {title_text}")
            
            # 메타 설명 추출
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                text_parts.append(f"설명: {meta_desc['content']}")
            
            # 주요 헤딩 추출
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text().strip()
                if heading_text and len(heading_text) > 3:
                    headings.append(heading_text)
                    text_parts.append(heading_text)
            
            # 본문 텍스트 추출
            content_selectors = [
                'main', 'article', '.content', '.main-content', '.post-content',
                '.job-description', '.job-content', '.description', '.details',
                '[role="main"]', '.container', '.wrapper', '.job-detail',
                '.recruit-content', '.job-info', '.position-detail', '.job-text'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                content_text = main_content.get_text()
                text_parts.append(content_text)
            else:
                body = soup.find('body')
                if body:
                    content_text = body.get_text()
                    text_parts.append(content_text)
            
            # 모든 텍스트 결합 및 정리
            full_text = '\n'.join(text_parts)
            cleaned_text = clean_text(full_text)
            
            return cleaned_text, headings
            
    except ImportError:
        return None
    except Exception as e:
        return None

def extract_text_with_selenium(url: str) -> Tuple[str, List[str]]:
    """Selenium을 사용하여 동적 콘텐츠가 있는 웹사이트에서 텍스트 추출"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={get_robust_headers()['User-Agent']}")
        
        # 추가 안티봇 감지 방지 옵션
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")  # 일부 사이트에서는 JS 비활성화가 도움될 수 있음
        
        # WebDriver 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 자동화 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']})")
        
        try:
            # 페이지 로드
            driver.get(url)
            
            # 페이지 로딩 대기 (최대 15초)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 추가 대기 (JavaScript 로딩을 위해)
            time.sleep(5)
            
            # 페이지 스크롤 (동적 콘텐츠 로딩을 위해)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # 페이지 소스 가져오기
            page_source = driver.page_source
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'iframe']):
                tag.decompose()
            
            # 텍스트 추출
            text_parts = []
            
            # 제목 추출
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                if title_text:
                    text_parts.append(f"제목: {title_text}")
            
            # 메타 설명 추출
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                text_parts.append(f"설명: {meta_desc['content']}")
            
            # 주요 헤딩 추출
            headings = []
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text().strip()
                if heading_text and len(heading_text) > 3:
                    headings.append(heading_text)
                    text_parts.append(heading_text)
            
            # 본문 텍스트 추출
            content_selectors = [
                'main', 'article', '.content', '.main-content', '.post-content',
                '.job-description', '.job-content', '.description', '.details',
                '[role="main"]', '.container', '.wrapper', '.job-detail',
                '.recruit-content', '.job-info', '.position-detail'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                content_text = main_content.get_text()
                text_parts.append(content_text)
            else:
                body = soup.find('body')
                if body:
                    content_text = body.get_text()
                    text_parts.append(content_text)
            
            # 모든 텍스트 결합 및 정리
            full_text = '\n'.join(text_parts)
            cleaned_text = clean_text(full_text)
            
            return cleaned_text, headings
            
        finally:
            driver.quit()
            
    except ImportError:
        st.warning("⚠️ Selenium이 설치되지 않았습니다. pip install selenium webdriver-manager로 설치하세요.")
        return "", []
    except Exception as e:
        st.error(f"Selenium을 사용한 텍스트 추출 중 오류가 발생했습니다: {str(e)}")
        return "", []

def try_api_endpoint(url: str) -> Optional[str]:
    """API 엔드포인트가 있는지 확인하고 데이터 추출 시도"""
    try:
        # URL에서 API 엔드포인트 패턴 찾기
        parsed_url = urllib.parse.urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # 일반적인 API 패턴들
        api_patterns = [
            f"{parsed_url.scheme}://{parsed_url.netloc}/api/jobs/{path_parts[-1]}",
            f"{parsed_url.scheme}://{parsed_url.netloc}/api/recruit/{path_parts[-1]}",
            f"{parsed_url.scheme}://{parsed_url.netloc}/api/positions/{path_parts[-1]}",
        ]
        
        headers = get_robust_headers()
        headers['Accept'] = 'application/json'
        
        for api_url in api_patterns:
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # JSON에서 텍스트 추출
                    text_parts = []
                    if 'title' in data:
                        text_parts.append(f"제목: {data['title']}")
                    if 'description' in data:
                        text_parts.append(data['description'])
                    if 'requirements' in data:
                        text_parts.append(f"요구사항: {data['requirements']}")
                    if 'content' in data:
                        text_parts.append(data['content'])
                    
                    if text_parts:
                        return '\n'.join(text_parts)
            except:
                continue
        
        return None
    except:
        return None

def extract_text_from_url(url: str) -> Tuple[str, List[str]]:
    """URL에서 텍스트 추출 (다중 전략)"""
    
    with st.spinner("🔍 웹페이지에서 텍스트를 추출하는 중..."):
        # 1단계: API 엔드포인트 시도
        api_text = try_api_endpoint(url)
        if api_text and len(api_text) > 100:
            return clean_text(api_text), []
        
        # 2단계: Cloudscraper 시도 (Cloudflare 보호 사이트용)
        cloudscraper_result = try_cloudscraper(url)
        if cloudscraper_result and len(cloudscraper_result[0]) > 200:
            return cloudscraper_result
        
        # 3단계: 기본 HTTP 요청
    try:
        headers = get_robust_headers()
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # 응답 인코딩 확인 및 설정
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'iframe']):
            tag.decompose()
        
        # 특정 클래스나 ID를 가진 불필요한 요소들 제거
        unwanted_selectors = [
            '.advertisement', '.ads', '.banner', '.sidebar', '.navigation',
            '.menu', '.footer', '.header', '.cookie-notice', '.popup',
            '.modal', '.overlay', '.loading', '.spinner', '.breadcrumb'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # 텍스트 추출
        text_parts = []
        
        # 제목 추출
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            if title_text:
                text_parts.append(f"제목: {title_text}")
        
        # 메타 설명 추출
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            text_parts.append(f"설명: {meta_desc['content']}")
        
        # 주요 헤딩 추출
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text().strip()
            if heading_text and len(heading_text) > 3:
                headings.append(heading_text)
                text_parts.append(heading_text)
        
        # 본문 텍스트 추출 (더 정교하게)
        content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.job-description', '.job-content', '.description', '.details',
            '[role="main"]', '.container', '.wrapper', '.job-detail',
            '.recruit-content', '.job-info', '.position-detail', '.job-text'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            content_text = main_content.get_text()
            text_parts.append(content_text)
        else:
            body = soup.find('body')
            if body:
                content_text = body.get_text()
                text_parts.append(content_text)
        
        # 모든 텍스트 결합 및 정리
        full_text = '\n'.join(text_parts)
        cleaned_text = clean_text(full_text)
        
        # 4단계: 텍스트가 부족하면 Selenium 시도
        if len(cleaned_text) < 200:
            selenium_text, selenium_headings = extract_text_with_selenium(url)
            
            if selenium_text and len(selenium_text) > len(cleaned_text):
                cleaned_text = selenium_text
                headings = selenium_headings
        
        return cleaned_text, headings
        
    except requests.exceptions.Timeout:
        return extract_text_with_selenium(url)
    except requests.exceptions.ConnectionError:
        return "", []
    except requests.exceptions.HTTPError as e:
        return "", []
    except Exception as e:
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