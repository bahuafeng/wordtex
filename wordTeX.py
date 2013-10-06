# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 23:38:09 2013

@author: user
"""

import sys, os

import re
from cloudtb import textools

CMP_TYPE = type(re.compile(''))

class LaTeX_Error(ValueError):
    def __init__(self, msg = '', line = '?'):
         self.line
         self.msg
    def __str__(self):
        msg = "LaTeX LaTeX Error at line {0}: ".format(line) + repr(msg)
        return msg

Macros = {"\\to":"\\rightarrow",
          "\\B":"\\{ 0,1 \\}" ,
          "\\E":"\mathop{\\mathbb E}",
          "\\P":"\mathop{\\mathbb P}",
          "\\N":"{\\mathbb N}",
          "\\Z":"{\\mathbb Z}",
          "\\C":"{\\mathbb C}",
          "\\R":"{\\mathbb R}",
          "\\Q":"{\\mathbb Q}",
          "\\xor":"\\oplus",
          "\\eps":"\\epsilon",
          "\\more":"<!--more-->",
          "\\newblock":"\\\\",
          "\\sloppy":"",
          "\\S":"&sect;"
         }

def format_paragraph(text_data):
    pass

def format_font(text_data):
    pass

def format_outside(text_data, sub_outside):
    pass

#TODO: Need begins for colors and tables
class TexPart(object):
    r'''this class is a text object, normally preceeded by either a begin
    statement or a single line (i.e. \header) and ended by an end statement
    or a \n
    '''
    def __init__(self, text_block, sub_outside = None, paragraph_outside = False):
        '''
        text_block = start, text_data, end
            Should be used with get_objects_inout. start has value == 2,
            the text_data is all values inbetween == 1 and end has value == 3
        sub_outside = this is the outside characters that will be subbed
            during the format call.
        '''
        self.start, self.text_data, self.end = text_block
        self.no_format = no_format
        self.is_done = False
    
    def format(self):
        # do these last
        format_paragraph(self.text_data)
        format_font(self.text_data)
        if self.sub_outside:
            format_outside(text_data, self.sub_outside)

def call_items(array, call):
    '''perform a functoin call on every item in an array'''
    return [call(n) for n in ltxt]

# These two functions remain simple because they are simple -- they
# delete everything on the inside / outside of the matches.
# They should only be used at the beginning to simplify the stuff that
# is absolutely not needed.
def delete_outside(text, matches):
    '''only keep text that is inside and call a function on it
    matches = inside_list, start_list, end_list. See get_objects_inout for
    documentation'''
    isin = get_objects_inout(text, *matches)
    ltxt = [n[1] for n in inout if n[0]]
    return ''.join(ltxt)

def delete_inside(text, matches):
    '''only keep text that is outside and call a function on it
    matches = inside_list, start_list, end_list. See get_objects_inout for
    documentation'''
    isin = get_objects_inout(text, *matches)
    ltxt = [n[1] for n in inout if not n[1]]
    return ''.join(ltxt)

def handle_inside(text, matches, call = None, 
                  do_inlist = None, do_stlist = None, do_endlist = None):
    '''Handles the data inside the start/end by executing call on it. Does
    not remove it from the text.

    matches = inside_list, start_list, end_list. See get_objects_inout for
    documentation
    
    do_inlist: execute this function on the matches for 'inside_list'
    do_stlist: execute this function on the matches for 'start_list'
    do_endlist: execute this function on the matches for 'end_list'
    simple example:
        do_endlist = [[r'\\fi', lambda inout_val, in_str: 'this was an end' + in_str]]
        # replaces all end fi's with 'this was an end: \fi'
    So each call recieves the inout_val (0, 1, 2, or 3) and it's own text
    (Note: text is interpreted as a regular expression)
    '''
    #TODO: Going to wait till I actually need to use this to flush it out
    isin = get_objects_inout(text, *matches)
    if do_inlist:
        pass
        

###################################3
## GENERAL FUNCTIONS   
def split_text(matches, text):
    '''compiles the matches into simple re or uses custom one and splits'''
    matches = ['({0})'.format(m) for m in matches]
    matches = re.compile('|'.join(matches))
    return matches, matches.split(text)

def get_objects_inout(text_objects, inside_list, starters_list, end_list):
    '''given the matches, returns the text in order in tuples as the following
    (2, txt3),  # value was the first inside start of group    
    (True, txt1),
    (True, txt2),
    (True, TxtPart),
    (3, txt4),  # text was the final end of group
    (False, txt2),
    (False, TxtPart),
    etc...
    
    where True means that the text is inside your match parameters and False
    means they are outside. 2 and 3 are documented above.
    
    Note, the inside list takes precedence over the starter list, and the starter
    list takes precedence over the end list.
    This means that if something matches inside it will not match starter, etc.
    It is best to make your "insides" specific and not use special re 
    characters like .* etc.
    
    If a starters is imbeded in an inside, it is considered inside. For instance
    /iffase /ifblog no hello to world /fi /fi -- ifblog will be inside of /iffalse
    '''
    re_in = textools.re_in
    
    # error checking on file
    match_cmp = check_brackets(text_objects, inside_list + starters_list, end_list)
    
    # split up text for compiling
    splited = []
    for tobj in text_objects:
        if type(tobj) == TexPart:
            splited.append(tobj)
        else:
            splited.extend(match_cmp.split(text_objects))
        
    inside = [re.compile(m) for m in inside_list]
    starter = [re.compile(m) for m in starters_list]
    end = [re.compile(m) for m in end_list]
    
    num_in = 0
    set_num = None
    ltext = []
    #TODO: It has to match arbitrary if statements. I think this should be
    # pretty easy
    for txt in splited:
        assert(num_in >= 0)
        if txt in (None, ''):
            continue
        if type(txt) == TexPart:
            pass    # TexParts have been alrady processed.
        elif re_in(txt, inside):
            if num_in == 0:
                set_num = 2
            num_in += 1
        elif inside > 0 and re_in(txt, starter):
            # i.e. if you wrote something like /iffalse /ifblog
            num_in += 1
        elif re_in(txt, end):
            # make sure we only count ends if you are removing!
            num_in -= 1
            if num_in == 0:
                set_num = 3
        
        if set_num:
            ltext.append((set_num, txt))
            set_num = None
        elif num_in > 0:
            ltext.append((True, txt))
        else:
            ltext.append((False, txt))
            
    return ltext

def check_brackets(text_objects, start_list, end_list):
    '''
    This works more simply than it looks.
    text_objects = list of objects, either strings (not processed) or TexPart's
    (processed and checked already). It skips the TexParts, keeping them
    
    Checks to make sure all brackets are completed (i.e. \iffalse or \(ifblog) or \iftex
    is completed by an \fi.
    Example input:
    found, gnumbers = check_brackets([r'(\\iffalse)', r'\\(ifblog)', r'\\(iftex)', r'\\(if.*) ', r'\\(fi)'],
                                      text_objects)
    note: only returns the first group number found!
    raises LaTeX_Error on failure

    return match_compile
    '''
    match_cmp = re.compile('|'.join(start_list + end_list))
    found = []
    gnumbers = []
    for tobj in text_objects:
        if type(tobj) != TexPart:
            found = match_cmp.findall(tobj)
            gnumbers.extend([textools.group_num(n) for n in found])

    n = 0
    end_num = len(gnumbers) + 1
    for gn in gnumbers:
        if gn < end_num:
            n += 1
        else:
            n -= 1
    if n != 0:
        raise LaTeX_Error("Brackets not matched")
    return match_cmp
    
class LatexWordpress(object):
    '''Reads a LaTeX text document and processes it.
    The class works by first filtering out stuff that is absolutely not needed
    (i.e. comments) and then splitting up the document into various class
    handlers. These are defined in #TODO
    '''
    def __init__(self, path):
        with open(path) as f:
            self.text = f.read()
        self.get_doc()