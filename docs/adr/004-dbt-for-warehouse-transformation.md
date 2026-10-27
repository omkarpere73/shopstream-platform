# ADR-004: dbt for warehouse transformation
- Status: accepted
- Date: 2026-10-27

## Context
Silver and Gold models in BigQuery are built over the Datastream tables and the Silver event tables. I need tests on every model, generated docs and lineage, an SCD Type 2 customer dimension, and incremental models for the hourly funnel. Heavy compute should stay inside BigQuery.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Plain SQL files run by Airflow (BigQuery jobs) | No new tool; full control | No built-in tests, docs or lineage; SCD2 and incremental logic written by hand |
| Dataform (Google-native SQL workflows) | Native to Google Cloud | Not checked against current docs for this ADR; guide asks for dbt, and dbt skills are more widely asked for |
| dbt Core with dbt-bigquery | SQL-first; tests, docs and lineage built in; snapshots for SCD2; incremental models including microbatch on BigQuery | New tool for me; each run costs BigQuery bytes scanned; I must pin versions |

## Decision
dbt Core with the dbt-bigquery adapter. The biggest reason: tests, docs, lineage and snapshots come with the tool, so quality and SCD2 are built in and not hand-made, and the compute stays in BigQuery.

## Consequences
- Easier: tests on every model, generated docs and lineage, dim_customer as a dbt snapshot, incremental models for fct_events_funnel_hourly; Airflow runs dbt in dbt_build_daily.
- Harder: I must pin dbt Core and dbt-bigquery versions in Week 5; every run costs BigQuery bytes scanned, so I use partitioning, clustering and incremental models and record bytes scanned.
- Not yet verified: current dbt Core and dbt-bigquery version numbers, the newer dbt Fusion engine (not evaluated), dbt Core licence terms, and a current Dataform comparison.
- Revisit: Week 5 after the first dbt run in dev; if cost or version problems appear, record a new ADR.
