ENV=$(CURDIR)/.env
BIN=$(ENV)/bin

PYTHON=$(shell which python)
DJANGO_ADMIN=$(shell which django-admin.py)

MANAGER=$(PYTHON) $(CURDIR)/jsonapi/tests/django/manage.py


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
	$(PYTHON) run_tests.py

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
