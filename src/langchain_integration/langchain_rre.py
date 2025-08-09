#!/usr/bin/env python3
"""
LangChain RRE Integration
-------------------------

A LangChain application that integrates the RRE (Request Response Explorer) 
and HAR collector functionality with OpenAI-powered analysis and automation.

Features:
- Automated HAR collection with intelligent waiting
- AI-powered traffic analysis and pattern recognition
- Intelligent seed discovery and dependency mapping
- Automated exploit chain generation
- Natural language querying of traffic data
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, SequentialChain
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import our existing RRE functionality
from ..rre_core.rre_enhanced import EnhancedRREAnalyzer
from ..rre_core.har_collect import collect_har

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HARCollectorTool(BaseTool):
    """Tool for collecting HAR files from URLs"""
    
    name: str = "har_collector"
    description: str = "Collects HAR (HTTP Archive) files from web pages using browser automation"
    
    def _run(self, url: str, output_path: str = None, wait_time: float = 5.0, headful: bool = False) -> str:
        """Collect HAR from a URL"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"collected_{timestamp}.har"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Collecting HAR from {url}")
            result = collect_har(
                url=url,
                out_path=output_path,
                headful=headful,
                wait_seconds=wait_time,
                user_agent=None,
                extra_headers={},
                timeout_ms=45000
            )
            
            if result == 0:
                return f"Successfully collected HAR from {url} to {output_path}"
            else:
                return f"Failed to collect HAR from {url}"
                
        except Exception as e:
            return f"Error collecting HAR: {str(e)}"
    
    async def _arun(self, url: str, output_path: str = None, wait_time: float = 5.0, headful: bool = False) -> str:
        """Async version of HAR collection"""
        return self._run(url, output_path, wait_time, headful)

class RREAnalysisTool(BaseTool):
    """Tool for analyzing HAR files using RRE"""
    
    name: str = "rre_analyzer"
    description: str = "Analyzes HAR files using the RRE (Request Response Explorer) to find patterns, dependencies, and potential exploit chains"
    
    def _run(self, har_path: str, mode: str = "analyze", seed_value: str = None, auto_discover: bool = False) -> str:
        """Analyze HAR file using RRE"""
        try:
            har_path = Path(har_path)
            if not har_path.exists():
                return f"HAR file not found: {har_path}"
            
            analyzer = EnhancedRREAnalyzer(har_path)
            analyzer.load_har_entries()
            
            if mode == "analyze" or auto_discover:
                # Capture the output
                import io
                import sys
                
                # Redirect stdout to capture output
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout
                
                try:
                    if auto_discover:
                        seeds = analyzer.auto_discover_seeds()
                        analyzer.analyze_patterns()
                    else:
                        analyzer.analyze_patterns()
                finally:
                    sys.stdout = old_stdout
                
                output = new_stdout.getvalue()
                return output
                
            elif mode == "trace" and seed_value:
                # Capture trace output
                import io
                import sys
                
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout
                
                try:
                    analyzer.enhanced_full_walkback_chain(seed_value)
                finally:
                    sys.stdout = old_stdout
                
                output = new_stdout.getvalue()
                return output
            else:
                return "Invalid mode. Use 'analyze', 'trace', or set auto_discover=True"
                
        except Exception as e:
            return f"Error analyzing HAR: {str(e)}"
    
    async def _arun(self, har_path: str, mode: str = "analyze", seed_value: str = None, auto_discover: bool = False) -> str:
        """Async version of RRE analysis"""
        return self._run(har_path, mode, seed_value, auto_discover)

class TrafficIntelligenceChain:
    """LangChain for intelligent traffic analysis"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        self.tools = [
            HARCollectorTool(),
            RREAnalysisTool()
        ]
        
        # Create the agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the agent prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert cybersecurity analyst and web traffic investigator. 
            You have access to tools for collecting HAR files and analyzing them using RRE (Request Response Explorer).
            
            Your capabilities include:
            1. Collecting HAR files from web pages using browser automation
            2. Analyzing traffic patterns, dependencies, and potential security issues
            3. Discovering API endpoints, authentication mechanisms, and data flows
            4. Identifying potential exploit chains and security vulnerabilities
            
            Always provide clear, actionable insights and explain your findings in detail.
            When analyzing traffic, look for:
            - Authentication mechanisms and tokens
            - API endpoints and their security
            - Data dependencies and relationships
            - Potential injection points
            - Information disclosure vulnerabilities
            """),
            ("human", "{input}"),
            ("human", "Chat History: {chat_history}"),
        ])
    
    def analyze_traffic(self, query: str) -> str:
        """Analyze traffic based on a natural language query"""
        try:
            # Add memory to the input
            input_with_memory = {
                "input": query,
                "chat_history": self.memory.chat_memory.messages
            }
            
            result = self.agent_executor.invoke(input_with_memory)
            
            # Update memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(result["output"])
            
            return result["output"]
            
        except Exception as e:
            logger.error(f"Error in traffic analysis: {e}")
            return f"Error analyzing traffic: {str(e)}"

