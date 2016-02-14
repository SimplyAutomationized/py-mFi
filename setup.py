#!/usr/bin/env python

from setuptools import setup, Extension

setup(name='mfi',
      version='1.0',
      description='Python Light module for working with color LEDs',
      author='Kevron Rees, Nathan Rees',
      author_email='tripzero.kev@gmail.com, nextabyte@gmail.com',
      url='https://github.com/SimplyAutomationized/py-mFi-LD',
      packages=["mfi", "mfi_iftt"],
      install_requires=["trollius", "twisted"]
      )
