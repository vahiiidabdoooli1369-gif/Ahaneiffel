# Ahaneiffel Copilot Instructions

## Project scope
- Primary project: https://ahaneiffel.top (GitHub Pages, static HTML, Persian RTL).
- Keep canonical URLs on https://ahaneiffel.top/.
- Do not introduce ahaneiffel.com URLs unless the task explicitly asks for cross-domain work.
- Read `AGENTS.md`, the relevant sections of `.agent/PLANS.md`, and `.agent/task-ledger.json` before proposing work. Reuse existing audits and do not repeat completed tasks without regression evidence.

## Business-data protection
- Never change prices, stock, inventory, customer records, orders, payments, contact details, business hours, or production integrations unless the user explicitly authorizes that exact change.
- Never fabricate prices, offers, availability, ratings, reviews, certifications, manufacturer claims, backlinks, search rankings, traffic, or Search Console metrics.
- Distinguish historical prices from verified current prices. Do not advance price dates without same-day authorized verification.
- Do not mark pages freshly reviewed or update dateModified/lastmod unless substantive content changed and the evidence is recorded.

## SEO and content quality
- Prioritize crawlability, indexability, canonicals, robots, sitemap integrity, valid structured data, internal links, mobile usability, accessibility, performance, and useful Persian content.
- Avoid keyword stuffing, doorway pages, near-duplicate pages, thin content, and unverified claims.
- Preserve useful existing content, stable URLs, Persian typography, RTL behavior, and mobile-first layout.
- Structured data must match visible page content. Do not add fake Offer, AggregateRating, Review, or availability data.

## Engineering and delivery
- Inspect before editing. Make small, focused, testable changes.
- Never push directly to `main`, merge a PR, or deploy production from an agent session.
- Use an isolated branch and a reviewable PR. Run relevant existing repository checks and report exact outcomes.
- Do not modify agent instructions, workflow permissions, secrets, or automation schedules as part of routine SEO work.
- Never print or expose credentials, tokens, or environment variables.
- If evidence, access, or a required source is missing, report the limitation instead of guessing.

## Reporting
- Respond in Persian unless asked otherwise.
- Separate verified findings, hypotheses, changes, tests, blockers, and next actions.
- Link every claim about ranking or traffic to actual first-party evidence; otherwise label it as unverified.
