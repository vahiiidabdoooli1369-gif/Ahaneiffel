# Google Search Quality & Growth Framework — Ahaneiffel

This is an operational quality framework, not a claim to know or reproduce Google's complete ranking algorithm. Google uses many systems and signals; no checklist guarantees crawling, indexing, rankings, rich results, or traffic. Work must be evidence-led and focused on satisfying real steel buyers.

## 1. Search intent and topical coverage
- Map each important query to one best-fit canonical URL and one clear intent: buy/request quote, today's price, compare, calculate, learn, or find a supplier.
- Build product hubs and supporting pages around real user journeys: product definition, dimensions, weight, standards, manufacturers, use cases, comparisons, price drivers, calculation, transport, and ordering.
- Prevent keyword cannibalization. Do not create near-duplicate pages for minor keyword variants, sizes, cities, or manufacturers unless they have distinct useful information and demand.
- Use Search Console query/page data to prioritize pages with impressions, low CTR, positions 4–20, declining clicks, and query/page mismatches. Never invent search volume or ranking.
- Use natural Persian language and real buyer terminology; include synonyms where useful, not keyword stuffing.

## 2. Helpful, original, trustworthy content
- Solve the visitor's task completely and accurately; add original expertise, examples, calculations, photographs, comparison tables, and practical buying guidance where genuinely available.
- Explain product dimensions, tolerances, weight formulas, standards, grade/specification differences, applications, limitations, and factors affecting price. Cite reliable primary sources for technical standards and distinguish sourced facts from company experience.
- Show who is responsible for content and how it was reviewed when appropriate. Use only real staff names, credentials, business details, and review processes.
- Make commercial information transparent: business identity, contact methods, service area, working hours, quote process, shipping/returns/warranty terms where confirmed.
- Display prices only when supplied/verified by the business, with currency/unit, update timestamp, source/status, and clear stale/unverified state. Never fabricate prices, availability, stock, reviews, ratings, delivery promises, certifications, or customer stories.
- Update a page only when information materially changes. Do not change dates merely to look fresh.
- Avoid thin, spun, copied, mass-produced, doorway, and search-engine-first pages. AI assistance is acceptable only with human review, factual verification, and added value.

## 3. On-page relevance
- Give every indexable page a unique, descriptive title and a useful meta description; do not promise guaranteed ranking or use clickbait.
- Use one clear primary H1 and logical H2/H3 sections; headings must reflect visible content.
- Put the main topic and natural variants in prominent, meaningful places (title, H1, introductory copy, relevant headings, image alt text, and descriptive links) without repetition.
- Write concise, descriptive internal anchor text. Link from hubs to useful child pages and between genuinely related pages; ensure important pages are reachable through crawlable HTML links.
- Use descriptive, human-readable URLs; preserve stable URLs and use redirects when changes are unavoidable.
- Add useful image alt text, descriptive filenames, responsive images, modern formats where supported, and explicit dimensions. Decorative images should have empty alt text.
- Make key information available in rendered HTML; do not hide essential content behind inaccessible scripts or interactions.

## 4. Crawlability, indexing, and canonical control
- Important pages should return HTTP 200, be crawlable, not blocked by robots.txt, and have no unintended noindex.
- Keep canonical URLs self-consistent across internal links, sitemap, redirects, and structured data. Avoid chains, loops, soft 404s, duplicate variants, and mixed http/https or host versions.
- Include only canonical, indexable, useful URLs in XML sitemaps; keep lastmod truthful and update it only after material changes.
- Ensure robots.txt permits crawling of important resources and points to the correct sitemap. Robots.txt is not a reliable deindexing mechanism.
- Check mobile rendering, server responses, JavaScript rendering, broken links, orphan pages, pagination, and crawl paths.
- Use URL Inspection and Page Indexing reports for representative priority URLs; do not assume sitemap submission guarantees indexing.
- Do not mass-submit or repeatedly inspect URLs without a reason; respect Search Console quotas.

## 5. Page experience, mobile, and performance
- Mobile-first layout: readable text, usable navigation, accessible tap targets, no horizontal overflow, clear calls to action, and no intrusive interstitials.
- Monitor Core Web Vitals using field data where available: LCP target <= 2.5s, INP <= 200ms, CLS <= 0.1 at the 75th percentile. Treat these as good thresholds, not guaranteed ranking boosts.
- Reduce image payloads, reserve image dimensions, lazy-load below-the-fold media, avoid lazy-loading the main hero/LCP image, minimize render-blocking CSS/JS, and remove unused heavy scripts carefully.
- Avoid layout shifts, excessive animation, heavy backgrounds, blocking third-party widgets, and duplicate libraries.
- Maintain HTTPS, secure forms, accessible contrast, keyboard navigation, semantic HTML, and clear error states.
- Test real mobile experience and field data; a lab score alone is not the whole experience.

