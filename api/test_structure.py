#!/usr/bin/env python3
"""
Test script to verify the API structure is correct.
This validates imports and basic structure without requiring full dependencies.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        print("  - Importing models...")
        from models import (
            Provider, Model, Workflow, Agent, Task,
            StartWorkflowRequest, ErrorResponse
        )
        print("    ✓ Models imported successfully")
        
        print("  - Importing config...")
        from config import settings
        print(f"    ✓ Config loaded (API base URL: {settings.api_base_url})")
        
        print("  - Importing routers...")
        from routers import providers, models, workflows, chat, yaml_validator
        print("    ✓ All routers imported successfully")
        
        return True
    except ImportError as e:
        print(f"    ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False


def test_model_validation():
    """Test Pydantic model validation."""
    print("\nTesting model validation...")
    
    try:
        from models import Provider, Agent
        
        # Test Provider creation
        provider = Provider(
            name="Test Provider",
            type="openai",
            models=[]
        )
        print(f"  ✓ Provider model validated: {provider.name}")
        
        # Test Agent creation
        agent = Agent(
            name="Test Agent",
            role="Tester",
            goal="Test the system",
            backstory="A test agent",
            model="gpt-4"
        )
        print(f"  ✓ Agent model validated: {agent.name}")
        
        return True
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
        return False


def test_router_structure():
    """Test that routers are properly structured."""
    print("\nTesting router structure...")
    
    try:
        from routers import providers, models, workflows, chat, yaml_validator
        
        routers = [
            ("providers", providers.router),
            ("models", models.router),
            ("workflows", workflows.router),
            ("chat", chat.router),
            ("yaml_validator", yaml_validator.router),
        ]
        
        for name, router in routers:
            print(f"  ✓ Router '{name}' has prefix: {router.prefix}")
        
        return True
    except Exception as e:
        print(f"  ✗ Router error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("API Structure Tests")
    print("=" * 60)
    
    results = {
        "imports": test_imports(),
        "validation": test_model_validation(),
        "routers": test_router_structure(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
