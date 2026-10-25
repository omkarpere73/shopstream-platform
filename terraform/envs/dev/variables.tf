variable "project_id" {
  description = "GCP project that this environment deploys into."
  type        = string
  default     = "shopstream-dev"
}

variable "labels" {
  description = "Labels applied to every labelable resource (cost tracking)."
  type        = map(string)
  default = {
    env     = "dev"
    owner   = "omkar"
    project = "shopstream"
  }

  validation {
    condition     = alltrue([for k in ["env", "owner", "project"] : contains(keys(var.labels), k)])
    error_message = "labels must include the keys env, owner and project."
  }
}
