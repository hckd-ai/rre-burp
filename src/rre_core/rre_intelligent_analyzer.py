#!/usr/bin/env python3
"""
Intelligent RRE Analyzer
------------------------

This script automates the manual reasoning process used to analyze HAR files
and discover dependency chains. It implements the same logic flow that was
done manually in the previous analysis.

Features:
- Automatic seed discovery from high-entropy values
- Intelligent pattern recognition for different data types
- Automated dependency chain mapping
- API endpoint discovery and categorization
- External service identification
- Comprehensive report generation

Usage:
    python3 rre_intelligent_analyzer.py --har yeahscore_stream.har
    python3 rre_intelligent_analyzer.py --har yeahscore_stream.har --auto-trace
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from collections import defaultdict, Counter


class IntelligentHARAnalyzer:
    def __init__(self, har_path: Path):
        self.har_path = har_path
        self.entries = []
        self.visited_values = set()
        self.dependency_chains = defaultdict(list)
        self.api_endpoints = defaultdict(list)
        self.external_services = set()
        self.patterns = {
            'match_ids': r'\b\d{10}\b',  # 10-digit match IDs
            'team_ids': r'\b100000\d{4}\b',  # Team IDs like 1000000441
            'timestamps': r'\b1[0-9]{9}\b',  # Unix timestamps
            'stream_tokens': r'[a-f0-9]{40}\.[a-z]+\.\d{10}-[A-Za-z0-9+/=]+',  # Stream tokens
            'device_ids': r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUIDs
            'client_ids': r'[A-Za-z0-9]{32}',  # 32-char client IDs
            'cloudfront_ids': r'[a-f0-9]{16}-[A-Z]{3}',  # CloudFront distribution IDs
        }
        
    def load_har(self) -> None:
        """Load and parse HAR file"""
        try:
            with self.har_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = data.get("log", {}).get("entries", [])
            if not isinstance(self.entries, list):
                raise ValueError("HAR file does not contain a valid 'log.entries' list")
            print(f"✓ Loaded {len(self.entries)} HAR entries")
        except Exception as e:
            print(f"✗ Failed to load HAR file: {e}")
            sys.exit(1)

    def calculate_entropy(self, value: str) -> float:
        """Calculate Shannon entropy for a string"""
        if not value:
            return 0.0
        probabilities = [float(value.count(char)) / len(value) for char in set(value)]
        return -sum(p * math.log(p, 2) for p in probabilities)

    def extract_high_entropy_values(self, min_entropy: float = 3.0) -> List[Tuple[str, float, str]]:
        """Extract high-entropy values from URLs and response bodies"""
        high_entropy_values = []
        
        for entry in self.entries:
            # Extract from URLs
            url = entry.get("request", {}).get("url", "")
            path = urlparse(url).path or ""
            
            for match in re.findall(r"/([A-Za-z0-9_-]{10,})", path):
                entropy = self.calculate_entropy(match)
                if entropy > min_entropy:
                    high_entropy_values.append((match, entropy, f"URL path: {url}"))
            
            # Extract from response bodies
            response_text = self.get_response_text(entry)
            if response_text:
                for pattern_name, pattern in self.patterns.items():
                    for match in re.findall(pattern, response_text):
                        entropy = self.calculate_entropy(match)
                        if entropy > min_entropy:
                            high_entropy_values.append((match, entropy, f"Response body: {pattern_name}"))
        
        # Remove duplicates and sort by entropy
        unique_values = {}
        for value, entropy, source in high_entropy_values:
            if value not in unique_values or entropy > unique_values[value][0]:
                unique_values[value] = (entropy, source)
        
        return sorted(unique_values.items(), key=lambda x: x[1][0], reverse=True)

    def get_response_text(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract response text from HAR entry"""
        response = entry.get("response", {})
        content = response.get("content", {})
        text = content.get("text")
        
        if text is None:
            return None
            
        # Handle base64 encoding
        encoding = content.get("encoding")
        if encoding == "base64":
            try:
                import base64
                decoded = base64.b64decode(text)
                try:
                    return decoded.decode("utf-8")
                except UnicodeDecodeError:
                    return decoded.decode("latin-1", errors="ignore")
            except Exception:
                return None
        return text

    def discover_api_endpoints(self) -> None:
        """Discover and categorize API endpoints"""
        for entry in self.entries:
            url = entry.get("request", {}).get("url", "")
            method = entry.get("request", {}).get("method", "")
            
            if not url:
                continue
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path
            
            # Categorize by domain
            if "yeahscore" in domain:
                if "/api/" in path:
                    self.api_endpoints["yeahscore_api"].append({
                        "method": method,
                        "url": url,
                        "path": path
                    })
                elif "/game/" in path:
                    self.api_endpoints["yeahscore_game"].append({
                        "method": method,
                        "url": url,
                        "path": path
                    })
            elif "livecdn.rumsport.com" in domain:
                self.external_services.add("RumSport CDN")
                self.api_endpoints["external_streaming"].append({
                    "method": method,
                    "url": url,
                    "path": path
                })
            elif "xiaolin.live" in domain:
                self.external_services.add("Xiaolin Live")
                self.api_endpoints["external_streaming"].append({
                    "method": method,
                    "url": url,
                    "path": path
                })

    def trace_dependency_chain(self, seed_value: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """Trace dependency chain from a seed value"""
        chain = []
        visited = set()
        
        def recursive_trace(current_value: str, depth: int = 0) -> None:
            if depth > max_depth or current_value in visited:
                return
                
            visited.add(current_value)
            
            for entry in self.entries:
                response_text = self.get_response_text(entry)
                if not response_text or current_value not in response_text:
                    continue
                
                # Found the value in this response
                request = entry.get("request", {})
                response = entry.get("response", {})
                
                chain_entry = {
                    "depth": depth,
                    "value": current_value,
                    "method": request.get("method", ""),
                    "url": request.get("url", ""),
                    "status": response.get("status", ""),
                    "mime_type": response.get("content", {}).get("mimeType", ""),
                    "dependencies": []
                }
                
                # Look for new dependencies in the response
                for pattern_name, pattern in self.patterns.items():
                    for match in re.findall(pattern, response_text):
                        if match != current_value and match not in visited:
                            chain_entry["dependencies"].append({
                                "type": pattern_name,
                                "value": match,
                                "entropy": self.calculate_entropy(match)
                            })
                
                chain.append(chain_entry)
                
                # Continue tracing with new dependencies
                for dep in chain_entry["dependencies"]:
                    if dep["entropy"] > 3.0:  # Only trace high-entropy values
                        recursive_trace(dep["value"], depth + 1)
                
                break  # Found the value, no need to check other entries
        
        recursive_trace(seed_value)
        return chain

    def auto_discover_seeds(self) -> List[str]:
        """Automatically discover potential seed values"""
        print("\n🔍 Auto-discovering potential seed values...")
        
        # Get high-entropy values
        high_entropy = self.extract_high_entropy_values(min_entropy=3.5)
        
        # Prioritize by pattern type and entropy
        seeds = []
        
        # First priority: Match IDs (they're usually the starting point)
        for value, (entropy, source) in high_entropy:
            if re.match(self.patterns['match_ids'], value):
                seeds.append(value)
                print(f"  ✓ Match ID candidate: {value} (entropy: {entropy:.2f})")
                if len(seeds) >= 3:  # Limit to top 3
                    break
        
        # Second priority: Stream tokens
        for value, (entropy, source) in high_entropy:
            if re.match(self.patterns['stream_tokens'], value):
                seeds.append(value)
                print(f"  ✓ Stream token candidate: {value[:50]}... (entropy: {entropy:.2f})")
                if len(seeds) >= 5:  # Limit to top 5
                    break
        
        # Third priority: High-entropy values from URLs
        for value, (entropy, source) in high_entropy:
            if "URL path" in source and entropy > 4.0:
                seeds.append(value)
                print(f"  ✓ URL path candidate: {value} (entropy: {entropy:.2f})")
                if len(seeds) >= 8:  # Limit to top 8
                    break
        
        return seeds

    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("INTELLIGENT RRE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"File: {self.har_path.name}")
        report.append(f"Total entries: {len(self.entries)}")
        report.append("")
        
        # API Endpoints Summary
        report.append("📡 API ENDPOINTS DISCOVERED")
        report.append("-" * 40)
        for category, endpoints in self.api_endpoints.items():
            report.append(f"\n{category.upper().replace('_', ' ')} ({len(endpoints)} endpoints):")
            for endpoint in endpoints[:5]:  # Show first 5
                report.append(f"  {endpoint['method']} {endpoint['path']}")
            if len(endpoints) > 5:
                report.append(f"  ... and {len(endpoints) - 5} more")
        
        # External Services
        if self.external_services:
            report.append(f"\n🌐 EXTERNAL SERVICES: {', '.join(self.external_services)}")
        
        # High-Entropy Values
        report.append("\n🔑 HIGH-ENTROPY VALUES DISCOVERED")
        report.append("-" * 40)
        high_entropy = self.extract_high_entropy_values(min_entropy=3.0)
        for value, (entropy, source) in high_entropy[:10]:  # Top 10
            report.append(f"  {value} (entropy: {entropy:.2f}) - {source}")
        
        return "\n".join(report)

    def run_auto_analysis(self) -> None:
        """Run the complete automated analysis"""
        print("🚀 Starting Intelligent RRE Analysis...")
        
        # Load HAR file
        self.load_har()
        
        # Discover API endpoints
        print("\n📡 Discovering API endpoints...")
        self.discover_api_endpoints()
        
        # Generate initial report
        print(self.generate_comprehensive_report())
        
        # Auto-discover seeds
        seeds = self.auto_discover_seeds()
        
        if not seeds:
            print("\n❌ No suitable seed values found for analysis")
            return
        
        # Analyze top seeds
        print(f"\n🎯 Analyzing top {len(seeds)} seed values...")
        for i, seed in enumerate(seeds[:3], 1):  # Analyze top 3
            print(f"\n--- Seed {i}: {seed} ---")
            chain = self.trace_dependency_chain(seed, max_depth=3)
            
            if chain:
                print(f"  Dependency chain length: {len(chain)}")
                for entry in chain:
                    indent = "    " * entry["depth"]
                    print(f"{indent}→ {entry['method']} {entry['url']}")
                    if entry["dependencies"]:
                        for dep in entry["dependencies"][:3]:  # Show top 3 deps
                            print(f"{indent}  ↓ {dep['type']}: {dep['value']}")
            else:
                print("  No dependency chain found")

    def run_targeted_analysis(self, target_value: str) -> None:
        """Run analysis on a specific target value"""
        print(f"🎯 Running targeted analysis on: {target_value}")
        
        # Load HAR file
        self.load_har()
        
        # Discover API endpoints
        self.discover_api_endpoints()
        
        # Trace dependency chain
        chain = self.trace_dependency_chain(target_value, max_depth=5)
        
        if chain:
            print(f"\n📊 Dependency chain found ({len(chain)} entries):")
            for entry in chain:
                indent = "  " * entry["depth"]
                print(f"{indent}→ {entry['method']} {entry['url']}")
                print(f"{indent}  Status: {entry['status']}")
                print(f"{indent}  MIME: {entry['mime_type']}")
                
                if entry["dependencies"]:
                    print(f"{indent}  Dependencies:")
                    for dep in entry["dependencies"]:
                        print(f"{indent}    ↓ {dep['type']}: {dep['value']} (entropy: {dep['entropy']:.2f})")
                print()
        else:
            print("❌ No dependency chain found for this value")


def main():
    parser = argparse.ArgumentParser(description="Intelligent RRE HAR Analyzer")
    parser.add_argument("--har", required=True, help="Path to HAR file")
    parser.add_argument("--target", help="Specific value to analyze")
    parser.add_argument("--auto-trace", action="store_true", help="Automatically trace discovered seeds")
    
    args = parser.parse_args()
    har_path = Path(args.har)
    
    if not har_path.exists():
        print(f"❌ HAR file not found: {har_path}")
        sys.exit(1)
    
    analyzer = IntelligentHARAnalyzer(har_path)
    
    if args.target:
        analyzer.run_targeted_analysis(args.target)
    else:
        analyzer.run_auto_analysis()


if __name__ == "__main__":
    main() 