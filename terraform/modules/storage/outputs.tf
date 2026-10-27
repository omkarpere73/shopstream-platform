output "bucket_names" {
  description = "Map of purpose to bucket name."
  value       = { for purpose, b in google_storage_bucket.this : purpose => b.name }
}
