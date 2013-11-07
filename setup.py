#!/usr/bin/env python

from distutils.core import setup
import publish
import shutil
shutil.move(publish.publish.CLOUDTB_PATH, 
            publish.publish.CLOUDTB_PACKAGE_STR)
try:
    setup(name='wordtex',
          version=publish.VERSION,
          description='Latex to Word Press HTML converter',
          author='Garrett Berg',
          author_email='garrett@cloudformdesign.com',
          url='https://github.com/cloudformdesign/wordtex',
#          modules = ['wordtex', 'wp_formatting', 'texlib'],
          packages = ['wordtex', 'wordtex.cloudtb',],
          package_dir = {'wordtex': ''}
    #      packages=['wordtex', 'wordtex.cloudtb'],
         )
finally:
    import pdb
    pdb.set_trace()
    shutil.move(publish.publish.CLOUDTB_PACKAGE_STR, 
                publish.publish.CLOUDTB_PATH)
    