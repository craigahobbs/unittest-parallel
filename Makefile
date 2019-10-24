PYTHON_VERSIONS := \
    3.8 \
    3.7 \
    3.6 \
    3.5

ifeq '$(wildcard .makefile)' ''
    $(info Downloading base makefile...)
    $(shell curl -s -o .makefile 'https://raw.githubusercontent.com/craigahobbs/chisel/master/Makefile.base')
endif
ifeq '$(wildcard pylintrc)' ''
    $(info Downloading pylintrc...)
    $(shell curl -s -o pylintrc 'https://raw.githubusercontent.com/craigahobbs/chisel/master/pylintrc')
endif
include .makefile

clean:
	rm -rf .makefile pylintrc
