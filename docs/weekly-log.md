# Weekly log

## Week 1 (2026-10-23 onwards)

Goal: design and foundation. Repo, planning setup, GCP guardrails, design doc.

Done:
- Repo skeleton, Makefile, lint config, PR template and ADR template merged to main
- GitHub project board with 8 epics and 7 stories (F-1 to F-7)
- GCP account with free trial; projects `shopstream-dev` and `shopstream-prod`
- Budgets: `budget-dev` and `budget-prod`, alerts at 50/80/100%
- Branch protection proven: a direct push to `main` was rejected by the server
  (evidence: [rejection screenshot](evidence/branch-protection-rejection.png))
- Design doc sections 1 to 4 merged (PR #16 for sections 1 and 2, PR #22 for section 4)
- Architecture diagram pass 1 (streaming path) merged; pass 2 is ticket #27
- Terraform state buckets for dev and prod
- Terraform skeleton for dev and prod (PR #24): own state bucket per env, google provider pinned to ~> 7.0, fmt, validate and plan pass
- Region check for asia-south1 (PR #26, issue #25), recorded in design doc section 4.5
- Board cleanup: #13 reopened because ADRs are not written, #27 created for diagram pass 2
- Squash-only merge setting applied on 26 Oct (see correction in the PR #16 incident)
- Self-review comments added to PRs #24 and #26

Broke and how I fixed it:
- Labelled the wrong GCP project (`My First Project`) on the first attempt. Fixed by
  checking the project picker before every save. Prevention: labels will come from
  Terraform, not the console.

### Incident: test commit leaked into PR #16
- What happened: an empty test commit was already on local main when I created the
  feature branch, so it travelled into the PR and landed in main's history.
- Detection: the PR commit list showed 3 commits instead of 2; `git log --graph` confirmed it.
- Root cause: I branched without reading `git status`, which said "ahead of origin/main by 1".
- Impact: one empty commit in history. No functional impact.
- Fix (planned): allow squash merges only.
- Correction (26 Oct): this fix was NOT applied at the time. The repo allowed merge, squash and rebase until 26 Oct, so PRs #20 to #26 used merge commits.
- Squash-only is now set in repo settings and verified with the GitHub API.
- Prevention: run `git status` before branching. Run protection tests only after a merge,
  and print `git branch --show-current` first.

### Incident: could not resolve host github.com on first push of F-7
- What happened: the first `git push` of the Terraform skeleton branch failed with `Could not resolve host: github.com`.
- Detection: the error printed in the terminal.
- Root cause: not diagnosed.
- Impact: none. The push worked on retry.
- Prevention: if it repeats, note the time, then check network and DNS before retrying.

### Incident: ticket numbering drift
- What happened: board labels (F-n) did not match the GitHub issue numbers used in commits and PRs.
- Detection: while updating status I found #13 (ADRs) in Done with no ADRs written, and #12 (diagram) in Done with pass 2 not drawn.
- Root cause: two numbering schemes, and tickets closed before their acceptance criteria were met.
- Impact: the board showed work as done that was not. No code impact.
- Fix: renamed #13, #14 and #15; reopened #13 and moved it to Backlog; kept #12 closed because pass 1 shipped; created #27 for diagram pass 2.
- Prevention: commits and PRs reference the issue number (#N); F-n is only a label. Close a ticket only when its acceptance criteria are met.

Decisions made (link ADR):
- Repo is public so rulesets are enforced (they need a paid plan on private repos).
- Squash merge only, to keep one commit per PR on main.
- Per-project budgets. Alerts only notify, so the trial credit plus a teardown script
  are the real cost protection.
- ADRs not written yet (issue #13, label F-9). Planned for Day 5.

Metrics captured:
- Free trial credit: INR 28,796.63
- Trial expiry: about 21 Jan 2027 (confirm exact date in Billing)
- Budgets: dev INR 1,500 per month, prod INR 500 per month (provisional until cost model)

Next week:
- ADRs 001 to 008 (issue #13). ADR-001: note the Dataproc rename. ADR-005: verify Composer 2 vs 3 and compare INR cost from the official pricing page
- Design doc: fill sections 5, 6 (ADR index) and 7, and close the small section 1 gaps
- Architecture diagram pass 2 (issue #27)
- First real Terraform resources (modules, plan before apply in dev) and a teardown script. This is the open Week 1 deliverable. Cost warning first
- INR cost model
