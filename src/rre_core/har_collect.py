"""
HAR Collector — Playwright-based
--------------------------------

Collect a HAR with embedded response bodies by visiting a URL in Chromium
via Playwright. The resulting HAR can be fed into rre_standalone.py.

Examples:
    python3 har_collect.py --url https://example.com --out ./traffic.har
    python3 har_collect.py --url https://example.com --out ./traffic.har --headful --wait 5

Prereqs:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Optional

from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect a HAR from a single page load")
    parser.add_argument("--url", required=True, help="Page URL to visit")
    parser.add_argument("--out", required=True, help="Path to write HAR file")
    parser.add_argument("--headful", action="store_true", help="Run a visible browser window")
    parser.add_argument(
        "--wait",
        type=float,
        default=2.0,
        help="Seconds to wait after network idle before closing (default: 2.0)",
    )
    parser.add_argument(
        "--user-agent",
        default=None,
        help="Override User-Agent string for the context",
    )
    parser.add_argument(
        "--extra-header",
        action="append",
        default=[],
        help="Extra header in the form Name: Value (can be passed multiple times)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=45000,
        help="Navigation timeout in ms (default: 45000)",
    )
    return parser.parse_args()


def parse_extra_headers(raw_headers: list[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for item in raw_headers:
        if ":" not in item:
            continue
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def collect_har(url: str, out_path: Path, headful: bool, wait_seconds: float, user_agent: Optional[str], extra_headers: Dict[str, str], timeout_ms: int) -> int:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headful)
        context = browser.new_context(
            record_har={
                "path": str(out_path),
                "content": "embed",  # include response bodies
            },
            user_agent=user_agent,
            extra_http_headers=extra_headers or None,
        )
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        try:
            page.goto(url, wait_until="networkidle")
        except Exception as exc:
            print(f"Navigation failed: {exc}", file=sys.stderr)
            # Still attempt to close context to flush HAR
        # Allow background requests to finish
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        context.close()  # flush HAR
        browser.close()
    return 0


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    extra_headers = parse_extra_headers(args.extra_header)
    return collect_har(
        url=args.url,
        out_path=out_path,
        headful=bool(args.headful),
        wait_seconds=float(args.wait),
        user_agent=args.user_agent,
        extra_headers=extra_headers,
        timeout_ms=int(args.timeout),
    )


if __name__ == "__main__":
    raise SystemExit(main())

