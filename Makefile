test-py:
	poetry run pytest -v

test-js:
	npm test --prefix web

test-e2e: build-web
	npm run test:e2e --prefix web

test: test-py test-js test-e2e

fmt:
	poetry run black .

build-web:
	rm -rf web/batalha_naval
	cp -r batalha_naval web/batalha_naval

serve:
	cd web && python3 -m http.server 8000
