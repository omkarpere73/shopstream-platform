# ADR-005: Cloud Composer 3 for orchestration, created only for sessions
- Status: accepted
- Date: 2026-10-27

## Context
Batch jobs, quality checks, dbt runs and backfills need an orchestrator with retries, sensors, SLAs and alerts. Composer is the most expensive part of this project and bills for as long as the environment exists, even when no DAG runs. I need Airflow skills on GCP without a large bill.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Local Docker Airflow only | Free; fast to change; fine for writing and testing DAGs | Does not exercise Composer itself (GCS DAG sync, Secret Manager config, IAM) |
| Cloud Scheduler plus Cloud Run jobs | Pay per run; the guide's cheaper fallback | No Airflow features (sensors, retries, backfill UI, SLAs); I would build them by hand |
| Cloud Composer 3 (Composer 2 can still be created, not chosen) | Managed Airflow 2 and 3; Google upgrades the infrastructure; usage billed in DCU-hours | Billed while it exists; Mumbai and INR price not read yet; local Airflow version must match |

## Decision
Cloud Composer 3, created with Terraform only for integration and demo sessions and destroyed the same day. Daily DAG work runs on local Docker Airflow. The biggest reason: cost is controlled by how long the environment lives, so I keep the real Composer skills without paying for idle hours.

## Consequences
- Easier: managed Airflow with DAGs synced from a GCS bucket; Google upgrades the infrastructure; a Terraform module makes create and destroy repeatable.
- Harder: the local Docker Airflow version must match the Composer Airflow version; Airflow 3 may rename datasets, to check in Week 2; the cost depends on destroying the environment after every session.
- Not yet verified: Composer 2 in asia-south1, the Composer 2 price, and the Mumbai and INR price for Composer 3 (open questions 6 and 9). Unofficial monthly cost claims from blogs are not used.
- Revisit: first Composer session in Week 2; if the cost is too high, switch to Cloud Scheduler plus Cloud Run jobs (guide fallback) and record a new ADR. Teardown: destroy the Composer module after each session and check nothing is left running.
