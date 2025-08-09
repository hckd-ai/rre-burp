"""
Recursive Request Exploit (RRE) — Standalone
-------------------------------------------

This script provides the core "walkback" and "full chain discovery" logic
from the Burp extension, but operates on a HAR file exported from a browser
or proxy. It searches response bodies for a target value, walks backward to
find where it originated, and surfaces high-entropy IDs found in request URLs
to continue the chain.

Usage examples:
    python3 rre_standalone.py --har traffic.har --value <seed>
    python3 rre_standalone.py --har traffic.har --value <seed> --mode full

Notes:
    - The HAR should include response bodies. Ensure your capture tool is set
      to record content, not just headers.
    - This runs on Python 3; no external dependencies.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recursive Request Exploit over HAR")
    parser.add_argument("--har", required=True, help="Path to HAR file with recorded traffic")
    parser.add_argument("--value", required=True, help="Seed value to trace (e.g., asset ID/token)")
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
    return parser.parse_args()


def load_har_entries(har_path: Path) -> List[Dict[str, Any]]:
    with har_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("log", {}).get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("HAR file does not contain a valid 'log.entries' list")
    return entries


def get_request_top_line(entry: Dict[str, Any]) -> str:
    request = entry.get("request", {})
    method = request.get("method", "?")
    url = request.get("url", "?")
    http_version = request.get("httpVersion") or entry.get("response", {}).get("httpVersion") or "HTTP/?"
    return f"{method} {url} {http_version}"


def get_response_text(entry: Dict[str, Any]) -> Optional[str]:
    response = entry.get("response", {})
    content = response.get("content", {})
    text = content.get("text")
    if text is None:
        return None
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


def is_likely_json(text: str, mime_type: Optional[str]) -> bool:
    if not text:
        return False
    trimmed = text.lstrip()
    if mime_type and "json" in mime_type.lower():
        return True
    return trimmed.startswith("{") or trimmed.startswith("[")


def parse_json_body(entry: Dict[str, Any], response_text: str) -> Optional[Any]:
    content = entry.get("response", {}).get("content", {})
    mime_type = content.get("mimeType")
    if not is_likely_json(response_text, mime_type):
        return None
    try:
        return json.loads(response_text)
    except Exception:
        return None


def calculate_shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    probabilities = [float(value.count(char)) / len(value) for char in set(value)]
    return -sum(p * math.log(p, 2) for p in probabilities)


def find_in_json(json_data: Any, current_value: str) -> Optional[str]:
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


def find_in_text(text: str, current_value: str) -> Optional[str]:
    try:
        for line in text.splitlines():
            if current_value in line:
                for part in line.split():
                    if part.startswith("key=") or part.startswith("id="):
                        return part.split("=")[-1].strip('"')
        return None
    except Exception:
        return None


def extract_dependency(entry: Dict[str, Any], response_text: str, current_value: str) -> Optional[str]:
    json_data = parse_json_body(entry, response_text)
    if json_data is not None:
        found = find_in_json(json_data, current_value)
        if found:
            return found
    return find_in_text(response_text, current_value)


def full_walkback_chain(entries: List[Dict[str, Any]], seed_value: str, entropy_threshold: float) -> None:
    visited: Set[str] = set()

    def recursive_chain(current_value: str, depth: int = 0) -> None:
        indent = "    " * depth
        if current_value in visited:
            print(f"{indent}↺ Already visited: {current_value}")
            return
        visited.add(current_value)

        for entry in entries:
            response_text = get_response_text(entry)
            if not response_text:
                continue

            if current_value in response_text:
                top_line = get_request_top_line(entry)
                print(f"{indent}→ Found in: {top_line}")

                # High-entropy path tokens in request URL
                url = entry.get("request", {}).get("url", "")
                try:
                    path = urlparse(url).path or ""
                except Exception:
                    path = ""
                for match in re.findall(r"/([A-Za-z0-9_-]{10,})", path):
                    entropy = calculate_shannon_entropy(match)
                    if entropy > entropy_threshold and match not in visited:
                        print(f"{indent}    ↑ High entropy match: {match} (entropy: {entropy:.2f})")
                        recursive_chain(match, depth + 1)

                dependency = extract_dependency(entry, response_text, current_value)
                if dependency and isinstance(dependency, str) and dependency not in visited:
                    print(f"{indent}    ↓ Dependency: {dependency}")
                    recursive_chain(dependency, depth + 1)
                return

        print(f"{indent}× No reference found for: {current_value}")

    print("\n→ Starting Recursive Chain Discovery")
    print(f"Initial Target: {seed_value}\n")
    recursive_chain(seed_value)


def walkback_to_first_reference(entries: List[Dict[str, Any]], seed_value: str) -> None:
    visited: Set[str] = set()

    def recursive_walk(current_value: str) -> None:
        if current_value in visited:
            return
        visited.add(current_value)

        for entry in entries:
            response_text = get_response_text(entry)
            if not response_text:
                continue

            if current_value in response_text:
                top_line = get_request_top_line(entry)
                print(f"→ Found in: {top_line}")

                dependency = extract_dependency(entry, response_text, current_value)
                if dependency and isinstance(dependency, str):
                    recursive_walk(dependency)
                return

    recursive_walk(seed_value)


def main() -> int:
    args = parse_args()
    har_path = Path(args.har)
    if not har_path.exists():
        print(f"HAR not found: {har_path}", file=sys.stderr)
        return 1

    try:
        entries = load_har_entries(har_path)
    except Exception as exc:
        print(f"Failed to parse HAR: {exc}", file=sys.stderr)
        return 1

    if args.mode == "first":
        walkback_to_first_reference(entries, args.value)
    else:
        full_walkback_chain(entries, args.value, args.entropy_threshold)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

