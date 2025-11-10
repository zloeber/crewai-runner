#!/usr/bin/env python3
"""Script to update all API test files to include server check fixture and Bearer token authentication."""

import os
import re
from pathlib import Path

def update_test_file(file_path):
    """Update a single test file to include skip_if_no_server fixture."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update docstring to mention HTTP Bearer token authentication
    content = re.sub(
        r'"""Tests for (.*?) API endpoints\."""',
        r'"""Tests for \1 API endpoints via HTTP with Bearer token authentication."""',
        content
    )
    
    # Update async test function signatures to include skip_if_no_server
    # Pattern: async def test_.*\(api_client(?:,.*?)?\):
    def add_server_check(match):
        func_def = match.group(0)
        if 'skip_if_no_server' in func_def:
            return func_def  # Already has the fixture
        
        # Find the closing parenthesis before the colon
        if ', ' in func_def and not func_def.endswith('api_client):'):
            # There are other parameters after api_client
            return func_def.replace('):', ', skip_if_no_server):')
        elif func_def.endswith('api_client):'):
            # Only api_client parameter
            return func_def.replace('api_client):', 'api_client, skip_if_no_server):')
        else:
            # api_client with other parameters before it
            return func_def.replace('):', ', skip_if_no_server):')
    
    content = re.sub(
        r'async def test_\w+\([^)]*api_client[^)]*\):',
        add_server_check,
        content
    )
    
    # Update docstrings of test functions to mention Bearer token
    content = re.sub(
        r'"""(Test .*?)\."""',
        r'"""\1 via HTTP with Bearer token authentication."""',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

def main():
    """Update all test files."""
    api_dir = Path(__file__).parent
    test_dir = api_dir / "src" / "tests"
    
    test_files = [
        "test_chat_api.py",
        "test_config_api.py", 
        "test_mcp_api.py",
        "test_models_api.py",
        "test_profiles_api.py",
        "test_providers_api.py",
        "test_yaml_validator_api.py",
        "test_workflows_api.py"
    ]
    
    for test_file in test_files:
        file_path = test_dir / test_file
        if file_path.exists():
            update_test_file(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()