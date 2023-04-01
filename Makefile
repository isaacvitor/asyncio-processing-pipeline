# Don't forget to add all non-producing file targets to the PHONY list
.PHONY: help dev-dependencies compose-up compose-down
.DEFAULT_GOAL := help

help: ## Prints this help message and exits.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

PROJECT_PATH=async_pipeline
TESTPATH=./tests
ifdef file
	 TESTPATH=./tests -k $(file)
endif

all: lint coverage ## Run all tests and checks

# Linters
mypy: # mypy linter
	mypy $(PROJECT_PATH)

pylint: # mypy linter
	pylint $(PROJECT_PATH)

lint: mypy pylint ## Run linters


# Formater
formatter: ## Run formatter
	black .

test: ## Execute pytest in a given file or all tests - Ex: make tests file=test_my_test.py or make tests to run all tests
	pytest -s -x $(TESTPATH)


coverage: TESTPATH=--cov=$(PROJECT_PATH) --cov-report term-missing --cov-report html ./tests
coverage:test ## Run pytest and coverage


## Run pytest
unit-test: TESTPATH=./tests/unit
unit-test: test ## Execute unit tests

integration-test: TESTPATH=./tests/integration
integration-test: test ## Execute integration tests

# Make sure you have nodemon installed
wtest: ## Start pytest in watch mode using nodemon
	nodemon -w "./**/*" -e ".py" --exec pytest --log-cli-level=20 $(path)

wtest-unit: ## Start pytest in watch to unit tests
	nodemon -w "./**/*" -e ".py" --exec pytest --log-cli-level=20 tests/unit

wmypy: # Start mypy in watch mode
	nodemon -w "./**/*" -e ".py" --exec mypy .
