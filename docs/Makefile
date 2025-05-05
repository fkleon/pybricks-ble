export PATH := .venv/bin:$(PATH)

VERSION ?= $(shell git describe --always)
FOOTER := pb_ble v:$(VERSION)

.PHONY: help
help: ## Display this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.venv: ../pyproject.toml ## Create the python virtual environment.
	/usr/bin/python3 -m venv --clear --upgrade-deps .venv
	pip install --group '../pyproject.toml:docs' -e ..

.PHONY: dev
dev: .venv ## Start locally hosted version of the documentation.
	pdoc --footer-text "$(FOOTER)" --template-directory . pb_ble

.PHONY: html
html: .venv ## Generate the documentation.
	pdoc --footer-text "$(FOOTER)" --template-directory . -o build/ pb_ble