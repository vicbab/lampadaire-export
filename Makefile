.DEFAULT_GOAL := help
RED=\033[0;31m
GREEN=\033[0;32m
ORANGE=\033[0;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

.PHONY: deps
deps: ## Generate dependencies from pyproject.toml
	@echo "${GREEN}🤖 Updating requirements${NC}"
	pip-compile --quiet --resolver=backtracking --output-file=requirements.txt pyproject.toml
	pip-compile --quiet --resolver=backtracking --extra=dev --output-file=requirements-dev.txt pyproject.toml

.PHONY: install
install: ## Install the dependencies
	@echo "${GREEN}🤖 Installing dependencies${NC}"
	python3 -m pip install --upgrade pip
	python3 -m pip install --editable .

.PHONY: dev
dev: install ## Install the development dependencies
	python -m pip install --editable ".[dev]"

PRETTIER := $(shell command -v prettier 2> /dev/null)
.PHONY: lint
lint: ## Ensure code consistency
	@echo "${GREEN}🤖 Linting code${NC}"
	@ruff . --fix
	@black . --quiet
	@mypy styloexport --no-error-summary
ifdef PRETTIER
	@prettier styloexport/static/css/*.css --write --loglevel warn
else
	@echo "${ORANGE}✋ Prettier executable is not available${NC}"
endif

.PHONY: bump
bump: ## Bump the current version to a new minor one
	@echo "${GREEN}🤖 Bump the current version${NC}"
	@hatch version fix

.PHONY: release
release: ## Create a new Docker image and publish it
	@echo "${GREEN}🤖 Building a new docker image${NC}"
	$(eval VERSION=$(shell hatch version))
	@echo "Version to build: ${VERSION}"
	docker build -t davidbgk/stylo-export:${VERSION} .
	docker push davidbgk/stylo-export:${VERSION}

.PHONY: run
run: ## Run the development server
	FLASK_APP=styloexport FLASK_DEBUG=1 flask run --exclude-patterns *0.zip:*1.zip:images.zip

.PHONY: styles
styles: ## Download and prepare bibliographic styles
	FLASK_APP=styloexport flask styles download
	FLASK_APP=styloexport flask styles reduce
	FLASK_APP=styloexport flask styles retrieve
	FLASK_APP=styloexport flask styles custom

.PHONY: production
production: ## Run the production server
	gunicorn styloexport.wsgi:app \
		--bind 0.0.0.0:8001 \
		--error-logfile gunicorn.error.log \
		--access-logfile gunicorn.access.log \
		--capture-output \
		--timeout 300 \
		--log-level debug

.PHONY: test
test: ## Run the test suite
	@echo "${GREEN}🤖 Testing code${NC}"
	@pytest --cov=styloexport tests/

.PHONY: docs
docs: ## Generate documentation for the API
	pdoc --force --output-dir public --html styloexport

.PHONY: docslive
docslive: ## Run the autoreload docs server
	pdoc --http localhost:8003 styloexport

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# See https://daniel.feldroy.com/posts/autodocumenting-makefiles
define PRINT_HELP_PYSCRIPT # start of Python section
import re, sys

output = []
# Loop through the lines in this file
for line in sys.stdin:
    # if the line has a command and a comment start with
    #   two pound signs, add it to the output
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        output.append("\033[36m%-10s\033[0m %s" % (target, help))
# Sort the output in alphanumeric order
output.sort()
# Print the help result
print('\n'.join(output))
endef
export PRINT_HELP_PYSCRIPT # End of python section
