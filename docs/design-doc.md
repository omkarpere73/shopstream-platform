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
| G7a: pipeline failure alert within 5 min | Time the failure is caused (my clock, noted in the log) | Time the alert email arrives (email timestamp) | `docs/measurements/alert-latency.md` |
| G7b: Pub/Sub backlog alert within 5 min | Time the streaming job is paused on purpose | Time the alert email arrives | `docs/measurements/alert-latency.md` |
| G7c: stale data alert within 5 min | Time the simulator is stopped on purpose | Time the alert email arrives | `docs/measurements/alert-latency.md` |

### 3.2 Latency budget

G1 allows 60 seconds from Pub/Sub receiving an event to that event being saved in Silver. This table splits the 60 seconds into stages. Stage 3 is a design choice (the trigger interval), and the other stages are placeholders until measured in Week 3.

| Stage | What happens | Budget |
|---|---|---|
| 1 | Pub/Sub makes the event available to Spark (the G1 clock starts when Pub/Sub receives it) | TBD (measure in Week 3) |
| 2 | Spark picks the event up from Pub/Sub | TBD (measure in Week 3) |
| 3 | Event waits for the next micro-batch to start | Up to 30 s (trigger interval) |
| 4 | Spark processes the batch (parse, dedupe) | TBD (measure in Week 3) |
| 5 | Spark saves the batch to Silver (Iceberg commit) | TBD (measure in Week 3) |

Stage 3 can use half of the 60 seconds, so stages 1, 2, 4 and 5 must fit in the remaining 30 seconds. If the measured total exceeds 60 s at p95, the first lever is a shorter trigger interval, at the cost of more small files.

### 3.3 Capacity estimate

These numbers are back-of-envelope estimates based on the 1 KB per event assumption in Section 1. They will be replaced by the simulator's measured average event size.

| Scenario | Events per second | Events per day | Data per second | Data per day |
|---|---|---|---|---|
| Peak (benchmark only, run for minutes) | 5,000 | 432 million | about 5 MB | about 432 GB |
| Development rate | 100 | 8.64 million | about 0.1 MB | about 8.6 GB |

The platform only runs during work sessions, so real daily volume is far below these figures. Cost of one peak benchmark run: TBD (INR, from the billing report in Week 3).

If data were 100 times larger, the first things to revisit would be Spark cluster size, the trigger interval (to avoid small files) and BigQuery partitioning.

## 4. Architecture overview

### 4.1 Streaming path (diagram pass 1)

This section covers the streaming path only. CDC, the FX batch job, BigQuery, dbt and Composer are added in diagram pass 2.

![ShopStream streaming path](diagrams/streaming-path.png)

Editable source: `diagrams/streaming-path.excalidraw`.

**One event, left to right**

1. The event simulator sends a JSON event (schema_version 2) to a Pub/Sub topic. It also writes the event ID to a ground-truth log at send time. The log is what lets us prove "no loss, no duplicates" after a restart.
2. One Spark Structured Streaming job on Dataproc reads from Pub/Sub. The read mechanism (Pub/Sub connector or a fallback) is pending an ADR.
3. The job parses and validates each row against an explicit schema. Rows that fail go to the dead-letter sink with the raw payload, the error reason and the ingestion time. The sink type (GCS path or Pub/Sub topic) is pending ADR-008. The pipeline keeps running.
4. Valid rows are appended untouched to Bronze (Iceberg on GCS, partitioned by event date). Bronze is written before dedupe, so it keeps duplicates and is a faithful record of what arrived.
5. The job then deduplicates on `event_id` inside a 10-minute watermark on `event_time` and writes Silver (Iceberg on GCS).
6. Each query writes offsets and state to its own checkpoint path on GCS, and reads them back on restart. Checkpoint locations are never shared between queries.

**Accounting rule:** Bronze rows plus dead-letter rows should equal the events in the ground-truth log, duplicates included. This is the check for the restart test.

**Latency link:** the 30 s trigger in the diagram is the stage-3 allowance in the latency budget (Section 3.2).

**Not decided yet:** where events later than the watermark go is an open question (Section 8).

### 4.2 Components and failure behaviour

| Component | Role | Where its state lives | If it fails | Detection |
|---|---|---|---|---|
| Event simulator | Generates events with duplicates, late and malformed rows | Stateless; writes the ground-truth log | Events stop arriving. Nothing downstream is corrupted. | Freshness alert on Silver (TBD threshold, see Section 8) |
| Ground-truth log | Independent record of every event ID sent | Durable file or table (location TBD) | Cannot prove no-loss for that run. Pipeline is unaffected. | Manual check before each restart test |
| Pub/Sub topic | Buffers events between producer and Spark | Managed by Google | Managed service; messages are retained until acknowledged | Oldest unacked message age over 5 minutes |
| Spark Structured Streaming job | Parse, validate, write Bronze, dedupe, write Silver | Checkpoint on GCS (job holds no durable state) | Unacknowledged messages stay in Pub/Sub. A restart resumes from the checkpoint. A half-finished batch may be replayed, so sinks must be idempotent. | Job not running, or processing lag growing for 10 minutes |
| Dead-letter sink | Quarantines rows that fail parse or validation | GCS path or Pub/Sub topic (pending ADR-008) | Bad rows could be lost, so this sink must be at least as reliable as Bronze | Dead-letter rate over threshold (TBD) |
| Bronze (Iceberg on GCS) | Faithful raw copy of valid events, before dedupe | GCS | Reprocess from Pub/Sub if still retained, else from the ground-truth comparison | Volume vs 7-day baseline (guide Section 15) |
| Silver (Iceberg on GCS) | Deduplicated, typed events | GCS | Rebuild from Bronze | Freshness: max event_time older than 10 minutes |
| Checkpoint (GCS) | Offsets, state and a log of finished batches | GCS, one path per query, never shared | If lost, the job cannot resume safely and must be rebuilt from Bronze | Bucket versioning and access alerts (TBD, Week 3) |

Failure-behaviour claims for Pub/Sub acknowledgement and retention depend on the connector chosen in the pending ADR. Verify against the official docs in Week 3.

## 5. Data sources and data design
## 6. Key design decisions (link ADRs)
## 7. Risks and mitigations
## 8. Open questions

Each question has an owner and a date to resolve it.

1. **How will BigQuery read the Iceberg Silver tables, and how much delay does that add?** This decides whether the dashboard is as fresh as G1. Owner: me. Resolve by: end of Week 3.
2. **Does the Datastream staleness setting for BigQuery allow G3 (2 minutes)?** I must check the docs before promising it. Owner: me. Resolve by: start of Week 4, before configuring CDC.
3. **How do we route events older than the watermark to a late-data table (G2)?** Spark discards them by default, so we need our own logic. Owner: me. Resolve by: end of Week 3.
4. **How do we handle 06:00 IST for G4 when Airflow defaults to UTC?** 06:00 IST is 00:30 UTC. Owner: me. Resolve by: end of Week 2, when the first DAG is written.
5. **Do the alert thresholds match G7?** The guide fires the stale-data alert after 10 minutes, but G7 promises 5. Either the rule or the goal must change. Owner: me. Resolve by: start of Week 7, when alerts are built.

