'''
#TODO:
- Indenting is accomplished via <ul> </ul>
- Indexing in lists:
this:
\begin{itemize}
\item A bulleted item.
\item Another bulleted item.
\begin{itemize}
\item A nested bulleted item.
\end{itemize}
\item You get the idea.
\end{itemize}

produces
    * A bulleted item.
    * Another bulleted item.
        - A nested bulleted item.
    * You get the idea.

this:
    \begin{enumerate}
    \item A numbered item.
    \item Another numbered item.
    \begin{enumerate}
    \item A nested numbered item.
    \end{enumerate}
    \item You get the idea.
    \end{enumerate}

creates:
    1. A numbered item.
    2. Another numbered item.
        (a) A nested numbered item.
    3. You get the idea.

- his brackets are totally useless as far as I can tell.
- Creating tables -- it only barely works and it looks crapy. 
    Find something better.
- Formatting code -- The latext:
\begin{lstlisting}
...
...
...
\end{lstlisting}

- And in wordpress
<pre> ...
...
...</pre>
'''

import re
from sys import argv
import os
from cloudtb import dbe, textools

from wordTeXstyle import *

class LaTeX_Error(ValueError):
    def __init__(self, msg = '', line = '?'):
         self.line
         self.msg
    def __str__(self):
        msg = "LaTeX LaTeX Error at line {0}: ".format(line) + repr(msg)
        return msg

# prepare variables computed from the info in latex2wpstyle
count = dict()
for thm in ThmEnvs:
  count[T[thm]] = 0
count["section"] = count["subsection"] = count["equation"] = 0

ref={}

endlatex = "&fg="+textcolor
if HTML: 
    endproof = ("<img src=\"http://l.wordpress.com/latex.php?latex="
                "\Box&fg=000000\">")

inthm = ""

#TODO: This looks like a terrible system, not sure what to do about it yet though
"""
 At the beginning, the commands \$, \% and \& are temporarily
 replaced by placeholders (the second entry in each 4-tuple).
 At the end, The placeholders in text mode are replaced by
 the third entry, and the placeholders in math mode are
 replaced by the fourth entry.
"""

esc = [["\\$","_dollar_","&#36;","\\$"],
       ["\\%","_percent_","&#37;","\\%"],
       ["\\&","_amp_","&amp;","\\&"],
       [">","_greater_",">","&gt;"],
       ["<","_lesser_","<","&lt;"]]

M = M + [ ["\\more","<!--more-->"],
          ["\\newblock","\\\\"],
          ["\\sloppy",""],
          ["\\S","&sect;"]]

Mnomath =[["\\\\","<br/>\n"],
          ["\\ "," "],
          ["\\`a","&agrave;"],
          ["\\'a","&aacute;"],
          ["\\\"a","&auml;"],
          ["\\aa ","&aring;"],
          ["{\\aa}","&aring;"],
          ["\\`e","&egrave;"],
          ["\\'e","&eacute;"],
          ["\\\"e","&euml;"],
          ["\\`i","&igrave;"],
          ["\\'i","&iacute;"],
          ["\\\"i","&iuml;"],
          ["\\`o","&ograve;"],
          ["\\'o","&oacute;"],
          ["\\\"o","&ouml;"],
          ["\\`o","&ograve;"],
          ["\\'o","&oacute;"],
          ["\\\"o","&ouml;"],
          ["\\H o","&ouml;"],
          ["\\`u","&ugrave;"],
          ["\\'u","&uacute;"],
          ["\\\"u","&uuml;"],
          ["\\`u","&ugrave;"],
          ["\\'u","&uacute;"],
          ["\\\"u","&uuml;"],
          ["\\v{C}","&#268;"]]


cb = re.compile("\\{|}")

