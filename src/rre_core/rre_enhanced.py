#!/usr/bin/env python3
"""
Enhanced RRE Standalone with Intelligent Analysis
------------------------------------------------

This enhanced version of the RRE standalone script adds intelligent pattern
recognition and automated seed discovery to the existing functionality.

New Features:
- Automatic seed discovery from high-entropy values
- Pattern-based categorization of discovered values
- Enhanced dependency extraction with context
- Better reporting and visualization
- Integration with existing RRE functionality

Usage:
    python3 rre_enhanced.py --har yeahscore_stream.har --auto-discover
    python3 rre_enhanced.py --har yeahscore_stream.har --value <seed> --mode full
    python3 rre_enhanced.py --har yeahscore_stream.har --analyze-patterns
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhanced RRE Standalone with Intelligent Analysis")
    parser.add_argument("--har", required=True, help="Path to HAR file with recorded traffic")
    parser.add_argument("--value", help="Seed value to trace (e.g., asset ID/token)")
    parser.add_argument(
        "--mode",
        choices=["first", "full"],
        default="full",
        help="Tracing mode: 'first' (walkback to first reference) or 'full' (recursive chain)",
    )
    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=3.0,
        help="Minimum Shannon entropy for URL path token to be considered interesting",
    )
    parser.add_argument(
        "--auto-discover",
        action="store_true",
        help="Automatically discover and analyze potential seed values"
    )
    parser.add_argument(
        "--analyze-patterns",
        action="store_true",
        help="Analyze patterns in the HAR file without tracing"
    )
    return parser.parse_args()


class EnhancedRREAnalyzer:
    def __init__(self, har_path: Path, entropy_threshold: float = 3.0):
        self.har_path = har_path
        self.entropy_threshold = entropy_threshold
        self.entries = []
        
        # Enhanced pattern recognition
        self.patterns = {
            'match_ids': r'\b\d{10}\b',  # 10-digit match IDs
            'team_ids': r'\b100000\d{4}\b',  # Team IDs like 1000000441
            'timestamps': r'\b1[0-9]{9}\b',  # Unix timestamps
            'stream_tokens': r'[a-f0-9]{40}\.[a-z]+\.\d{10}-[A-Za-z0-9+/=]+',  # Stream tokens
            'device_ids': r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUIDs
            'client_ids': r'[A-Za-z0-9]{32}',  # 32-char client IDs
            'cloudfront_ids': r'[a-f0-9]{16}-[A-Z]{3}',  # CloudFront distribution IDs
            'api_keys': r'[A-Za-z0-9]{20,}',  # Generic API keys
        }
        
        # Statistics
        self.stats = {
            'total_entries': 0,
            'api_calls': 0,
            'external_services': set(),
            'high_entropy_values': 0,
            'pattern_matches': defaultdict(int)
        }

    def load_har_entries(self) -> List[Dict[str, Any]]:
        """Load and parse HAR file with enhanced error handling"""
        try:
            with self.har_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            entries = data.get("log", {}).get("entries", [])
            if not isinstance(entries, list):
                raise ValueError("HAR file does not contain a valid 'log.entries' list")
            
            self.entries = entries
            self.stats['total_entries'] = len(entries)
            print(f"✓ Loaded {len(entries)} HAR entries")
            return entries
        except Exception as exc:
            print(f"✗ Failed to parse HAR: {exc}", file=sys.stderr)
            sys.exit(1)

    def calculate_shannon_entropy(self, value: str) -> float:
        """Calculate Shannon entropy for a string"""
        if not value:
            return 0.0
        probabilities = [float(value.count(char)) / len(value) for char in set(value)]
        return -sum(p * math.log(p, 2) for p in probabilities)

    def extract_high_entropy_values(self) -> List[Tuple[str, float, str, str]]:
        """Extract high-entropy values with enhanced pattern recognition"""
        high_entropy_values = []
        
        for entry in self.entries:
            # Extract from URLs
            url = entry.get("request", {}).get("url", "")
            path = urlparse(url).path or ""
            
            for match in re.findall(r"/([A-Za-z0-9_-]{10,})", path):
                entropy = self.calculate_shannon_entropy(match)
                if entropy > self.entropy_threshold:
                    high_entropy_values.append((match, entropy, "URL_PATH", url))
                    self.stats['high_entropy_values'] += 1
            
            # Extract from response bodies with pattern matching
            response_text = self.get_response_text(entry)
            if response_text:
                for pattern_name, pattern in self.patterns.items():
                    for match in re.findall(pattern, response_text):
                        entropy = self.calculate_shannon_entropy(match)
                        if entropy > self.entropy_threshold:
                            high_entropy_values.append((match, entropy, pattern_name, "response_body"))
                            self.stats['pattern_matches'][pattern_name] += 1
                            self.stats['high_entropy_values'] += 1
        
        # Remove duplicates and sort by entropy
        unique_values = {}
        for value, entropy, pattern, source in high_entropy_values:
            if value not in unique_values or entropy > unique_values[value][0]:
                unique_values[value] = (entropy, pattern, source)
        
        return sorted(unique_values.items(), key=lambda x: x[1][0], reverse=True)

    def get_response_text(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract response text from HAR entry with enhanced encoding support"""
        response = entry.get("response", {})
        content = response.get("content", {})
        text = content.get("text")
        
        if text is None:
            return None
            
        # Handle base64 encoding
        encoding = content.get("encoding")
        if encoding == "base64":
            try:
                decoded = base64.b64decode(text)
                try:
                    return decoded.decode("utf-8")
                except UnicodeDecodeError:
                    return decoded.decode("latin-1", errors="ignore")
            except Exception:
                return None
        return text

    def discover_api_endpoints(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover and categorize API endpoints"""
        endpoints = defaultdict(list)
        
        for entry in self.entries:
            url = entry.get("request", {}).get("url", "")
            method = entry.get("request", {}).get("method", "")
            
            if not url:
                continue
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path
            
            # Categorize by domain and path
            if "yeahscore" in domain:
                if "/api/" in path:
                    endpoints["yeahscore_api"].append({
                        "method": method,
                        "url": url,
                        "path": path,
                        "status": entry.get("response", {}).get("status", "")
                    })
                    self.stats['api_calls'] += 1
                elif "/game/" in path:
                    endpoints["yeahscore_game"].append({
                        "method": method,
                        "url": url,
                        "path": path,
                        "status": entry.get("response", {}).get("status", "")
                    })
            elif "livecdn.rumsport.com" in domain:
                self.stats['external_services'].add("RumSport CDN")
                endpoints["external_streaming"].append({
                    "method": method,
                    "url": url,
                    "path": path
                })
            elif "xiaolin.live" in domain:
                self.stats['external_services'].add("Xiaolin Live")
                endpoints["external_streaming"].append({
                    "method": method,
                    "url": url,
                    "path": path
                })
        
        return endpoints

    def auto_discover_seeds(self) -> List[str]:
        """Automatically discover potential seed values for analysis"""
        print("\n🔍 Auto-discovering potential seed values...")
        
        high_entropy = self.extract_high_entropy_values()
        seeds = []
        
        # Prioritize by pattern type and entropy
        for value, (entropy, pattern, source) in high_entropy:
            if pattern == 'match_ids':
                seeds.append(value)
                print(f"  ✓ Match ID: {value} (entropy: {entropy:.2f})")
                if len(seeds) >= 3:
                    break
        
        # Add stream tokens if available
        for value, (entropy, pattern, source) in high_entropy:
            if pattern == 'stream_tokens' and len(seeds) < 5:
                seeds.append(value)
                print(f"  ✓ Stream token: {value[:50]}... (entropy: {entropy:.2f})")
        
        # Add high-entropy URL values
        for value, (entropy, pattern, source) in high_entropy:
            if pattern == 'URL_PATH' and entropy > 4.0 and len(seeds) < 8:
                seeds.append(value)
                print(f"  ✓ URL path: {value} (entropy: {entropy:.2f})")
        
        return seeds

    def analyze_patterns(self) -> None:
        """Analyze patterns in the HAR file"""
        print("\n📊 Pattern Analysis")
        print("=" * 50)
        
        # Discover API endpoints
        endpoints = self.discover_api_endpoints()
        
        # Extract high-entropy values
        high_entropy = self.extract_high_entropy_values()
        
        # Print statistics
        print(f"Total entries: {self.stats['total_entries']}")
        print(f"API calls: {self.stats['api_calls']}")
        print(f"External services: {', '.join(self.stats['external_services']) if self.stats['external_services'] else 'None'}")
        print(f"High-entropy values: {self.stats['high_entropy_values']}")
        
        # API Endpoints
        print("\n📡 API Endpoints:")
        for category, endpoint_list in endpoints.items():
            print(f"\n{category.upper().replace('_', ' ')} ({len(endpoint_list)} endpoints):")
            for endpoint in endpoint_list[:5]:  # Show first 5
                print(f"  {endpoint['method']} {endpoint['path']}")
            if len(endpoint_list) > 5:
                print(f"  ... and {len(endpoint_list) - 5} more")
        
        # Pattern matches
        print("\n🔑 Pattern Matches:")
        for pattern, count in self.stats['pattern_matches'].items():
            if count > 0:
                print(f"  {pattern}: {count} matches")
        
        # Top high-entropy values
        print("\n🎯 Top High-Entropy Values:")
        for value, (entropy, pattern, source) in high_entropy[:10]:
            print(f"  {value} (entropy: {entropy:.2f}, pattern: {pattern})")

    def enhanced_full_walkback_chain(self, seed_value: str) -> None:
        """Enhanced full walkback chain with pattern recognition"""
        visited: Set[str] = set()

        def recursive_chain(current_value: str, depth: int = 0) -> None:
            indent = "    " * depth
            if current_value in visited:
                print(f"{indent}↺ Already visited: {current_value}")
                return
            visited.add(current_value)

            for entry in self.entries:
                response_text = self.get_response_text(entry)
                if not response_text:
                    continue

                if current_value in response_text:
                    top_line = self.get_request_top_line(entry)
                    print(f"{indent}→ Found in: {top_line}")

                    # Enhanced high-entropy path token discovery
                    url = entry.get("request", {}).get("url", "")
                    try:
                        path = urlparse(url).path or ""
                    except Exception:
                        path = ""
                    
                    for match in re.findall(r"/([A-Za-z0-9_-]{10,})", path):
                        entropy = self.calculate_shannon_entropy(match)
                        if entropy > self.entropy_threshold and match not in visited:
                            print(f"{indent}    ↑ High entropy match: {match} (entropy: {entropy:.2f})")
                            recursive_chain(match, depth + 1)

                    # Enhanced dependency extraction with pattern recognition
                    dependencies = self.enhanced_extract_dependencies(entry, response_text, current_value)
                    for dep in dependencies:
                        if dep not in visited:
                            print(f"{indent}    ↓ Dependency: {dep}")
                            recursive_chain(dep, depth + 1)
                    return

            print(f"{indent}× No reference found for: {current_value}")

        print("\n→ Starting Enhanced Recursive Chain Discovery")
        print(f"Initial Target: {seed_value}\n")
        recursive_chain(seed_value)

    def enhanced_extract_dependencies(self, entry: Dict[str, Any], response_text: str, current_value: str) -> List[str]:
        """Enhanced dependency extraction with pattern recognition"""
        dependencies = []
        
        # Check for JSON responses
        json_data = self.parse_json_body(entry, response_text)
        if json_data is not None:
            found = self.find_in_json(json_data, current_value)
            if found:
                dependencies.append(found)
        
        # Enhanced pattern-based extraction
        for pattern_name, pattern in self.patterns.items():
            for match in re.findall(pattern, response_text):
                if match != current_value and match not in dependencies:
                    dependencies.append(match)
        
        # Fallback to text-based extraction
        text_dep = self.find_in_text(response_text, current_value)
        if text_dep and text_dep not in dependencies:
            dependencies.append(text_dep)
        
        return dependencies

    def get_request_top_line(self, entry: Dict[str, Any]) -> str:
        """Get request top line"""
        request = entry.get("request", {})
        method = request.get("method", "?")
        url = request.get("url", "?")
        http_version = request.get("httpVersion") or entry.get("response", {}).get("httpVersion") or "HTTP/?"
        return f"{method} {url} {http_version}"

    def parse_json_body(self, entry: Dict[str, Any], response_text: str) -> Optional[Any]:
        """Parse JSON body with enhanced detection"""
        content = entry.get("response", {}).get("content", {})
        mime_type = content.get("mimeType")
        
        if not self.is_likely_json(response_text, mime_type):
            return None
        try:
            return json.loads(response_text)
        except Exception:
            return None

    def is_likely_json(self, text: str, mime_type: Optional[str]) -> bool:
        """Enhanced JSON detection"""
        if not text:
            return False
        trimmed = text.lstrip()
        if mime_type and "json" in mime_type.lower():
            return True
        return trimmed.startswith("{") or trimmed.startswith("[")

    def find_in_json(self, json_data: Any, current_value: str) -> Optional[str]:
        """Find value in JSON with enhanced search"""
        def recursive_search(node: Any) -> Optional[str]:
            if isinstance(node, dict):
                for key, value in node.items():
                    try_value = str(value)
                    if current_value in try_value:
                        return key if isinstance(value, str) else try_value
                    if isinstance(value, (dict, list)):
                        found = recursive_search(value)
                        if found:
                            return found
            elif isinstance(node, list):
                for item in node:
                    found = recursive_search(item)
                    if found:
                        return found
            return None

        return recursive_search(json_data)

    def find_in_text(self, text: str, current_value: str) -> Optional[str]:
        """Enhanced text-based dependency extraction"""
        try:
            for line in text.splitlines():
                if current_value in line:
                    for part in line.split():
                        if part.startswith("key=") or part.startswith("id="):
                            return part.split("=")[-1].strip('"')
            return None
        except Exception:
            return None


def main() -> int:
    args = parse_args()
    har_path = Path(args.har)
    
    if not har_path.exists():
        print(f"HAR not found: {har_path}", file=sys.stderr)
        return 1

    analyzer = EnhancedRREAnalyzer(har_path, args.entropy_threshold)
    analyzer.load_har_entries()

    if args.analyze_patterns:
        analyzer.analyze_patterns()
    elif args.auto_discover:
        seeds = analyzer.auto_discover_seeds()
        if seeds:
            print(f"\n🎯 Auto-discovered {len(seeds)} seed values")
            print("Run with --value <seed> to trace specific values")
        else:
            print("\n❌ No suitable seed values found")
    elif args.value:
        if args.mode == "first":
            # Use original first mode logic
            analyzer.walkback_to_first_reference(args.value)
        else:
            analyzer.enhanced_full_walkback_chain(args.value)
    else:
        print("Use --auto-discover to find seeds or --value <seed> to trace")
        analyzer.analyze_patterns()

    return 0


if __name__ == "__main__":
    raise SystemExit(main()) 