# Ahaneiffel Free Agent Mode

This mode is designed for running the Ahaneiffel maintenance agent through a signed-in ChatGPT/Codex client instead of the GitHub Actions API workflow.

## Purpose

Maintain `https://ahaneiffel.top/` with the same safety contract as `AGENTS.md`, without requiring an OpenAI API key.

## Operating loop

1. Open the repository in Codex (desktop/CLI/IDE) and sign in with the ChatGPT account.
2. Read `AGENTS.md`, `.agent/PLANS.md`, and this file.
3. Inspect current branches, open PRs, recent commits, and existing SEO workflows.
4. Never repeat a task already implemented in an open PR or recent commit.
5. Select exactly one highest-impact safe SEO/GEO/engineering task.
6. Work on a dedicated branch named `agent/free-YYYYMMDD-<short-task>`.
7. Run relevant tests/audits.
8. Summarize files changed, validation, risks, and the next task.
9. Push the branch and open a PR against `main`.
10. Never merge automatically.

## Safety

- Primary domain: `ahaneiffel.top`.
- Do not change prices, inventory, orders, customer data, or production APIs.
- Do not fabricate prices, reviews, ratings, certifications, stock, authorship, or business claims.
- Preserve Persian/RTL content and working design.
- Prefer the smallest reviewable patch.
- Stop if the task is destructive or ambiguous.

## First-run priorities

Check existing open PRs before choosing work. Current known PRs may already cover HTML audits and a product-wide growth batch; review those changes first and do not duplicate them.

Recommended order:

A. indexing/canonical/robots/sitemap defects
B. structured-data defects
C. internal-linking and topical-cluster gaps
D. AI/GEO retrieval quality
E. performance/accessibility
F. targeted content improvements backed by repository evidence

## Important limitation

This is a local/client agent mode. It is not a background GitHub Actions service. The existing scheduled GitHub Actions workflow uses `OPENAI_API_KEY` and therefore remains unavailable when API quota is unavailable.