def check_brackets(match_list, text, line = '?'):
    '''Checks to make sure all brackets are completed (i.e. \iffalse or \(ifblog) or \iftex
    is completed by an \fi.
    Example input:
    found, gnumbers = check_brackets([r'(\\iffalse)', r'\\(ifblog)', r'\\(iftex)', r'\\(if), r'\\(fi)'],
                                      text)
    note: only returns the first group number found!
    raises LaTeX_Error on failure

    return match_compile, found, gnumbers
    '''
    match_cmp = re.compile('|'.join(match_list))
    found = match_cmp.findall(text)
    gnumbers = [textools.group_num(n) for n in found]
    fi = 0
    n = 0
    for gn in gnumbers:
        if gn != len(gnumbers):
            n += 1
        else:
            n -= 1
    if n != 0:
        raise LaTeX_Error("Brackets not matched")

    return match_cmp, found, gnumbers

def extractbody(text):
    """
      extractbody() takes the text between a \begin{document}
      and \end{document}, if present, (otherwise it keeps the
      whole document), normalizes the spacing, and removes comments
    """
    begin = re.compile("\\\\begin\s*")
    text= begin.sub("\\\\begin",text)
    end = re.compile("\\\\end\s*")
    text = end.sub("\\\\end",text)

    beginenddoc = re.compile("\\\\begin\\{document}"
                          "|\\\\end\\{document}")
    parse = beginenddoc.split(text)
    if len(parse) == 1:
       text = parse[0]
    else:
       text = parse[1]

    """
      removes comments, replaces double returns with <p> and
      other returns and multiple spaces by a single space.
    """

    for e in esc:
        text = text.replace(e[0],e[1])

    comments = re.compile("%.*?\n")
    #text = comments.sub(" ",m) # why were we putting spaces in for comments? very odd.
    text = comments.sub('', text)

    multiplereturns = re.compile("\n\n+")
    text= multiplereturns.sub ("<p>",text)
    #TODO: Does latex not let you format with spaces??? This will remove all multiple spaces.
    spaces=re.compile("(\n|[ ])+")
    text=spaces.sub(" ",text)

    #TODO: Almost positive there is a more sane way to do this with re...
    # these have like no error checking
    """
     removes text between \iffalse ... \fi and
     between \iftex ... \fi keeps text between
     \ifblog ... \fi
    """

    # do error checking to make sure all are complemented by an (fi)
    fs = r'\\'    
    keep = fs+'(ifblog)', fs+'(if)',
    remove = fs+'(iffalse)', fs+'(iftex)',
    end = fs+'(fi)',
    match_list = keep + remove + end
    match_cmp = check_brackets(match_list, text)[0]
    match_set = set(match_list)

    r = 0
    ltext = []
    #TODO: It has to match arbitrary if statements. I think this should be
    # pretty easy
    for tx in match_cmp.split(text):
        if tx in (None, ''):
            continue
        if tx in remove:
            r += 1
        if remove > 0 and tx in keep:
            # i.e. if you wrote something like /iffalse /ifblog
            r += 1
        if tx in end:
            r -= 1
        if r == 0:
            ltext.append(tx)
    text = ''.join(ltext)
    
    #TODO: This could be done better too
    """
     changes $$ ... $$ into \[ ... \] and reformats
     eqnarray* environments as regular array environments
    """
    doubledollar = re.compile(r"\$\$")
    L=doubledollar.split(text)

    text=L[0]
    for i in range(1,(len(L)+1)/2):
        text = text+ "\\[" + L[2*i-1] + "\\]" + L[2*i]

    text = text.replace(r"\begin{eqnarray*}", r"\[ \begin{array}{rcl} ")
    text = text.replace(r"\end{eqnarray*}",r"\end{array} \]")

    return text

def convertsqb(text):
    r = re.compile("\\\\item\\s*\\[.*?\\]")

    Litems = r.findall(text)
    Lrest = r.split(text)

    text = Lrest[0]
    for i in range(0,len(Litems)):
      s= Litems[i]
      s=s.replace("\\item","\\nitem")
      s=s.replace("[","{")
      s=s.replace("]","}")
      text=text+s+Lrest[i+1]

    r = re.compile("\\\\begin\\s*\\{\\w+}\\s*\\[.*?\\]")
    Lthms = r.findall(text)
    Lrest = r.split(text)

    text = Lrest[0]
    for i in range(0,len(Lthms)):
      s= Lthms[i]
      s=s.replace("\\begin","\\nbegin")
      s=s.replace("[","{")
      s=s.replace("]","}")
      text=text+s+Lrest[i+1]

    return text


