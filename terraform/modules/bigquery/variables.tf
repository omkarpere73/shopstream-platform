variable "project_id" {
  description = "GCP project that owns the datasets."
  type        = string
}

variable "location" {
  description = "Dataset location, for example asia-south1. Cannot be changed later."
  type        = string
}

variable "dataset_ids" {
  description = "Dataset ids. Each must start with bronze_, silver_ or gold_ and use snake_case."
  type        = set(string)

  validation {
    condition     = alltrue([for d in var.dataset_ids : can(regex("^(bronze|silver|gold)_[a-z0-9_]+$", d))])
    error_message = "dataset_ids must start with bronze_, silver_ or gold_ and use lowercase snake_case."
  }
}

variable "delete_contents_on_destroy" {
  description = "Allow destroy to delete datasets that still hold tables. Dev only."
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels for cost tracking. Must include env, owner and project."
  type        = map(string)
}
