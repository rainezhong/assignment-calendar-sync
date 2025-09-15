#!/usr/bin/env python3
"""Debug script to examine course status indicators on Gradescope main page"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_course_status():
    print("🔍 DEBUGGING GRADESCOPE COURSE STATUS INDICATORS")
    print("="*60)
    
    # Set up Chrome driver with existing session
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_gradescope_debug")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Go to main Gradescope page
        print("🌐 Loading Gradescope main page...")
        driver.get("https://www.gradescope.com")
        time.sleep(3)
        
        # Check if logged in
        if "login" in driver.current_url.lower():
            print("❌ Not logged in to Gradescope. Please log in first.")
            return
            
        print("✅ Connected to Gradescope")
        
        # Look for course cards/elements on main page
        print("\n📚 ANALYZING COURSE CARDS...")
        print("-" * 40)
        
        # Find course elements using various selectors
        course_selectors = [
            '.courseBox',
            '.course-card',
            '.course',
            '[class*="course"]',
            'a[href*="/courses/"]'
        ]
        
        course_elements = []
        for selector in course_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    course_elements = elements
                    break
            except:
                continue
        
        if not course_elements:
            print("❌ No course elements found. Let me check the page structure...")
            
            # Print page title and some content for debugging
            print(f"Page title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            
            # Look for any text containing course names
            page_text = driver.page_source
            course_indicators = ['CS 61A', 'CS 61B', 'CS 61C', 'EECS 16', 'MATH 53']
            
            for indicator in course_indicators:
                if indicator in page_text:
                    print(f"Found '{indicator}' in page source")
            
            return
        
        print(f"\n📋 EXAMINING {len(course_elements)} COURSE ELEMENTS:")
        print("-" * 50)
        
        for i, course_element in enumerate(course_elements[:8], 1):  # Limit to first 8
            try:
                print(f"\n🎓 COURSE {i}:")
                
                # Get course link
                course_link = None
                if course_element.tag_name == 'a':
                    course_link = course_element.get_attribute('href')
                else:
                    link_elements = course_element.find_elements(By.CSS_SELECTOR, 'a[href*="/courses/"]')
                    if link_elements:
                        course_link = link_elements[0].get_attribute('href')
                
                if course_link:
                    course_id = course_link.split('/')[-1] if '/courses/' in course_link else 'Unknown'
                    print(f"   Course ID: {course_id}")
                    print(f"   URL: {course_link}")
                
                # Get course name/title
                title_selectors = ['h3', 'h2', '.title', '.name', '[class*="title"]', '[class*="name"]']
                course_name = "Unknown"
                
                for selector in title_selectors:
                    try:
                        title_elem = course_element.find_element(By.CSS_SELECTOR, selector)
                        text = title_elem.text.strip()
                        if text and len(text) < 100:
                            course_name = text
                            break
                    except:
                        continue
                
                print(f"   Name: {course_name}")
                
                # Look for status indicators
                print("   Status indicators:")
                
                # Check element classes
                classes = course_element.get_attribute('class') or ''
                print(f"     Classes: '{classes}'")
                
                # Look for status text/badges
                status_selectors = [
                    '.status', '.badge', '.tag', '.label',
                    '[class*="status"]', '[class*="active"]', '[class*="inactive"]',
                    '[class*="archived"]', '[class*="past"]', '[class*="current"]'
                ]
                
                for selector in status_selectors:
                    try:
                        status_elements = course_element.find_elements(By.CSS_SELECTOR, selector)
                        for elem in status_elements:
                            text = elem.text.strip()
                            if text:
                                print(f"     Status [{selector}]: '{text}'")
                    except:
                        continue
                
                # Look for date information
                date_selectors = [
                    '.date', '.term', '.semester', '.year',
                    '[class*="date"]', '[class*="term"]', '[class*="semester"]'
                ]
                
                for selector in date_selectors:
                    try:
                        date_elements = course_element.find_elements(By.CSS_SELECTOR, selector)
                        for elem in date_elements:
                            text = elem.text.strip()
                            if text and len(text) < 50:
                                print(f"     Date [{selector}]: '{text}'")
                    except:
                        continue
                
                # Get all text content and look for patterns
                all_text = course_element.text
                if len(all_text) < 200:  # Don't print huge blocks
                    print(f"   Full text: '{all_text}'")
                
            except Exception as e:
                print(f"   Error analyzing course {i}: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()

if __name__ == '__main__':
    debug_course_status()