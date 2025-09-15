#!/usr/bin/env python3
"""Debug script to examine what semester info is available on Gradescope pages"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_gradescope_course_info():
    print("🔍 DEBUGGING GRADESCOPE COURSE INFORMATION")
    print("="*60)
    
    # Set up Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_gradescope_debug")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Use existing session if available
        driver.get("https://www.gradescope.com")
        time.sleep(2)
        
        # Check if logged in
        if "login" in driver.current_url.lower():
            print("❌ Not logged in to Gradescope. Please log in first using the main app.")
            return
        
        print("✅ Connected to Gradescope")
        
        # Use specific course URLs from your sync output
        course_urls = [
            "https://www.gradescope.com/courses/961758",  # CS 61B (assignments from Spring 2025)
            "https://www.gradescope.com/courses/843175",  # CS 61A (assignments from Fall 2025)
            "https://www.gradescope.com/courses/1104572"  # CS 61C (current Fall 2025)
        ]
        
        print(f"📚 Found {len(course_urls)} courses to examine")
        
        for i, course_url in enumerate(course_urls, 1):
            print(f"\n{'='*40}")
            print(f"COURSE {i}: {course_url}")
            print(f"{'='*40}")
            
            driver.get(course_url)
            time.sleep(3)
            
            # Extract all possible course information
            print("📋 COURSE HEADER INFORMATION:")
            print("-" * 30)
            
            # Basic course name
            try:
                course_name = driver.find_element(By.CSS_SELECTOR, 'h1.courseHeader--title, .courseHeader h1').text.strip()
                print(f"  Course Name: '{course_name}'")
            except:
                print("  Course Name: Not found")
            
            # Look for semester/term information in various places
            potential_semester_selectors = [
                '.courseHeader--term',
                '.courseHeader .term',
                '.course-term',
                '.semester',
                '.term',
                'h2',
                'h3', 
                '.courseHeader p',
                '.courseHeader small',
                '.course-info',
                '.course-details',
                '[class*="term"]',
                '[class*="semester"]',
                '[class*="year"]'
            ]
            
            print("  Potential Semester Info:")
            found_semester_info = False
            
            for selector in potential_semester_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) < 100:  # Reasonable length
                            print(f"    [{selector}] '{text}'")
                            found_semester_info = True
                except:
                    continue
            
            if not found_semester_info:
                print("    ❌ No semester information found in headers")
            
            # Look at the full page source for semester patterns
            print("  Page Source Analysis:")
            page_source = driver.page_source.lower()
            
            semester_patterns = [
                'fall 2024', 'fall 2025', 'spring 2024', 'spring 2025', 'summer 2024', 'summer 2025',
                'f24', 'f25', 's24', 's25', 'su24', 'su25',
                'fa24', 'fa25', 'sp24', 'sp25'
            ]
            
            found_patterns = []
            for pattern in semester_patterns:
                if pattern in page_source:
                    found_patterns.append(pattern)
            
            if found_patterns:
                print(f"    Found patterns: {', '.join(found_patterns)}")
            else:
                print("    ❌ No semester patterns found in page source")
            
            # Look at course URL for patterns
            print("  URL Analysis:")
            course_id = course_url.split('/')[-1]
            print(f"    Course ID: {course_id}")
            
            # Check if there's a pattern in course IDs that might indicate semester
            if course_id.isdigit():
                print(f"    Numeric ID - might contain semester encoding")
            else:
                print(f"    Non-numeric ID")
            
            print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()

if __name__ == '__main__':
    debug_gradescope_course_info()