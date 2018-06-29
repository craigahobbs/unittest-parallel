PACKAGE_NAME := unittest_parallel

PYTHON_VERSIONS := \
    3.7.0 \
    3.6.6 \
    3.5.5

$(shell if [ ! -f .makefile ]; then $(if $(shell which curl), curl -s -o, wget -q -O) .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base'; fi)
include .makefile
