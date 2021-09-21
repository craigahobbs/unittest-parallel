# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE

import os

from setuptools import setup


def main():
    # Read the readme for use as the long description
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as readme_file:
        long_description = readme_file.read()

    # Do the setup
    setup(
        name='unittest-parallel',
        description='Parallel unit test runner with coverage support',
        long_description=long_description,
        long_description_content_type='text/markdown',
        version='1.4.6',
        author='Craig A. Hobbs',
        author_email='craigahobbs@gmail.com',
        keywords='test unittest coverage parallel',
        url='https://github.com/craigahobbs/unittest-parallel',
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
            'Programming Language :: Python :: 3.10',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities'
        ],
        package_dir={'': 'src'},
        packages=['unittest_parallel'],
        install_requires=[
            'coverage >= 5.1'
        ],
        entry_points={
            'console_scripts': [
                'unittest-parallel = unittest_parallel.main:main'
            ]
        }
    )


if __name__ == '__main__':
    main()
