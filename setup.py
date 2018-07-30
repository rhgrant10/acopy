#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()


setup_requirements = [
    'pytest-runner'
]

test_requirements = [
    'pytest', 'pytest-cov'
]

setup(
    name='pants',
    version='0.6.0',
    description="Traveling salesman, ant style",
    long_description=readme + '\n\n' + history,
    author="Robert Grant",
    author_email='rhgrant10@gmail.com',
    url='https://github.com/rhgrant10/pants',
    packages=find_packages(include=['pants']),
    data_files={'sample-graphs': ['sample-graphs/*']},
    entry_points={
        'console_scripts': ['pants=pants.cli:main'],
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=True,
    keywords='pants',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require={
        'plot': [
            'matplotlib==2.1.1',
            'pandas==0.23.3',
        ],
    }
)
