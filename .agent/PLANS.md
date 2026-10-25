# Ahaneiffel Agent Execution Plans

For work spanning multiple files, use a short living execution plan.

Required sections:
- Objective
- Current state
- Constraints
- Files/components in scope
- Implementation steps
- Validation
- Risks
- Rollback
- Completion status

Keep plans factual and update them as discoveries change the approach. Do not invent repository behavior that has not been inspected.

## Current execution: buying, price-calculation, and shipping guides

- **Objective:** Improve useful buyer guidance and strengthen internal paths between pricing, transport, and order validation without inventing market rates.
- **Current state:** Three existing guides were short and not linked from the main guide hub: `guides/iron-order-check/index.html`, `guides/iron-price-calculation/index.html`, and `guides/iron-shipping-cost/index.html`.
- **Constraints:** Preserve Persian RTL, canonical host `https://ahaneiffel.top/`, existing phone details, and the current pricing feed. Do not alter prices, stock, or commercial dates. No unsupported promises or fabricated product specifications.
- **Files/components in scope:** The three guide pages, `guides/index.html`, and `.github/workflows/live-deployment-smoke.yml`.
- **Implementation steps:** Expand each guide with actionable checklists, tables, FAQs, safe calculation guidance, structured Article/Breadcrumb metadata, and related links; add a visible hub section; localize 52 guide-hub anchors into Persian; include all three URLs in live smoke checks.
- **Validation:** Confirmed title, description, canonical, one H1, visible text length, and parseable JSON-LD on all three expanded guides; verified all 52 localized hub links resolve to existing guide files; key cross-link targets exist. Workflow and CI checks are still pending on the final review-branch commit.
- **Risks:** Static-site publication may lag behind repository changes; the live smoke check can fail until deployment finishes. Shipping charges are not stated as fixed values.
- **Rollback:** Revert the PR commit(s) if the live checks or site validation fail.
- **Completion status:** Implemented on review branch; validation and PR review pending. Do not merge automatically.


## Current execution: sitemap target integrity

- **Objective:** Catch XML sitemap entries that point to missing pages, non-canonical hosts, duplicate URLs, or noindex pages before they reach production.
- **Current state:** The reference sitemap listed `/reference/steel-buying-checklist/`, but no corresponding HTML file existed. The repository has the indexable, self-canonical page `/reference/steel-project-buying-checklist/`.
- **Constraints:** Do not generate new URLs or pages by assumption; only list verified files with self-canonical, indexable HTML. Preserve the canonical host and do not alter market prices or business data.
- **Files/components in scope:** `scripts/audit_internal_links.py`, `sitemap-reference.xml`, and the existing internal-link audit workflow.
- **Implementation steps:** Add sitemap XML parsing and target checks to the existing audit; verify canonical host, duplicate locs, local target existence, and noindex/canonical mismatch; replace the nonexistent reference URL with the verified existing checklist page.
- **Validation:** Confirmed the replacement page exists, has a self-referencing canonical, and is indexable. GitHub Actions validation is required to confirm the full repository audit has no additional blocking sitemap issues.
- **Risks:** Existing sitemap entries may expose additional historical inconsistencies; the new checks intentionally fail the audit when a listed URL has no local target or conflicts with indexing signals.
- **Rollback:** Revert this branch's two commits if the full audit identifies false positives that cannot be resolved safely.
- **Completion status:** Code and sitemap correction committed to review branch; automated checks pending.
