PACKAGE_NAME := unittest_parallel

PYTHON_VERSIONS := \
    3.7.0 \
    3.6.6 \
    3.5.5 \
    3.4.8

COVERAGE_REPORT_ARGS := --fail-under 11

ifeq '$(wildcard .makefile)' ''
    $(info Downloading base makefile...)
    $(shell curl -s -o .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base')
endif
include .makefile
