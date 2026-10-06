# Ahaneiffel 50-Step SEO/GEO/AEO Execution Plan

## Objective
Harden ahaneiffel.top's technical SEO, topical hub architecture, AI/GEO retrieval signals, and automated quality gates without paid APIs or production mutation.

## Current state
- Sitemap index contains 13 child sitemaps.
- robots.txt points to the sitemap index.
- llms.txt and an AI retrieval map already exist.
- HTML integrity and AI/GEO workflows already exist.
- Codex agent workflow requires an OpenAI API key and is not the free automation path.

## Constraints
- Work only on ahaneiffel.top.
- No price, inventory, order, customer, or production API mutation.
- No fabricated facts.
- No automatic merge or deployment.
- Preserve Persian/RTL content and existing design.

## Files/components in scope
- .github/workflows/seo-free-integrity.yml
- .github/workflows/seo-live-smoke.yml
- scripts/seo_architecture_audit.py
- reference/ai-retrieval-map/index.html
- llms.txt
- sitemap index and child sitemaps
- existing HTML integrity workflow

## Implementation steps
1. Validate sitemap index shape.
2. Validate all sitemap hosts.
3. Validate sitemap child URL extensions.
4. Detect duplicate sitemap URLs.
5. Detect malformed XML.
6. Verify robots sitemap reference.
7. Verify AI retrieval map is indexed.
8. Verify llms.txt exists.
9. Verify primary hub routes are represented.
10. Verify price routes are represented.
11. Verify guide routes are represented.
12. Verify knowledge routes are represented.
13. Verify reference routes are represented.
14. Verify local routes are represented.
15. Verify services route is represented.
16. Verify buying route is represented.
17. Build deterministic architecture audit.
18. Flag duplicate intent routes for review.
19. Flag missing core hubs.
20. Flag alternate-domain references.
21. Flag HTTP internal URLs.
22. Validate canonical normalization in static HTML.
23. Validate exactly one canonical per HTML document.
24. Validate exactly one title per HTML document.
25. Validate useful H1 presence.
26. Validate JSON-LD parseability.
27. Validate schema.org context.
28. Validate AI map canonical.
29. Validate AI map dateModified.
30. Validate AI map sitemap inclusion.
31. Validate llms.txt core product routes.
32. Validate llms.txt buying/pricing routes.
33. Validate llms.txt source hierarchy.
34. Validate no fabricated price assertions in machine-readable map.
35. Keep price data out of static integrity assumptions.
36. Run existing HTML audit.
37. Run AI/GEO integrity checks.
38. Add live HTTP smoke checks.
39. Check sitemap child URLs return non-error responses.
40. Check robots returns success.
41. Check sitemap index returns success.
42. Check AI retrieval map returns success.
43. Check llms.txt returns success.
44. Check canonical host consistency from live HTML samples.
45. Check redirect/error signals are reported, not auto-fixed.
46. Preserve safe rollback via branch/PR.
47. Keep free automation independent of OpenAI API.
48. Produce machine-readable audit output.
49. Schedule the audit every six hours.
50. End in a reviewable PR; no automatic merge.

## Validation
Run the architecture audit, existing HTML audit, XML parsing, and workflow syntax/static checks available in CI.

## Risks
Live smoke checks depend on site availability. Existing pages may intentionally redirect or return non-200 responses; these are reported rather than mutated automatically.

## Rollback
Close the PR or revert its commits. No production deployment is performed by this work.

## Completion status
Implementation in progress.