def converttables(text):
    '''Converts tables'''
    retable = re.compile("\\\\begin\s*\\{tabular}.*?\\\\end\s*\\{tabular}"
                         "|\\\\begin\s*\\{btabular}.*?\\\\end\s*\\{btabular}")
    tables = retable.findall(text)
    rest = retable.split(text)


    text = rest[0]
    for i in range(len(tables)):
        if tables[i].find("{btabular}") != -1:
            text = text + convertonetable(tables[i],True)
        else:
            text = text + convertonetable(tables[i],False)
        text = text + rest[i+1]


    return text


def convertmacros(text):
    comm = re.compile("\\\\[a-zA-Z]*")
    commands = comm.findall(text)
    rest = comm.split(text)


    r= rest[0]
    for i in range( len (commands) ):
      for s1,s2 in M:
        if s1==commands[i]:
          commands[i] = s2
      r=r+commands[i]+rest[i+1]
    return(r)


def convertonetable(text,border):

    tokens = re.compile("\\\\begin\\{tabular}\s*\\{.*?}"
                        "|\\\\end\\{tabular}"
                        "|\\\\begin\\{btabular}\s*\\{.*?}"
                        "|\\\\end\\{btabular}"
                        "|&|\\\\\\\\")

    align = { "c": "center", "l": "left" , "r": "right" }

    T = tokens.findall(text)
    C = tokens.split(text)


    L = cb.split(T[0])
    format = L[3]

    columns = len(format)
    if border:
        text = "<table border=\"1\" align=center>"
    else:
        text="<table align = center><tr>"
    p=1
    i=0


    while T[p-1] != "\\end{tabular}" and T[p-1] != "\\end{btabular}":
        text = text + "<td align="+align[format[i]]+">" + C[p] + "</td>"
        p=p+1
        i=i+1
        if T[p-1]=="\\\\":
            for i in range (p,columns):
                text=text+"<td></td>"
            text=text+"</tr><tr>"
            i=0
    text = text+ "</tr></table>"
    return (text)

def separatemath(text):
    mathre = re.compile("\\$.*?\\$"
                   "|\\\\begin\\{equation}.*?\\\\end\\{equation}"
                   "|\\\\\\[.*?\\\\\\]")
    math = mathre.findall(text)
    text = mathre.split(text)
    return(math,text)

def processmath( M ):
    R = []
    counteq=0
    global ref

    mathdelim = re.compile("\\$"
                           "|\\\\begin\\{equation}"
                           "|\\\\end\\{equation}"
                           "|\\\\\\[|\\\\\\]")
    label = re.compile("\\\\label\\{.*?}")

    for m in M:
        md = mathdelim.findall(m)
        mb = mathdelim.split(m)

        """
          In what follows, md[0] contains the initial delimiter,
          which is either \begin{equation}, or $, or \[, and
          mb[1] contains the actual mathematical equation
        """

        if md[0] == "$":
            if HTML:
                m=m.replace("$","")
                m=m.replace("+","%2B")
                m=m.replace(" ","+")
                m=m.replace("'","&#39;")
                m="<img src=\"http://l.wordpress.com/latex.php?latex=%7B"+m+"%7D"+endlatex+"\">"
            else:
                m="$latex {"+mb[1]+"}"+endlatex+"$"

        else:
            if md[0].find("\\begin") != -1:
                count["equation"] += 1
                mb[1] = mb[1] + "\\ \\ \\ \\ \\ ("+str(count["equation"])+")"
            if HTML:
                mb[1]=mb[1].replace("+","%2B")
                mb[1]=mb[1].replace("&","%26")
                mb[1]=mb[1].replace(" ","+")
                mb[1]=mb[1].replace("'","&#39;")
                m = "<p align=center><img src=\"http://l.wordpress.com/latex.php?latex=\displaystyle " + mb[1] +endlatex+"\"></p>\n"
            else:
                m = "<p align=center>$latex \displaystyle " + mb[1] +endlatex+"$</p>\n"
            if m.find("\\label") != -1:
                mnolab = label.split(m)
                mlab = label.findall(m)
                """
                 Now the mathematical equation, which has already
                 been formatted for WordPress, is the union of
                 the strings mnolab[0] and mnolab[1]. The content
                 of the \label{...} command is in mlab[0]
                """
                lab = mlab[0]
                lab=cb.split(lab)[1]
                lab=lab.replace(":","")
                ref[lab]=count["equation"]

                m="<a name=\""+lab+"\">"+mnolab[0]+mnolab[1]+"</a>"

        R= R + [m]
    return R

