variable "project_id" {
  description = "GCP project that owns the buckets."
  type        = string
}

variable "location" {
  description = "Bucket location, for example asia-south1. Cannot be changed later."
  type        = string
}

variable "name_suffix" {
  description = "Short suffix that makes bucket names globally unique."
  type        = string
}

variable "purposes" {
  description = "One bucket per purpose, for example bronze and silver. Names are project_id-purpose-suffix."
  type        = set(string)
}

variable "force_destroy" {
  description = "Allow destroy to delete a bucket that still holds objects. Dev only."
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels for cost tracking. Must include env, owner and project."
  type        = map(string)
}
