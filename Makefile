STYLES = Regular Bold
# italiques des droits construits (Regular → Italic, Bold → BoldItalic)
ITALICS = $(patsubst RegularItalic,Italic,$(addsuffix Italic,$(STYLES)))
.PHONY: build test all specimen install

build:
	@for s in $(STYLES); do \
	  echo "== $$s"; \
	  LUCIOLE_STYLE=$$s fontforge -quiet -script make_source.py || exit 1; \
	  LUCIOLE_STYLE=$$s fontforge -quiet -script build.py || exit 1; \
	  LUCIOLE_STYLE=$$s .venv/bin/python finalize.py || exit 1; \
	done
	@echo "== $(ITALICS)"; .venv/bin/python italicize.py $(STYLES)

test:
	@for s in $(STYLES); do \
	  echo "== $$s"; LUCIOLE_STYLE=$$s .venv/bin/pytest -q || exit 1; \
	done

all: build test

specimen:
	@for s in $(STYLES) $(ITALICS); do \
	  LUCIOLE_STYLE=$$s .venv/bin/python specimen.py specimens/$$s || exit 1; \
	done

install: build
	mkdir -p $(HOME)/.local/share/fonts/LucioleMono
	cp dist/LucioleMono-*.ttf $(HOME)/.local/share/fonts/LucioleMono/
	fc-cache -f $(HOME)/.local/share/fonts
