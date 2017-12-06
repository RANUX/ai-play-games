venv:
	rm -rf .venv
	python3 -m venv .venv
	( \
	source .venv/bin/activate; \
	python -m pip install --upgrade pip; \
	pip install -Ur requirements.txt; \
	)
