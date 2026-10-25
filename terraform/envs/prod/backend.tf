terraform {
  backend "gcs" {
    bucket = "shopstream-prod-tfstate-14a27a"
    prefix = "terraform/state"
  }
}
