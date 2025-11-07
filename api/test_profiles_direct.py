#!/usr/bin/env python3
"""Simple direct test of the profile API functionality."""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up environment
os.environ.setdefault("CREWAI_API_KEY", "test-api-key")

# Test our profile models and functions
def test_profile_models():
    """Test that our profile models work correctly."""
    print("Testing profile models...")
    
    from engine.models import ProfileConfig, ProfileMetadata, MCPServerConfig, MCPTransport
    
    # Create a simple profile
    metadata = ProfileMetadata(
        name="test",
        description="Test profile",
        version="1.0.0",
        tags=["test"]
    )
    
    transport = MCPTransport(
        type="stdio",
        command="echo",
        args=["test"]
    )
    
    mcp_server = MCPServerConfig(
        name="test-server",
        description="Test server",
        transport=transport,
        tools=["test_tool"]
    )
    
    profile = ProfileConfig(
        metadata=metadata,
        mcpServers=[mcp_server]
    )
    
    print(f"✓ Created profile: {profile.metadata.name}")
    print(f"  - API Version: {profile.apiVersion}")
    print(f"  - Kind: {profile.kind}")
    print(f"  - MCP Servers: {len(profile.mcpServers)}")
    
    return True

def test_profile_yaml():
    """Test loading our example profile."""
    print("\nTesting profile YAML loading...")
    
    import yaml
    from engine.models import ProfileConfig
    
    profile_path = Path("profiles/default.yaml")
    if not profile_path.exists():
        print(f"✗ Profile file not found: {profile_path}")
        return False
    
    try:
        with open(profile_path, 'r') as f:
            profile_data = yaml.safe_load(f)
        
        profile = ProfileConfig(**profile_data)
        
        print(f"✓ Loaded profile: {profile.metadata.name}")
        print(f"  - Description: {profile.metadata.description}")
        print(f"  - MCP Servers: {len(profile.mcpServers)}")
        print(f"  - Providers: {len(profile.providers)}")
        print(f"  - Model Overrides: {len(profile.modelOverrides)}")
        
        # Print MCP server names
        for server in profile.mcpServers:
            print(f"    - MCP Server: {server.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading profile: {e}")
        return False

def test_profile_router_functions():
    """Test the router functions without FastAPI."""
    print("\nTesting profile router functions...")
    
    from engine.routers.profiles import load_profile_from_file, get_profile_path
    
    try:
        # Test path generation
        path = get_profile_path("default")
        print(f"✓ Profile path: {path}")
        
        # Test loading
        profile = load_profile_from_file("default")
        print(f"✓ Loaded profile via router: {profile.metadata.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in router functions: {e}")
        return False

def main():
    """Run all tests."""
    print("CrewAI Profile System Test")
    print("=" * 30)
    
    tests = [
        test_profile_models,
        test_profile_yaml,
        test_profile_router_functions,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 30)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All profile system tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())