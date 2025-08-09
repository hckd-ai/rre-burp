# RRE Burp - Request Response Explorer with AI Integration

A comprehensive toolkit for analyzing web traffic using RRE components integrated with LangChain for intelligent analysis.

## 🏗️ Project Structure

```
rre-burp/
├── src/                          # Source code
│   ├── rre_core/                # Core RRE components
│   │   ├── __init__.py
│   │   ├── rre.py              # Basic RRE implementation
│   │   ├── rre_enhanced.py     # Enhanced RRE with AI analysis
│   │   ├── rre_standalone.py   # Standalone RRE script
│   │   ├── rre_intelligent_analyzer.py  # AI-powered analyzer
│   │   ├── rre_explore.py      # RRE exploration tools
│   │   └── har_collect.py      # HAR collection utilities
│   │
│   ├── langchain_integration/   # LangChain integration
│   │   ├── __init__.py
│   │   ├── langchain_rre.py    # Main LangChain integration
│   │   └── config_langchain.py # LangChain configuration
│   │
│   ├── site_explorer/          # Intelligent site exploration
│   │   ├── __init__.py
│   │   └── intelligent_explorer.py
│   │
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   └── site_explorer_config.py
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   └── web_helpers.py
│   │
│   ├── analysis/               # Analysis tools
│   │   └── __init__.py
│   │
│   ├── examples/               # Example scripts
│   │   ├── __init__.py
│   │   ├── demo_langchain_rre.py
│   │   └── compare_approaches.py
│   │
│   ├── tests/                  # Test files
│   │   ├── __init__.py
│   │   └── test_langchain_integration.py
│   │
│   ├── __init__.py             # Main package exports
│   └── site_explorer_cli.py    # CLI interface
│
├── docs/                       # Documentation
│   ├── README.md              # This file
│   ├── README_LANGCHAIN.md    # LangChain integration docs
│   ├── README_ENHANCED_RRE.md # Enhanced RRE docs
│   └── README_SITE_EXPLORER.md # Site explorer docs
│
├── data/                       # Data files
│   ├── test_sites.json        # Test site definitions
│   └── yeahscore_stream.har   # Example HAR file
│
├── .env                        # Environment variables
├── pyproject.toml             # Project configuration
├── requirements_langchain.txt # Python dependencies
└── uv.lock                    # Dependency lock file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/farzan/rre-burp.git
   cd rre-burp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_langchain.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

### Basic Usage

#### Using the Site Explorer CLI
```bash
# Explore a single site
python -m src.site_explorer_cli explore https://example.com

# Run against test sites
python -m src.site_explorer_cli test-sites

# Create default configuration
python -m src.site_explorer_cli create-config
```

#### Using the LangChain Integration
```python
from src import TrafficIntelligenceChain, HARCollectorTool

# Initialize the chain
chain = TrafficIntelligenceChain()

# Analyze traffic
result = chain.run("Analyze this HAR file for security vulnerabilities")
```

#### Using Core RRE Components
```python
from src import RREEnhanced, HARCollector

# Collect HAR data
collector = HARCollector()
har_data = collector.collect("https://example.com")

# Analyze with RRE
rre = RREEnhanced()
analysis = rre.analyze(har_data)
```

## 🔧 Components

### Core RRE (`src/rre_core/`)
- **RREEnhanced**: Advanced RRE with AI-powered analysis
- **HARCollector**: Playwright-based HAR collection
- **RREStandalone**: Standalone RRE implementation
- **RREIntelligentAnalyzer**: AI-driven traffic analysis

### LangChain Integration (`src/langchain_integration/`)
- **HARCollectorTool**: LangChain tool for HAR collection
- **RREAnalysisTool**: LangChain tool for RRE analysis
- **TrafficIntelligenceChain**: AI-powered traffic analysis chain
- **AutomatedExploitChain**: Automated vulnerability detection

### Site Explorer (`src/site_explorer/`)
- **IntelligentSiteExplorer**: Smart web exploration with obstacle handling
- Cookie consent management
- Ad overlay handling
- Video content detection
- Intelligent scrolling and waiting

### Configuration (`src/config/`)
- **SiteExplorerConfig**: Centralized configuration management
- YAML-based configuration files
- Environment variable support

### Utilities (`src/utils/`)
- **Web Helpers**: Common web interaction utilities
- Page stability detection
- Element finding and clicking
- Video content detection

## 📚 Documentation

- **[LangChain Integration](docs/README_LANGCHAIN.md)**: Complete guide to using RRE with LangChain
- **[Enhanced RRE](docs/README_ENHANCED_RRE.md)**: Advanced RRE features and usage
- **[Site Explorer](docs/README_SITE_EXPLORER.md)**: Intelligent site exploration guide

## 🧪 Testing

Run the test suite:
```bash
python -m pytest src/tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/farzan/rre-burp/issues)
- **Documentation**: Check the `docs/` directory
- **Examples**: See `src/examples/` for usage examples

## 🔄 Development

### Building the Package
```bash
pip install build
python -m build
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Running Examples
```bash
# LangChain integration demo
python src/examples/demo_langchain_rre.py

# Site explorer demo
python src/examples/demo_site_explorer.py
``` 