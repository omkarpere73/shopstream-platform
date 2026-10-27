# ADR-008: Dead-letter handling: quarantine bad rows in a GCS path
- Status: accepted
- Date: 2026-10-27

## Context
About 0.5 percent of simulated events are malformed (missing fields, wrong types). Spark finds this when it parses each row, so the job itself must quarantine the row. Bad data must never be dropped silently, the accounting rule (Bronze rows plus dead-letter rows equal the ground-truth log) must hold, and a quarantined row must be inspectable, countable and replayable.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Log the error and drop the row | Simplest | Loses data silently; breaks the accounting rule; nothing to replay |
| Pub/Sub topic as the sink | Backlog metrics and alerts already exist for topics; easy fan-out | Needs a subscriber to inspect or count rows; retention limit not verified; one more thing to run |
| GCS path (files, partitioned by ingestion date) | Same storage and durability class as Bronze; queryable with Spark or BigQuery; easy to count and replay; cheap | I must build the rate metric and alert myself |

## Decision
A dedicated GCS path, partitioned by ingestion date, holding raw_payload, error_reason and ingestion_time for every row that fails parse or validation. The biggest reason: I can query, count and replay the files with tools I already use, and the sink is as durable as Bronze, so the accounting rule is one count query.

## Consequences
- Easier: the accounting check is a count query; replay is re-reading the files after the fix and sending the rows through the same dedupe on event_id; the pipeline keeps running while bad rows pile up safely.
- Harder: I build the rate check myself (planned in dq_checks_hourly); the alert threshold is TBD until I measure the simulator baseline of about 0.5 percent; raw payloads may hold PII, so access is limited like Bronze (see ADR-006); retention is TBD.
- Not yet verified: how Pub/Sub's own dead-letter feature for subscriptions relates to parse failures (the guide lists a dead-letter topic in Week 3), the file format for the sink (Parquet planned), and Pub/Sub retention limits.
- Revisit: end of Week 3 after the 1,000 malformed events drill; switch to a Pub/Sub sink only if the rate alert is hard to build.
