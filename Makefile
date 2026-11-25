.PHONY: build test all

build:
	fontforge -quiet -script build.py
	.venv/bin/python finalize.py

test:
	.venv/bin/pytest -q

all: build test
