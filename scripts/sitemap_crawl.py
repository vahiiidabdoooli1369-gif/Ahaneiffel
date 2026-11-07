"""Read-only sitemap-index crawler used by the six-hour SEO audit."""
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET


def _local_name(tag):
    return tag.rsplit("}", 1)[-1].lower()


def collect_sitemap_page_urls(fetch, site, max_pages=80, max_sitemaps=50):
    """Return unique same-host HTTPS page URLs, sitemap count, and parse/fetch errors.

    fetch must return (status, final_url, body) and accept timeout=.
    Both sitemap indexes and urlsets are supported, including XML namespaces.
    """
    site_host = urlparse(site).hostname
    queue = [urljoin(site.rstrip("/") + "/", "/sitemap.xml")]
    seen_sitemaps = set()
    seen_pages = set()
    page_urls = []
    errors = []

    while queue and len(seen_sitemaps) < max_sitemaps and len(page_urls) < max_pages:
        sitemap_url = queue.pop(0)
        parsed_sitemap = urlparse(sitemap_url)
        if parsed_sitemap.scheme != "https" or parsed_sitemap.hostname != site_host:
            errors.append(f"Skipped non-primary sitemap URL: {sitemap_url}")
            continue
        if sitemap_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sitemap_url)
        try:
            status, final_url, body = fetch(sitemap_url, timeout=20)
            if status != 200:
                errors.append(f"Sitemap {sitemap_url} returned HTTP {status}.")
                continue
            final = urlparse(final_url)
            if final.scheme != "https" or final.hostname != site_host:
                errors.append(f"Sitemap redirected outside the primary HTTPS host: {final_url}")
                continue
            root = ET.fromstring(body)
            kind = _local_name(root.tag)
            if kind == "sitemapindex":
                for element in root.iter():
                    if _local_name(element.tag) == "loc" and element.text:
                        child = urljoin(sitemap_url, element.text.strip())
                        if child not in seen_sitemaps and child not in queue:
                            queue.append(child)
            elif kind == "urlset":
                for element in root.iter():
                    if _local_name(element.tag) == "loc" and element.text:
                        page = urljoin(sitemap_url, element.text.strip())
                        parsed_page = urlparse(page)
                        if parsed_page.scheme != "https" or parsed_page.hostname != site_host:
                            errors.append(f"Skipped non-primary page URL: {page}")
                            continue
                        if page not in seen_pages:
                            seen_pages.add(page)
                            page_urls.append(page)
                            if len(page_urls) >= max_pages:
                                break
            else:
                errors.append(f"Unsupported sitemap root element in {sitemap_url}: {root.tag}")
        except Exception as exc:
            errors.append(f"Sitemap parse/fetch failed for {sitemap_url}: {exc}")

    if queue and len(seen_sitemaps) >= max_sitemaps:
        errors.append(f"Sitemap traversal stopped at safety limit ({max_sitemaps} files).")
    return page_urls[:max_pages], len(seen_sitemaps), errors
