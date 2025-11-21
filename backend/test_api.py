"""
Simple API tester to verify deployment functionality.
Run: python test_api.py
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://assignment-calendar-sync-production.up.railway.app/api/v1"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()

def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    print_response("Health Check", response)
    return response.status_code == 200

def test_register(email, password, full_name):
    """Test user registration."""
    data = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response(f"Register User: {email}", response)
    return response.status_code in [200, 201]

def test_login(email, password):
    """Test user login."""
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response(f"Login: {email}", response)

    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_get_user(token):
    """Test getting current user info."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("Get Current User", response)
    return response.status_code == 200

def test_create_assignment(token, title, course, due_date):
    """Test creating an assignment."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": "Test assignment for API testing",
        "course_name": course,
        "assignment_type": "homework",
        "due_date": due_date
    }
    response = requests.post(f"{BASE_URL}/assignments", json=data, headers=headers)
    print_response(f"Create Assignment: {title}", response)

    if response.status_code in [200, 201]:
        return response.json().get("id")
    return None

def test_get_assignments(token):
    """Test getting all assignments."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    print_response("Get All Assignments", response)
    return response.status_code == 200

def test_analyze_assignment(token, assignment_id):
    """Test AI analysis of assignment."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/intelligence/{assignment_id}/analyze",
        headers=headers
    )
    print_response(f"Analyze Assignment #{assignment_id}", response)
    return response.status_code == 200

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  Assignment Calendar Sync - API Testing Suite           ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Test configuration
    test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    test_password = "TestPassword123"
    test_name = "API Test User"

    try:
        # Step 1: Health check
        print("\n🔍 Step 1: Testing Health Check...")
        if not test_health():
            print("❌ Health check failed!")
            return
        print("✅ Server is healthy!")

        # Step 2: Register user
        print("\n🔍 Step 2: Registering New User...")
        if not test_register(test_email, test_password, test_name):
            print("❌ Registration failed! Check the error above.")
            print("\n💡 TIP: Check Railway logs for detailed error:")
            print("   railway logs --follow")
            return
        print(f"✅ User registered: {test_email}")

        # Step 3: Login
        print("\n🔍 Step 3: Logging In...")
        token = test_login(test_email, test_password)
        if not token:
            print("❌ Login failed!")
            return
        print(f"✅ Login successful! Token: {token[:20]}...")

        # Step 4: Get user info
        print("\n🔍 Step 4: Getting User Info...")
        if not test_get_user(token):
            print("❌ Failed to get user info!")
            return
        print("✅ User info retrieved!")

        # Step 5: Create assignment
        print("\n🔍 Step 5: Creating Test Assignment...")
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        assignment_id = test_create_assignment(
            token,
            "Test Assignment - Database Systems",
            "CS 440",
            due_date
        )
        if not assignment_id:
            print("❌ Failed to create assignment!")
            return
        print(f"✅ Assignment created with ID: {assignment_id}")

        # Step 6: Get assignments
        print("\n🔍 Step 6: Getting All Assignments...")
        if not test_get_assignments(token):
            print("❌ Failed to get assignments!")
            return
        print("✅ Assignments retrieved!")

        # Step 7: AI Analysis (optional - requires API key)
        print("\n🔍 Step 7: Testing AI Analysis...")
        if test_analyze_assignment(token, assignment_id):
            print("✅ AI analysis successful!")
        else:
            print("⚠️  AI analysis failed (may need OPENAI_API_KEY in Railway)")

        print("\n" + "="*60)
        print("🎉 ALL CORE TESTS PASSED!")
        print("="*60)
        print(f"\n📧 Test Account Created:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"\n🔗 Try it yourself in Swagger UI:")
        print(f"   {BASE_URL}/docs")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
