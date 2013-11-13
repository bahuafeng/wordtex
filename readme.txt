#!/usr/bin/python
# -*- coding: utf-8 -*-
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2.21
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

Version 0.6.3, Oct 1, 2013
  - Modified by Garrett Berg cloudformdesign.com
  - Headings changed in 

Version 0.6.2, May 6, 2009
  - Additional support for accented characters
  - Convert '>' and '<' to HTML codes
  - Changed to handling of \& and \% in math mode to reflect
    different WordPress treatment of them

Version 0.6.1 February 23, 2009
  - Simplified format of latex2wpstyle.py (by Radu Grigore)
  - Allow nesting of font styles such as \bf and \em (by Radu Grigore)
  - Allow escaped symbols such as \$ in math mode
  - LaTeX macros are correctly "tokenized"
  - Support eqnarray* environment


Version 0.6 February 21, 2009
  First release