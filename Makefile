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
    $$(shell if which wget > /dev/null; then wget -q '$(strip $(1))'; else curl -Os '$(strip $(1))'; fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc))

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc

PYLINT_ARGS := $(PYLINT_ARGS) --disable=missing-docstring
