#!/usr/bin/env python3
"""Read-only live HTTP audit for URLs exposed by the production XML sitemap.

This complements repository-local sitemap checks by testing the published site.
It deliberately does not modify files, prices, or sitemap entries.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
USER_AGENT = "AhaneiffelLiveSitemapAudit/1.0 (+read-only; SEO integrity check)"
MAX_SITEMAPS = 100
MAX_URLS = 10000
TIMEOUT_SECONDS = 18


@dataclass
class Result:
    url: str
    status: int | str
    final_url: str
    note: str = ""


def fetch(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/xml,text/xml,*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        return response.status, response.geturl(), response.read(8_000_001)


def parse_xml(payload: bytes, label: str):
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError(f"invalid XML at {label}: {exc}") from exc


def collect_sitemap_urls(base: str) -> tuple[list[str], list[str]]:
    root_url = urljoin(base.rstrip("/") + "/", "sitemap.xml")
    pending = [root_url]
    visited: set[str] = set()
    page_urls: list[str] = []
    errors: list[str] = []
    while pending:
        sitemap_url = pending.pop(0)
        if sitemap_url in visited:
            continue
        if len(visited) >= MAX_SITEMAPS:
            errors.append(f"sitemap limit exceeded ({MAX_SITEMAPS}); remaining children skipped")
            break
        visited.add(sitemap_url)
        try:
            status, final_url, payload = fetch(sitemap_url)
            if status != 200:
                errors.append(f"sitemap HTTP {status}: {sitemap_url}")
                continue
            if len(payload) > 8_000_000:
                errors.append(f"sitemap exceeds 8 MB safety limit: {sitemap_url}")
                continue
            root = parse_xml(payload, sitemap_url)
            if root.tag.endswith("sitemapindex"):
                for node in root.findall("sm:sitemap/sm:loc", NS):
                    if not node.text or not node.text.strip():
                        errors.append(f"empty child sitemap location in {sitemap_url}")
                        continue
                    child = node.text.strip()
                    parsed = urlparse(child)
                    if parsed.scheme != "https" or parsed.hostname != urlparse(base).hostname:
                        errors.append(f"off-host/non-HTTPS child sitemap rejected: {child}")
                    else:
                        pending.append(child)
            elif root.tag.endswith("urlset"):
                for node in root.findall("sm:url/sm:loc", NS):
                    if not node.text or not node.text.strip():
                        errors.append(f"empty URL location in {sitemap_url}")
                    else:
                        page_urls.append(node.text.strip())
                        if len(page_urls) > MAX_URLS:
                            errors.append(f"URL limit exceeded ({MAX_URLS}); audit stopped")
                            return page_urls[:MAX_URLS], errors
            else:
                errors.append(f"unexpected sitemap root element {root.tag!r}: {sitemap_url}")
        except (OSError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            errors.append(f"sitemap fetch/parse failed: {sitemap_url}: {exc}")
    # Remove duplicate URLs but preserve their first appearance for a stable report.
    return list(dict.fromkeys(page_urls)), errors


def check_url(url: str) -> Result:
    time.sleep(0.08)  # gentle request pacing per worker
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "ahaneiffel.top":
        return Result(url, "SKIP", "", "URL is not on the canonical HTTPS host")
    try:
        status, final_url, _ = fetch(url)
        note = "redirected" if final_url.rstrip("/") != url.rstrip("/") else ""
        return Result(url, status, final_url, note)
    except urllib.error.HTTPError as exc:
        return Result(url, exc.code, exc.geturl(), str(exc.reason))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return Result(url, "ERROR", "", str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://ahaneiffel.top", help="canonical site origin")
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9), metavar="{1..8}")
    parser.add_argument("--report", default="live-sitemap-http-report.csv")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    if urlparse(base).scheme != "https" or urlparse(base).hostname != "ahaneiffel.top":
        parser.error("--base-url must use https://ahaneiffel.top")

    urls, errors = collect_sitemap_urls(base)
    print(f"Sitemap URLs collected: {len(urls)}")
    print(f"Sitemap collection findings: {len(errors)}")
    for error in errors:
        print("SITEMAP | " + error)

    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_url, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item.url)
    counts: dict[str, int] = {}
    for item in results:
        key = str(item.status)
        counts[key] = counts.get(key, 0) + 1
    print("HTTP status counts: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    with open(args.report, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["url", "status", "final_url", "note"])
        writer.writerows((item.url, item.status, item.final_url, item.note) for item in results)
    for item in results:
        if item.status != 200:
            print(f"URL | {item.status} | {item.url} | final={item.final_url} | {item.note}")
    bad = [item for item in results if item.status != 200]
    print(f"CSV report: {args.report}")
    print(f"Result: {len(results) - len(bad)} URLs returned HTTP 200; {len(bad)} need review.")
    # Treat the audit as failed for non-200 URL responses or sitemap collection errors.
    return 1 if bad or errors else 0


if __name__ == "__main__":
    sys.exit(main())
