# RRE Burp - Project Structure

This document shows the complete organized structure of the RRE Burp project after reorganization.

## 📁 Complete Directory Structure

```
rre-burp/
├── 📁 src/                          # Source code
│   ├── 📁 rre_core/                # Core RRE components
│   │   ├── __init__.py             # Package exports
│   │   ├── rre.py                  # Basic RRE implementation (Burp extension)
│   │   ├── rre_enhanced.py         # Enhanced RRE with AI analysis
│   │   ├── rre_standalone.py       # Standalone RRE script
│   │   ├── rre_intelligent_analyzer.py  # AI-powered analyzer
│   │   ├── rre_explore.py          # RRE exploration tools
│   │   └── har_collect.py          # HAR collection utilities
│   │
│   ├── 📁 langchain_integration/   # LangChain integration
│   │   ├── __init__.py             # Package exports
│   │   ├── langchain_rre.py        # Main LangChain integration
│   │   └── config_langchain.py     # LangChain configuration
│   │
│   ├── 📁 site_explorer/          # Intelligent site exploration
│   │   ├── __init__.py             # Package exports
│   │   └── intelligent_explorer.py # Core explorer implementation
│   │
│   ├── 📁 config/                 # Configuration management
│   │   ├── __init__.py             # Package exports
│   │   └── site_explorer_config.py # Site explorer configuration
│   │
│   ├── 📁 utils/                  # Utility functions
│   │   ├── __init__.py             # Package exports
│   │   └── web_helpers.py          # Web interaction utilities
│   │
│   ├── 📁 analysis/               # Analysis tools (placeholder)
│   │   └── __init__.py
│   │
│   ├── 📁 examples/               # Example scripts
│   │   ├── __init__.py
│   │   ├── demo_langchain_rre.py  # LangChain integration demo
│   │   ├── demo_site_explorer.py  # Site explorer demo
│   │   └── compare_approaches.py  # Comparison demo
│   │
│   ├── 📁 tests/                  # Test files
│   │   ├── __init__.py
│   │   └── test_langchain_integration.py
│   │
│   ├── __init__.py                 # Main package exports
│   └── site_explorer_cli.py        # CLI interface
│
├── 📁 docs/                       # Documentation
│   ├── README.md                   # Main project README
│   ├── README_LANGCHAIN.md         # LangChain integration docs
│   ├── README_ENHANCED_RRE.md      # Enhanced RRE docs
│   └── README_SITE_EXPLORER.md     # Site explorer docs
│
├── 📁 data/                       # Data files
│   ├── test_sites.json             # Test site definitions
│   └── yeahscore_stream.har        # Example HAR file
│
├── 📁 output/                      # Generated output (runtime)
├── 📁 .git/                        # Git repository
├── 📁 .venv/                       # Virtual environment
├── 📁 __pycache__/                 # Python cache
├── .env                            # Environment variables
├── pyproject.toml                  # Project configuration
├── requirements_langchain.txt      # Python dependencies
├── uv.lock                         # Dependency lock file
└── PROJECT_STRUCTURE.md            # This file
```

## 🔧 Package Organization

### 1. Core RRE (`src/rre_core/`)
**Purpose**: Core Request Response Explorer functionality
- **`rre.py`**: Basic RRE implementation as Burp extension
- **`rre_enhanced.py`**: Enhanced RRE with AI-powered analysis (`EnhancedRREAnalyzer`)
- **`rre_standalone.py`**: Standalone RRE script for command-line use
- **`rre_intelligent_analyzer.py`**: AI-driven traffic analysis (`IntelligentHARAnalyzer`)
- **`rre_explore.py`**: RRE exploration tools with HAR collection
- **`har_collect.py`**: Playwright-based HAR collection utilities

### 2. LangChain Integration (`src/langchain_integration/`)
**Purpose**: AI-powered analysis using LangChain
- **`langchain_rre.py`**: Main integration with custom tools and chains
- **`config_langchain.py`**: Configuration management for LangChain components

**Key Components**:
- `HARCollectorTool`: LangChain tool for HAR collection
- `RREAnalysisTool`: LangChain tool for RRE analysis
- `TrafficIntelligenceChain`: AI-powered traffic analysis
- `AutomatedExploitChain`: Automated vulnerability detection
- `TrafficQueryChain`: Natural language traffic queries

