PYTHON_VERSIONS := \
    3.7 \
    3.6 \
    3.5

ifeq '$(wildcard .makefile)' ''
    $(info Downloading base makefile...)
    $(shell curl -s -o .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base')
endif
include .makefile
