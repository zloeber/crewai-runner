#!/usr/bin/env python3
"""Debug script to see the actual YAML validation response."""

import requests
import json

# Test YAML content
yaml_content = """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    role: Test Role
    goal: Test Goal
    backstory: Test Backstory
    model: gpt-4
tasks:
  - name: test_task
    description: Test Description
    expectedOutput: Test Output
    agent: test_agent
"""

# Make request to local API
url = "http://localhost:8000/api/yaml/validate"
headers = {"Authorization": "Bearer test-api-key", "Content-Type": "application/json"}
data = {"yamlContent": yaml_content}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
