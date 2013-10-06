# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 23:38:09 2013

@author: user
"""

import sys, os

import library as lib

tp = lib.TexPart

# Create a dict of begin objects
begin_objects = [
    'document',
    'tabular',
    'lstlisting',
    'itemize',
    'enumerate',
    'equation',    
    ]


re_begin_inside_template = r'(\\begin\{{0}}\n)'
re_begin_end_template = r'(\\end\{{0}}\n)'

begin_re_dict = ((b, (re_begin_inside_template.format(b),
                      [],
                      re_begin_end_template.format(b))
                 ) for b in begin_objects
                )
begin_re_dict = dict(begin_re_dict)

# Create a dict for ifs
re_if_template = r'(\\if{0} )'
START_IF = r'(\\if.*? )'
END_IF = r'(\\fi )'

if_objects = [
    'blog',
    'tex',
    'false']
if_re_dict = ((b, (re_if_template.format(b),
                      START_IF,
                      END_IF)
              ) for b in if_objects
             )
if_re_dict = dict(if_re_dict)

re_txt_attributes_template_inside = r'(\\{0}\{)'
END_attributes_template = r'(\})'
txt_attributes = [
'textbf',   # bolded
'textit',   # italicized
'uline',    # underlined
]
txt_attr_dict = ((b, (re_txt_attributes_template_inside.format(b),
                      [],
                      END_attributes_template)
                 ) for b in if_objects
             )
txt_attr_dict = dict(txt_attr_dict)


## Create some final formatting substitutions
final_subs = [
    [r'\#'      ,'#'],
    [r'\$'      ,"$"],
    [r'\%'      ,"%"],
    [r'\textasciicircum{}'    ,r'^'],
    [r'\&'      ,r'&amp;'],
    [r'{*}'     ,r'* '],
    [r'{[}'        ,r'['],
    [r'{]}'    ,r']'],
    [r'\{'    ,r'{'],
    [r'\}'    ,r'}'],
    [r'\textbackslash{}'    ,'\\'],
    [r'\textasciitilde{}'    ,r'~'],
#    [r''    ,r''],
]


# Create a dict for other symbols


         
if __name__ == '__main__':
    
    text