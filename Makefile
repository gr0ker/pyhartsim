init:
	pip install -r requirements.txt

test:
	py.test tests

ruff:
	ruff --format=github --select=E9,F63,F7,F82 --target-version=py37 .
	ruff --format=github --target-version=py37 .

.PHONY: init test