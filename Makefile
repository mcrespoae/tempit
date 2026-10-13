# Makefile
# Check if the OS is Windows
ifeq ($(OS),Windows_NT)
	RM = del /Q
	RMDIR = rmdir /S /Q

else
	RM = rm -f
	RMDIR = rm -rf

endif

.PHONY: install build example test test-all clean upload-pypi upload-testpypi


install:
	$(info Installing the repo)
	uv sync --group dev

build:
	uv build

example:
	uv run python examples/examples.py

test:
	uv run python -m unittest discover -v -s ./tests -p "*test*.py"

# Run the test suite across all supported Python versions (uv provisions any
# missing interpreters). Each version runs in an isolated environment so the
# main .venv is left untouched.
# TODO: add Python 3.15 as soon as uv can provision the 3.15 GA interpreter
# (as of 2026-10-13 uv only ships 3.15.0b3, a beta). Then enable:
#	uv run --isolated --python 3.15 python -m unittest discover -s ./tests -p "*test*.py"
test-all:
	uv run --isolated --python 3.11 python -m unittest discover -s ./tests -p "*test*.py"
	uv run --isolated --python 3.12 python -m unittest discover -s ./tests -p "*test*.py"
	uv run --isolated --python 3.13 python -m unittest discover -s ./tests -p "*test*.py"
	uv run --isolated --python 3.14 python -m unittest discover -s ./tests -p "*test*.py"


clean:
ifeq ($(OS),Windows_NT)
	@if exist build $(RMDIR) build
	@if exist dist $(RMDIR) dist
	@if exist .eggs $(RMDIR) .eggs
	@if exist tempit.egg-info $(RMDIR) tempit.egg-info

else
	$(RMDIR) build
	$(RMDIR) dist
	$(RMDIR) .eggs
	$(RMDIR) tempit.egg-info

endif

upload-pypi: clean install test build
# DEPRECATED
# Instead use tags and the pypi_release.yml will upload the Github release and pypi
# Push your changes to main
# git tag 0.0.1 # or whatever version needed
# git push origin --tags

# Upload to PyPI. Make sure you have in your ~/.pypirc file in home directory
	uv run twine upload dist/*

upload-testpypi: clean install test build
# DEPRECATED

# Upload to TestPyPI. Make sure you have in your ~/.pypirc file in home directory
# Use uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tempit
# for installing the testpypi version
	uv run twine upload --repository testpypi dist/*
