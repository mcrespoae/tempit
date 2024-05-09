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

.PHONY: test
run:
	$(PYTHON) examples/main.py
test:
	$(PYTHON) -m unittest discover -v -s ./tests -p "*test*.py"
