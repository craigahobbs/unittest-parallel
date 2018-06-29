# Copyright (C) 2017 Craig Hobbs
#
# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

from setuptools import setup

TESTS_REQUIRE = []

setup(
    name='unittest-parallel',
    version='0.1',
    author='Craig Hobbs',
    author_email='craigahobbs@gmail.com',
    description=('Parallel unittest runner.'),
    keywords='unittest parallel',
    url='https://github.com/craigahobbs/unittest-parallel',
    license='MIT',
    classifiers=[
        "Environment :: Console",
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Topic :: Utilities",
    ],
    packages=['unittest_parallel'],
    install_requires=[],
    test_suite='unittest_parallel.tests',
    tests_require=TESTS_REQUIRE,
    extras_require={
        'tests': TESTS_REQUIRE,
    },
    entry_points={
        'console_scripts': ['unittest-parallel = unittest_parallel:main'],
    },
)
