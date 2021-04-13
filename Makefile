PYTHON_VERSIONS := \
    3.9 \
    3.10-rc \
    3.8 \
    3.7 \
    3.6

# Download Python Build base makefile and pylintrc
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell if which wget; then wget -q $(1); else curl -Os $(1); fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/pylintrc))

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc

PYLINT_ARGS := $(PYLINT_ARGS) --disable=missing-docstring
