# ADR-007: Dev and prod as separate GCP projects
- Status: accepted
- Date: 2026-10-27

## Context
I will test risky things in this project: teardown scripts, failure drills, IAM changes and Terraform destroys. Prod must only change through CI/CD. I need a hard wall between the two so a mistake in dev cannot touch prod.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| One project, names prefixed dev_ and prod_ | Least setup; one bill | Only naming separation; one IAM policy, one quota pool, one audit log; a wrong role or destroy can reach prod |
| Two projects: shopstream-dev and shopstream-prod | Separate IAM, quotas, billing view and audit logs; separate Terraform state per env | Two projects to set up and watch; more config to keep in sync |
| Three projects (dev, staging, prod) | Closest to large teams; a safe place for pre-prod tests | Extra cost and setup for a solo project; the guide asks for two |

## Decision
Two separate projects, shopstream-dev and shopstream-prod. The biggest reason: a mistake in dev must not be able to reach prod, and project boundaries are the strongest isolation GCP gives for IAM, quota and audit.

## Consequences
- Easier: each env has its own Terraform folder (terraform/envs/dev and terraform/envs/prod), its own state bucket and its own project_id; labels env, owner and project are enforced in both.
- Harder: two projects to keep in sync; prod only changes through CD, so I must get CI/CD working in Week 7 before real prod deploys.
- Not yet verified: that each project has its own budget alert at 50, 80 and 100 percent. Check in the billing console.
- Revisit: add a staging project only if I need a pre-prod test step.
