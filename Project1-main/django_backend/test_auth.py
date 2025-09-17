import requests
import json

# Base URL for API
BASE_URL = "http://localhost:8000"

def test_registration_default_role():
    """Test user registration with default role (EMPLOYEE)"""
    url = f"{BASE_URL}/api/auth/register/"
    data = {
        "email": "employee@example.com",
        "name": "Test Employee",
        "password": "securepassword123"
    }
    
    response = requests.post(url, json=data)
    print("\n=== Test Registration (Default Role) ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"User created with role: {result['user']['role']}")
        print(f"Access token received: {result['access_token'][:20]}...")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def test_login_and_me_endpoint(email, password):
    """Test login and /me endpoint to verify role is returned"""
    # Login
    login_url = f"{BASE_URL}/api/auth/login/"
    login_data = {
        "email": email,
        "password": password
    }
    
    login_response = requests.post(login_url, json=login_data)
    print("\n=== Test Login ===")
    print(f"Status Code: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login Error: {login_response.text}")
        return
    
    login_result = login_response.json()
    access_token = login_result['access_token']
    print(f"Login successful, role from response: {login_result['user']['role']}")
    
    # Test /me endpoint
    me_url = f"{BASE_URL}/api/auth/me/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    me_response = requests.get(me_url, headers=headers)
    print("\n=== Test /me Endpoint ===")
    print(f"Status Code: {me_response.status_code}")
    
    if me_response.status_code == 200:
        me_result = me_response.json()
        print(f"User data from /me endpoint:")
        print(f"  - ID: {me_result['id']}")
        print(f"  - Name: {me_result['name']}")
        print(f"  - Email: {me_result['email']}")
        print(f"  - Role: {me_result['role']}")
    else:
        print(f"Error accessing /me endpoint: {me_response.text}")

if __name__ == "__main__":
    # Test registration with default role
    registration_result = test_registration_default_role()
    
    if registration_result:
        # Test login and /me endpoint
        test_login_and_me_endpoint(
            "employee@example.com", 
            "securepassword123"
        )
    
    print("\n=== CURL Commands for Testing ===")
    print("# Register a new user (default to EMPLOYEE role):")
    print('''curl -X POST http://localhost:8000/api/auth/register/ \\
    -H "Content-Type: application/json" \\
    -d '{"email": "newuser@example.com", "name": "New User", "password": "securepassword123"}'
    ''')
    
    print("\n# Login:")
    print('''curl -X POST http://localhost:8000/api/auth/login/ \\
    -H "Content-Type: application/json" \\
    -d '{"email": "employee@example.com", "password": "securepassword123"}'
    ''')
    
    print("\n# Get user profile with role:")
    print('''curl -X GET http://localhost:8000/api/auth/me/ \\
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ''')