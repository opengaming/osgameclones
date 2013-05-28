# To build this you'll need to install cyrax:
# http://github.com/piranha/cyrax
CYRAX ?= cyrax

build:
	$(CYRAX)

update:
	git pull
	$(CYRAX)
