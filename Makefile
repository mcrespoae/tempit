# Makefile
# Check if the OS is Windows
ifeq ($(OS),Windows_NT)
	VENV_ACTIVATE = .venv\Scripts\activate
	PYTHON = python
	RM = del /Q
	RMDIR = rmdir /S /Q

else
	VENV_ACTIVATE = . .venv/bin/activate
	PYTHON = python3
	RM = rm -f
	RMDIR = rm -rf

endif

.PHONY: install build example test check clean upload_pypi


install: clean
	$(PYTHON) -m venv .venv
	$(VENV_ACTIVATE)
	pipenv install -e .

build:
	$(PYTHON) setup.py sdist bdist_wheel

example:
	$(VENV_ACTIVATE)
	$(PYTHON) examples/examples.py

test:
	$(VENV_ACTIVATE)
	$(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"

check:
	$(PYTHON) setup.py check

clean:
ifeq ($(OS),Windows_NT)
	if exist build $(RMDIR) build
	if exist dist $(RMDIR) dist
	if exist tempit.egg-info $(RMDIR) tempit.egg-info
	if exist .venv $(RMDIR) .venv

else
	$(RMDIR) build
	$(RMDIR) dist
	$(RMDIR) tempit.egg-info
	$(RMDIR) .venv
endif

upload_pypi: clean install test build check
	$(PYTHON) -m twine upload dist/*


