init:
	pip install -r requirements.txt

test:
	py.test tests --cov --cov-report=html:cov-report

ruff:
	ruff --format=github --select=E9,F63,F7,F82 --target-version=py37 .
	ruff --format=github --target-version=py37 .

.PHONY: init test