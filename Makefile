ENV=$(CURDIR)/.env
BIN=$(ENV)/bin
PYTHON=$(BIN)/python
DJANGO_ADMIN=$(shell which django-admin.py)
SETTINGS_TEST=tests.testapp.settings.test
SETTINGS_DEV=tests.testapp.settings.dev
PARAMS_DEV=--settings=$(SETTINGS_DEV) --pythonpath=$(CURDIR)
SPHINXBUILD=sphinx-build

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
	@find . -name jsonapi\__pycache__ -delete
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
	$(DJANGO_ADMIN) test --settings=$(SETTINGS_TEST) --pythonpath=$(CURDIR) tests

$(ENV):
	virtualenv --no-site-packages .env
	$(BIN)/pip install -r requirements.txt

.PHONY: run
# target: run - run test server
run: $(ENV)
	$(DJANGO_ADMIN) syncdb --noinput $(PARAMS_DEV)
	$(DJANGO_ADMIN) runserver $(PARAMS_DEV) 0.0.0.0:8000

.PHONY: shell
# target: shell - run shell console
shell:
	$(DJANGO_ADMIN) shell_plus $(PARAMS_DEV)

.PHONY: install
# target: install - install package to current environment
install:
	$(PYTHON) setup.py install

.PHONY: graph_models
# target: graph_models - graph models
graph_models: $(ENV)
	$(DJANGO_ADMIN) graph_models --output=docs/models.png $(PARAMS_DEV) testapp

.PHONY: docs
# target: docs - build documentation
docs:
	$(SPHINXBUILD) -b html docs docs/_build
