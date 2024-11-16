export PATH := .venv/bin:$(PATH)

.PHONY: help
help: ## Display this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.venv: pyproject.toml ## Create the python virtual environment.
	/usr/bin/python3 -m venv --clear --upgrade-deps --system-site-packages .venv
	pip install -e '.[dev]'

.PHONY: lint
lint: .venv ## Lint the code base.
	ruff check --diff
	ruff format --diff

.PHONY: format
format: .venv ## Format the code base.
	ruff check . --fix
	ruff format .

.PHONY: type
typecheck: .venv ## Type-check the code base.
	mypy \
		--disable-error-code=method-assign \
		--ignore-missing-imports \
		--check-untyped-defs \
		--exclude build/ \
		.

.PHONY: test
test: .venv ## Run the unit tests against a BlueZ mock service
	pytest

.PHONY: integration-test
integration-test: export DISABLE_BLUEZ_MOCK=1
integration-test: .venv ## Run the integration tests against the real BlueZ service
	pytest

