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

build:
	uv build

dist:
	rm -fr dist/
	uv build
	uv publish

clean:
	rm -rf __pycache__
	rm -fr dist/
	rm -f dpytest_*.dat
	find . -type f -name ‘*.pyc’ -delete