def convertcolors(m,c):
    if m.find("begin") != -1:
        return("<span style=\"color:#"+colors[c]+";\">")
    else:
        return("</span>")

def convertitm(m):
    if m.find("begin") != -1:
        return ("\n\n<ul>")
    else:
        return ("\n</ul>\n\n")

def convertenum(m):
    if m.find("begin") != -1:
        return ("\n\n<ol>")
    else:
        return ("\n</ol>\n\n")

def convertbeginnamedthm(thname,thm):
  global inthm

  count[T[thm]] +=1
  inthm = thm
  t = beginnamedthm.replace("_ThmType_",thm.capitalize())
  t = t.replace("_ThmNumb_",str(count[T[thm]]))
  t = t.replace("_ThmName_",thname)
  return(t)

def convertbeginthm(thm):
  global inthm

  count[T[thm]] +=1
  inthm = thm
  t = beginthm.replace("_ThmType_",thm.capitalize())
  t = t.replace("_ThmNumb_",str(count[T[thm]]))
  return(t)

def convertendthm(thm):
  global inthm

  inthm = ""
  return(endthm)

def convertlab(m):
    global inthm
    global ref
    m=cb.split(m)[1]
    m=m.replace(":","")
    if inthm != "":
        ref[m]=count[T[inthm]]
    else:
        ref[m]=count["section"]
    return("<a name=\""+m+"\"></a>")


def convertproof(m):
    if m.find("begin") != -1:
        return(beginproof)
    else:
        return(endproof)

def convertsection (m):
      L=cb.split(m)

      """
        L[0] contains the \\section or \\section* command, and
        L[1] contains the section name
      """
      if L[0].find("*") == -1:
          t=section
          count["section"] += 1
          count["subsection"]=0
      else:
          t=sectionstar

      t=t.replace("_SecNumb_",str(count["section"]) )
      t=t.replace("_SecName_",L[1])
      return(t)

def convertsubsection (m):
    L=cb.split(m)

    if L[0].find("*") == -1:
        t=subsection
    else:
        t=subsectionstar

    count["subsection"] += 1
    t=t.replace("_SecNumb_",str(count["section"]) )
    t=t.replace("_SubSecNumb_",str(count["subsection"]) )
    t=t.replace("_SecName_",L[1])
    return(t)

def convert_lstlisting(m):
    wpbegin = '<pre>'
    wpend = '</pre>'
    if 'begin' in m:
        return wpbegin
    if 'end' in m:
        return wpend
    assert(0)

def converturl (m):
    L = cb.split(m)
    return ("<a href=\""+L[1]+"\">"+L[3]+"</a>")

def converturlnosnap (m):
    L = cb.split(m)
    return ("<a class=\"snap_noshots\" href=\""+L[1]+"\">"+L[3]+"</a>")


def convertimage (m):
    L = cb.split (m)
    return ("<p align=center><img "+L[1] + " src=\""+L[3]
         +"\"></p>")

def convertstrike (m):
    L=cb.split(m)
    return("<s>"+L[1]+"</s>")

