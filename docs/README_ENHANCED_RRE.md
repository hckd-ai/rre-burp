# Enhanced RRE (Recursive Request Exploit) Tools

This repository now contains enhanced versions of the RRE tools that **automate the manual reasoning process** used to analyze HAR files and discover dependency chains. These tools implement the same logic flow that was previously done manually through AI reasoning.

## 🚀 What's New

The enhanced tools now include:

- **Automatic seed discovery** from high-entropy values
- **Intelligent pattern recognition** for different data types (match IDs, stream tokens, timestamps, etc.)
- **Automated dependency chain mapping** with context
- **API endpoint discovery** and categorization
- **External service identification**
- **Comprehensive reporting** and visualization

## 📁 Available Tools

### 1. `rre_intelligent_analyzer.py` - Full AI-Powered Analysis
The most comprehensive tool that completely automates the analysis process.

**Features:**
- Automatic seed discovery and prioritization
- Pattern-based categorization of discovered values
- Complete dependency chain mapping
- Comprehensive report generation
- No manual intervention required

**Usage:**
```bash
# Run complete automated analysis
python3 rre_intelligent_analyzer.py --har yeahscore_stream.har

# Analyze specific target value
python3 rre_intelligent_analyzer.py --har yeahscore_stream.har --target 1629454135
```

### 2. `rre_enhanced.py` - Enhanced RRE Standalone
Enhanced version of the original RRE standalone script with intelligent features.

**Features:**
- Auto-discovery of potential seed values
- Pattern analysis without tracing
- Enhanced dependency extraction
- Better reporting and visualization
- Maintains compatibility with original RRE functionality

**Usage:**
```bash
# Analyze patterns in HAR file
python3 rre_enhanced.py --har yeahscore_stream.har --analyze-patterns

# Auto-discover potential seeds
python3 rre_enhanced.py --har yeahscore_stream.har --auto-discover

# Trace specific value with enhanced analysis
python3 rre_enhanced.py --har yeahscore_stream.har --value 1629454135 --mode full
```

### 3. `rre_standalone.py` - Original RRE Tool
The original RRE standalone script (unchanged).

**Usage:**
```bash
python3 rre_standalone.py --har yeahscore_stream.har --value <seed> --mode full
```

## 🔍 How It Works (The Automation)

### Before (Manual AI Reasoning)
Previously, analyzing a HAR file required:
1. Manually searching for high-entropy values
2. Guessing which values might be important
3. Running multiple RRE traces with different seeds
4. Manually piecing together dependency chains
5. Reasoning about the relationships between discovered values

### After (Automated Intelligence)
Now the tools automatically:

1. **Discover Seeds**: Scan the HAR file for high-entropy values and categorize them by pattern
2. **Prioritize Analysis**: Automatically rank seeds by importance (match IDs first, then stream tokens, etc.)
3. **Extract Dependencies**: Use pattern recognition to find related values in responses
4. **Map Chains**: Automatically trace dependency relationships
5. **Generate Reports**: Provide comprehensive analysis summaries

## 📊 Example Output

### Pattern Analysis
```
📊 Pattern Analysis
==================================================
Total entries: 115
API calls: 2
External services: Xiaolin Live
High-entropy values: 6468

📡 API Endpoints:
YEAHSCORE GAME (8 endpoints):
  GET /game/leagues/featured
  GET /game/leagues
  GET /game/sports
  GET /game/fixtures/1629454135
  ... and 3 more

🔑 Pattern Matches:
  api_keys: 5352 matches
  client_ids: 1010 matches
  stream_tokens: 1 matches
  match_ids: 13 matches
  timestamps: 2 matches
  device_ids: 32 matches
```

### Auto-Seed Discovery
```
🔍 Auto-discovering potential seed values...
  ✓ Match ID: 1629454135 (entropy: 3.32)
  ✓ Stream token: ce668b42b5aa86daa41378940bc4b29b49464b37.false.175... (entropy: 4.87)
  ✓ URL path: chicago-cubs-vs-st-louis-cardinals-1629454135 (entropy: 4.23)

🎯 Auto-discovered 7 seed values
```

