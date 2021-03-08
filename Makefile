PYTHON_VERSIONS := \
    3.9 \
    3.10-rc \
    3.8 \
    3.7 \
    3.6

# Download Python Build base makefile
ifeq '$(wildcard Makefile.base)' ''
    $(info Downloading Makefile.base)
    $(shell curl -s -o Makefile.base 'https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base')
endif

# Download Python Build's pylintrc
ifeq '$(wildcard pylintrc)' ''
    $(info Downloading pylintrc)
    $(shell curl -s -o pylintrc 'https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc')
endif

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc

PYLINT_ARGS := $(PYLINT_ARGS) --disable=missing-docstring
