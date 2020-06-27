clean:
	@find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete
	@find . -type d -name "*pytest_cache*" -exec rm -rf {} +

run:
	@poetry run python server.py

test:
	@poetry run pytest