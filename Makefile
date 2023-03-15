
coverage: # Run pytest and coverage 
	pytest  --cov=src --cov-report term-missing $(path)

# Make sure you have nodemon installed
wtest: ## Start pytest in watch mode using nodemon
	nodemon -w "./**/*" -e ".py" --exec pytest --log-cli-level=20 $(path)

wmypy: # Start mypy in watch mode
	nodemon -w "./**/*" -e ".py" --exec mypy .
