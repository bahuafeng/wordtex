#!/usr/bin/python
# -*- coding: utf-8 -*-
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2.23
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

import pdb
import sys, os
sys.path.insert(1, '..')
from cloudtb import dbe
from cloudtb import system, logtools
log = logtools.get_logger()
logtools.log_fatal_exception()
log.info('starting')

import texlib

document = None

def main():
    import argparse
    import wp_formatting
    import publish
    import pdb
    
    texlib.TexPart.FORMAT_MODULE = wp_formatting

    parser = argparse.ArgumentParser(description = "Convert .tex file to "
        "wordpress html.")
    parser.add_argument('file_input',
                        help = "The input path")
    parser.add_argument('file_output',
                        default = '', nargs = '?',
                        help = 'The output path. Default is <in>.wp.html')
    parser.add_argument('-L', '--lyx', nargs = 2,
                        help = "Custom option for Lyx")
    parser.add_argument('--version', action='version', 
                        version='%(prog)s {0}'.format(publish.VERSION))
    
    args = parser.parse_args()
    
    if args.file_output == '':
        if system.is_file_ext(args.file_input, 'tex'):
            args.file_output = args.file_input[:-4] + ".wp.html"
        else:
            args.file_output = args.file_input + ".wp.html"
'''python -tt /home/user/Projects/CloudformDesign/PythonCloudform/wordtex/\
wordtex.py $$i $$o --lyx $$p $$r'''
    if args.lyx:
        # output file needs directory
        # lyx variable has original input file directory
        args.file_input = args.lyx[0] + args.file_input
        args.file_output = args.lyx[1] + args.file_output
    
    print "Input:", args.file_input
    document = texlib.process_document(args.file_input)
    
#    texlib.print_tex_tree(document)
#    document.check_no_update_text()
    document.format()
    try:
        import bs4
        html_text = bs4.BeautifulSoup(document.get_wp_text()).prettify()
    except ImportError:
        html_text = document.get_wp_text()
    with open(args.file_output, 'w') as f:
        f.write(html_text)
    print 'Done, file at :', args.file_output
    
if __name__ == '__main__':
    main()
    
    
    
    
    