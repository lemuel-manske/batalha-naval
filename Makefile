test:
	poetry run pytest -v

fmt:
	poetry run black .

lint:
	poetry run black --check .

typecheck:
	poetry run mypy batalha_naval
