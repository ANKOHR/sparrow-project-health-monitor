# Build evidence

Local CPU-only end-to-end installed CLI demo measured on 2026-10-01: 0.865 seconds for fixtures, run, and Markdown report in three separate processes. Acceptance limit: under 5 seconds. This is measured program runtime, not time saved for a business.

Synthetic ground truth: 40 groups of five. Each group contains one clear project, one overdue project, one over-budget project, one blocked project, and one project triggering all three rules. Thus 200 projects, 160 flagged, 80 overdue, 80 over-budget, 80 blocked. Each group budgets 50000 cents and spends 39000 cents, yielding 2000000 budget cents and 1560000 spent cents. All are illustrative synthetic amounts.

All totals and reason counts matched the independent expectations file exactly. Planted flagged IDs match exactly, with zero synthetic false positives. Changed input spending changes the computed flag count; corrupted expectation totals do not match computed results. Tests also cover schema drift, duplicate IDs, malformed JSON, write failure, empty directories, completion/date boundaries, Unicode, large strings and deterministic bytes.

No real business data, saved time, revenue, predictive accuracy or trial verdict has been measured. Two-week improvement decision is pending.
