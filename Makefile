# Makefile
# Check if the OS is Windows
ifeq ($(OS),Windows_NT)
	PYTHON = python
	RM = del /Q
	RMDIR = rmdir /S /Q

else
	PYTHON = python3
	RM = rm -f
	RMDIR = rm -rf

endif

.PHONY: build install example test check clean upload_pypi

build:
	$(PYTHON) setup.py sdist bdist_wheel

install:
	$(PYTHON) setup.py install

example:
ifeq ($(OS),Windows_NT)
	$(PYTHON) examples/examples.py
else
	$(PYTHON) "examples/examples.py"
endif
test:
	$(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"
check:
	$(PYTHON) setup.py check

clean:
ifeq ($(OS),Windows_NT)
	if exist build $(RMDIR) build
	if exist dist $(RMDIR) dist
	if exist tempit.egg-info $(RMDIR) tempit.egg-info
else
	$(RMDIR) build
	$(RMDIR) dist
	$(RMDIR) tempit.egg-info
endif

upload_pypi: clean check build
	$(PYTHON) -m twine upload dist/*


