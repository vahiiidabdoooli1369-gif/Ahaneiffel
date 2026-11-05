"""Offline regression tests for sitemap-index traversal."""
from scripts.sitemap_crawl import collect_sitemap_page_urls


DOCS = {
    "https://ahaneiffel.top/sitemap.xml": (200, "https://ahaneiffel.top/sitemap.xml",
        """<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap><loc>https://ahaneiffel.top/sitemap-products.xml</loc></sitemap>
        <sitemap><loc>https://ahaneiffel.top/sitemap-prices.xml</loc></sitemap>
        <sitemap><loc>https://evil.example/sitemap.xml</loc></sitemap>
        </sitemapindex>"""),
    "https://ahaneiffel.top/sitemap-products.xml": (200, "https://ahaneiffel.top/sitemap-products.xml",
        """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://ahaneiffel.top/products/rebar/</loc></url>
        <url><loc>https://ahaneiffel.top/products/beam/</loc></url>
        </urlset>"""),
    "https://ahaneiffel.top/sitemap-prices.xml": (200, "https://ahaneiffel.top/sitemap-prices.xml",
        """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://ahaneiffel.top/prices/rebar/</loc></url>
        <url><loc>https://ahaneiffel.top/products/rebar/</loc></url>
        </urlset>"""),
}


def fake_fetch(url, timeout=20):
    if url not in DOCS:
        raise AssertionError(f"Unexpected URL fetched: {url}")
    return DOCS[url]


pages, sitemap_count, errors = collect_sitemap_page_urls(fake_fetch, "https://ahaneiffel.top")
assert sitemap_count == 3, sitemap_count
assert pages == [
    "https://ahaneiffel.top/products/rebar/",
    "https://ahaneiffel.top/products/beam/",
    "https://ahaneiffel.top/prices/rebar/",
], pages
assert any("non-primary" in error for error in errors), errors

limited, _, _ = collect_sitemap_page_urls(fake_fetch, "https://ahaneiffel.top", max_pages=2)
assert len(limited) == 2, limited
print("PASS: sitemap index recursion, XML namespaces, duplicate removal, host filtering, and page limit.")
