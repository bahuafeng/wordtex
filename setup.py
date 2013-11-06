#!/usr/bin/env python

from distutils.core import setup
import publish

setup(name='wordtex',
      version=publish.VERSION,
      description='Latex to Word Press HTML converter',
      author='Garrett Berg',
      author_email='garrett@cloudformdesign.com',
      url='https://github.com/cloudformdesign/wordtex',
      packages = ['wordtex']
#      packages=['wordtex', 'wordtex.cloudtb'],
#      package_dir = {'wordtex.cloudtb': '_publish'}
     )