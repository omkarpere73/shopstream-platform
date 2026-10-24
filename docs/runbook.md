# ShopStream runbook

Operational procedures for the platform. Every alert gets an entry here before its ticket closes (definition of done).

## Contents

- Bootstrap: Terraform state buckets

---

## Bootstrap: Terraform state buckets

**Status:** done on 2026-10-24. This is the one deliberate manual step in the project. Everything after it is Terraform and CI/CD.

### Why it is manual

Terraform stores its state in a GCS bucket, and that bucket must exist before Terraform can use it. So the two state buckets were created once with gcloud.

### What was created

| Environment | Project | Bucket | Region |
|---|---|---|---|
| dev | shopstream-dev | gs://shopstream-dev-tfstate-14a27a | asia-south1 |
| prod | shopstream-prod | gs://shopstream-prod-tfstate-14a27a | asia-south1 |

Settings on both: uniform bucket-level access on, public access prevention enforced, object versioning on. Labels: env, owner, project.

### Commands used

The create command in the installed gcloud version did not accept versioning or labels, so each bucket took two commands. Run once per environment (ENV is dev or prod):

```
gcloud storage buckets create gs://shopstream-${ENV}-tfstate-14a27a --project=shopstream-${ENV} --location=asia-south1 --uniform-bucket-level-access --public-access-prevention
gcloud storage buckets update gs://shopstream-${ENV}-tfstate-14a27a --project=shopstream-${ENV} --versioning --update-labels=env=${ENV},owner=omkar,project=shopstream
```

### How to verify

```
gcloud storage buckets describe gs://shopstream-dev-tfstate-14a27a --project=shopstream-dev --format="yaml(name,location,labels,uniform_bucket_level_access,public_access_prevention,versioning_enabled)"
gcloud storage buckets describe gs://shopstream-prod-tfstate-14a27a --project=shopstream-prod --format="yaml(name,location,labels,uniform_bucket_level_access,public_access_prevention,versioning_enabled)"
```

Expected on both: public_access_prevention enforced, uniform_bucket_level_access true, versioning_enabled true, location ASIA-SOUTH1.

### Rules

- **Never include these buckets in teardown.** Deleting them makes Terraform lose track of what it manages.
- Cost is effectively zero (a few KB of state).
- Each environment has its own state bucket, so a dev mistake cannot touch prod state.
- If a state file is overwritten or deleted by mistake, restore a previous object version from the bucket.

### If you need to recreate them

Bucket names are global. If a name is ever lost, pick a new suffix, update the Terraform backend config in the same pull request, and record the change here.
