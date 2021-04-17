clean:
	@find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete
	@find . -type d -name "*pytest_cache*" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} + -or -name ".coverage" -delete

run_server:
	cd api && poetry run uvicorn ytdl_api.asgi:app \
		--host 127.0.0.1 \
		--port 8000 \
		--log-level debug \
		--reload \
		--ssl-keyfile ./certs/localhost+1-key.pem \
		--ssl-certfile ./certs/localhost+1.pem

test:
	@poetry run pytest

run_frontend:
	npm run --prefix ./web/ devserver

make_dev_certs:
	mkdir api/certs && mkcert localhost 127.0.0.1