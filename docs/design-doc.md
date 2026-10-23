# ShopStream Platform Design Doc

- Status: draft v0.1
- Author: omkarpere
- Last updated: 2026-10-23

## 1. Problem and goals
ShopStream is a fictional online retailer. Today its teams work from different, delayed views of the business. Marketing cannot see the shopper funnel live. Finance cannot prove that reported revenue matches orders. Customer success has no single view of a customer, and security has no guarantee that personal data is protected. This project builds one platform on Google Cloud that serves all four needs with data that is fresh, correct and safe.

This is a portfolio project built on simulated data to practice production data engineering patterns. It is not a production system.

| ID | Goal | How we will measure it |
|---|---|---|
| G1 | Live funnel and sales dashboards | Clickstream event to queryable table in under 60 seconds at p95 |
| G2 | Correct streaming results | Zero duplicate event IDs in Silver after a one-hour replay; events up to 10 minutes late land in the correct windows |
| G3 | Fresh operational data | Postgres inserts, updates and deletes visible in BigQuery within 2 minutes |
| G4 | Trusted revenue and customer 360 | Gold tables reconcile to source orders to the cent; daily marts ready by 06:00 |
| G5 | PII protected by default | Analyst role sees masked email and phone; steward role sees raw values |
| G6 | Safe reprocessing | A 30-day backfill reproduces the original row counts and checksums |
| G7 | Failures are noticed fast | Alerts within 5 minutes for pipeline failure, Pub/Sub backlog and stale data |

Engineering goals: all infrastructure in Terraform, every change through a pull request with automated checks, every pipeline idempotent and restartable, and measured before-and-after numbers for performance and cost.


## 2. Non-goals (what we deliberately won't build)
- **Multi-region deployment and disaster recovery.** It multiplies cost and failure modes without teaching anything the single-region design does not already cover.
- **Real customers or real personal data.** All data is simulated, which removes legal exposure while still letting us practice PII classification, masking and audit.
- **Machine learning features or a feature store.** The goal is the data platform, not models. Adding ML would compete for the same limited time.
- **Self-managed CDC with Debezium.** Datastream gives the same outcome with far less operational work. We document the trade-off in an ADR instead of building both.
- **24/7 on-call and formal SLAs.** There is no real business or pager. We write alert runbooks and run failure drills to practice the thinking.
- **Sustained peak throughput.** The simulator can reach 5,000 events per second, but we run it at that rate only briefly for benchmarks, because holding it would burn the trial credit without new learning.

## 3. Stakeholders and requirements
## 4. Architecture overview
## 5. Data sources and data design
## 6. Key design decisions (link ADRs)
## 7. Risks and mitigations
## 8. Open questions
