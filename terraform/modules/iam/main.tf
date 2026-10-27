resource "google_service_account" "this" {
  for_each = var.service_accounts

  project      = var.project_id
  account_id   = each.key
  display_name = each.key
  description  = each.value
}
