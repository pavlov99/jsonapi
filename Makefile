ENV=$(CURDIR)/.env
BIN=$(ENV)/bin
PYTHON=$(BIN)/python
PYVERSION=$(shell pyversions --default)
SITE_PACKAGES=numpy scipy
MANAGER=$(PYTHON) $(CURDIR)/jsonapi/tests/django/manage.py

RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m

all: $(ENV)
	@echo "Virtualenv is installed"

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	@rm -rf build dist docs/_build
	@rm -f *.py[co]
	@rm -f *.orig
	@rm -f *.prof
	@rm -f *.lprof
	@rm -f *.so
	@rm -f */*.py[co]
	@rm -f */*.orig
	@rm -f */*/*.py[co]

.PHONY: register
# target: register - Register module on PyPi
register:
	@python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload:
	@python setup.py sdist upload || echo 'Upload already'

.PHONY: test
# target: test - Runs tests
test: clean
	#NOSE_REDNOSE=1 $(BIN)/nosetests
	$(MANAGER) test myapp.tests --settings=myapp.settings.dev

$(ENV):
	virtualenv --no-site-packages .env
	$(ENV)/bin/pip install -r requirements.txt

.PHONY: run
# target: run - run test server
run: $(ENV)
	$(MANAGER) syncdb --noinput --settings=myapp.settings.dev
	$(MANAGER) runserver 0.0.0.0:8000 --settings=myapp.settings.dev

.PHONY: shell
# target: shell - run shell console
shell:
	$(MANAGER) shell_plus --settings=myapp.settings.dev

.PHONY: install
# target: install - install package to current environment
install:
	$(PYTHON) setup.py install
