PYTHON_VERSIONS := \
    3.9 \
    3.10-rc \
    3.8 \
    3.7 \
    3.6

ifeq '$(wildcard .makefile)' ''
    $(info Downloading base makefile...)
    $(shell curl -s -o .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base')
endif
ifeq '$(wildcard pylintrc)' ''
    $(info Downloading pylintrc...)
    $(shell curl -s -o pylintrc 'https://raw.githubusercontent.com/craigahobbs/chisel/master/pylintrc')
endif
include .makefile

PYLINT_ARGS := $(PYLINT_ARGS) --disable=missing-docstring

clean:
	rm -rf .makefile pylintrc
