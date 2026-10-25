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
- **Implementation steps:** Expand each guide with actionable checklists, tables, FAQs, safe calculation guidance, structured Article/Breadcrumb metadata, and related links; add a visible hub section; include all three URLs in live smoke checks.
- **Validation:** Check title, description, canonical, one H1, visible text length, JSON-LD parseability, internal link targets, workflow syntax, and CI checks on the review branch.
- **Risks:** Static-site publication may lag behind repository changes; the live smoke check can fail until deployment finishes. Shipping charges are not stated as fixed values.
- **Rollback:** Revert the PR commit(s) if the live checks or site validation fail.
- **Completion status:** Implemented on review branch; validation and PR review pending. Do not merge automatically.
