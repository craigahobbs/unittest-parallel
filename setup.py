# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

import os

from setuptools import setup

import unittest_parallel

TESTS_REQUIRE = [
    'coverage'
]

def main():
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as readme_file:
        long_description = readme_file.read()

    setup(
        name='unittest-parallel',
        long_description=long_description,
        long_description_content_type='text/markdown',
        version=unittest_parallel.__version__,
        author='Craig Hobbs',
        author_email='craigahobbs@gmail.com',
        description=('Parallel unittest runner.'),
        keywords='unittest parallel',
        url='https://github.com/craigahobbs/unittest-parallel',
        license='MIT',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            "Topic :: Software Development :: Testing",
            "Topic :: Utilities",
        ],
        packages=['unittest_parallel'],
        install_requires=[],
        entry_points={
            'console_scripts': ['unittest-parallel = unittest_parallel.main:main'],
        },
        test_suite='unittest_parallel.tests',
        tests_require=TESTS_REQUIRE,
        extras_require={
            'tests': TESTS_REQUIRE
        }
    )


if __name__ == '__main__':
    main()
