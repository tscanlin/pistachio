.PHONY : test

test:
	python -m test

upload: docs
	python setup.py sdist upload

docs:
	pandoc --from=markdown --to=rst --output=README.rst README.md
