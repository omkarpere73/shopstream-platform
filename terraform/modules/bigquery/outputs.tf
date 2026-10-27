output "dataset_ids" {
  description = "Created dataset ids."
  value       = sort([for d in google_bigquery_dataset.this : d.dataset_id])
}
