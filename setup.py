# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

"""
The package build script
"""

import re
import os

from setuptools import setup

MODULE_NAME = 'unittest_parallel'
PACKAGE_NAME = 'unittest-parallel'
TESTS_REQUIRE = [
    'coverage >= 5.1'
]

def main():
    """
    The package build script's main entry point
    """

    # Read the package version
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src', MODULE_NAME, '__init__.py'), encoding='utf-8') as init_file:
        version = re.search(r"__version__ = '(.+?)'", init_file.read()).group(1)

    # Read the readme for use as the long description
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as readme_file:
        long_description = readme_file.read()

    # Do the setup
    setup(
        name=PACKAGE_NAME,
        description=('Parallel unit test runner for Python3 with coverage support'),
        long_description=long_description,
        long_description_content_type='text/x-rst',
        version=version,
        author='Craig Hobbs',
        author_email='craigahobbs@gmail.com',
        keywords='unittest parallel',
        url='https://github.com/craigahobbs/' + PACKAGE_NAME,
        license='MIT',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities'
        ],
        package_dir={
            '': 'src'
        },
        packages=[MODULE_NAME],
        entry_points={
            'console_scripts': [
                PACKAGE_NAME + ' = ' + MODULE_NAME + '.main:main'
            ],
        },
        test_suite='tests',
        tests_require=TESTS_REQUIRE,
        extras_require={
            'tests': TESTS_REQUIRE
        }
    )

if __name__ == '__main__':
    main()
