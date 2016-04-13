.PHONY : test

test:
	python -m test

upload: docs
	python setup.py sdist upload

docs:
	pandoc --from=markdown --to=rst --output=README.rst README.md

virtualenv:
	virtualenv .virtualenv
	.virtualenv/bin/pip install -e .
	.virtualenv/bin/pip install -r requirements/test.txt
