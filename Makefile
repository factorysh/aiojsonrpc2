PYTHON_VERSION=$(shell python3 -V | grep  -o -e "3\.\d*")

lib/python$(PYTHON_VERSION)/site-packages/aiohttp: bin/python
	./bin/pip install .

bin/python:
	python3 -m venv .
	./bin/pip install --upgrade pip
	./bin/pip install wheel

bin/pytest: lib/python$(PYTHON_VERSION)/site-packages/aiohttp
	./bin/pip install .[test]

dev: bin/python
	./bin/pip install -e .

test: bin/pytest
	./bin/pytest tests -v -s

clean:
	rm -rf bin include lib pip-selfcheck.json pyvenv.cfg
