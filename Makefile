NAME:=nexus_autodl

all: build

build: $(NAME).py
	pyinstaller --clean --noconsole --add-data "templates;templates" -F $<

clean:
	$(RM) -r build dist *.spec

.PHONY: build clean
