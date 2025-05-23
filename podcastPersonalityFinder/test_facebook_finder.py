#!/usr/bin/env python3
"""
Simple test script for Facebook Group Finder to verify the tool structure works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from crewai import Agent, Task, Crew, Process
        print("✓ CrewAI imports successful")
        
        # Test config import
        import config
        print("✓ Config import successful")
        
        # Test search tools import
        from usefulTools.search_tools import facebook_serper_tool
        print("✓ Facebook SerperTool import successful")
        
        # Test LLM import
        try:
            from usefulTools.llm_repository import ClaudeSonnet
            print("✓ Claude Sonnet LLM import successful")
        except Exception as e:
            print(f"⚠ Claude Sonnet LLM import failed (expected if no API key): {e}")
        
        print("\n🎉 All essential imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_facebook_finder_structure():
    """Test the structure of the Facebook finder without running it"""
    try:
        print("\nTesting Facebook Group Finder structure...")
        
        # Import the main module
        from facebookGroupFinder import research_focuses
        print("✓ Facebook Group Finder module loaded")
        
        print(f"✓ Research focuses defined: {len(research_focuses)} areas")
        for i, focus in enumerate(research_focuses, 1):
            lines = focus.strip().split('\n')
            title = lines[1].strip() if len(lines) > 1 else "Unknown"
            print(f"  {i}. {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

def test_serper_tool():
    """Test the Serper tool configuration"""
    try:
        print("\nTesting Serper tool configuration...")
        
        from usefulTools.search_tools import facebook_serper_tool, serper_search
        print("✓ Serper tools imported successfully")
        
        # Test basic configuration
        print(f"✓ Facebook Serper tool type: {type(facebook_serper_tool)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Serper tool test failed: {e}")
        return False

if __name__ == "__main__":
    print("Facebook Group Finder - Test Suite")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_facebook_finder_structure() 
    all_tests_passed &= test_serper_tool()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Facebook Group Finder is ready to use.")
        print("\nTo run the full Facebook Group Finder:")
        print("1. Set up your ANTHROPIC_API_KEY environment variable")
        print("2. Run: python facebookGroupFinder.py")
    else:
        print("❌ Some tests failed. Please check the issues above.")