def processtext ( t ):
    p = re.compile("\\\\begin\\{\\w+}"
               "|\\\\nbegin\\{\\w+}\\s*\\{.*?}"
               "|\\\\end\\{\\w+}"
               "|\\\\item"
               "|\\\\nitem\\s*\\{.*?}"
               "|\\\\label\\s*\\{.*?}"
               "|\\\\section\\s*\\{.*?}"
               "|\\\\section\\*\\s*\\{.*?}"
               "|\\\\subsection\\s*\\{.*?}"
               "|\\\\subsection\\*\\s*\\{.*?}"
               "|\\\\href\\s*\\{.*?}\\s*\\{.*?}"
               "|\\\\hrefnosnap\\s*\\{.*?}\\s*\\{.*?}"
               "|\\\\image\\s*\\{.*?}\\s*\\{.*?}\\s*\\{.*?}"
               "|\\\\sout\\s*\\{.*?}")

    for s1, s2 in Mnomath:
        t=t.replace(s1,s2)

    ttext = p.split(t)
    tcontrol = p.findall(t)

    w = ttext[0]

    i=0
    while i < len(tcontrol):
        if tcontrol[i].find("{itemize}") != -1:
            w=w+convertitm(tcontrol[i])
        elif tcontrol[i].find("{enumerate}") != -1:
            w= w+convertenum(tcontrol[i])
        elif tcontrol[i][0:5]=="\\item":
            w=w+"<li>"
        elif tcontrol[i][0:6]=="\\nitem":
                lb = tcontrol[i][7:].replace("{","")
                lb = lb.replace("}","")
                w=w+"<li>"+lb
        elif tcontrol[i].find("\\hrefnosnap") != -1:
            w = w+converturlnosnap(tcontrol[i])
        elif tcontrol[i].find("\\href") != -1:
            w = w+converturl(tcontrol[i])
        elif tcontrol[i].find("{proof}") != -1:
            w = w+convertproof(tcontrol[i])
        elif tcontrol[i].find("\\subsection") != -1:
            w = w+convertsubsection(tcontrol[i])
        elif tcontrol[i].find("\\section") != -1:
            w = w+convertsection(tcontrol[i])
        elif tcontrol[i].find("\\label") != -1:
            w=w+convertlab(tcontrol[i])
        elif tcontrol[i].find("\\image") != -1:
            w = w+convertimage(tcontrol[i])
        elif tcontrol[i].find("\\sout") != -1:
            w = w+convertstrike(tcontrol[i])
        elif re.findall(r"\\begin|end\{lstlisting}", tcontrol[i]):
            pdb.set_trace()
            w = w+convert_lstlisting(tcontrol[i])
        elif tcontrol[i].find("\\begin") !=-1 and tcontrol[i].find("{center}")!= -1:
            w = w+"<p align=center>"
        elif tcontrol[i].find("\\end")!= -1  and tcontrol[i].find("{center}") != -1:
            w = w+"</p>"
        else:
          for clr in colorchoice:
            if tcontrol[i].find("{"+clr+"}") != -1:
                w=w + convertcolors(tcontrol[i],clr)
          for thm in ThmEnvs:
            if tcontrol[i]=="\\end{"+thm+"}":
                w=w+convertendthm(thm)
            elif tcontrol[i]=="\\begin{"+thm+"}":
                w=w+convertbeginthm(thm)
            elif tcontrol[i].find("\\nbegin{"+thm+"}") != -1:
                L=cb.split(tcontrol[i])
                thname=L[3]
                w=w+convertbeginnamedthm(thname,thm)
        w += ttext[i+1]
        i += 1

    return processfontstyle(w)

def processfontstyle(w):

        close = dict()
        ww = ""
        level = i = 0
        while i < len(w):
          special = False
          for k, v in fontstyle.items():
            l = len(k)
            if w[i:i+l] == k:
              level += 1
              ww += '<' + v + '>'
              close[level] = '</' + v + '>'
              i += l
              special = True
          if not special:
            if w[i] == '{':
              ww += '{'
              level += 1
              close[level] = '}'
            elif w[i] == '}' and level > 0:
              ww += close[level]
              level -= 1
            else:
              ww += w[i]
            i += 1
        return ww


