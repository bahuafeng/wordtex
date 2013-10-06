# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 23:38:09 2013

@author: user
"""
from cloudtb import dbe

import sys, os

import library
import formating

         
if __name__ == '__main__':
    import pdb
    inputfile = "/home/user/Documents/Website/Blog/Python Memory Management Helpers.tex"
    if len(argv) > 1:
        inputfile = argv[1]
    else:
        inputfile = os.path.join(os.getcwd(), inputfile)

    if len(argv) > 2:
        outputfile = argv[2]
    else:
        if is_file_ext(inputfile, 'tex'):
            outputfile = inputfile[:-4] + ".wp.html"
        else:
            outputfile = inputfile + ".wp.html"

    document = library.process_document(inputfile)
    
    
    
    
    