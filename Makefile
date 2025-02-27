.PHONY: all run clean

# Simple makefile to help with repetitive Python tasks
# Targets are:
# - venv     : build a venv in ./.venv
# - test     : run the unit test suite
# - coverage : run the unit tests and generate a minimal coverage report
# - htmlcov  : run the unit tests and generate a full report in htmlcov/


# test: $(VENV)/bin/activate
# 	$(PYTHON) -m tests

# coverage: $(VENV)/bin/activate
# 	$(PYTHON) -m coverage run -m tests
# 	$(PYTHON) -m coverage report

# htmlcov: $(VENV)/bin/activate
# 	$(PYTHON) -m coverage run -m tests
# 	$(PYTHON) -m coverage html

ruff:
	uvx ruff check

lint: ruff

build:
	uv build

deploy: build
	uv deploy

dist: clean deploy

clean:
	rm -rf __pycache__
	rm -fr dist/
	rm -rf $(VENV)
	rm -rf htmlcov
	rm -f discord.log
	rm -f dpytest_*.dat
	find . -type f -name ‘*.pyc’ -delete