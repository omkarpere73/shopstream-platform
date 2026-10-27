.PHONY: lint format test teardown-dev
lint:
	ruff check .
	black --check .
format:
	ruff check --fix .
	black .
test:
	pytest -q
teardown-dev:
	bash scripts/teardown-dev.sh
