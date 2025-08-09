"""
RRE Explore — One-shot collector + analyzer
-------------------------------------------

Given a URL, collect a HAR with embedded response bodies using Playwright and
immediately run the recursive reverse engineering walker over the captured data.

Examples:
    # Provide a seed explicitly
    uv run rre-explore --url https://example.com --seed abcd1234ef --mode full

    # Let the tool guess seeds from high-entropy URL path tokens
    uv run rre-explore --url https://example.com --auto-seeds --top 5

Requires:
    uv sync
    uv run python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from playwright.sync_api import sync_playwright

from . import rre_standalone as rre


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect a HAR from a URL and run RRE analysis")
    parser.add_argument("--url", required=True, help="Page URL to visit")
    parser.add_argument("--mode", choices=["first", "full"], default="full", help="Trace mode")
    parser.add_argument("--seed", action="append", default=[], help="Seed value to start tracing (can repeat)")
    parser.add_argument("--auto-seeds", action="store_true", help="Guess seeds from high-entropy URL tokens")
    parser.add_argument("--top", type=int, default=5, help="How many auto seeds to take (default: 5)")
    parser.add_argument("--entropy-threshold", type=float, default=3.0, help="Entropy cutoff for guessing seeds")
    parser.add_argument("--headful", action="store_true", help="Run a visible browser window")
    parser.add_argument("--wait", type=float, default=3.0, help="Wait seconds after network idle (default: 3.0)")
    parser.add_argument("--timeout", type=int, default=45000, help="Navigation timeout in ms (default: 45000)")
    parser.add_argument("--user-agent", default=None, help="Override User-Agent string")
    parser.add_argument(
        "--extra-header",
        action="append",
        default=[],
        help="Extra header in the form Name: Value (can be passed multiple times)",
    )
    parser.add_argument("--out", default=None, help="Optional path to save the HAR (default: temp file)")
    return parser.parse_args()


def parse_extra_headers(raw_headers: Iterable[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for item in raw_headers:
        if ":" not in item:
            continue
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def collect_har(url: str, out_path: Path, headful: bool, wait_seconds: float, user_agent: Optional[str], extra_headers: Dict[str, str], timeout_ms: int) -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headful)
        context = browser.new_context(
            record_har_path=str(out_path),
            record_har_content="embed",
            user_agent=user_agent,
            extra_http_headers=extra_headers or None,
        )
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        try:
            page.goto(url, wait_until="networkidle")
        except Exception as exc:
            print(f"Navigation failed: {exc}", file=sys.stderr)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        context.close()
        browser.close()


def guess_seeds_from_entries(entries: List[dict], entropy_threshold: float, top_k: int) -> List[str]:
    tokens: List[Tuple[str, float]] = []
    seen: Set[str] = set()
    for entry in entries:
        url = entry.get("request", {}).get("url", "")
        try:
            # Reuse rre's path token finder by emulating its regex
            from urllib.parse import urlparse

            path = urlparse(url).path or ""
        except Exception:
            path = ""
        for match in rre.re.findall(r"/([A-Za-z0-9_-]{10,})", path):
            if match in seen:
                continue
            seen.add(match)
            entropy = rre.calculate_shannon_entropy(match)
            if entropy > entropy_threshold:
                tokens.append((match, entropy))
    tokens.sort(key=lambda t: t[1], reverse=True)
    return [t[0] for t in tokens[: max(0, top_k)]]


def analyze(har_path: Path, seeds: List[str], mode: str, entropy_threshold: float) -> None:
    entries = rre.load_har_entries(har_path)
    if not seeds:
        print("No seeds provided; nothing to analyze.")
        return
    for idx, seed in enumerate(seeds, start=1):
        print(f"\n===== Seed {idx}: {seed} =====")
        if mode == "first":
            rre.walkback_to_first_reference(entries, seed)
        else:
            rre.full_walkback_chain(entries, seed, entropy_threshold)


def main() -> int:
    args = parse_args()
    extra_headers = parse_extra_headers(args.extra_header)

    if args.out:
        har_path = Path(args.out)
        har_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.NamedTemporaryFile(prefix="rre_", suffix=".har", delete=False)
        har_path = Path(tmp.name)
        tmp.close()

    print(f"Collecting HAR → {har_path}")
    collect_har(
        url=args.url,
        out_path=har_path,
        headful=bool(args.headful),
        wait_seconds=float(args.wait),
        user_agent=args.user_agent,
        extra_headers=extra_headers,
        timeout_ms=int(args.timeout),
    )

    try:
        entries = rre.load_har_entries(har_path)
    except Exception as exc:
        print(f"Failed to parse HAR: {exc}", file=sys.stderr)
        return 1

    seeds: List[str] = list(args.seed)
    if args.auto_seeds:
        guessed = guess_seeds_from_entries(entries, args.entropy_threshold, args.top)
        if guessed:
            print("Guessed seeds:", ", ".join(f"{s}" for s in guessed))
            seeds.extend(guessed)
        else:
            print("No seeds guessed from high-entropy URL tokens.")

    analyze(har_path, seeds, args.mode, args.entropy_threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

