output "bucket_names" {
  description = "Buckets created in this environment."
  value       = module.storage.bucket_names
}

output "dataset_ids" {
  description = "BigQuery datasets created in this environment."
  value       = module.bigquery.dataset_ids
}

output "service_account_emails" {
  description = "Service accounts created in this environment."
  value       = module.iam.service_account_emails
}
