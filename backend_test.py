import requests
import sys
from datetime import datetime, timezone
import json

class TaskFlowAPITester:
    def __init__(self, base_url="https://task-hub-80.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'projects': [],
            'tasks': []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_demo_login(self):
        """Test login with demo credentials"""
        success, response = self.run_test(
            "Demo Login",
            "POST",
            "auth/login",
            200,
            data={"email": "demo@taskflow.com", "password": "demo123"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            print(f"   User ID: {self.user_id}")
            return True
        return False

    def test_register_new_user(self):
        """Test user registration"""
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@test.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "name": "Test User",
                "password": "testpass123",
                "role": "employee"
            }
        )
        return success

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        if success:
            required_fields = ['tasks_completed', 'avg_completion_time', 'team_productivity', 
                             'overdue_tasks', 'daily_focus_time', 'completion_rate', 
                             'active_projects', 'recent_tasks']
            for field in required_fields:
                if field not in response:
                    print(f"   Warning: Missing field '{field}' in dashboard stats")
        return success

    def test_create_project(self):
        """Test project creation"""
        project_data = {
            "title": "Test Project",
            "description": "A test project for API testing",
            "deadline": "2024-12-31T23:59:59Z",
            "team_members": []
        }
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=project_data
        )
        if success and 'id' in response:
            self.created_resources['projects'].append(response['id'])
            print(f"   Created project ID: {response['id']}")
        return success

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get Projects",
            "GET",
            "projects",
            200
        )
        if success:
            print(f"   Found {len(response)} projects")
        return success

    def test_create_task(self):
        """Test task creation"""
        project_id = self.created_resources['projects'][0] if self.created_resources['projects'] else None
        task_data = {
            "title": "Test Task",
            "description": "A test task for API testing",
            "priority": "medium",
            "project_id": project_id,
            "due_date": "2024-12-25T10:00:00Z",
            "estimated_hours": 4.0
        }
        success, response = self.run_test(
            "Create Task",
            "POST",
            "tasks",
            200,
            data=task_data
        )
        if success and 'id' in response:
            self.created_resources['tasks'].append(response['id'])
            print(f"   Created task ID: {response['id']}")
        return success

    def test_get_tasks(self):
        """Test getting all tasks"""
        success, response = self.run_test(
            "Get Tasks",
            "GET",
            "tasks",
            200
        )
        if success:
            print(f"   Found {len(response)} tasks")
        return success

    def test_update_task(self):
        """Test task update"""
        if not self.created_resources['tasks']:
            print("   Skipping - No tasks to update")
            return True
            
        task_id = self.created_resources['tasks'][0]
        update_data = {
            "status": "in_progress",
            "title": "Updated Test Task"
        }
        success, response = self.run_test(
            "Update Task",
            "PUT",
            f"tasks/{task_id}",
            200,
            data=update_data
        )
        return success

    def test_get_users(self):
        """Test getting all users"""
        success, response = self.run_test(
            "Get Users",
            "GET",
            "users",
            200
        )
        if success:
            print(f"   Found {len(response)} users")
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, _ = self.run_test(
            "Unauthorized Access (should fail)",
            "GET",
            "dashboard/stats",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

def main():
    print("🚀 Starting TaskFlow API Testing...")
    print("=" * 50)
    
    tester = TaskFlowAPITester()
    
    # Test sequence
    tests = [
        ("Demo Login", tester.test_demo_login),
        ("User Registration", tester.test_register_new_user),
        ("Dashboard Stats", tester.test_dashboard_stats),
        ("Create Project", tester.test_create_project),
        ("Get Projects", tester.test_get_projects),
        ("Create Task", tester.test_create_task),
        ("Get Tasks", tester.test_get_tasks),
        ("Update Task", tester.test_update_task),
        ("Get Users", tester.test_get_users),
        ("Unauthorized Access", tester.test_unauthorized_access)
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} tests failed. Backend needs attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())