# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 03:10:39 2013

@author: user
"""
import pdb
import re
import copy
from cloudtb import textools

CMP_TYPE = type(re.compile(''))

class LatexError(ValueError):
    def __init__(self, msg = '', line = '?'):
        ValueError.__init__(self)
        self.line = line
        self.msg = msg
        
    def __str__(self):
        msg = ("LaTeX LaTeX Error at line "
            "{0}: ").format(self.line) + repr(self.msg)
        return msg

def format_paragraph(text_data):
    pass

def format_font(text_data):
    pass

def format_outside(text_data, add_outside):
    pass

###################################3
## GENERAL FUNCTIONS   
def get_objects_inout(text_objects, inside_list, starters_list, 
                      end_list):
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
    match_cmp = re.compile('|'.join(inside_list + starters_list + end_list))
    
    # split up text for compiling
    splited = []
    for tobj in text_objects:
        if type(tobj) == TexPart:
            splited.append(tobj)
        else:
            splited.extend(match_cmp.split(tobj))
        
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
        elif type(txt) == TexPart:
            pass    # TexParts have been alrady processed.
        elif re_in(txt, inside):
            if num_in == 0:
                set_num = 2
            num_in += 1
        elif num_in > 0 and re_in(txt, starter):
            # i.e. if you wrote something like /iffalse /ifblog
            num_in += 1
        elif num_in > 0 and re_in(txt, end):
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

def reform_text(text_data, is_in = False):
    '''put all text objects that are next to eachother into a 
    single string'''
    all_txt = []
    out = []
    for n, txt in text_data:
        if is_in == False:
            assert(n == 0)  # something wasn't processed!
        else:
            assert(n > 0)
        if type(txt) == TexPart:
            if all_txt:
                out.append(''.join(all_txt))
                out.append(txt)
                all_txt = []
        else:
            all_txt.append(txt)
    if all_txt:
        out.append(''.join(all_txt))
    return out

def process_document(path):
    '''converts the document into a list of recursively generated TextParts
    Each of which has an object called text_data that stores the strings and
    other TextParts that comprise it.
    '''
    with open(path) as f:
        text = f.read()

    # Get the document part
#    text = delete_outside([text], formating.begin_re_dict['document'])
    document_type = formatting.begin_dict['document']
    inout = get_objects_inout([text], *document_type.match_re)
    document = convert_inout(inout, document_type, return_first = True)
    # The major call of this function: does all the processing recursively
    return document

def print_tex_tree(texpart, tabs = 0):
    tform = ' '*(2*tabs) + '- {0}'
    if type(texpart) == str:
        print tform.format('base string len: ' + str(len(texpart)))
    else:
        print tform.format(texpart.label),
        print  ' ||start:{0} |end:{1}'.format(repr(texpart.start), 
                                              repr(texpart.end))
        tabs += 1
        for tp in texpart.text_data:
            print_tex_tree(tp, tabs)

def convert_inout(inout, texpart_constructor, return_first = False):
    if len(inout) == 1:
        assert(inout[0][0] == False)
        return inout[0][1]
    
    def convert_processed(start, body, end):
        assert(start[0] == 2 and end[0] == 3)
        body = reform_text(body, is_in = True)
        tp = copy.copy( texpart_constructor)
        tp.init_text((start[1], body, end[1]))
        print 'Converting', start
        return tp
    
    def get_processed(was_in, processing):
        if was_in > 0:  # object
            converted = convert_processed(processing[0],
                    processing[1:-1], processing[-1])
            return [converted]
        else:
            return reform_text(processing)
    
    text = []
    was_in = None
    processing = []
    # goes through text list and organizes things by whether they are
    # in or out. Then converts them to the specified constructor
    for i, item in enumerate(inout):
        indicator, ti = item
        is_in = bool(indicator)
        
        if was_in == None:
            was_in = is_in
        
        if was_in == is_in:
            processing.append(item)
        else:
            data = get_processed(was_in, processing)
            text.extend(data)
            processing = [item]
            if was_in and return_first:
                return data[0]
        was_in = is_in
    
    if processing:
        data = get_processed(was_in, processing)
        text.extend(data)
        if was_in and return_first:
            return data[0]
    
    return text


#TODO: Need begins for colors and tables
class TexPart(object):
    r'''this class is a text object, normally preceeded by either a begin
    statement or a single line (i.e. \header) and ended by an end statement
    or a \n
    '''
    def __init__(self, label = None, add_outside = None, 
                 no_update_text = None, format_call = None,
                 call_first = None, call_last = None,
                 no_std_format = None, no_final_subs = None,
                 no_paragraphs = False, no_outer_pgraphs = None):
        '''
        add_outside = this is the outside characters that will be added
            during the format call (front, back)
        no_update_text - update_text will not be called on this module once
            it is discovered (it cannot contain ANY internal TexPart objects)
        call_first - call this function before any processing
        call_last - call this function after all processing
        format_call - call this function instead of format
        no_std_format = std_format won't be called during format. Will
            still be called on internal data.
        no_final_subs - final substitutions (i.e. \$ -> $) won't be made.
            will still be called on internal data
        no_paragraphs - override std format and don't use paragraphs. Useful
            for things like lists.
        '''
        self.label = label      # convinience, mostly for debugging
        self.add_outside = add_outside
        self.no_update_text = no_update_text
        self.no_std_format = no_std_format
        self.format_call = format_call
        self.call_first = call_first
        self.call_last = call_last
        self.no_final_subs = no_final_subs
        self.no_paragraphs = no_paragraphs
        self.no_outer_pgraphs = no_outer_pgrahs
        
        self.match_re = None
        self.is_done = False
    
    def update_match_re(self, match_re):
        self.match_re = match_re
        self.cmp_inside, self.cmp_starters, self.cmp_end = (
            [[re.compile(n) for n in c] for c in self.match_re])
        
    def add_text(self, text_block):
        '''
        This function does most of the work of converting the document into
        objects.
            Each call calls all regular expression blocks of the dictionaries
            in formatting and converts them to the respected TexPart object
        '''
        self.start, self.text_data, self.end = text_block

        if self.call_first: self.call_first(self)
        
        if not self.no_update_text:
            self.init_text(self.text_data)
        
        if not self.no_std_format:
            self.std_format()
        
        if self.call_last: self.call_last(self)
        self.text_data = text_data
    
    def init_text(self, text_data):
        every_dict = formatting.every_dict_formatting
        for key, texpart in every_dict.iteritems():
            inout = get_objects_inout(text_data, *texpart.match_re)
            text_data = convert_inout(inout, texpart)
        self.text_data = text_data
                
    def insert_tex(self, index, data):
        return self.text_data.insert(index, data)
    
    def append_tex(self, data):
        return self.text_data.append(data)
    
    def get_wp_text(self):
        pass
        
    def std_format(self):
        ''' performs standard formating.
        Currently:
            - converts double line spaces to paragraph boundaries.
                - Note: if std_format is set then paragraph boundaries
                    are automatically added to the outside of the item.
                    To disable all paragraph boundaries, use 
            - makes sure all spaces are only single spaces
        '''
        fmat = formatting
        one_space = re.compile('( {2,})')
        paragraphs = re.compile('(\n{2,})')

        final_subs_re = re.compile('|'.join(final_subs_str))
        replace_dict = d
        subfun = textools.subfun(replace_dict = fmat.final_subs)
        
        subs_dict = fmat.concatenate_dicts(fmat.final_subs,
                    )
        # Strip all dangling new-lines and spaces.
        for i, tp in enumerate(self.text_data):
            if tp != type(str):
                continue
            tp = tp.strip()
            if not self.no_paragraphs:
                tp = paragraphs.sub(''.join(fmat.PARAGRAPH), tp)
            if not self.no_outer_pgraphs:
                tp = ''.join([fmat.PARAGRAPH[0], 
                              tp,
                              fmat.PARAGRAPH[1]])
            if not self.no_final_subs:
                tp = final_subs_re.sub(subfun, tp)
                
        
        
        

import formatting

if __name__ == '__main__':
    import wordTeX
    wordTeX.main()