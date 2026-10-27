resource "google_bigquery_dataset" "this" {
  for_each = var.dataset_ids

  project                    = var.project_id
  dataset_id                 = each.key
  location                   = var.location
  delete_contents_on_destroy = var.delete_contents_on_destroy
  labels                     = var.labels
}
