.PHONY: build test all specimen

build:
	fontforge -quiet -script build.py
	.venv/bin/python finalize.py

test:
	.venv/bin/pytest -q

all: build test

specimen:
	.venv/bin/python specimen.py
