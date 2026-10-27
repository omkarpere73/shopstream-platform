variable "project_id" {
  description = "GCP project that owns the service accounts."
  type        = string
}

variable "service_accounts" {
  description = "Map of account_id to description. No roles are granted here; grant roles on the resource that needs them."
  type        = map(string)
}
