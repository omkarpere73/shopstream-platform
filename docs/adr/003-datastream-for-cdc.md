# ADR-003: Datastream for CDC from Postgres to BigQuery
- Status: accepted
- Date: 2026-10-27

## Context
Orders and customers live in Cloud SQL Postgres. Inserts, updates and deletes (including GDPR-style customer deletion) must be visible in BigQuery within 2 minutes (goal F3). I want a managed tool so my time goes to modeling, not to running connectors.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Scheduled batch pulls (query tables using updated_at) | Simplest; no replication setup | Misses hard deletes and changes between pulls; extra load on the database; hard to reach 2 minutes |
| Debezium (self-managed connector) | More control over format, filtering and routing; widely used | I run and monitor the connector and its servers myself; more setup and cost; not checked against current docs for this ADR |
| Datastream to BigQuery | Managed; Postgres source and BigQuery destination are GA; merge mode applies updates and deletes; priced per GiB processed | Less control than Debezium; BigQuery processing to apply changes is billed separately |

## Decision
Datastream with merge write mode. The biggest reason: it is managed, so I spend Week 4 on correctness (deletes, out-of-order changes, SCD2) and not on operating a connector.

## Consequences
- Easier: no servers to run; updates and deletes are applied in BigQuery; dbt Silver models sit on top of the Datastream tables.
- Harder: less control over table layout; I must handle out-of-order changes and soft deletes in dbt; Postgres needs logical replication, a replication user and a publication.
- Not yet verified: Datastream in asia-south1 (Mumbai), the Mumbai price in INR (open question 9), Cloud SQL cost, and the real lag against the 2-minute goal (open question 2).
- Revisit: Week 4 after the insert, update, delete test. If region or cost blocks it, fall back to scheduled batch pulls and record that in a new ADR. Teardown when idle: pause or delete the stream, then stop the Cloud SQL instance.
