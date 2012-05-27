# =============================================================================
# lib/utils.py
#
# Copyright (c) 2009 Frank Smit (FSX)
# License: GPL v3, see the COPYING file for details
#
# Modified 5/21/2012 by Spencer Julian
# =============================================================================
  
import os
import sys
import cPickle
from pickletools import genops
import re
import webbrowser
import subprocess
  
REGEX_HTML_TAG = re.compile(r'<[^<]*?/?>')
  
def open_url(url):
    """Opens the webbrowser and goes to the given url."""
  
    if sys.platform in ('linux', 'linux2'):
        subprocess.call(['xdg-open', url])
    else:
        webbrowser.open(url)
  
# http://code.activestate.com/recipes/545418/
# The filesize of a file goes from ~49.8KB to ~42.2KB
def optimize_pickle(p):
    """Optimize a pickle string by removing unused PUT opcodes."""
  
    gets = set()      # set of args used by a GET opcode
    puts = []         # (arg, startpos, stoppos) for the PUT opcodes
    prevpos = None    # set to pos if previous opcode was a PUT
  
    for opcode, arg, pos in genops(p):
        if prevpos is not None:
            puts.append((prevarg, prevpos, pos))
            prevpos = None
        if 'PUT' in opcode.name:
            prevarg, prevpos = arg, pos
        elif 'GET' in opcode.name:
            gets.add(arg)
  
    # Copy the pickle string except for PUTS without a corresponding GET
    s = []
    i = 0
  
    for arg, start, stop in puts:
        j = stop if (arg in gets) else start
        s.append(p[i:j])
        i = stop
  
    s.append(p[i:])
    return ''.join(s)
  
def cache_data(path, data):
    """Pickle data and write if to the disk."""
  
    #with open(path, 'wb') as f:
    #    pickle = optimize_pickle(cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL))
    #    f.write(pickle)
  
    fh = open(path, 'wb')
    pickle = optimize_pickle(cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL))
    fh.write(pickle)
    fh.close()
  
def get_cache(path):
    """Get data from disk and upickle it."""
  
    #with open(path, 'rb') as f:
    #    contents = cPickle.load(f)
  
    fh = open(path, 'rb')
    contents = cPickle.load(fh)
    fh.close()
  
    return contents
  
def htmldecode(string):
    """Decode htmlentities."""
  
    return string.replace('&apos;', '\'')
 
# http://love-python.blogspot.com/2008/07/strip-html-tags-using-python.html
def strip_html_tags(string):
    """Strip HTML tags from a string."""
  
    return REGEX_HTML_TAG.sub('', string)
  
