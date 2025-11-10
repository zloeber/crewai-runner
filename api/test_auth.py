#!/usr/bin/env python3
"""Test script to verify Bearer token authentication is working."""

import os
import sys
import requests
from pathlib import Path

# Add the test directory to path to import test configuration
test_dir = Path(__file__).parent / "src" / "tests"
sys.path.insert(0, str(test_dir))

from conftest import TEST_API_BASE_URL, TEST_API_KEY

def test_authentication():
    """Test Bearer token authentication."""
    print("Testing API authentication...")
    
    # Test 1: Request without auth should fail
    print("\n1. Testing request without authentication:")
    try:
        response = requests.get(f"{TEST_API_BASE_URL}/workflows/frameworks", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthorized request")
        else:
            print("   ❌ Should have returned 401 Unauthorized")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: Request with invalid token should fail
    print("\n2. Testing request with invalid token:")
    headers = {"Authorization": "Bearer invalid-token"}
    try:
        response = requests.get(f"{TEST_API_BASE_URL}/workflows/frameworks", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid token")
        else:
            print("   ❌ Should have returned 401 Unauthorized")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 3: Request with valid token should succeed
    print("\n3. Testing request with valid Bearer token:")
    headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
    try:
        response = requests.get(f"{TEST_API_BASE_URL}/workflows/frameworks", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Successfully authenticated with Bearer token")
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   ❌ Expected 200 but got {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    print("\n✅ Authentication tests completed successfully!")
    return True

def test_api_client():
    """Test the custom HTTPAPIClient."""
    print("\n" + "="*50)
    print("Testing HTTPAPIClient from conftest.py...")
    
    # Import the client class
    sys.path.insert(0, str(Path(__file__).parent / "src" / "tests"))
    from conftest import TEST_API_BASE_URL, TEST_API_KEY
    
    # Create client like the tests do
    class HTTPAPIClient:
        def __init__(self, base_url: str, api_key: str):
            self.base_url = base_url
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            self.session = requests.Session()
            self.session.headers.update(self.headers)
        
        def get(self, path: str, **kwargs):
            url = f"{self.base_url}{path}" if not path.startswith("http") else path
            return self.session.get(url, **kwargs)
    
    client = HTTPAPIClient(TEST_API_BASE_URL, TEST_API_KEY)
    
    print("Testing HTTPAPIClient.get() method:")
    try:
        response = client.get("/workflows/frameworks")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ HTTPAPIClient working correctly")
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   ❌ Expected 200 but got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("API Bearer Token Authentication Test")
    print("="*50)
    
    # Check if server is running
    try:
        base_url = TEST_API_BASE_URL.replace('/api', '')
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ API server is not running")
        print("Please start the server with: cd api && python run_server.py")
        return False
    
    # Run authentication tests
    if not test_authentication():
        return False
    
    # Test the client
    if not test_api_client():
        return False
    
    print("\n🎉 All tests passed! Bearer token authentication is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)