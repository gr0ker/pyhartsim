init:
	pip install -r requirements.txt

test:
	py.test tests --cov --cov-report=html:cov-report

ruff:
	ruff check . --output-format=github --select=E9,F63,F7,F82 --target-version=py313
	ruff check . --output-format=github --target-version=py313

.PHONY: init test