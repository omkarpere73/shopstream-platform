terraform {
  backend "gcs" {
    bucket = "shopstream-dev-tfstate-14a27a"
    prefix = "terraform/state"
  }
}
