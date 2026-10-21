.PHONY: lint format test
lint:
	ruff check .
	black --check .
format:
	ruff check --fix .
	black .
test:
	pytest -q
