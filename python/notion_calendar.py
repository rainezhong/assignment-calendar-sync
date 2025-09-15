#!/usr/bin/env python3
"""Notion Calendar integration for assignment sync"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timezone
from utils import logger
import config

class NotionCalendarSync:
    """Handles syncing assignments to Notion Calendar via Notion API"""
    
    def __init__(self, api_token: str = None, database_id: str = None):
        self.api_token = api_token or config.NOTION_API_TOKEN
        self.database_id = database_id or config.NOTION_DATABASE_ID
        self.base_url = "https://api.notion.com/v1"
        
        # Notion API headers
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def is_configured(self) -> bool:
        """Check if Notion integration is properly configured"""
        return bool(self.api_token and self.database_id)
    
    def test_connection(self) -> Dict:
        """Test connection to Notion API and database"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Notion API token or database ID not configured"
            }
        
        try:
            # Test API connection by retrieving database info
            response = requests.get(
                f"{self.base_url}/databases/{self.database_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                db_info = response.json()
                return {
                    "success": True,
                    "database_name": db_info.get("title", [{}])[0].get("text", {}).get("content", "Unknown"),
                    "message": "Successfully connected to Notion database"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid Notion API token"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Database not found - check database ID and permissions"
                }
            else:
                return {
                    "success": False,
                    "error": f"Notion API error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    def create_assignment_page(self, assignment: Dict) -> Dict:
        """Create a new assignment page in the Notion database"""
        
        if not self.is_configured():
            return {
                "success": False,
                "error": "Notion not configured"
            }
        
        try:
            # Prepare assignment data
            course = assignment.get('course', 'Unknown Course')
            name = assignment.get('name', 'Unnamed Assignment')
            due_date = assignment.get('due_date')
            description = assignment.get('description', '')
            
            # Format title
            title = f"{course}: {name}"
            
            # Prepare page properties
            properties = {
                "Task name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
            
            # Add due date if available
            if due_date:
                # Convert to ISO format for Notion
                iso_date = due_date.isoformat()
                properties["Due date"] = {
                    "date": {
                        "start": iso_date
                    }
                }
            
            # Add description if available
            if description:
                properties["Description"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": description[:2000]  # Notion has limits
                            }
                        }
                    ]
                }
            
            # Create page payload
            payload = {
                "parent": {
                    "database_id": self.database_id
                },
                "properties": properties
            }
            
            # Send request to create page
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                page_data = response.json()
                return {
                    "success": True,
                    "page_id": page_data["id"],
                    "url": page_data["url"],
                    "message": f"Created assignment: {title}"
                }
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                return {
                    "success": False,
                    "error": f"Failed to create page: {response.status_code} - {error_data}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def sync_assignments(self, assignments: List[Dict]) -> Dict:
        """Sync multiple assignments to Notion Calendar"""
        
        if not assignments:
            return {
                "success": True,
                "synced_count": 0,
                "message": "No assignments to sync"
            }
        
        logger.info(f"Syncing {len(assignments)} assignments to Notion Calendar...")
        
        synced_count = 0
        failed_count = 0
        errors = []
        
        for assignment in assignments:
            try:
                result = self.create_assignment_page(assignment)
                
                if result["success"]:
                    synced_count += 1
                    logger.info(f"✅ {result['message']}")
                else:
                    failed_count += 1
                    error_msg = f"❌ Failed to sync {assignment.get('name', 'Unknown')}: {result['error']}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"❌ Error syncing {assignment.get('name', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "success": failed_count == 0,
            "synced_count": synced_count,
            "failed_count": failed_count,
            "errors": errors,
            "message": f"Synced {synced_count} assignments to Notion Calendar" + 
                      (f" ({failed_count} failed)" if failed_count > 0 else "")
        }

def test_notion_integration():
    """Test the Notion Calendar integration"""
    
    print("🔍 Testing Notion Calendar Integration...")
    print("=" * 60)
    
    notion = NotionCalendarSync()
    
    if not notion.is_configured():
        print("❌ Notion not configured")
        print("Please set NOTION_API_TOKEN and NOTION_DATABASE_ID in your .env file")
        return False
    
    print("✅ Notion configuration found")
    print(f"Database ID: {notion.database_id}")
    
    # Test connection
    print("\n🌐 Testing connection...")
    connection_result = notion.test_connection()
    
    if connection_result["success"]:
        print(f"✅ {connection_result['message']}")
        print(f"Database: {connection_result.get('database_name', 'Unknown')}")
    else:
        print(f"❌ {connection_result['error']}")
        return False
    
    # Test creating a sample assignment
    print("\n📝 Testing assignment creation...")
    test_assignment = {
        "course": "TEST COURSE",
        "name": "Test Assignment - Calendar Sync",
        "due_date": datetime.now().replace(hour=23, minute=59, second=0, microsecond=0),
        "description": "This is a test assignment created by the Assignment Calendar Sync app."
    }
    
    result = notion.create_assignment_page(test_assignment)
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"Page URL: {result['url']}")
        print("\n💡 Check your Notion Calendar to see the test assignment!")
        return True
    else:
        print(f"❌ {result['error']}")
        return False

if __name__ == '__main__':
    success = test_notion_integration()
    exit(0 if success else 1)