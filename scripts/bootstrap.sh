# scripts/bootstrap.sh  (run once from repo root: bash scripts/bootstrap.sh)
set -euo pipefail

dirs=(
  docs/adr docs/diagrams
  terraform/modules/pubsub terraform/modules/dataproc terraform/modules/bigquery
  terraform/modules/composer terraform/modules/iam terraform/envs/dev terraform/envs/prod
  simulator streaming batch airflow/dags airflow/plugins airflow/tests
  dbt/models/silver dbt/models/gold dbt/snapshots dbt/tests dbt/macros
  contracts .github/workflows scripts
)
for d in "${dirs[@]}"; do mkdir -p "$d" && touch "$d/.gitkeep"; done

cat > .gitignore <<'EOF'
__pycache__/
.venv/
.pytest_cache/
.ruff_cache/
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
!*.tfvars.example
.env
*.json.key
target/
logs/
.DS_Store
EOF

cat > pyproject.toml <<'EOF'
[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ANN"]

[tool.pytest.ini_options]
testpaths = ["streaming", "batch", "airflow/tests", "simulator"]
EOF

cat > Makefile <<'EOF'
.PHONY: lint format test
lint:
	ruff check .
	black --check .
format:
	ruff check --fix .
	black .
test:
	pytest -q
EOF

cat > docs/adr/000-template.md <<'EOF'
# ADR-000: <title>
- Status: proposed | accepted | superseded
- Date: YYYY-MM-DD

## Context
What problem are we solving? What constraints exist?

## Options considered
| Option | Pros | Cons |
|---|---|---|

## Decision
What we chose and the single biggest reason.

## Consequences
What gets easier, what gets harder, what we will revisit and when.
EOF

mkdir -p .github
cat > .github/pull_request_template.md <<'EOF'
## What changed and why

## How I tested it

## Risks and rollback plan

## Docs, runbook, and contract updates
yes / not needed
EOF

cat > docs/weekly-log.md <<'EOF'
# Weekly log
## Week 1
Goal:
Done:
Broke and how I fixed it:
Decisions made (link ADR):
Metrics captured:
Next week:
EOF

cat > README.md <<'EOF'
# ShopStream Data Platform
Portfolio project: a real-time e-commerce data platform on GCP, built to practice
production data engineering patterns with simulated data. Work in progress.
EOF