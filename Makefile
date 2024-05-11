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

.PHONY: build example test

build:
	$(PYTHON) setup.py sdist bdist_wheel
example:
	cd examples & $(PYTHON) examples.py
test:
	$(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"
test-pkg:
	$(PYTHON) setup.py test
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


