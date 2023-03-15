# Make sure you have nodemon installed

wtest: ## Start pytest in watch mode using nodemon
	nodemon -w "./**/*" -e ".py" --exec pytest $(path)

wmypy: # Start mypy in watch mode
	nodemon -w "./**/*" -e ".py" --exec mypy .
