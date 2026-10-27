locals {
  # Makes bucket names globally unique. Same suffix as the state bucket. Not a secret.
  name_suffix = "14a27a"
}

resource "google_project_service" "apis" {
  for_each = toset(["bigquery.googleapis.com", "iam.googleapis.com", "storage.googleapis.com"])

  project = var.project_id
  service = each.key

  # Never disable an API on destroy: storage.googleapis.com is also used by the state bucket.
  disable_on_destroy = false
}

module "storage" {
  source = "../../modules/storage"

  project_id    = var.project_id
  location      = var.region
  name_suffix   = local.name_suffix
  purposes      = toset(["bronze", "silver"])
  force_destroy = true
  labels        = var.labels

  depends_on = [google_project_service.apis]
}

module "bigquery" {
  source = "../../modules/bigquery"

  project_id                 = var.project_id
  location                   = var.region
  dataset_ids                = toset(["bronze_cdc", "silver_core", "gold_marts"])
  delete_contents_on_destroy = true
  labels                     = var.labels

  depends_on = [google_project_service.apis]
}

module "iam" {
  source = "../../modules/iam"

  project_id = var.project_id
  service_accounts = {
    "pipeline-sa" = "Runs the streaming and batch jobs. No roles yet; roles are added on the resource that needs them."
  }

  depends_on = [google_project_service.apis]
}
