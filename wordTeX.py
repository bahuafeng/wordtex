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

begin = {'document': delete_outside,
         'lstlisting': None,
         }

#from functools import update_wrapper
#def dec_interpret_matches(function):
#    def decorated_function(matches, call, *args):
#        if type(matches) == str:
#            inside_list = [r'\begin\{{0}}'.format(matches)]
#            outside_list = []
#            end_list = [r'\end\{{0}}'.format(matches)]
#        else:
#            inside_list, outside_list, end_list = matches
#        return function(matches, *args)
#    update_wrapper(decorated_function, function)
#    return decorated_function

def call_items(array, call):
    '''perform a functoin call on every item in an array'''
    return [call(n) for n in ltxt]

def delete_outside(text, matches, call = None):
    '''only keep text that is inside and call a function on it
    matches = inside_list, start_list, end_list. See get_text_inout for
    documentation'''
    isin = get_text_inout(text, *matches)
    ltxt = [n[1] for n in inout if n[0]]
    if call:
        ltxt = call_item(ltxt)
    return ''.join(ltxt)

def delete_inside(text, matches, call = None):
    '''only keep text that is outside and call a function on it
    matches = inside_list, start_list, end_list. See get_text_inout for
    documentation'''
    isin = get_text_inout(text, *matches)
    ltxt = [n[1] for n in inout if not n[1]]
    if call:
        ltxt = call_items(ltxt)
    return ''.join(ltxt)

def handle_inside(text, matches, call = None, 
                  do_inlist = None, do_stlist = None, do_endlist = None)
    '''Handles the data inside the start/end by executing call on it. Does
    not remove it from the text.
    matches = inside_list, start_list, end_list. See get_text_inout for
    documentation
    '''
    do_inlist: execute this function on the matches for 'inside_list'
    do_stlist: execute this function on the matches for 'start_list'
    do_endlist: execute this function on the matches for 'end_list'

###################################3
## GENERAL FUNCTIONS   
def split_text(matches, text):
    '''compiles the matches into simple re or uses custom one and splits'''
    matches = ['({0})'.format(m) for m in matches]
    matches = re.compile('|'.join(matches))
    return matches, matches.split(text)

def get_text_inout(raw_text, inside_list, starters_list, end_list):
    '''given the matches, returns the text in order in tuples as the following
    (True, txt1),
    (False, txt2),
    etc...
    where True means that the text is inside your match parameters and False
    means they are outside
    
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
    match_cmp = check_brackets(inside_list + starters_list, end_list, raw_text)[0]
    
    # split up text for compiling
    splited = match_cmp.split(raw_text)
    inside = [re.compile(m) for m in inside_list]
    starter = [re.compile(m) for m in starters_list]
    end = [re.compile(m) for m in end_list]
    
    num_in = 0
    ltext = []
    #TODO: It has to match arbitrary if statements. I think this should be
    # pretty easy
    for txt in splited:
        if txt in (None, ''):
            continue
        if re_in(txt, inside):
            num_in += 1
        elif inside > 0 and re_in(txt, starter):
            # i.e. if you wrote something like /iffalse /ifblog
            num_in += 1
        elif re_in(txt, end):
            # make sure we only count ends if you are removing!
            num_in -= 1
        if num_in == 0:
            ltext.append((True, txt))
        else:
            ltext.append((False, txt))
    return ltext

def check_brackets(match_list, end_list, text):
    '''Checks to make sure all brackets are completed (i.e. \iffalse or \(ifblog) or \iftex
    is completed by an \fi.
    Example input:
    found, gnumbers = check_brackets([r'(\\iffalse)', r'\\(ifblog)', r'\\(iftex)', r'\\(if.*) ', r'\\(fi)'],
                                      text)
    note: only returns the first group number found!
    raises LaTeX_Error on failure

    return match_compile, found, gnumbers
    '''
    match_cmp = re.compile('|'.join(match_list + end_list))
    found = match_cmp.findall(text)
    gnumbers = [textools.group_num(n) for n in found]
    n = 0
    end_num = len(gnumbers) + 1
    for gn in gnumbers:
        if gn < end_num:
            n += 1
        else:
            n -= 1
    if n != 0:
        raise LaTeX_Error("Brackets not matched")
    return match_cmp, found, gnumbers
    
class LatexWp(object):
    def __init__(self, path):
        with open(path) as f:
            self.text = f.read()
        self.get_doc()
    
    def get_doc(self):
        ''' I have to decide the general overview of how these functions work.
        I think I will be constructing the re like:
            ({0})|({1})|... This will let me pull out all the data.
        '''
        pass