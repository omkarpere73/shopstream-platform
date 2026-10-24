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
- Design doc sections 1 and 2 merged via PR #16

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
- Fix: repo now allows squash merges only.
- Prevention: run `git status` before branching. Run protection tests only after a merge,
  and print `git branch --show-current` first.

Decisions made (link ADR):
- Repo is public so rulesets are enforced (they need a paid plan on private repos).
- Squash merge only, to keep one commit per PR on main.
- Per-project budgets. Alerts only notify, so the trial credit plus a teardown script
  are the real cost protection.
- ADRs not written yet (F-5).

Metrics captured:
- Free trial credit: INR 28,796.63
- Trial expiry: about 21 Jan 2027 (confirm exact date in Billing)
- Budgets: dev INR 1,500 per month, prod INR 500 per month (provisional until cost model)

Next week:
- Finish design doc sections 3 to 8 (F-3)
- Architecture diagram (F-4)
- ADRs 001 to 008 (F-5)
- Terraform skeleton, remote state and teardown (F-6)
- INR cost model
