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

.PHONY: install build example test check clean upload_pypi


install:
	$(PYTHON) -m venv .venv
	pipenv install -e . --dev

build:
	$(VENV_ACTIVATE) $(PYTHON) -m build

example:
	$(VENV_ACTIVATE) $(PYTHON) examples/examples.py

test:
	$(VENV_ACTIVATE) $(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"

check:
	$(VENV_ACTIVATE) $(PYTHON) setup.py check

clean:
ifeq ($(OS),Windows_NT)
	if exist build $(RMDIR) build
	if exist dist $(RMDIR) dist
	if exist .eggs $(RMDIR) .eggs
	if exist tempit.egg-info $(RMDIR) tempit.egg-info
#	-@$(VENV_ACTIVATE) pipenv --rm
#	-@del /F /Q .venv\\Scripts\\python.exe
#	-@$(shell if exist .venv $(RMDIR) .venv)

else
	$(RMDIR) build
	$(RMDIR) dist
	$(RMDIR) .eggs
	$(RMDIR) tempit.egg-info
	-@$(VENV_ACTIVATE) pipenv --rm
#	-@$(RMDIR) .venv
endif

upload-pypi: clean install test build check
# Upload to PyPI. Make sure you have in your ~/.pypirc file in home directory
	$(VENV_ACTIVATE) $(PYTHON) -m twine upload dist/*


