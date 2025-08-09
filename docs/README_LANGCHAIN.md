# LangChain RRE Integration

A powerful LangChain application that integrates the RRE (Request Response Explorer) and HAR collector functionality with OpenAI-powered analysis and automation for cybersecurity research and web traffic investigation.

## 🚀 Features

### Core Capabilities
- **Automated HAR Collection**: Browser automation for capturing web traffic
- **AI-Powered Traffic Analysis**: OpenAI integration for intelligent pattern recognition
- **Intelligent Seed Discovery**: Automatic identification of potential analysis targets
- **Dependency Mapping**: Recursive analysis of request-response relationships
- **Exploit Chain Generation**: Automated vulnerability assessment and exploit chain creation
- **Natural Language Querying**: Ask questions about traffic data in plain English

### Advanced Analysis
- **Pattern Recognition**: AI-powered identification of security-relevant patterns
- **Authentication Analysis**: Deep dive into authentication mechanisms and tokens
- **API Security Assessment**: Comprehensive API endpoint security analysis
- **Vulnerability Scanning**: Automated detection of common security issues
- **Business Logic Analysis**: Identification of application logic flaws

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- OpenAI API key
- Playwright (for HAR collection)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rre-burp
   ```

2. **Install dependencies**
   ```bash
   # Install LangChain dependencies
   pip install -r requirements_langchain.txt
   
   # Install Playwright
   playwright install chromium
   ```

3. **Configure OpenAI API key**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   
   # Or export in shell
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 📖 Usage

### Quick Start

```python
from langchain_rre import TrafficIntelligenceChain, AutomatedExploitChain

# Initialize chains
traffic_intelligence = TrafficIntelligenceChain(openai_api_key)
exploit_chain = AutomatedExploitChain(openai_api_key)

# Analyze traffic
result = traffic_intelligence.analyze_traffic("Analyze this traffic for security vulnerabilities")

# Generate exploit chains
exploit_chain.load_har_data("yeahscore_stream.har")
exploits = exploit_chain.generate_exploit_chains("authentication")
```

### Command Line Usage

```bash
# Run the demo
python demo_langchain_rre.py

# Run the main integration
python langchain_rre.py

# Run with configuration
python config_langchain.py
```

## 🔧 Components

### 1. Traffic Intelligence Chain
The main analysis chain that combines HAR collection and RRE analysis with AI-powered insights.

```python
from langchain_rre import TrafficIntelligenceChain

chain = TrafficIntelligenceChain(openai_api_key)
result = chain.analyze_traffic("What authentication mechanisms are used?")
```

**Features:**
- Natural language traffic analysis
- Automated HAR collection
- Pattern recognition and dependency mapping
- Security vulnerability identification

### 2. Automated Exploit Chain
Generates potential exploit chains based on traffic analysis.

```python
from langchain_rre import AutomatedExploitChain

chain = AutomatedExploitChain(openai_api_key)
chain.load_har_data("traffic.har")
exploits = chain.generate_exploit_chains("authentication")
```

**Target Types:**
- `general`: Overall security analysis
- `authentication`: Auth bypass and privilege escalation
- `data_exfiltration`: Data exposure and extraction

### 3. Traffic Query Chain
Natural language querying of traffic data.

```python
from langchain_rre import TrafficQueryChain

chain = TrafficQueryChain(openai_api_key)
chain.load_har("traffic.har")
answer = chain.query_traffic("What API endpoints are exposed?")
```

**Example Questions:**
- "How many external services are contacted?"
- "What types of authentication tokens are used?"
- "Are there any high-entropy values that might be sensitive?"

### 4. HAR Collection Tool
Automated HAR file collection from web applications.

```python
from langchain_rre import HARCollectorTool

collector = HARCollectorTool()
result = collector._run(
    url="https://example.com",
    output_path="collected.har",
    wait_time=5.0,
    headful=False
)
```

## ⚙️ Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-api-key
LANGCHAIN_MODEL=gpt-4-turbo-preview
LANGCHAIN_TEMPERATURE=0.1

# RRE Configuration
RRE_ENTROPY_THRESHOLD=3.0
RRE_MAX_DEPTH=10
```

### Configuration File
Create `config.yaml`:

