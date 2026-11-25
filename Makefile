.PHONY: build test all specimen install

build:
	fontforge -quiet -script build.py
	.venv/bin/python finalize.py

test:
	.venv/bin/pytest -q

all: build test

specimen:
	.venv/bin/python specimen.py

install: build
	mkdir -p $(HOME)/.local/share/fonts/LucioleMono
	cp dist/LucioleMono-Regular.ttf $(HOME)/.local/share/fonts/LucioleMono/
	fc-cache -f $(HOME)/.local/share/fonts
