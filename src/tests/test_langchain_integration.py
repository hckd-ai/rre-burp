#!/usr/bin/env python3
"""
Test Script for LangChain RRE Integration
-----------------------------------------

This script tests the basic functionality of the LangChain RRE integration
to ensure all components are working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from langchain_rre import (
            TrafficIntelligenceChain,
            AutomatedExploitChain,
            TrafficQueryChain,
            HARCollectorTool
        )
        print("✅ All LangChain RRE modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config_langchain import get_config, update_config
        
        config = get_config()
        print(f"✅ Configuration loaded: {config.openai_model}")
        
        # Test configuration update
        update_config(openai_temperature=0.2)
        updated_config = get_config()
        if updated_config.openai_temperature == 0.2:
            print("✅ Configuration update successful")
        else:
            print("❌ Configuration update failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_openai_key():
    """Test OpenAI API key availability"""
    print("\n🔑 Testing OpenAI API key...")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    if len(openai_api_key) < 20:
        print("❌ OPENAI_API_KEY appears to be invalid (too short)")
        return False
    
    print(f"✅ OpenAI API key found: {openai_api_key[:20]}...")
    return True

def test_har_file():
    """Test if HAR file exists for analysis"""
    print("\n📁 Testing HAR file availability...")
    
    har_path = Path("yeahscore_stream.har")
    if not har_path.exists():
        print("❌ HAR file not found: yeahscore_stream.har")
        print("   This will prevent some tests from running")
        return False
    
    file_size = har_path.stat().st_size
    print(f"✅ HAR file found: {har_path} ({file_size:,} bytes)")
    return True

def test_basic_functionality():
    """Test basic functionality without OpenAI calls"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from langchain_rre import HARCollectorTool, RREAnalysisTool
        
        # Test HAR collector tool
        har_collector = HARCollectorTool()
        print("✅ HAR Collector Tool created successfully")
        
        # Test RRE analysis tool
        rre_tool = RREAnalysisTool()
        print("✅ RRE Analysis Tool created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        return False

def test_chain_initialization():
    """Test chain initialization (without making API calls)"""
    print("\n🚀 Testing chain initialization...")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Cannot test chains without OpenAI API key")
        return False
    
    try:
        from langchain_rre import (
            TrafficIntelligenceChain,
            AutomatedExploitChain,
            TrafficQueryChain
        )
        
        # Test Traffic Intelligence Chain
        traffic_intelligence = TrafficIntelligenceChain(openai_api_key)
        print("✅ Traffic Intelligence Chain initialized")
        
        # Test Automated Exploit Chain
        exploit_chain = AutomatedExploitChain(openai_api_key)
        print("✅ Automated Exploit Chain initialized")
        
        # Test Traffic Query Chain
        traffic_query = TrafficQueryChain(openai_api_key)
        print("✅ Traffic Query Chain initialized")
        
        return True
    except Exception as e:
        print(f"❌ Chain initialization error: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        "langchain",
        "langchain_openai", 
        "langchain_core",
        "openai",
        "playwright"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements_langchain.txt")
        return False
    
    print("✅ All required packages available")
    return True

def run_integration_test():
    """Run a basic integration test if HAR file is available"""
    print("\n🔄 Running integration test...")
    
    har_path = Path("yeahscore_stream.har")
    if not har_path.exists():
        print("❌ Skipping integration test - no HAR file available")
        return False
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Skipping integration test - no OpenAI API key")
        return False
    
    try:
        from langchain_rre import TrafficQueryChain
        
        # Initialize chain
        traffic_query = TrafficQueryChain(openai_api_key)
        
        # Load HAR file
        print("📁 Loading HAR file...")
        traffic_query.load_har("yeahscore_stream.har")
        print("✅ HAR file loaded successfully")
        
        # Test a simple query
        print("❓ Testing traffic query...")
        result = traffic_query.query_traffic("How many total requests are in this traffic?")
        
        if result and len(result) > 10:
            print("✅ Traffic query successful")
            print(f"   Response preview: {result[:100]}...")
            return True
        else:
            print("❌ Traffic query failed or returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 LangChain RRE Integration Test Suite")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("OpenAI Key", test_openai_key),
        ("HAR File", test_har_file),
        ("Basic Functionality", test_basic_functionality),
        ("Chain Initialization", test_chain_initialization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Run integration test if basic tests passed
    if passed == total:
        print(f"\n🎯 Basic tests passed ({passed}/{total}), running integration test...")
        if run_integration_test():
            passed += 1
            total += 1
    
    # Summary
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LangChain RRE integration is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Run the demo: python demo_langchain_rre.py")
        print("2. Try the main integration: python langchain_rre.py")
        print("3. Start analyzing your HAR files!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements_langchain.txt")
        print("2. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("3. Ensure you have a HAR file for testing")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 