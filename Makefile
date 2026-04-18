test:
	poetry run pytest -v

fmt:
	poetry run black .

lint:
	poetry run black --check .

typecheck:
	poetry run mypy batalha_naval

setup-web:
	ln -sf ../batalha_naval web/batalha_naval

build-web:
	rm -rf web/batalha_naval
	mkdir -p web/batalha_naval
	cp batalha_naval/*.py web/batalha_naval/

serve:
	cd web && python3 -m http.server 8000
