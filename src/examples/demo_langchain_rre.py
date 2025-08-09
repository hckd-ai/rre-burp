#!/usr/bin/env python3
"""
Demo Script for LangChain RRE Integration
-----------------------------------------

This script demonstrates the various capabilities of the LangChain RRE integration,
including traffic analysis, exploit chain generation, and natural language querying.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our LangChain RRE integration
from langchain_rre import (
    TrafficIntelligenceChain,
    AutomatedExploitChain,
    TrafficQueryChain,
    HARCollectorTool
)

def demo_traffic_intelligence():
    """Demonstrate the Traffic Intelligence Chain"""
    print("\n🔍 Demo: Traffic Intelligence Chain")
    print("=" * 50)
    
    # Initialize the chain
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    traffic_intelligence = TrafficIntelligenceChain(openai_api_key)
    
    # Example queries
    queries = [
        "Analyze the yeahscore_stream.har file for security vulnerabilities",
        "What authentication mechanisms are used in this traffic?",
        "Identify potential API security issues in this traffic"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        try:
            # Note: This would normally analyze the HAR file
            # For demo purposes, we'll show the structure
            print("This would trigger the Traffic Intelligence Chain to:")
            print("1. Load and parse the HAR file")
            print("2. Analyze traffic patterns using RRE")
            print("3. Generate AI-powered insights")
            print("4. Provide actionable security recommendations")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_exploit_chain():
    """Demonstrate the Automated Exploit Chain"""
    print("\n⚡ Demo: Automated Exploit Chain")
    print("=" * 50)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    exploit_chain = AutomatedExploitChain(openai_api_key)
    
    # Check if HAR file exists
    har_path = "yeahscore_stream.har"
    if not Path(har_path).exists():
        print(f"❌ HAR file not found: {har_path}")
        print("Please ensure you have a HAR file to analyze")
        return
    
    try:
        print(f"📁 Loading HAR data from: {har_path}")
        exploit_chain.load_har_data(har_path)
        print("✅ HAR data loaded successfully")
        
        # Generate different types of exploit chains
        target_types = ["general", "authentication", "data_exfiltration"]
        
        for target_type in target_types:
            print(f"\n🎯 Generating {target_type} exploit chains...")
            print("-" * 40)
            
            try:
                result = exploit_chain.generate_exploit_chains(target_type)
                print(f"Generated exploit chains for {target_type}:")
                print(result[:500] + "..." if len(result) > 500 else result)
                
            except Exception as e:
                print(f"❌ Error generating {target_type} exploit chains: {e}")
                
    except Exception as e:
        print(f"❌ Error loading HAR data: {e}")

def demo_traffic_query():
    """Demonstrate the Traffic Query Chain"""
    print("\n❓ Demo: Traffic Query Chain")
    print("=" * 50)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    traffic_query = TrafficQueryChain(openai_api_key)
    
    # Check if HAR file exists
    har_path = "yeahscore_stream.har"
    if not Path(har_path).exists():
        print(f"❌ HAR file not found: {har_path}")
        print("Please ensure you have a HAR file to analyze")
        return
    
    try:
        print(f"📁 Loading HAR file: {har_path}")
        traffic_query.load_har(har_path)
        print("✅ HAR file loaded successfully")
        
        # Example questions
        questions = [
            "What API endpoints are exposed in this traffic?",
            "How many external services are contacted?",
            "What types of authentication tokens are used?",
            "Are there any high-entropy values that might be sensitive?",
            "What is the overall structure of the API calls?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Question {i}: {question}")
            print("-" * 40)
            
            try:
                result = traffic_query.query_traffic(question)
                print("Answer:")
                print(result[:300] + "..." if len(result) > 300 else result)
                
            except Exception as e:
                print(f"❌ Error querying traffic: {e}")
                
    except Exception as e:
        print(f"❌ Error loading HAR file: {e}")

def demo_har_collection():
    """Demonstrate HAR collection capabilities"""
    print("\n📡 Demo: HAR Collection Tool")
    print("=" * 50)
    
    har_collector = HARCollectorTool()
    
    # Example URLs to collect from (replace with actual targets)
    example_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers"
    ]
    
    print("This would demonstrate collecting HAR files from web pages:")
    print("1. Launch browser automation")
    print("2. Navigate to target URLs")
    print("3. Capture all network traffic")
    print("4. Save as HAR file for analysis")
    
    print(f"\nExample collection commands:")
    for url in example_urls:
        print(f"har_collector._run('{url}', 'demo_{url.split('//')[1].replace('/', '_')}.har')")
    
    print("\n⚠️  Note: Actual collection requires valid URLs and may take time")

def demo_integrated_workflow():
    """Demonstrate an integrated workflow"""
    print("\n🔄 Demo: Integrated Workflow")
    print("=" * 50)
    
    print("Complete workflow demonstration:")
    print("1. 🎯 Collect HAR from target application")
    print("2. 🔍 Analyze traffic patterns with RRE")
    print("3. 🤖 Generate AI-powered security insights")
    print("4. ⚡ Identify potential exploit chains")
    print("5. ❓ Query traffic data naturally")
    print("6. 📊 Generate comprehensive security report")
    
    print("\nThis workflow combines all the tools:")
    print("- HAR Collector: Automated traffic capture")
    print("- RRE Analyzer: Pattern recognition and dependency mapping")
    print("- Traffic Intelligence: AI-powered analysis")
    print("- Exploit Chain Generator: Automated vulnerability assessment")
    print("- Traffic Query: Natural language exploration")

def main():
    """Main demo function"""
    print("🚀 LangChain RRE Integration Demo")
    print("=" * 60)
    
    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("✅ OpenAI API key found")
    print(f"🔑 Key preview: {openai_api_key[:20]}...")
    
    # Run demos
    demo_traffic_intelligence()
    demo_exploit_chain()
    demo_traffic_query()
    demo_har_collection()
    demo_integrated_workflow()
    
    print("\n🎉 Demo completed!")
    print("\n📚 Next steps:")
    print("1. Install dependencies: pip install -r requirements_langchain.txt")
    print("2. Run the main integration: python langchain_rre.py")
    print("3. Use the interactive chains for your own analysis")
    print("4. Customize prompts and analysis for your specific needs")

if __name__ == "__main__":
    main() 