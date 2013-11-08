#!/usr/bin/env python

from setuptools import setup

setup(name='Memorious',
    version='0.0.2',
    description='A simple CLI to manage website accounts',
    author='Vincent Ollivier',
    author_email='me@vinc.cc',
    url='https://github.com/vinc/memorious',
    packages=['memorious'],
    scripts=['bin/memorious'],
    test_suite='memorious.test',
    license='GNU GPL v3',
    install_requires=['pycrypto']
)