```yaml
# OpenAI Configuration
openai_model: "gpt-4-turbo-preview"
openai_temperature: 0.1

# RRE Analysis Configuration
entropy_threshold: 3.0
max_analysis_depth: 10

# Analysis Modes
enabled_analysis_modes:
  - pattern_recognition
  - dependency_mapping
  - vulnerability_scanning
  - api_analysis
  - authentication_analysis
```

## 🔍 Analysis Examples

### 1. Authentication Analysis
```python
# Analyze authentication mechanisms
result = traffic_intelligence.analyze_traffic(
    "Analyze the authentication flow in this traffic. "
    "Look for token generation, validation, and potential bypasses."
)
```

### 2. API Security Assessment
```python
# Assess API security
result = traffic_intelligence.analyze_traffic(
    "Review all API endpoints for security vulnerabilities. "
    "Check for proper authentication, authorization, and input validation."
)
```

### 3. Dependency Chain Analysis
```python
# Trace dependencies
exploit_chain.load_har_data("traffic.har")
result = exploit_chain.generate_exploit_chains("general")
```

## 📊 Output and Reports

### Analysis Reports
The system generates comprehensive reports including:
- Traffic pattern summaries
- Security vulnerability assessments
- Exploit chain recommendations
- API endpoint analysis
- Authentication mechanism review

### Output Formats
- **Console Output**: Real-time analysis results
- **Structured Data**: JSON-formatted analysis data
- **Natural Language**: Human-readable security insights
- **Actionable Recommendations**: Specific steps for further investigation

## 🚨 Security Considerations

### Ethical Usage
- **Authorized Testing Only**: Only test applications you own or have explicit permission to test
- **Responsible Disclosure**: Report vulnerabilities through proper channels
- **Legal Compliance**: Ensure compliance with applicable laws and regulations

### Data Handling
- **Sensitive Data**: Be cautious with captured authentication tokens and sensitive information
- **Data Retention**: Implement appropriate data retention policies
- **Access Control**: Restrict access to captured traffic data

## 🔧 Customization

### Custom Patterns
Add custom pattern recognition:

```python
from config_langchain import update_config

update_config(
    custom_patterns={
        "custom_token": r"your-regex-pattern",
        "business_id": r"\b[A-Z]{2}\d{6}\b"
    }
)
```

### Custom Analysis Modes
Extend analysis capabilities:

```python
# Add custom analysis mode
config = get_config()
config.enabled_analysis_modes.append("custom_analysis")
```

## 📚 Examples

### Complete Workflow Example

```python
from langchain_rre import (
    TrafficIntelligenceChain,
    AutomatedExploitChain,
    HARCollectorTool
)

# 1. Collect HAR
collector = HARCollectorTool()
collector._run("https://target-app.com", "captured.har")

# 2. Analyze with AI
intelligence = TrafficIntelligenceChain(openai_api_key)
analysis = intelligence.analyze_traffic("Analyze for security issues")

# 3. Generate exploit chains
exploit = AutomatedExploitChain(openai_api_key)
exploit.load_har_data("captured.har")
chains = exploit.generate_exploit_chains("authentication")

# 4. Review results
print("Analysis:", analysis)
print("Exploit Chains:", chains)
```

### Interactive Analysis

```python
# Interactive traffic analysis
while True:
    question = input("Ask about the traffic (or 'quit' to exit): ")
    if question.lower() == 'quit':
        break
    
    result = traffic_query.query_traffic(question)
    print(f"\nAnswer: {result}\n")
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   # Ensure API key is set
   export OPENAI_API_KEY="your-key"
   # Or check .env file
   cat .env
   ```

2. **Playwright Installation Issues**
   ```bash
   # Reinstall Playwright
   pip uninstall playwright
   pip install playwright
   playwright install chromium
   ```

3. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install -r requirements_langchain.txt
   ```

### Debug Mode
Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for all functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **RRE Project**: Built on the Request Response Explorer framework
- **LangChain**: AI application framework
- **OpenAI**: AI model provider
- **Playwright**: Browser automation framework

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review example code
- Join the community discussions

---

**⚠️ Disclaimer**: This tool is for authorized security testing and research purposes only. Always ensure you have proper authorization before testing any application or system. 