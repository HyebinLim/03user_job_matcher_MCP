#!/usr/bin/env python3
"""
Text Extraction Test Script
Tests the enhanced text extraction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.extract_text import extract_text_from_url, extract_text_with_selenium, try_cloudscraper, try_api_endpoint
import streamlit as st

def test_extraction():
    """Test text extraction with various URLs"""
    
    # Test URLs
    test_urls = [
        "https://recruit.kakaobank.com/jobs/213948",
        "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=123456",
        "https://job.incruit.com/jobdb_info/jobpost.asp?job=123456",
    ]
    
    print("🧪 Testing Text Extraction System")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\n🔗 Testing URL: {url}")
        print("-" * 30)
        
        try:
            # Test API endpoint
            print("1. Testing API endpoint...")
            api_text = try_api_endpoint(url)
            if api_text:
                print(f"✅ API success: {len(api_text)} characters")
            else:
                print("❌ API failed")
            
            # Test cloudscraper
            print("2. Testing cloudscraper...")
            cloud_result = try_cloudscraper(url)
            if cloud_result and cloud_result[0]:
                print(f"✅ Cloudscraper success: {len(cloud_result[0])} characters")
            else:
                print("❌ Cloudscraper failed")
            
            # Test full extraction
            print("3. Testing full extraction...")
            text, headings = extract_text_from_url(url)
            if text:
                print(f"✅ Full extraction success: {len(text)} characters")
                print(f"📋 Headings found: {len(headings)}")
                if headings:
                    print(f"   First heading: {headings[0]}")
            else:
                print("❌ Full extraction failed")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_extraction()

