# ShopStream Platform Design Doc

- Status: draft v0.1
- Author: omkarpere
- Last updated: 2026-10-23

## 1. Problem and goals
ShopStream is a fictional online retailer. Today its teams work from different, delayed views of the business. Marketing cannot see the shopper funnel live. Finance cannot prove that reported revenue matches orders. Customer success has no single view of a customer, and security has no guarantee that personal data is protected. This project builds one platform on Google Cloud that serves all four needs with data that is fresh, correct and safe.

This is a portfolio project built on simulated data to practice production data engineering patterns. It is not a production system.

| ID | Stakeholder | Goal | How we will measure it |
|---|---|---|---|
| G1 | Marketing | Live funnel data | From the simulator publishing an event to it being saved in Silver: under 60 seconds at p95. The start clock is the Pub/Sub publish timestamp, not `event_time`, which is client time. The end clock is the Silver commit time. The Silver to BigQuery delay is measured separately (see Section 8) |
| G2 | Marketing, Finance | Correct streaming results | Zero duplicate event IDs in Silver after a one-hour replay; events up to 10 minutes late land in the correct windows; events later than the watermark go to a late-data table, never dropped silently |
| G3 | Customer success | Fresh operational data | Postgres inserts, updates and deletes visible in BigQuery within 2 minutes at p95, measured with a timestamp written at the source |
| G4 | Finance | Trusted revenue and customer 360 | Gold tables reconcile to source orders to the cent; daily marts ready by 06:00 IST |
| G5 | Security and compliance | PII protected by default | Analyst role sees masked email and phone; steward role sees raw values |
| G6 | Engineering leadership | Safe reprocessing | A 30-day backfill reproduces the original row counts and checksums |
| G7 | Engineering leadership | Failures are noticed fast | Alerts within 5 minutes for pipeline failure, Pub/Sub backlog and stale data |

Engineering goals: all infrastructure in Terraform, every change through a pull request with automated checks, every pipeline idempotent and restartable, and measured before-and-after numbers for performance and cost.

### Assumptions

- All data is simulated. There are no real customers.
- Everything runs in a single GCP region.
- The environment is only switched on during work sessions, so freshness and alert goals (G1, G3, G7) only apply while it is running.
- An average event is about 1 KB of JSON. This is a guess and will be replaced by the real average measured from the simulator.
- Free trial credit is the budget limit, and budget alerts warn but do not stop spending.

## 2. Non-goals (what we deliberately won't build)
- **Multi-region deployment and disaster recovery.** It multiplies cost and failure modes without teaching anything the single-region design does not already cover.
- **Real customers or real personal data.** All data is simulated, which removes legal exposure while still letting us practice PII classification, masking and audit.
- **Machine learning features or a feature store.** The goal is the data platform, not models. Adding ML would compete for the same limited time.
- **Self-managed CDC with Debezium.** Datastream gives the same outcome with far less operational work. We document the trade-off in an ADR instead of building both.
- **24/7 on-call and formal SLAs.** There is no real business or pager. We write alert runbooks and run failure drills to practice the thinking.
- **Sustained peak throughput.** The simulator can reach 5,000 events per second, but we run it at that rate only briefly for benchmarks, because holding it would burn the trial credit without new learning.

## 3. Stakeholders and requirements

### 3.1 How each goal is measured

G1 to G7 match F1 to F7 in the project guide. Every goal needs a start point, an end point and a place where the result is written down.

| Goal | Start point | End point | Where recorded |
|---|---|---|---|
| G1: event saved in Silver within 60 s at p95 | Time Pub/Sub receives the event (set by Pub/Sub's server) | Time the Spark job saves the event in Silver | `docs/measurements/latency.md` |
| G2a: no duplicates | Silver row count before the replay | Silver row count after the replay (must be equal) | `docs/measurements/dedupe.md` |
| G2b: 8 min late events still included | Simulator sends an event with `event_time` 8 min in the past | Event found in the correct 1-minute window in Silver | `docs/measurements/late-events.md` |
| G2c: 15 min late events go to the late-data table | Simulator sends an event with `event_time` 15 min in the past | Event found in the late-data table and not in Silver windows | `docs/measurements/late-events.md` |
| G3: Postgres insert, update and delete visible in BigQuery within 2 min at p95 | Timestamp written in the Postgres row when the change is made (source clock) | Time the change first shows up in a BigQuery query (query time) | `docs/measurements/cdc-latency.md` |
| G4a: revenue matches source orders to the cent | Total revenue from the source orders table for one day | Total from the Gold daily revenue table for the same day (difference must be 0.00) | `docs/measurements/reconciliation.md` |
| G4b: daily marts ready by 06:00 IST (00:30 UTC) | Daily job starts (Airflow run start, UTC) | Gold tables finish building (must be before 00:30 UTC) | `docs/measurements/mart-readiness.md` |
| G5a: PII masked for analysts, raw for stewards | Same query run as the analyst role, then as the steward role | Analyst sees masked email and phone, steward sees raw values (screenshot of both) | `docs/measurements/pii-masking.md` |
| G5b: access to PII columns is auditable | A query reads a PII column as a named role | The access log shows who read it and when | `docs/measurements/pii-audit.md` |
| G6: 30-day backfill reproduces the original | Row count and checksum of the 30-day range from the original run | Row count and checksum after the backfill (must be identical) | `docs/measurements/backfill.md` |

## 4. Architecture overview
## 5. Data sources and data design
## 6. Key design decisions (link ADRs)
## 7. Risks and mitigations
## 8. Open questions

Each question has an owner and a date to resolve it.

1. **How will BigQuery read the Iceberg Silver tables, and how much delay does that add?** This decides whether the dashboard is as fresh as G1. Owner: me. Resolve by: end of Week 3.
2. **Does the Datastream staleness setting for BigQuery allow G3 (2 minutes)?** I must check the docs before promising it. Owner: me. Resolve by: start of Week 4, before configuring CDC.
3. **How do we route events older than the watermark to a late-data table (G2)?** Spark discards them by default, so we need our own logic. Owner: me. Resolve by: end of Week 3.
4. **How do we handle 06:00 IST for G4 when Airflow defaults to UTC?** 06:00 IST is 00:30 UTC. Owner: me. Resolve by: end of Week 2, when the first DAG is written.