### Dependency Chain Tracing
```
🎯 Running targeted analysis on: 1629454135

📊 Dependency chain found (3 entries):
→ GET https://yeahscore1.co/game/fixtures/1629454135
  Status: 200
  MIME: application/json
  Dependencies:
    ↓ match_ids: 1000001661 (entropy: 3.32)
    ↓ match_ids: 1000000441 (entropy: 3.32)
    ↓ match_ids: 1000000476 (entropy: 3.32)
```

## 🎯 Use Cases

### 1. **Security Research**
- Automatically discover API endpoints and their relationships
- Identify potential authentication bypasses
- Map out service dependencies

### 2. **API Documentation**
- Understand how different endpoints relate to each other
- Discover hidden API parameters and dependencies
- Map out data flow between services

### 3. **Penetration Testing**
- Find high-value targets for testing
- Understand attack surfaces
- Identify potential privilege escalation paths

### 4. **Development & Debugging**
- Understand API dependencies during development
- Debug complex request chains
- Document API relationships

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7+
- No external dependencies (uses only standard library)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd rre-burp

# Run intelligent analysis
python3 rre_intelligent_analyzer.py --har your_file.har

# Or use enhanced RRE
python3 rre_enhanced.py --har your_file.har --auto-discover
```

## 🔧 Configuration

### Entropy Threshold
Adjust the sensitivity of high-entropy value detection:
```bash
python3 rre_enhanced.py --har file.har --entropy-threshold 4.0
```

### Analysis Modes
- `--analyze-patterns`: Just analyze patterns without tracing
- `--auto-discover`: Find potential seeds
- `--value <seed>`: Trace specific value
- `--mode full`: Full recursive chain discovery
- `--mode first`: Walkback to first reference

## 📈 Performance

The enhanced tools are designed to handle large HAR files efficiently:
- **Memory efficient**: Processes entries one at a time
- **Fast pattern matching**: Uses compiled regex patterns
- **Smart filtering**: Only processes relevant content
- **Configurable depth**: Limit recursion depth to prevent infinite loops

## 🎨 Customization

### Adding New Patterns
Edit the `patterns` dictionary in the analyzer classes:
```python
self.patterns = {
    'custom_pattern': r'your_regex_here',
    'api_keys': r'[A-Za-z0-9]{20,}',
    # ... existing patterns
}
```

### Custom Seed Discovery Logic
Override the `auto_discover_seeds()` method to implement custom prioritization:
```python
def auto_discover_seeds(self) -> List[str]:
    # Your custom logic here
    pass
```

## 🚨 Troubleshooting

### Common Issues

1. **"No suitable seed values found"**
   - Lower the entropy threshold: `--entropy-threshold 2.5`
   - Check if HAR file contains response bodies

2. **"Failed to parse HAR"**
   - Ensure HAR file is valid JSON
   - Check file encoding (should be UTF-8)

3. **Memory issues with large files**
   - Use `--mode first` instead of `--mode full`
   - Limit recursion depth in the code

### Debug Mode
Add debug prints to understand what's happening:
```python
# In the analyzer classes, add:
print(f"DEBUG: Processing entry {i}/{len(self.entries)}")
```

## 🔮 Future Enhancements

Planned improvements:
- **Machine learning** for better pattern recognition
- **Graph visualization** of dependency chains
- **Export to various formats** (JSON, CSV, GraphML)
- **Real-time analysis** of live traffic
- **Integration with Burp Suite** for live analysis

## 📚 Examples

### Complete Analysis Workflow
```bash
# 1. Analyze patterns first
python3 rre_enhanced.py --har traffic.har --analyze-patterns

# 2. Auto-discover seeds
python3 rre_enhanced.py --har traffic.har --auto-discover

# 3. Trace specific interesting values
python3 rre_enhanced.py --har traffic.har --value <discovered_seed> --mode full

# 4. Or run everything at once with intelligent analyzer
python3 rre_intelligent_analyzer.py --har traffic.har
```

### Batch Analysis
```bash
# Analyze multiple HAR files
for file in *.har; do
    echo "Analyzing $file..."
    python3 rre_intelligent_analyzer.py --har "$file"
    echo "---"
done
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- New pattern recognition algorithms
- Better dependency extraction
- Performance optimizations
- Additional export formats
- Integration with other tools

## 📄 License

Same as the original RRE project.

---

**The enhanced RRE tools now provide the same level of analysis that previously required manual AI reasoning, making HAR file analysis accessible to everyone!** 🎉 