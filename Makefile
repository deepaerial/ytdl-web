clean:
	@find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete
	@find . -type d -name "*pytest_cache*" -exec rm -rf {} +

run_server:
	@poetry run python server.py

test:
	@poetry run pytest

run_frontend:
	npm run --prefix ./ytdl_web/ dev

make_dev_certs:
	mkdir certs && mkcert localhost 127.0.0.1