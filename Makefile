PYTHON_VERSION=$(shell python3 -V | grep  -o -e "3\.\d*")

venv/lib/python$(PYTHON_VERSION)/site-packages/aiohttp: venv/bin/python
	./venv/bin/pip install .

venv/bin/python:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip wheel

venv/bin/pytest: venv/lib/python$(PYTHON_VERSION)/site-packages/aiohttp
	./venv/bin/pip install .[test]

dev: venv/bin/python
	./venv/bin/pip install -e .[test]

test: venv/bin/pytest
	./venv/bin/pytest tests -v -s

clean:
	rm -rf venv pip-selfcheck.json pyvenv.cfg

docker-test:
	docker run --rm \
		-u `id -u` \
		-v ~/.cache:/.cache \
		-e XDG_CACHE_HOME=/.cache \
		-v `pwd`:/z \
		-w /z \
		-t \
		python:3.5 make test
