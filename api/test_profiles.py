#!/usr/bin/env python3
"""Test script for the CrewAI Profile API endpoints."""

import json
import requests
import yaml
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api"
API_KEY = "test-api-key"  # You'll need to configure this
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_list_profiles():
    """Test listing profiles."""
    print("Testing: List Profiles")
    try:
        response = requests.get(f"{API_BASE}/profiles", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {len(data['profiles'])} profiles")
            for profile in data['profiles']:
                print(f"  - {profile['name']} (v{profile['version']})")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_load_profile():
    """Test loading a specific profile."""
    print("\nTesting: Load Profile")
    try:
        payload = {"name": "default"}
        response = requests.post(f"{API_BASE}/profiles/load", headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            profile = data['profile']
            print(f"✓ Loaded profile: {profile['metadata']['name']}")
            print(f"  - MCP Servers: {len(profile.get('mcpServers', []))}")
            print(f"  - Providers: {len(profile.get('providers', []))}")
            print(f"  - Model Overrides: {len(profile.get('modelOverrides', []))}")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_export_profile():
    """Test exporting a profile as YAML."""
    print("\nTesting: Export Profile")
    try:
        response = requests.get(f"{API_BASE}/profiles/default/export", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            yaml_content = data['yamlContent']
            print(f"✓ Exported profile YAML ({len(yaml_content)} characters)")
            
            # Validate the YAML
            try:
                parsed = yaml.safe_load(yaml_content)
                print(f"  - Valid YAML with {len(parsed.keys())} top-level keys")
                return True
            except yaml.YAMLError as e:
                print(f"✗ Invalid YAML: {e}")
                return False
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_create_test_profile():
    """Test creating a new profile."""
    print("\nTesting: Create Test Profile")
    try:
        test_profile = {
            "apiVersion": "crewai/v1",
            "kind": "Profile",
            "metadata": {
                "name": "test",
                "description": "Test profile for API validation",
                "version": "1.0.0",
                "tags": ["test", "api"]
            },
            "mcpServers": [
                {
                    "name": "test-server",
                    "description": "Test MCP server",
                    "transport": {
                        "type": "stdio",
                        "command": "echo",
                        "args": ["test"]
                    },
                    "env": {},
                    "tools": ["test_tool"],
                    "enabled": True
                }
            ],
            "providers": [],
            "modelOverrides": [],
            "defaultToolSets": {},
            "workflowDefaults": {
                "verbose": True,
                "allowDelegation": False,
                "maxConcurrentTasks": 1,
                "timeoutMinutes": 10
            },
            "environment": {},
            "security": {
                "allowedDomains": ["localhost"],
                "restrictedTools": [],
                "rateLimits": {}
            }
        }
        
        payload = {
            "profile": test_profile,
            "overwrite": True
        }
        
        response = requests.post(f"{API_BASE}/profiles/save", headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Created test profile: {data['name']}")
            print(f"  - Message: {data['message']}")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_delete_test_profile():
    """Test deleting the test profile."""
    print("\nTesting: Delete Test Profile")
    try:
        response = requests.delete(f"{API_BASE}/profiles/test", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Deleted profile: {data['name']}")
            print(f"  - Message: {data['message']}")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all profile API tests."""
    print("CrewAI Profile API Test Suite")
    print("=" * 40)
    
    tests = [
        test_list_profiles,
        test_load_profile,
        test_export_profile,
        test_create_test_profile,
        test_list_profiles,  # Run again to see the new profile
        test_delete_test_profile,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All profile API tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())