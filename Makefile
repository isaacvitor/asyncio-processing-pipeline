
coverage: # Run pytest and coverage 
	pytest  --cov=src --cov-report term-missing $(path)

# Make sure you have nodemon installed
wtest: ## Start pytest in watch mode using nodemon
	nodemon -w "./**/*" -e ".py" --exec pytest --log-cli-level=20 $(path)

wtest-unit: ## Start pytest in watch to unit tests
	nodemon -w "./**/*" -e ".py" --exec pytest --log-cli-level=20 tests/unit

wmypy: # Start mypy in watch mode
	nodemon -w "./**/*" -e ".py" --exec mypy .
