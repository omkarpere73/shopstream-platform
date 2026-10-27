resource "google_storage_bucket" "this" {
  for_each = var.purposes

  name                        = "${var.project_id}-${each.key}-${var.name_suffix}"
  project                     = var.project_id
  location                    = var.location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = var.force_destroy
  labels                      = var.labels
}