### 3. Site Explorer (`src/site_explorer/`)
**Purpose**: Intelligent web exploration and HAR collection
- **`intelligent_explorer.py`**: Core explorer implementation (`IntelligentSiteExplorer`)
- **`site_explorer_cli.py`**: Command-line interface

**Features**:
- Cookie consent handling
- Ad overlay management
- Video content detection
- Intelligent scrolling and waiting
- Comprehensive HAR collection

### 4. Configuration (`src/config/`)
**Purpose**: Centralized configuration management
- **`site_explorer_config.py`**: Configuration classes and YAML serialization
- **`__init__.py`**: Configuration package exports

### 5. Utilities (`src/utils/`)
**Purpose**: Common utility functions
- **`web_helpers.py`**: Web interaction utilities
- **`__init__.py`**: Utility package exports

**Functions**:
- `wait_for_page_stable`: Wait for page to stabilize
- `detect_video_content`: Find video elements
- `handle_cookie_consent`: Manage cookie banners
- `handle_ads_and_overlays`: Deal with advertisements

### 6. Examples (`src/examples/`)
**Purpose**: Demonstration and example scripts
- **`demo_langchain_rre.py`**: LangChain integration examples
- **`demo_site_explorer.py`**: Site explorer usage examples
- **`compare_approaches.py`**: Comparison of different approaches

### 7. Tests (`src/tests/`)
**Purpose**: Testing and validation
- **`test_langchain_integration.py`**: Integration tests

## 📚 Documentation Structure

### Root Documentation
- **`README.md`**: Main project overview and quick start
- **`PROJECT_STRUCTURE.md`**: This detailed structure document

### Specialized Documentation (`docs/`)
- **`README_LANGCHAIN.md`**: Complete LangChain integration guide
- **`README_ENHANCED_RRE.md`**: Enhanced RRE features and usage
- **`README_SITE_EXPLORER.md`**: Site explorer comprehensive guide

## 🚀 Usage Examples

### Importing Components
```python
# Core RRE components
from src import EnhancedRREAnalyzer, IntelligentHARAnalyzer, collect_har

# LangChain integration
from src import HARCollectorTool, TrafficIntelligenceChain

# Site Explorer
from src import IntelligentSiteExplorer

# Configuration
from src import SiteExplorerConfig, load_config
```

### Command Line Usage
```bash
# Site Explorer CLI
python -m src.site_explorer_cli explore https://example.com
python -m src.site_explorer_cli --test

# Package installation
pip install -e .
site-explorer --help
```

### Running Examples
```bash
# Site Explorer demo
python src/examples/demo_site_explorer.py

# LangChain integration demo
python src/examples/demo_langchain_rre.py
```

## 🔄 Development Workflow

### 1. Adding New Components
- Place in appropriate package under `src/`
- Update package `__init__.py` to export new components
- Update main `src/__init__.py` if needed

### 2. Configuration Management
- Add new config classes to `src/config/`
- Use YAML serialization for external configuration
- Support environment variable overrides

### 3. Testing
- Add tests to `src/tests/`
- Run with `python -m pytest src/tests/`

### 4. Documentation
- Update relevant README files in `docs/`
- Keep examples current in `src/examples/`

## 📦 Package Management

### Dependencies
- **Core**: `requirements_langchain.txt`
- **Development**: `pyproject.toml` optional dependencies
- **Build**: `pyproject.toml` with hatchling

### Installation
```bash
# Development install
pip install -e .

# Production install
pip install .
```

## 🎯 Key Benefits of This Organization

1. **Modularity**: Clear separation of concerns
2. **Maintainability**: Easy to locate and modify components
3. **Scalability**: Simple to add new features and packages
4. **Documentation**: Comprehensive guides for each component
5. **Testing**: Organized test structure
6. **Examples**: Practical usage demonstrations
7. **CLI Integration**: Easy command-line access
8. **Import Simplicity**: Clean import paths from `src`

## 🔍 Navigation Tips

- **Core functionality**: Start with `src/rre_core/`
- **AI integration**: Check `src/langchain_integration/`
- **Web automation**: Explore `src/site_explorer/`
- **Configuration**: See `src/config/`
- **Examples**: Run scripts in `src/examples/`
- **Documentation**: Read files in `docs/`
- **CLI**: Use `python -m src.site_explorer_cli`

This organization makes the RRE Burp project easy to understand, maintain, and extend while providing clear separation between different types of functionality. 