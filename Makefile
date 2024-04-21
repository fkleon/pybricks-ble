export PATH := .venv/bin:$(PATH)

.PHONY: help
help: ## Display this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.venv: pyproject.toml  ## Create the python virtual environment.
	python3 -m venv --clear .venv
	pip install -e '.[dev]'
	pip install pybricksdev==1.0.0a46 --no-deps

.PHONY: lint
lint: .venv  ## Lint the code base.
	ruff check --diff
	ruff format --diff

.PHONY: format
format: .venv  ## Format the code base.
	ruff check . --fix
	ruff format .

.PHONY: test
test: .venv
	pytest