class AutomatedExploitChain:
    """LangChain for automated exploit chain generation"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2,
            openai_api_key=openai_api_key
        )
        
        self.analyzer = None
        self.har_data = None
    
    def load_har_data(self, har_path: str) -> None:
        """Load and prepare HAR data for analysis"""
        try:
            self.analyzer = EnhancedRREAnalyzer(Path(har_path))
            self.analyzer.load_har_entries()
            
            # Extract key information for the LLM
            self.har_data = {
                "total_entries": self.analyzer.stats['total_entries'],
                "api_calls": self.analyzer.stats['api_calls'],
                "external_services": list(self.analyzer.stats['external_services']),
                "high_entropy_values": self.analyzer.stats['high_entropy_values']
            }
            
        except Exception as e:
            logger.error(f"Error loading HAR data: {e}")
            raise
    
    def generate_exploit_chains(self, target_type: str = "general") -> str:
        """Generate potential exploit chains based on the traffic analysis"""
        
        if not self.har_data:
            return "No HAR data loaded. Please load a HAR file first."
        
        # Create specialized prompts for different target types
        if target_type == "authentication":
            prompt = PromptTemplate(
                input_variables=["har_data"],
                template="""
                Based on the following HAR traffic data, identify potential authentication bypass or privilege escalation vectors:
                
                {har_data}
                
                Analyze the traffic for:
                1. Authentication mechanisms and tokens
                2. Session management patterns
                3. Authorization bypass opportunities
                4. Token manipulation possibilities
                5. Session fixation vulnerabilities
                
                Provide specific, actionable exploit chains with step-by-step instructions.
                """
            )
        elif target_type == "data_exfiltration":
            prompt = PromptTemplate(
                input_variables=["har_data"],
                template="""
                Based on the following HAR traffic data, identify potential data exfiltration vectors:
                
                {har_data}
                
                Analyze the traffic for:
                1. Sensitive data exposure in responses
                2. API endpoints with excessive data return
                3. Information disclosure vulnerabilities
                4. Parameter pollution opportunities
                5. Mass assignment vulnerabilities
                
                Provide specific, actionable exploit chains with step-by-step instructions.
                """
            )
        else:
            prompt = PromptTemplate(
                input_variables=["har_data"],
                template="""
                Based on the following HAR traffic data, identify potential security vulnerabilities and exploit chains:
                
                {har_data}
                
                Analyze the traffic for:
                1. Injection vulnerabilities (SQL, XSS, Command)
                2. Authentication and authorization issues
                3. Information disclosure
                4. Business logic flaws
                5. API security weaknesses
                
                Provide specific, actionable exploit chains with step-by-step instructions.
                """
            )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(har_data=json.dumps(self.har_data, indent=2))
            return result
        except Exception as e:
            logger.error(f"Error generating exploit chains: {e}")
            return f"Error generating exploit chains: {str(e)}"

class TrafficQueryChain:
    """LangChain for natural language querying of traffic data"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        self.analyzer = None
    
    def load_har(self, har_path: str) -> None:
        """Load HAR file for querying"""
        self.analyzer = EnhancedRREAnalyzer(Path(har_path))
        self.analyzer.load_har_entries()
    
    def query_traffic(self, question: str) -> str:
        """Answer questions about the traffic data"""
        
        if not self.analyzer:
            return "No HAR data loaded. Please load a HAR file first."
        
        # Extract relevant traffic information
        traffic_summary = {
            "total_requests": self.analyzer.stats['total_entries'],
            "api_endpoints": self.analyzer.discover_api_endpoints(),
            "high_entropy_values": self.analyzer.extract_high_entropy_values()[:20],  # Top 20
            "external_services": list(self.analyzer.stats['external_services'])
        }
        
        prompt = PromptTemplate(
            input_variables=["question", "traffic_data"],
            template="""
            You are analyzing web traffic data. Answer the following question based on the traffic information:
            
            Question: {question}
            
            Traffic Data:
            {traffic_data}
            
            Provide a comprehensive answer with specific details from the traffic data.
            If the question cannot be answered with the available data, explain what additional information would be needed.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(
                question=question,
                traffic_data=json.dumps(traffic_summary, indent=2, default=str)
            )
            return result
        except Exception as e:
            logger.error(f"Error querying traffic: {e}")
            return f"Error querying traffic: {str(e)}"

def main():
    """Main function to demonstrate the LangChain RRE integration"""
    
    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        return
    
    print("🚀 LangChain RRE Integration")
    print("=" * 50)
    
    # Initialize the chains
    traffic_intelligence = TrafficIntelligenceChain(openai_api_key)
    exploit_chain = AutomatedExploitChain(openai_api_key)
    traffic_query = TrafficQueryChain(openai_api_key)
    
    print("✅ All chains initialized successfully")
    print("\nAvailable functionality:")
    print("1. Traffic Intelligence Chain - AI-powered traffic analysis")
    print("2. Automated Exploit Chain - Generate exploit chains")
    print("3. Traffic Query Chain - Natural language traffic queries")
    print("4. HAR Collection - Automated traffic capture")
    
    # Example usage
    print("\n📝 Example usage:")
    print("traffic_intelligence.analyze_traffic('Analyze this traffic for security vulnerabilities')")
    print("exploit_chain.load_har_data('yeahscore_stream.har')")
    print("exploit_chain.generate_exploit_chains('authentication')")
    print("traffic_query.load_har('yeahscore_stream.har')")
    print("traffic_query.query_traffic('What API endpoints are exposed?')")
    
    return {
        "traffic_intelligence": traffic_intelligence,
        "exploit_chain": exploit_chain,
        "traffic_query": traffic_query
    }

if __name__ == "__main__":
    chains = main() 