venv:
	pip install --upgrade virtualenv
	rm -rf .venv
	virtualenv -p python3 .venv
	( \
	source .venv/bin/activate; \
	python -m pip install --upgrade pip; \
	pip install -Ur requirements.txt; \
	)
