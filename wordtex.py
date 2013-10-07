# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 23:38:09 2013

@author: user
"""
import sys, os
sys.path.insert(1, '..')
from cloudtb import dbe, system



import texlib

document = None

def main():
    import wp_formatting
    import pdb
    
    texlib.TexPart.FORMAT_MODULE = wp_formatting
    argv = sys.argv
    inputfile = "tex_docs/simple.tex"
    if len(argv) > 1:
        inputfile = argv[1]
    else:
        inputfile = os.path.join(os.getcwd(), inputfile)

    if len(argv) > 2:
        outputfile = argv[2]
    else:
        if system.is_file_ext(inputfile, 'tex'):
            outputfile = inputfile[:-4] + ".wp.html"
        else:
            outputfile = inputfile + ".wp.html"

    document = texlib.process_document(inputfile)
    texlib.print_tex_tree(document)
    
    document.format()
    print document.text_data
    with open(outputfile, 'w') as f:
        f.write(document.get_wp_text())
        
    print 'File output: ', outputfile
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    