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

'''
OK, tables
Note: raggedright means left justified. centering means centered, etc.
It looks like everything is really set up in the very first line. Everyting 
else is just standard processing.

For the non-lists you have to watch out for the enter key -- it looks like it
is using standard spacing! See the first line "center aligned" row

\begin{tabular}{|>{\raggedright}p{5cm}||>{\centering}p{3cm}||>{\raggedright}p{7cm}|}
\hline 
r1 c1 with width 5. These columns wrap rather nicely & r1c 

center aligned & \begin{itemize}
\item r1c3
\item look! I'm a list!
\item For lists, it is a good idea to left justify, like this column!
\item I have a width of 7\end{itemize}
\tabularnewline
\hline 
\hline 
r2 &  & this one is now also aligned left\tabularnewline
\hline 
\hline 
r3 &  & \tabularnewline
\hline 
\end{tabular}

### HTML TABLE FROM WORDPRESS
<style type="text/css"><!--
TD P { margin-bottom: 0in; }P { margin-bottom: 0.08in; }A:link {  }
--></style>
<table width="689" cellspacing="0" cellpadding="0"><colgroup> <col width="128" /> <col width="168" /> <col width="393" /> </colgroup>
<tbody>
<tr valign="TOP">
<td width="128">r1 c1 with width 5. These columns wrap rather nicely</td>
<td width="168">
<p align="CENTER">r1c2</p>
<p align="CENTER">center alligned</p>
</td>
<td width="393">
<ul>
	<li>r1c3</li>
	<li>look! I'm a list!</li>
	<li>For lists, it is a good idea to left justify, like this column!</li>
	<li>I have a width of 7</li>
</ul>
</td>
</tr>
<tr valign="TOP">
<td width="128">r2</td>
<td width="168"></td>
<td width="393">this one is left aligned</td>
</tr>
<tr valign="TOP">
<td width="128">r3</td>
<td width="168"></td>
<td width="393"></td>
</tr>
</tbody>
</table>


##############
## Changing font type to courier new (should work)
# I just need to add the following around the block
# I think the "style = "padd..." could be replaced with the std indent
# STILL NEED TO CHECK IN WP
<p style="padding-left: 30px;"><span style="font-family: comic sans ms,sans-serif; background-color: #c0c0c0; color: #000000;">This is an example of the kind of output I want for my code
Note that it is indented, of a different font, and has a different background color.</span>
'''
#TODO: Need colors and tables
#TODO: need math
range = xrange

import re
import copy

import texlib
from cloudtb import textools


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

def hline_call(texpart, *args, **kwargs):
    texpart.reset_text()
    body, = texpart.text_data
    columns = re.split(' [&] ', body)
    use_dict = [['tabular_column', texlib.TexPart(no_outer_pgraphs= True,
                              add_outside = ('<td>', '</td>'))]]
    use_dict = build_dict('hline_custom', use_dict)
                              

def tabular_call(texpart, *args, **kwargs):
    get_columns_raw = r'\\begin{tabular}{(.*)}'
    get_split_columns = r'|'
    get_column_info = r'>{\\(.*?)}p{([0-9]*)[\\\w]*}'
    
    raw_cols = re.match(get_columns_raw, texpart.start_txt).group(1)
    split_cols = re.split(get_split_columns, raw_cols)
    default_align = 'raggedright'
    default_width = ('1', 'DEFAULT')
    align_data, width_data = [], []
    for col in split_cols:
        if col == '':
            continue
        if col == 'c':
            align_data.append(default_align)
            width_data.append(default_width)
        else:
            cgroup = re.match(get_column_info, col).group
            align_data.append(cgroup(1))
            width_data.append((cgroup(2), cgroup(3)))
    
    align_dict = {'raggedright' : 'left',
                  'centering'   : 'center'
                 }
    for i, value in enumerate(align_data):
        align_data[i] = align_dict[value]
    
    perc_width_format = r'style="width: {0}%;"'
    # we are going to do this better in the future
    tot_width = sum([n[0] for n in width_data])
    last_type = -1
    for i, value in enumerate(width_data):
        amount, ctype = value
        if last_type != -1:
            assert(ctype == last_type)  # doing this for now.
        
        amount = int(amount * 100.0 / tot_width)
        # TODO: more dynamic possibilities for width data
        width_data[i] = perc_width_format.format(amount)
    
    td_format = r'<td align="{col_align}" valign="{row_align}" {width}>'
    
    class hline_call:
        def __init__(self, use_dict_list):
            use_dict_list = []
            self.index = 0
        
        def __call__(self, texpart, *args, **kwargs):
            pass
        
    use_dict = [['hline'        ,texlib.TexPart(
                    add_outside = ('<tr>','</tr>'),
                    call_first = hline_call,
                    no_outer_pgraphs = False)]]
    use_dict = build_dict('hline', use_dict, r'\\{0} ', None, r'\n')
    


########################
## Automatically creating dictionaries of regexp's
tp = texlib.TexPart
# TODO: make label store the dictionary it is from
def build_dict(name, patterns, 
               inside_template = None, start_template = None, 
               end_template = None, custom = None):
    mydict = {}
    i = 0
    for p, texpart in patterns:
        if custom != None:
            i += 1
            inside, start, end = p
            p = 'i {0}:{1}:{2}'.format(i, inside, start, end)
        else:
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
['enumerate'    ,tp(add_outside = ('<ol>','</ol>'),
                    no_outer_pgraphs = True)], #TODO: Placeholder
['equation'     ,tp(add_outside = ('','' ) )], #TODO: need basic equation
]

begin_dict = build_dict('begin', begin_objects, r'\\begin\{{{0}}}(\{{.*?}})? *?', None,
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
['subsection*' ,tp(add_outside = ('<h2><b>','</b></h2>'))], 
]
txt_attr_dict = build_dict('txt_attr', txt_attributes, 
                           r'\\{0}\{{', None, r'\}}')


line_items = [
['item'         ,tp(add_outside = ('<li>','</li>'), 
                    no_outer_pgraphs = True)], # used in itemize and enumerate
#[''     ,t(add_outside = '',''                      )],
]
line_dict = build_dict('line', line_items, r'\\{0} ', None, r'\n')


#################
## Custom items - #TODO NOT YET TESTED
# if you REALLY need to do your own custom regular expression matching,
# you can do so here. NOTE that you do NOT need to put parenthesis around
# the patter, as this will be done automatically.
custom_items = [
#[['custom regexp insisde'], ['custom regexp outside'], ['custom regexp end']], tp()]
]

custom_dict = build_dict('custom', custom_items)
                         
###########################
## Create some final formatting substitutions
## These should generally be of very few characters.

from cloudtb.extra import richtext
final_subs = [
[r'\#'      ,'#'],
[r'\$'      ,"$"],
[r'\%'      ,"%"],
[r'{*}'     ,r'* '],
[r'{[}'     ,r'['],
[r'{]}'     ,r']'],
[r'\{'      ,r'{'],
[r'\}'      ,r'}'],
[r'<'       ,r'&lt;'],
[r'>'       ,r'&gt;'],
[r'\&'      ,r'&amp;'],
[r'"'       ,r'&quot;'],
[r'\textbackslash{}'    ,'\\'],
[r'\textasciitilde{}'   ,r'~'],
[r'\textasciicircum{}'  ,r'^'],
#    [r''    ,r''],
]
final_subs = [(textools.convert_to_regexp(n[0], compile = True), n[1])
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

def concatenate_dicts(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out

every_dict_formatting = concatenate_dicts(begin_dict, if_dict, txt_attr_dict,
                                          line_dict, custom_dict)
        
    