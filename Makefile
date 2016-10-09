# To build this you'll need to install cyrax:
# http://github.com/piranha/cyrax
CYRAX ?= cyrax

build:
	$(CYRAX)

install:
	pip install -r requirements.txt

update:
	git pull
	$(CYRAX)
