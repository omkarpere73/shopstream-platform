output "service_account_emails" {
  description = "Map of account_id to service account email."
  value       = { for id, sa in google_service_account.this : id => sa.email }
}
