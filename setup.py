#!/usr/bin/env python

from setuptools import setup, Extension

install_requires = ["twisted", "wss", "PySignal"]

import sys
if sys.version_info < (3,0):
    install_requires.append("trollius")

setup(name='mfi',
      version='1.1',
      description='Python library for interacting with various ubiquity mfi devices',
      author='Kevron Rees, Nathan Rees',
      author_email='tripzero.kev@gmail.com, nextabyte@gmail.com',
      url='https://github.com/SimplyAutomationized/py-mFi',
      packages=["mfi"],
      scripts=['mfi/mpower'], 
      install_requires=install_requires
      )
