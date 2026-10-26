# ADR-001: Spark on Dataproc (Managed Service for Apache Spark) for streaming and batch
- Status: accepted
- Date: 2026-10-26

## Context
We need one compute engine for the streaming path (Pub/Sub to Iceberg) and the batch path (FX rates, compaction, skew lab). I already know Spark and want skills that transfer across clouds.

Naming note: Google renamed the product. "Managed Service for Apache Spark" is the new name for Dataproc on Compute Engine (clusters) and for Serverless for Apache Spark (formerly Dataproc Serverless). The API, gcloud commands and Terraform resources still say dataproc, so this project uses both names.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Spark on a Managed Spark (Dataproc) cluster for streaming, Serverless for Apache Spark for batch | One engine for both paths; I already know it; skills transfer to other clouds; mature Iceberg support | I own cluster sizing, upgrades and restarts; an always-on streaming cluster costs money |
| Dataflow (Apache Beam) | More managed; autoscaling and Pub/Sub integration are built in | New programming model; transfers less to my Spark experience; two engines if batch stays in Spark |
| BigQuery SQL (for example Pub/Sub into BigQuery, then SQL) | Least code and least operations | Does not exercise streaming mechanics (watermarks, checkpoints) or the Iceberg lake layer |

## Decision
Spark on Managed Service for Apache Spark. Streaming runs on a small autoscaling cluster that is deleted after each session. Batch runs on Serverless for Apache Spark. The biggest reason: one engine I already know covers both paths, so my learning time goes to streaming correctness, not a new framework.

## Consequences
- Harder: I own cluster sizing, restarts and the streaming watchdog. Cost control depends on the teardown script.
- Not yet verified: whether Serverless for Apache Spark can run Structured Streaming (the guide uses a standard cluster for streaming, so this ADR does not depend on it), and whether Serverless runs in asia-south1 (open question 7).
- Not yet verified: which connector reads from Pub/Sub (open question 8). The Pub/Sub Lite Spark connector is a different product and Pub/Sub Lite is closed to new customers, so it is not an option.
- Revisit: end of Week 3 after the connector time-box, and again if streaming cost is too high.
