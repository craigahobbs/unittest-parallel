PACKAGE_NAME := unittest_parallel

PYTHON_URLS_EXTRA := \
    https://www.python.org/ftp/python/3.4.6/Python-3.4.6.tgz \
    https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz

$(shell if [ ! -f .makefile ]; then $(if $(shell which curl), curl -s -o, wget -q -O) .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base'; fi)
include .makefile
