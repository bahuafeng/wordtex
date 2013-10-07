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

from cloudtb import publish

publish.YOUR_LICENSE = """%
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
%"""

if __name__ == '__main__':
    publish.main()