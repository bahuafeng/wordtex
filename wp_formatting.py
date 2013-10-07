#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
*** BEGIN PROJECT LICENSE ***
%
% Copyright 2013 Garrett Berg
% 
% Loosly based on LaTeX2WP version 0.6.2, Luca Trevisan Copyright 2009
%
% This file is part of wordtex, a program that converts
% a LaTeX document into a format that is ready to be
% copied and pasted into WordPress.
%
% You are free to redistribute and/or modify wordtex under the
% terms of the GNU General Public License (GPL), version 3
% or (at your option) any later version.
%
% You should have received a copy of the GNU General Public
% License along with wordtex.  If you can't find it,
% see <http://www.gnu.org/licenses/>
%
*** END PROJECT LICENSE ***
"""

#TODO: Need colors and tables
#TODO: need math


range = xrange

import texlib
from cloudtb import textools
import copy

## Feel Free to change these things if you want
SECTION_NAME = ""
SUBSECTION_NAME = ""


# keeps track of section number in document
SECTION_NUMBER = 0
SUBSECTION_NUMBER = 0
PARAGRAPH = ('<p>', '</p>')
###############################
### Call functions for formatting
def delete_self(texpart, *args, **kwargs):
    texpart.text_data = ['']

def section_num(texpart, *args, **kwargs):
    global SECTION_NUMBER
    SECTION_NUMBER += 1
    texpart.text_data.insert(0, SECTION_NAME + ' {0}: '.format(
        SECTION_NUMBER))
    texpart.text_data = texlib.reform_text(texpart.text_data, 
                                           no_indicators= True)

def subsection_num(texpart, *args, **kwargs):
    global SUBSECTION_NUMBER
    SUBSECTION_NUMBER += 1
    texpart.text_data.insert(0, SUBSECTION_NAME + ' {0}.{1}: '.format(
        SECTION_NUMBER, SUBSECTION_NUMBER))
    texpart.text_data = texlib.reform_text(texpart.text_data, 
                                           no_indicators= True)

########################
## Automatically creating dictionaries of regexp's
tp = texlib.TexPart
# TODO: make label store the dictionary it is from
def build_dict(name, patterns, 
               inside_template = None, start_template = None, 
               end_template = None):
    mydict = {}
    for p, texpart in patterns:
        if inside_template == None:
            inside = []
        else:
            inside = [inside_template.format(p)]
        if start_template == None: 
            start = []
        else:
            start = [start_template.format(p)]
        if end_template == None:
            end = []
        else:
            end = [end_template.format(p)]
        
        new_tp = copy.copy(texpart)
        new_tp.update_match_re((inside, start, end))
        new_tp.label = p + ' dict:' + name
        mydict[p] = new_tp
    return mydict
    
# Create a dict of begin objects
begin_objects = [
['document'     ,tp()                                                  ],
['tabular'      ,tp(add_outside = ('TABLE_START','TABLE_END'),
                    no_outer_pgraphs = True)], #TODO: Placeholder
['lstlisting'   ,tp(add_outside = ('<ul><pre>','</pre></ul>'),
                    no_update_text = True, no_std_format = True,
                    no_outer_pgraphs=True)],
['itemize'      ,tp(add_outside = ('<ul>', '</ul>'),
                    no_outer_pgraphs = True)],
['enumerate'    ,tp(add_outside = ('<ul>','</ul>'),
                    no_outer_pgraphs = True)], #TODO: Placeholder
['equation'     ,tp(add_outside = ('','' ) )], #TODO: need basic equation
]

begin_dict = build_dict('begin', begin_objects, r'\\begin\{{{0}}} *?', None,
                           r'\\end\{{{0}}} *?')

# Create a dict for ifs

if_objects = [
['blog'      , tp(no_outer_pgraphs = True)],
['tex'       , tp(call_first = delete_self,
                  no_outer_pgraphs = True)],
['false'     , tp(call_first = delete_self,
                  no_outer_pgraphs = True)]
]

if_dict = build_dict('if', if_objects, r'\\if{0} ', 
                        r'\\if.*? ', 
                        r'\\fi ')


txt_attributes = [
['textbf'   ,tp(add_outside = ('<strong>', '</strong>'),
                no_outer_pgraphs = True)],# bolded
['textit'   ,tp(add_outside = ('<em>', '</em>'),
                no_outer_pgraphs = True)],# italicized
['uline'    ,tp(add_outside = ('''<span style="text-decoration: ''', 
                'underline;"></span>'), 
                no_outer_pgraphs = True )],# underlined
['section'      ,tp(add_outside = ('<h1><b>','</b></h1>'),
    call_first = [section_num])],
['section\*'    ,tp(add_outside = ('<h1><b>','</b></h1>'),)],
['subsection'   ,tp(add_outside = ('<h2><b>','</b></h2>'),
    call_first = [subsection_num])], 
['subsection\*' ,tp(add_outside = ('<h2><b>','</b></h2>'))], 
]
txt_attr_dict = build_dict('txt_attr', txt_attributes, 
                           r'\\{0}\{{', None, r'\}}')


line_items = [
['item'         ,tp(add_outside = ('<li>','</li>'), 
                    no_outer_pgraphs = True)], # used in itemize and enumerate
['hline'        ,tp(add_outside = ('',''),
                    no_outer_pgraphs = True)], #TODO: used in tabular
#[''     ,t(add_outside = '',''                      )],
]
line_dict = build_dict('line', line_items, r'\\{0} ', None, r'\n')

###########################
## Create some final formatting substitutions
## Math can handle itself (need to create a new module)


final_subs = [
    [r'\#'      ,'#'],
    [r'\$'      ,"$"],
    [r'\%'      ,"%"],
    [r'\textasciicircum{}'  ,r'^'],
    [r'\&'      ,r'&amp;'],
    [r'{*}'     ,r'* '],
    [r'{[}'     ,r'['],
    [r'{]}'     ,r']'],
    [r'\{'      ,r'{'],
    [r'\}'      ,r'}'],
    [r'\textbackslash{}'    ,'\\'],
    [r'\textasciitilde{}'   ,r'~'],
#    [r''    ,r''],
]

final_subs = [(textools.convert_to_regexp(n[0]), n[1])
               for n in final_subs]

##### SUMMARY
# So, the objects we have are:
# Dictionaries, which were created to automaticaly format reg expressions
# begin_dict    - contains \begin \end statements
# if_dict       - \if \endif statements
# txt_attr_dict - text attributes of form \attr{modified text}
# line_dict     - variables of a single line, i.e. \header MY HEADER\n
#
# We also have final_subs, which substitutes characters in so wordpress can
#   read them.
#
# We need to put items into the appropriate dictionaries so that the appropriate
# flags can call them or not call them.

def concatenate_dicts(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out

every_dict_formatting = concatenate_dicts(begin_dict, if_dict, txt_attr_dict,
                                          line_dict)

def get_dict_items(from_dict, items):
    '''put in dict items as list or string and get them as a dict'''
    if type(items) == str:
        items = items.split(',')
    items = set(items)
    return dict(((i[0], i[1]) for i in from_dict.iteritems() if i[0] in items))

        
    