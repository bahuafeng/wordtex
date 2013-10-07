#!/usr/bin/python
# -*- coding: utf-8 -*-
#                       The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2
#     Copyright 2013 Garrett Berg
#     
#     Loosly based on LaTeX2WP version 0.6.2, Luca Trevisan Copyright 2009
#    
#     This file is part of wordtex, a program that converts
#     a LaTeX document into a format that is ready to be
#     copied and pasted into WordPress.
#    
#     You are free to redistribute and/or modify wordtex under the
#     terms of the GNU General Public License (GPL), version 3
#     or (at your option) any later version.
#    
#     You should have received a copy of the GNU General Public
#     License along with wordtex.  If you can't find it,
#     see <http://www.gnu.org/licenses/>
#    http://opensource.org/licenses/MIT

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
    
#    document.check_no_update_text()
    document.format()
    
    print document.text_data
    with open(outputfile, 'w') as f:
        f.write(document.get_wp_text())
        
    print 'File output: ', outputfile
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    