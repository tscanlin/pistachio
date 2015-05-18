.PHONY : test

test:
	python -m test

upload:
	python setup.py sdist upload
