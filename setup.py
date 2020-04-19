#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'click~=7.1',
    'networkx~=2.4',
    'tsplib95~=0.7.0',
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Robert Grant",
    author_email='rhgrant10@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Ant Colony Optimization for Tthe Traveling Salesman Problem.",
    entry_points={
        'console_scripts': [
            'acopy=acopy.cli:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'plot': [
            'matplotlib~=3.2',
            'pandas~=1.0',
        ],
    },
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='acopy',
    name='acopy',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rhgrant10/acopy',
    version='0.7.0',
    zip_safe=True,
)
