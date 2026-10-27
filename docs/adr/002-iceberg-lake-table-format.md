# ADR-002: Apache Iceberg as the lake table format
- Status: accepted
- Date: 2026-10-27

## Context
Bronze and Silver event tables live on Cloud Storage and are written by Spark Structured Streaming every 30 seconds, while other jobs read them and compaction rewrites them. I need safe concurrent writes, MERGE for idempotent upserts, replay and backfill, schema evolution (coupon_code in schema_version 3) and a fix for small files.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Plain Parquet in folders | Simplest; every engine reads it | No table-level commit, so readers can see half-written data; no MERGE; schema changes and small-file fixes are manual |
| Delta Lake | ACID, MERGE, time travel; mature Spark support | Not checked for BigQuery integration in this project; I did not verify the Google docs for it |
| Apache Iceberg | ACID commits, MERGE, time travel, schema evolution, compaction procedures (rewrite_data_files, expire_snapshots); open format read by Spark and BigQuery | Needs a catalog and the right Iceberg runtime version; Google docs mark parts of the BigQuery integration as preview |

## Decision
Iceberg for Bronze and Silver event tables on Cloud Storage. The biggest reason: Spark writes the tables and BigQuery can read Iceberg tables that open source engines create, so one table serves both the streaming path and the warehouse.

## Consequences
- Easier: replay and backfill with MERGE on event_id; time travel for debugging; schema evolution without rewriting data; compaction fixes small files.
- Harder: I must pick and pin the Iceberg runtime version and the catalog type, and run compaction and snapshot expiry as a daily job (Week 4).
- Not yet verified: the exact Spark catalog config, BigQuery reading these tables, preview status, and asia-south1 support (Week 3). Fallback from the guide: export Silver to native BigQuery tables and record it in an ADR.
- Revisit: end of Week 3 after the first Bronze write and BigQuery read.
