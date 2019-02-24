PACKAGE_NAME := unittest_parallel

PYTHON_VERSIONS := \
    3.7.2 \
    3.6.8 \
    3.5.6

ifeq '$(wildcard .makefile)' ''
    $(info Downloading base makefile...)
    $(shell curl -s -o .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base')
endif
include .makefile
