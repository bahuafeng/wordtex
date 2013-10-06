# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 04:41:47 2013

@author: user
"""
range = xrange

import texlib
from cloudtb import textools
import copy

# keeps track of section number in document
SECTION_NUMBER = 0
SUBSECTION_NUMBER = 0

PARAGRAPH = ('<p>', '</p>')
###############################
### Call functions for formatting
def delete_self(texpart, *args, **kwargs):
    texpart.text_data = ['']
    no_start_end(texpart)
    texpart.done = True

def no_start_end(texpart, *args, **kwargs):
    texpart.start, texpart.end = '', ''

def section_num(texpart, *args, **kwargs):
    global SECTION_NUMBER
    SECTION_NUMBER += 1
    sect = texlib.TexPart('*section')
    sect.update_text(('', 'Section {0}'.format(SECTION_NUMBER),
                      ''))
    texpart.insert_tex(0, sect)

def subsection_num(texpart, *args, **kwargs):
    global SUBSECTION_NUMBER
    SUBSECTION_NUMBER += 1
    sect = texlib.TexPart('*subsection', '')
    sect.update_text(('', 'Section {0}.{1}'.format(
        SECTION_NUMBER, SUBSECTION_NUMBER), 
        ''))
    texpart.insert_tex(0, sect)

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
['lstlisting'   ,tp(add_outside = ('<pre>','<\pre>'),
                    no_update_text = True, no_std_format = True)],
['itemize'      ,tp(add_outside = ('<ul>', '</ul>'),
                    no_outer_pgraphs = True)],
['enumerate'    ,tp(add_outside = ('<ul>','</ul>'),
                    no_outer_pgraphs = True)], #TODO: Placeholder
['equation'     ,tp(add_outside = ('','' )                            )], #TODO: need basic equation
]

begin_dict = build_dict('begin', begin_objects, r'(\n?\\begin\{{{0}}} *?\n?)', None,
                           r'(\n?\\end\{{{0}}} *?\n?)')

# Create a dict for ifs

if_objects = [
['blog'      , tp(no_outer_pgraphs = True)],
['tex'       , tp(call_first = delete_self,
                  no_outer_pgraphs = True)],
['false'     , tp(call_first = delete_self,
                  no_outer_pgraphs = True)]
]

if_dict = build_dict('if', if_objects, r'(\\if{0} )', 
                        r'(\\if.*? )', 
                        r'(\\fi )')


txt_attributes = [
['textbf'   ,tp(add_outside = ('<strong>', '</strong>'),
                no_outer_pgraphs = True)],# bolded
['textit'   ,tp(add_outside = ('<em>', '</em>'),
                no_outer_pgraphs = True)],# italicized
['uline'    ,tp(add_outside = ('''<span style="text-decoration: underline;">''', 
                '</span>'), 
                no_outer_pgraphs = True )],# underlined
['section'      ,tp(add_outside = ('<h1><b>','</b></h1>'),
    call_first = [section_num])],
['section\*'    ,tp(add_outside = ('<h1><b>','</b></h1>'),)],
['subsection'   ,tp(add_outside = ('<h2><b>','</b></h2>'),
    call_first = [subsection_num])], 
['subsection\*' ,tp(add_outside = ('<h2><b>','</b></h2>'))], 
]
txt_attr_dict = build_dict('txt_attr', txt_attributes, 
                           r'(\\{0}\{{)', None, r'(\}})')


line_items = [
['item'         ,tp(add_outside = ('<li>','<\li>'), 
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

fsubs_reg = ['(' + textools.convert_to_regexp(n[0]) + ')'
               for n in final_subs]
final_subs = dict([(fsubs_reg[i], final_subs[i][1]) 
                for i in range(len(fsubs_reg))])
del fsubs_reg

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
    
std_format = get_dict_items(txt_attr_dict, 'textbf, textit, uline')

tables_format = concatenate_dicts(get_dict_items(begin_dict, 'tabular'),
                           get_dict_items(line_dict, 'hline'))

lists_format = concatenate_dicts(get_dict_items(begin_dict, 'itemize, enumerate'),
                          get_dict_items(line_dict, 'item'))
                          
code_format = get_dict_items(begin_dict, 'lstlisting')

sections_format = get_dict_items(line_dict, 'section, section\*, subsection,'
                                      ' subsection\*')
    
    
        
    