# Makefile
# Check if the OS is Windows
ifeq ($(OS),Windows_NT)
	VENV_ACTIVATE = .venv\Scripts\activate &&
	PYTHON = python
	RM = del /Q
	RMDIR = rmdir /S /Q

else
	VENV_ACTIVATE = . .venv/bin/activate &
	PYTHON = python3
	RM = rm -f
	RMDIR = rm -rf

endif

.PHONY: install build example test clean upload_pypi upload-testpypi


install:
	$(info Installing the repo)
ifeq ($(OS),Windows_NT)
	@if not exist .venv mkdir .venv
else
	@mkdir -p .venv
endif
	pipenv install -e . --dev

build:
	$(VENV_ACTIVATE) $(PYTHON) -m build

example:
	$(VENV_ACTIVATE) $(PYTHON) examples/examples.py

test:
	$(VENV_ACTIVATE) $(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"


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

upload-pypi: clean install test build check
# DEPRECATED
# Instead use tags and the pypi_release.yml will upload the Github release and pypi
# git tag 0.0.1 # or whatever version needed
# git push origin --tags

# Upload to PyPI. Make sure you have in your ~/.pypirc file in home directory
	$(VENV_ACTIVATE) $(PYTHON) -m twine upload dist/*

upload-testpypi: clean install test build check
# DEPRECATED

# Upload to TestPyPI. Make sure you have in your ~/.pypirc file in home directory
# Use $(PYTHON) -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tempit
# for installing the testpypi version
# or use pipenv install tempit -i https://test.pypi.org/simple
	$(VENV_ACTIVATE) $(PYTHON) -m twine upload --repository testpypi dist/*