def convertref(m):
    global ref

    p=re.compile("\\\\ref\s*\\{.*?}|\\\\eqref\s*\\{.*?}")

    T=p.split(m)
    M=p.findall(m)

    w = T[0]
    for i in range(len(M)):
        t=M[i]
        lab=cb.split(t)[1]
        lab=lab.replace(":","")
        if t.find("\\eqref") != -1:
           w=w+"<a href=\"#"+lab+"\">("+str(ref[lab])+")</a>"
        else:
           w=w+"<a href=\"#"+lab+"\">"+str(ref[lab])+"</a>"
        w=w+T[i+1]
    return w

def is_file_ext(path, ext):
    n, fext = os.path.splitext(path)
#    period_pos = path[::-1].find('.')
#    fext = path[-period_pos:]
    
    fext = fext[1:] if fext else fext   # remove the period
    print fext, ext
    if fext == ext:
        print 'return True'
        return True
    return False

if __name__ == '__main__':
    """
    The program makes several passes through the input.

    In a first clean-up, all text before \begin{document}
    and after \end{document}, if present, is removed,
    all double-returns are converted
    to <p>, and all remaining returns are converted to
    spaces.

    The second step implements a few simple macros. The user can
    add support for more macros if desired by editing the
    convertmacros() procedure.

    Then the program separates the mathematical
    from the text parts. (It assumes that the document does
    not start with a mathematical expression.)

    It makes one pass through the text part, translating
    environments such as theorem, lemma, proof, enumerate, itemize,
    \em, and \bf. Along the way, it keeps counters for the current
    section and subsection and for the current numbered theorem-like
    environment, as well as a  flag that tells whether one is
    inside a theorem-like environment or not. Every time a \label{xx}
    command is encountered, we give ref[xx] the value of the section
    in which the command appears, or the number of the theorem-like
    environment in which it appears (if applicable). Each appearence
    of \label is replace by an html "name" tag, so that later we can
    replace \ref commands by clickable html links.

    The next step is to make a pass through the mathematical environments.
    Displayed equations are numbered and centered, and when a \label{xx}
    command is encountered we give ref[xx] the number of the current
    equation.

    A final pass replaces \ref{xx} commands by the number in ref[xx],
    and a clickable link to the referenced location.
    """
    import pdb
    inputfile = "/home/user/Documents/Website/Blog/Python Memory Management Helpers.tex"
    if len(argv) > 1:
        inputfile = argv[1]
    else:
        inputfile = os.path.join(os.getcwd(), inputfile)

    if len(argv) > 2:
        outputfile = argv[2]
    else:
        if is_file_ext(inputfile, 'tex'):
            outputfile = inputfile[:-4] + ".wp.html"
        else:
            outputfile = inputfile + ".wp.html"

    with open(inputfile) as f:
        s = f.read()

    
    s=extractbody(s)

    # formats tables
    s=converttables(s)

    # reformats optional parameters passed in square brackets
    s=convertsqb(s)

    #implement simple macros
    s=convertmacros(s)

    # extracts the math parts, and replaces the with placeholders
    # processes math and text separately, then puts the processed
    # math equations in place of the placeholders
    (math,text) = separatemath(s)

    s=text[0]
    for i in range(len(math)):
        s=s+"__math"+str(i)+"__"+text[i+1]

    s = processtext( s )
    math = processmath ( math )

    # converts escape sequences such as \$ to HTML codes
    # This must be done after formatting the tables or the '&' in
    # the HTML codes will create problems
    for e in esc:
        s=s.replace(e[1],e[2])
        for i in range ( len ( math ) ):
            math[i] = math[i].replace(e[1],e[3])

    # puts the math equations back into the text
    for i in range(len(math)):
        s=s.replace("__math"+str(i)+"__",math[i])

    # translating the \ref{} commands
    s=convertref(s)

    if HTML:
        s=("<head><style>body{max-width:55em;}a:link{color:#4444aa;}a:visited{color:#4444aa;}a:hover{background-color:#aaaaFF;}</style>"
        "</head><body>"+s+"</body></html>")

    s = s.replace("<p>","\n<p>\n")
    
    with open(outputfile,"w") as f:
        print 'Writing to file:', outputfile
        f.write(s)