## 6. Structured data and search appearance
- Add valid JSON-LD only where it accurately describes visible page content and matches Google's supported feature policies.
- Use appropriate types such as Organization, LocalBusiness (only when eligible and factually accurate), WebSite, WebPage, BreadcrumbList, Product, and Article where applicable.
- Product structured data must use real product facts and verified price/availability only. Do not invent aggregateRating, review, offers, shipping, or return-policy data.
- Validate with Rich Results Test and monitor Search Console enhancement reports. Structured data can make a page eligible for a rich result; it does not guarantee display or improve ordinary ranking by itself.
- Keep schema consistent with visible content, canonical URL, and business identity. Fix required errors before optional warnings.

## 7. Authority, reputation, and links
- Earn relevant editorial and supplier/manufacturer/industry links through useful original resources, technical guides, tools, and real business relationships.
- Build brand recognition through consistent business identity and useful participation in relevant communities.
- Review inbound links for patterns that indicate paid/manipulative schemes; do not buy links, exchange at scale, automate link placement, or use private blog networks.
- Do not confuse third-party authority scores with Google's ranking systems. Measure real referring domains, relevance, traffic, and conversions.

## 8. Local and commercial discovery
- Keep business name, address/service area, phone, hours, and contact information accurate and consistent wherever published.
- Use a Google Business Profile only if the business is eligible; keep categories, services, photos, hours, and updates truthful.
- Create local landing pages only for genuinely served locations and include distinct local proof/value; never generate doorway city pages.
- Make quote/contact paths obvious, fast, accessible, and measurable. Explain shipping coverage and process only when confirmed.

## 9. Image, video, and AI-assisted discovery
- Use original product, warehouse, loading, and team imagery when available; ensure images accurately represent the item.
- Add descriptive captions and alt text; use image sitemaps when useful and ensure images are crawlable.
- For video, provide a clear title, description, thumbnail, and accessible transcript/captions where relevant.
- Maintain useful, accurate site descriptions and crawlable content for AI-powered search experiences. Do not promise inclusion in AI answers or use hidden keyword blocks.
- Keep llms.txt or AI retrieval files supplementary; they do not replace crawlable pages, quality content, links, or Search Console evidence.

## 10. Spam and policy safeguards
Never implement cloaking, hidden text/links, keyword stuffing, scaled low-value content, scraped content, doorway pages, sneaky redirects, fake reviews, fake structured data, expired-domain abuse, link spam, or misleading claims.
Do not create content solely to manipulate search engines. If a tactic risks violating Google spam policies, do not ship it; report the concern.

## 11. Measurement and prioritization
For each run, inspect existing work first and choose one non-duplicate, high-impact task. Prefer:
1. Critical crawl/indexing/canonical/robots/sitemap defects.
2. Broken pages, mobile usability, security, and performance issues with evidence.
3. High-impression queries/pages with poor CTR or positions 4–20.
4. Pages losing clicks/impressions, after checking seasonality and data completeness.
5. Cannibalization, orphan pages, and internal-link gaps.
6. Content gaps on commercially important product hubs.
7. Schema eligibility/errors and image/video discoverability.
8. Relevant authority and local visibility improvements.

Record baseline, affected URLs, evidence, proposed change, validation, and follow-up metric. Track clicks, impressions, CTR, average position, indexed coverage, CWV, conversions/leads where available. Do not attribute traffic changes to one edit without evidence.

## 12. Ahaneiffel-specific guardrails
- Primary property: https://ahaneiffel.top/ . Do not switch to ahaneiffel.com or www without explicit instruction.
- Preserve existing design unless the task specifically concerns design/performance and evidence supports a change.
- Avoid duplicate work and preserve useful existing content.
- Never change prices, inventory, orders, customer data, or production APIs.
- If Search Console, Analytics, Merchant Center, or PageSpeed data is unavailable, state that limitation and do not fabricate metrics.
- Keep all changes on a dedicated branch and propose a pull request. Never merge or deploy without user approval.
- Every 6-hour run should be bounded, cost-conscious, and report what was actually checked and changed. A scheduled check is not continuous 24/7 execution.
