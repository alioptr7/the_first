"""Comprehensive API endpoint testing script with server log monitoring."""
import requests
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
SERVER_LOG_FILE = r"c:\Users\win\the_first\response-network\api\server.log"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.admin_id = None
        self.results = []
        self.errors = []
        self.last_log_size = 0
        self.log_file = SERVER_LOG_FILE
        
    def read_server_logs(self, lines_count: int = 10) -> List[str]:
        """Read recent logs from server log file."""
        try:
            if not os.path.exists(self.log_file):
                return [f"Log file not found: {self.log_file}"]
            
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                return all_lines[-lines_count:] if all_lines else ["No logs yet"]
        except Exception as e:
            return [f"Error reading logs: {str(e)}"]
        
    def print_section(self, title: str):
        """Print a section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}{Colors.ENDC}\n")
    
    def print_test(self, name: str, method: str = ""):
        """Print a test name."""
        print(f"{Colors.BLUE}▶ {name}{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"  {Colors.GREEN}✓ {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"  {Colors.RED}✗ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print info message."""
        print(f"  {Colors.YELLOW}ℹ {message}{Colors.ENDC}")
    
    def print_response(self, response: requests.Response, show_body: bool = True):
        """Print response details."""
        print(f"  Status Code: {Colors.BOLD}{response.status_code}{Colors.ENDC}")
        
        if show_body and response.text:
            try:
                data = response.json()
                # Limit output to first 500 chars
                response_str = json.dumps(data, indent=4, ensure_ascii=False)[:500]
                print(f"  Response:\n{response_str}")
            except:
                print(f"  Response: {response.text[:200]}")
    
    def print_server_logs(self):
        """Print recent server logs."""
        logs = self.read_server_logs(lines_count=5)
        if logs:
            print(f"\n  {Colors.YELLOW}Server Logs (last 5 lines):{Colors.ENDC}")
            for log_line in logs:
                log_line = log_line.strip()
                if log_line:
                    # Color ERROR lines in red
                    if "ERROR" in log_line or "error" in log_line:
                        print(f"    {Colors.RED}{log_line}{Colors.ENDC}")
                    elif "WARNING" in log_line:
                        print(f"    {Colors.YELLOW}{log_line}{Colors.ENDC}")
                    else:
                        print(f"    {log_line}")
    
    def make_request(self, method: str, endpoint: str, name: str, 
                    data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None,
                    expect_status: int = 200,
                    show_body: bool = True) -> Optional[requests.Response]:
        """Make an API request and handle response."""
        
        self.print_test(name, method)
        
        url = f"{API_V1}{endpoint}"
        
        # Prepare headers
        if headers is None:
            headers = {}
        
        # Add auth header if token exists and not explicitly disabled
        if self.auth_token and "Authorization" not in headers and headers.get("skip_auth") != True:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Remove skip_auth marker
        headers.pop("skip_auth", None)
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=5)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=5)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=5)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=5)
            else:
                self.print_error(f"Unknown method: {method}")
                return None
            
            # Small delay to let server write logs
            time.sleep(0.5)
            
            if response.status_code == expect_status:
                self.print_success(f"{method} {endpoint}")
            else:
                self.print_error(f"Expected {expect_status}, got {response.status_code}")
                self.print_response(response, show_body=True)
                return None
            
            self.print_response(response, show_body=show_body)
            self.print_server_logs()
            return response
            
        except requests.exceptions.ConnectionError:
            self.print_error(f"Connection failed - Server not responding")
            self.errors.append("Connection failed to server")
            return None
        except requests.exceptions.Timeout:
            self.print_error(f"Request timeout")
            self.errors.append("Request timeout")
            return None
        except Exception as e:
            self.print_error(f"Request failed: {str(e)}")
            self.errors.append(str(e))
            return None
    
    def test_health_check(self):
        """Test health check endpoints."""
        self.print_section("Health Check Endpoints")
        
        # Health endpoint (no auth needed)
        response = self.make_request(
            "GET", "/health", "Health Check",
            headers={"Authorization": ""},
            expect_status=200,
            show_body=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                self.print_success("Health check passed")
                self.results.append(("Health Check", "PASS"))
            else:
                self.print_error("Health check failed")
                self.results.append(("Health Check", "FAIL"))
    
    def test_auth(self):
        """Test authentication endpoints."""
        self.print_section("Authentication Endpoints")
        
        # Login with admin credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        # Make request WITHOUT Authorization header for login
        response = self.make_request(
            "POST", "/auth/login", "Admin Login",
            data=login_data,
            headers={"Authorization": "Bearer temp", "skip_auth": True},
            expect_status=200
        )
        
        if response and response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            if self.auth_token:
                self.print_success("Authentication token obtained")
                self.results.append(("Login", "PASS"))
            else:
                self.print_error("No token in response")
                self.results.append(("Login", "FAIL"))
        else:
            self.print_error("Login failed")
            self.results.append(("Login", "FAIL"))
    
    def test_users(self):
        """Test user management endpoints."""
        self.print_section("User Management Endpoints")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return
        
        # Get current user
        response = self.make_request(
            "GET", "/auth/me", "Get Current User",
            expect_status=200
        )
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_id = data.get("id")
            self.print_success(f"Current user: {data.get('username')}")
            self.results.append(("Get Current User", "PASS"))
        else:
            self.results.append(("Get Current User", "FAIL"))
        
        # List all users
        response = self.make_request(
            "GET", "/users", "List Users",
            expect_status=200
        )
        
        if response and response.status_code == 200:
            self.results.append(("List Users", "PASS"))
        else:
            self.results.append(("List Users", "FAIL"))
    
    def test_system_endpoints(self):
        """Test system endpoints."""
        self.print_section("System Endpoints")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return
        
        # System status
        response = self.make_request(
            "GET", "/system/status", "System Status",
            expect_status=200
        )
        
        if response:
            self.results.append(("System Status", "PASS" if response.status_code == 200 else "FAIL"))
        
        # System health
        response = self.make_request(
            "GET", "/system/health", "System Health Check",
            expect_status=200
        )
        
        if response:
            self.results.append(("System Health", "PASS" if response.status_code == 200 else "FAIL"))
    
    def test_worker_settings(self):
        """Test worker settings endpoints."""
        self.print_section("Worker Settings Endpoints")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return
        
        # Test connection with local storage
        test_data = {
            "worker_type": "EXPORT_SETTINGS",
            "storage_type": "local",
            "storage_settings": {
                "base_path": "/tmp/test_storage"
            }
        }
        
        response = self.make_request(
            "POST", "/worker-settings/test-connection", 
            "Test Storage Connection (Local)",
            data=test_data,
            expect_status=200
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.print_success("Local storage connection successful")
                self.results.append(("Worker Settings - Local Storage", "PASS"))
            else:
                self.print_error(f"Storage test failed: {data.get('message')}")
                self.results.append(("Worker Settings - Local Storage", "FAIL"))
        else:
            self.results.append(("Worker Settings - Local Storage", "FAIL"))
    
    def test_request_types(self):
        """Test request type endpoints."""
        self.print_section("Request Type Endpoints")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return
        
        # List request types
        response = self.make_request(
            "GET", "/request-types", "List Request Types",
            expect_status=200
        )
        
        if response and response.status_code == 200:
            self.results.append(("List Request Types", "PASS"))
        else:
            self.results.append(("List Request Types", "FAIL"))
    
    def test_monitoring(self):
        """Test monitoring endpoints."""
        self.print_section("Monitoring Endpoints")
        
        # Get metrics (no auth needed for this one, typically)
        response = self.make_request(
            "GET", "/monitoring/metrics", "Get Metrics",
            expect_status=200,
            show_body=False
        )
        
        if response:
            self.results.append(("Monitoring Metrics", "PASS" if response.status_code == 200 else "FAIL"))
    
    def print_summary(self):
        """Print test summary."""
        self.print_section("Test Summary")
        
        passed = sum(1 for _, result in self.results if result == "PASS")
        failed = sum(1 for _, result in self.results if result == "FAIL")
        
        print(f"{Colors.BOLD}Results:{Colors.ENDC}")
        for test_name, result in self.results:
            status_color = Colors.GREEN if result == "PASS" else Colors.RED
            print(f"  {status_color}{'✓' if result == 'PASS' else '✗'} {test_name}: {result}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"  Total Tests: {len(self.results)}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.ENDC}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.ENDC}")
        
        if self.errors:
            print(f"\n{Colors.BOLD}{Colors.RED}Errors:{Colors.ENDC}")
            for error in self.errors:
                print(f"  {Colors.RED}• {error}{Colors.ENDC}")
        
        success_rate = (passed / len(self.results) * 100) if self.results else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}\n")
    
    def run_all_tests(self):
        """Run all tests."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("=" * 80)
        print("  API Endpoint Comprehensive Testing Suite")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(Colors.ENDC)
        
        # Add small delay to ensure server is ready
        time.sleep(1)
        
        try:
            self.test_health_check()
            self.test_auth()
            self.test_users()
            self.test_system_endpoints()
            self.test_worker_settings()
            self.test_request_types()
            self.test_monitoring()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
        
        self.print_summary()

def main():
    """Main entry point."""
    print(f"{Colors.CYAN}Waiting for server to be ready...{Colors.ENDC}")
    
    # Check if server is up
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=2)
            if response.status_code == 200:
                print(f"{Colors.GREEN}Server is ready!{Colors.ENDC}\n")
                break
        except:
            if i < max_retries - 1:
                time.sleep(1)
                print(f"{Colors.YELLOW}.", end="", flush=True)
            else:
                print(f"\n{Colors.RED}Server is not responding!{Colors.ENDC}")
                print(f"Make sure to run the server with: python start_server.bat")
                return 1
    
    tester = APITester()
    tester.run_all_tests()
    
    return 0 if tester.results else 1

if __name__ == "__main__":
    sys.exit(main())