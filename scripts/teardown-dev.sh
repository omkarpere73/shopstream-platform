#!/usr/bin/env bash
# scripts/teardown-dev.sh (run via: make teardown-dev)
# Destroys DEV resources only. The tfstate buckets are not in this state, so they are never touched.
set -euo pipefail

expected_project="shopstream-dev"
env_dir="terraform/envs/dev"

cd "$(dirname "$0")/.."

if [[ -n "$(compgen -v TF_VAR_)" ]]; then
  echo "REFUSING: a TF_VAR_ variable is set in your shell. Unset it first." >&2
  exit 1
fi

if compgen -G "$env_dir/*tfvars*" > /dev/null; then
  echo "REFUSING: a tfvars file exists in $env_dir. Remove it first." >&2
  exit 1
fi

if ! grep -q 'shopstream-dev-tfstate' "$env_dir/backend.tf"; then
  echo "REFUSING: $env_dir/backend.tf does not point at the dev state bucket." >&2
  exit 1
fi

echo "About to destroy ALL Terraform-managed resources in project: $expected_project"
echo "Buckets and datasets are deleted even if they contain data."
terraform -chdir="$env_dir" destroy -var="project_id=$expected_project"
