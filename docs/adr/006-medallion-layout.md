# ADR-006: Medallion layout (Bronze, Silver, Gold)
- Status: accepted
- Date: 2026-10-27

## Context
Data arrives from three sources (clickstream, Postgres CDC, FX rates) with duplicates, late events and bad rows. I need clear layers so each job has one responsibility, PII can be controlled, and any layer can be rebuilt after a bug or a deleted partition.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| One layer: raw data straight into marts | Least storage and fewest jobs | Any bug or bad row reaches the marts; no clean copy to replay from; hard to test and to protect PII |
| Two layers: raw and marts | Simpler than three layers | Cleaning, deduplication and business logic mix in one step; harder to test and to find where a bug started |
| Three layers: Bronze, Silver, Gold (medallion) | One job per layer; Bronze can replay Silver and Gold; tests and contracts sit between layers | More tables, jobs and storage; more naming rules to follow |

## Decision
Three layers. Bronze is the raw record with ingestion metadata, Silver is cleaned, deduplicated and typed with bad rows quarantined, and Gold holds the business marts built by dbt. Datasets use the prefixes bronze_, silver_ and gold_; Gold tables use fct_ and dim_. The biggest reason: Bronze is the replay source, so a Silver or Gold bug is fixed by reprocessing and not by asking the source again.

## Consequences
- Easier: backfill and the 'delete a Silver partition' drill restore from Bronze; each layer has its own tests and contract; PII policy tags go on Silver and Gold columns.
- Harder: three copies cost more storage and need more jobs; each source needs a clear rule for what Bronze means for it.
- Caveat: Datastream in merge mode (ADR-003) keeps the current state, not history, so CDC Bronze is a replica and not append-only; event Bronze (Iceberg) is append-only. Whether CDC needs append-only mode for SCD2 and GDPR deletes is not decided. Revisit in Week 4 and Week 5.
- Risk: Bronze holds raw PII (email, phone) before masking, and the guide tags only Silver and Gold, so Bronze access must be limited to pipeline_sa; check in Week 6. Not yet verified: how BigQuery reads the Silver Iceberg tables (ADR-002).
