# file: ../Grunt/display_subtree.py

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from copy import deepcopy

#=======================================================================

def subtree (node, txt=None, level=1,
             done=None, skip_duplicate=True,
             skip_line_before=True,
             skip_line_after=True,
             show_initrec=True, recurse=1000):
    """Helper function to display a subtree (under node) recursively"""


    if level==1:
        if skip_duplicate: done = dict()
        if skip_line_before: print
    prefix = '  '
    if txt==None: txt = node.name               #........?
    if txt: prefix += ' ('+str(txt)+')'
    prefix += level*'..'
    s = prefix
    s += ' '+str(node.classname)+' '+str(node.name)

    if skip_duplicate:
        if done.has_key(node.name):
            done[node.name] += 1
            print s,'        ... ('+str(done[node.name])+') see above ... '
            return True

    if show_initrec:
        initrec = deepcopy(node.initrec())
        # if len(initrec.keys()) > 1:
        hide = ['name','class','defined_at','children','stepchildren','step_children']
        for field in hide:
            if initrec.has_key(field): initrec.__delitem__(field)
            if initrec.has_key('value'):
                value = initrec.value
                # if isinstance(value,(list,tuple)):
                #     initrec.value = value.flat
            if initrec.has_key('default_funklet'):
                coeff = initrec.default_funklet.coeff
                initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
        if len(initrec)>0: s += ' '+str(initrec)
    print s

    if skip_duplicate:
        done.setdefault(node.name, 0)
        done[node.name] += 1

    if recurse>0:
        if node.initialized():
            for child in node.children:
                subtree (child[1], txt=txt, level=level+1, done=done,
                         show_initrec=show_initrec, recurse=recurse-1)
    if level==1:
        if skip_line_after: print
    return True


    
#=======================================================================
