.PHONY: all run clean

# Simple makefile to help me remember uv tasks
# Targets are:
# - ruff     : run ruff linter
# - fix      : ... with fixes
# - build    : build
# - publish  : publish
# - dist     : clean, build, publish
# - clean    : remove anything built


ruff:
	uvx ruff check

fix:
	uvx ruff check --fix

lint: ruff

build:
	uv build

publish: build
	uv publish

dist: clean publish

clean:
	rm -rf __pycache__
	rm -fr dist/
	rm -f dpytest_*.dat
	find . -type f -name ‘*.pyc’ -delete