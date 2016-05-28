#!/usr/bin/env python

from setuptools import setup, Extension

setup(name='mfi',
      version='1.0',
      description='Python library for interacting with various ubiquity mfi devices',
      author='Kevron Rees, Nathan Rees',
      author_email='tripzero.kev@gmail.com, nextabyte@gmail.com',
      url='https://github.com/SimplyAutomationized/py-mFi-LD',
      packages=["mfi"],
      install_requires=["trollius", "twisted"]
      )
