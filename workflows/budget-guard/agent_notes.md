# Budget Guard — Agent Notes

Running learnings, exceptions, and corrections specific to this workflow's instance.
The `learning-loop` workflow may also append here.

## 2026-04-22 — v0.1.0 created

Pulled from `paperclipai/paperclip` Cost Control primitive. Selected because it is
the highest-leverage primitive Paperclip ships that we do not already have in some
form. `llm-usage-report` covers reporting; budget-guard covers prevention.

Designed deliberately to start in `dry_run` mode so the first 3 mornings produce
human-readable output without disabling anything. Nick reviews the decision list,
then flips `mode: enforce`.

## Failures

None yet — first run pending.

## Auto-applied

None — auto-apply class `monthly_cap_enforcement` is not yet listed in
`workflows/ecosystem-intel/rules.md#auto_apply_classes`.
