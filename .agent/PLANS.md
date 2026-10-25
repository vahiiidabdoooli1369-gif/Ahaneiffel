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


## Current execution: guide sitemap coverage batch

- **Objective:** Make selected existing, indexable buyer guides discoverable through the XML sitemap and verify publication after deployment.
- **Current state:** Four useful project guidance pages existed with self-referencing canonicals but were absent from `sitemap-guides.xml`: order master checklist, project material selection, quote normalization, and steel storage at the worksite.
- **Constraints:** Include only pages verified to exist, self-canonical, and indexable. Do not add alias/noindex pages or fabricate `lastmod` dates.
- **Files/components in scope:** `sitemap-guides.xml` and `.github/workflows/live-deployment-smoke.yml`.
- **Implementation steps:** Add the four canonical URLs without an invented modification date; add live smoke assertions for title, canonical, H1 count, and minimum visible content.
- **Validation:** Repository metadata verified for each target; final CI and live deployment checks must pass before considering this batch complete in production.
- **Risks:** Static-site publication may lag behind the repository; a page may fail the live visible-content threshold even if source metadata is correct.
- **Rollback:** Revert this PR if the new URLs fail the sitemap integrity or live publication checks.
- **Completion status:** Changes committed on review branch; automated checks pending.


### Additional verified navigation cleanup

- **Finding:** `guides/index.html` contained two sections with the same `id="seo-orphan-hub"`; the second repeated the same guide links with English slug labels, creating duplicate IDs and unnecessary duplicate navigation.
- **Change:** Removed the duplicate English-only section and added Persian links for the three existing guides missing from the localized hub: perforated-sheet hole pattern, scaffolding-pipe thickness, and quote normalization.
- **Validation:** The target files were verified to exist. HTML integrity and internal-link CI must pass on the updated branch before merge.


## Current execution: expand operational guides

- **Objective:** Replace short, repetitive operational guidance with practical workflows for order changes, purchase timing, receiving-quantity checks, and storage layout.
- **Current state:** Four self-canonical, indexable pages contained only a few short paragraphs and overlapping bullet lists. They were already linked from the guide directory but needed more actionable depth.
- **Constraints:** Preserve canonical URLs, Persian RTL, and existing internal-link relationships. Do not invent delivery lead times, fixed warehouse stack heights, engineering limits, market prices, or supplier availability.
- **Files/components in scope:** Four guide pages, `sitemap-guides.xml`, and `.github/workflows/live-deployment-smoke.yml`.
- **Implementation steps:** Add task-oriented procedures, practical checklists and tables, visible FAQs, related links, responsive table wrappers, and valid Article/Breadcrumb structured data; include verified pages in the guide sitemap and live smoke tests.
- **Validation:** Source changes committed to a review branch. HTML integrity, structured-data integrity, sitemap/internal-link audit, and live deployment smoke checks must pass before merge; production publication remains a separate check.
- **Risks:** More text does not itself guarantee rankings; structured data must stay aligned with visible page content. Safety-related storage advice deliberately avoids generic load/stack limits.
- **Rollback:** Revert this PR if automated validation detects malformed markup, schema, sitemap targets, or live pages.
- **Completion status:** Implemented on review branch; automated checks pending.


## Current execution: internal fragment-link audit

- **Objective:** Detect broken jump links such as `#specifications` or `/guides/example/#faq` that the existing path-only link audit cannot detect.
- **Current state:** The internal-link audit checked whether target pages exist but ignored fragment identifiers. A link can therefore point to a valid page and still jump to a nonexistent section.
- **Constraints:** Do not make fragment findings deployment-blocking until the report has been reviewed for dynamic/JavaScript-generated targets. Existing missing-path and sitemap failures remain blocking.
- **Files/components in scope:** `scripts/audit_internal_links.py`.
- **Implementation steps:** Parse HTML `id` attributes and legacy anchor `name` attributes, resolve local paths and URL-encoded fragments, cache target identifiers for performance, and report missing fragments with source page and target.
- **Validation:** The updated audit will run in the existing pull-request workflow. Findings are intentionally non-blocking for the first reporting pass.
- **Risks:** Dynamic tabs or scripts may create targets after page load; those require manual review before changing the report to a blocking gate.
- **Rollback:** Revert the fragment audit function if it produces excessive false positives or materially slows the repository audit.
- **Completion status:** Implemented on review branch; automated validation pending.


## Current execution: logistics and data-quality guide expansion

- **Objective:** Improve five thin, indexable guides covering loading sequence, stock reservation, unit conversion, delivery evidence, and market-price data confidence.
- **Current state:** The pages had short summaries and limited checklists; several were already linked from the guide hub but lacked enough practical decision support.
- **Constraints:** Preserve canonicals and avoid invented current prices, delivery promises, fixed stock reservations, or product-specific weights. Unit examples are explicitly educational; no lastmod dates are fabricated.
- **Files/components in scope:** Five guide pages, sitemap-guides.xml, and .github/workflows/live-deployment-smoke.yml.
- **Implementation steps:** Add unique procedures, responsive tables, evidence/checklists, visible FAQs, related links, and structured data where absent; add the expanded indexable pages to sitemap and live smoke checks.
- **Validation:** Source changes committed on a review branch. HTML, structured-data, sitemap/internal-link and free SEO integrity checks must pass before merge; live publication is checked separately after merge.
- **Risks:** Content completeness does not guarantee rankings; existing date metadata on pages with prior Article markup is retained, not newly asserted by this batch.
- **Rollback:** Revert the PR if validation detects schema, HTML, sitemap, or publication regressions.
- **Completion status:** Implemented on review branch; automated checks pending.
