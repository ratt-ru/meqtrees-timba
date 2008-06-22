# file: ../JEN/demo/EasyNode.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for dealing with nodes (stubs, names, etc)
#
# History:
#   - 22 june 2008: creation (from EasyTwig.py)
#
# Remarks:
#
# Description:
#


 
#********************************************************************************
# Initialisation:
#********************************************************************************

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

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100

import copy




#====================================================================================
# Functions for (unique) nodename/stub generation:
#====================================================================================

def nodename (ns, rootname, quals=None, kwquals=None, trace=False):
    """
    Helper function that forms a nodename from the given rootname and
    list (*) and keyword (**) qualifiers.
    """
    stub = nodestub (ns, rootname, quals=quals, kwquals=kwquals,
                     trace=trace)
    return stub.name

#-------------------------------------------------------------------------

def unique_name (ns, rootname, quals=None, kwquals=None, trace=False):
    """
    Helper function that forms a unique nodename from the given rootname and
    list (*) and keyword (**) qualifiers.
    """
    stub = unique_stub (ns, rootname, quals=quals, kwquals=kwquals,
                        trace=trace)
    return stub.name

#-------------------------------------------------------------------------

def unique_stub (ns, rootname, quals=None, kwquals=None, trace=False):
    """Helper function that forms a unique (i.e. uninitialized) nodestub
    from the given information.
    NB: Checking whether the proposed node has already been initialized
    in the given nodescope (ns) may be not an entirely safe method,
    when using unqualified nodes....
    """
    # First make a nodestub:
    stub = nodestub(ns, rootname, quals=quals, kwquals=kwquals,
                    trace=trace)

    # Decode the uniquifying parameter (see below):
    ss = rootname.split('|')
    n = 0
    nameroot = rootname
    if len(ss)==3:                       # assume: <nameroot>|<n>|
        n = int(ss[1])
        nameroot = ss[0]

    # Safety valve:
    if n>100:
        print s1
        raise ValueError,'** max of uniqueness parameter exceeded'

    # Testing:
    if False:
        if n<3:
            stub << n               
        s = (n*'--')+' initialized: '
        s += ' '+str(stub.initialized())            # the correct way
        s += ' '+str(ns[stub].initialized())        # .....?
        s += ' '+str(ns[stub.name].initialized())   # .....
        print s

    # Check whether the node already exists (i.e. initialized...):
    if stub.initialized():
        # Recursive: Try again with a modified rootname.
        # (using the incremented uniquifying parameter n)
        newname = nameroot+'|'+str(n+1)+'|'
        return unique_stub(ns, newname, quals=quals, kwquals=kwquals,
                           trace=trace)

    # Return the unique (!) nodestub:
    return stub

#-------------------------------------------------------------------------

def nodestub (ns, rootname, quals=None, kwquals=None, trace=False):
    """
    Helper function that forms a nodestub from the given rootname and
    any qualifiers quals(list or value) and/or kwquals(dict).
    """
    stub = ns[rootname]

    # Un-named qualifiers:
    if quals==None:
        pass
    elif isinstance(quals,(list,tuple)):
        if len(quals)>0:
            stub = stub(*quals)
    else:
        stub = stub(*[quals])

    # Keyword qualifiers:
    if isinstance(kwquals, dict):
        if len(kwquals)>0:
            stub = stub(**kwquals)

    if trace:
        s = '\n** EasyNode.nodestub('+str(rootname)+','+str(quals)+','+str(kwquals)+')'
        s += ' -> '+str(stub)
        # s += ' (initialized='+str(stub.initialized())+')'
        print s
    return stub




#====================================================================================
#====================================================================================

def format_tree (node, ss=None, level=0, recurse=True, mode='str', trace=False):
    """Helper function (recursive) to attach the subtree under the given node(s)
    to the given string (ss). If mode='list', return a list of strings (lines).
    The recursion depth is controlled by the 'recurse argument:
    - recurse=False or <=0: return '' or [] (if mode='list')
    - recurse=True is equivalent to recurse=1000 (i.e. deep enough for any subtree)
    The input node may be either a single node, or a list of nodes. The latter is
    used by MeqNode(), where the top node is shown in detail, and this function
    is used only to expand the subtrees of its children in somewhat less detail.
    """
    
    if isinstance(recurse,bool):
        if recurse: recurse=1000                            # True
    if not recurse:                                         # not required
        if mode=='list': return [] 
        return '' 

    prefix = '\n'+(level*' |  ')+' '
    if trace:
        print prefix+str(node),node
        # print dir(node)

    if level==0:
        if not isinstance(ss,str): ss = ''
        if isinstance(node,list):
            # Special case (see MeqNode()): Start with a list of children:
            ss += prefix+'Its subtree, starting with its '+str(len(node))+' children:'
            for c in node:
                ss = format_tree(c, ss, level=level+1, recurse=recurse, trace=trace)
        elif not is_node(node):                
            return '** not a node (??) **'                  # error
        else:
            ss += prefix+str(node)
    else:
        ss += prefix+str(node)
        if getattr(node,'initrec',None):
            initrec = node.initrec()
            v = getattr(initrec,'value',None)
            if isinstance(v,(int,float,complex)):
                ss += '   (value='+str(v)+')'

    # Do its children (recursively), if required:
    if getattr(node, 'children', None):
        if level<recurse:               # only to the specified recursion depth
            for c in node.children:
                ss = format_tree(c[1], ss, level=level+1, recurse=recurse, trace=trace)
        else:
            ss += prefix+'   .....'     # indicate that the subtree is deeper

    # Finished:
    if level==0:
        ss += '\n'
        if mode=='list':
            ss = ss.split('\n')
    return ss


#====================================================================================
# Functions dealing with finding nodes in a tree:
#====================================================================================

def find_parms (tree, trace=False):
    """Get a list of all the MeqParm nodes in the given tree"""
    return find_nodes (tree, meqtype='MeqParm', trace=trace)


def find_nodes (tree, meqtype='MeqParm', level=0, trace=False):
    """Get a list of nodes of the specified type from the given tree.
    """
    prefix = level*'..'
    if level==0:
        if trace:
            s1 = '** .find_nodes('+str(tree)+','+meqtype+'):'
    nn = []
    if getattr(tree,'children', None):
        for child in tree.children:
            c1 = child[1]
            if c1.classname==meqtype:
                nn.append(c1)
            nn.extend(find_nodes(c1, meqtype=meqtype, level=level+1, trace=trace))
    if level==0:
        if trace:
            print prefix,s1,'found',len(nn),'nodes'
            for i,n in enumerate(nn):
                print '   -',i,':',str(n)
            print
    return nn
    

#-----------------------------------------------------------------------------------

#====================================================================================
# Helper fuctions:
#====================================================================================

def unique_list (ss, trace=False):
    """Helper function to remove doubles from the given list (ss)
    """
    if trace:
        print '\n** unique_list(',ss,'):'
    if isinstance(ss, list):
        ss.reverse()
        for item in copy.copy(ss):
            if trace: print '-',item,':',
            while ss.count(item)>1:
                ss.remove(item)
                if trace: print ss,
            if trace: print
        ss.reverse()
    if trace:
        print '   ->',ss
    return ss



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: EasyNode.py:\n' 
   ns = NodeScope()

   if 0:
       nodestub(ns, 'xxx', trace=True)
       nodestub(ns, 'xxx', quals=range(3), trace=True)
       nodestub(ns, 'xxx', quals=3, trace=True)
       nodestub(ns, 'xxx', kwquals=dict(a=3), trace=True)
       nodestub(ns, 'xxx', quals=4, kwquals=dict(a=3), trace=True)
       # Empty:
       nodestub(ns, 'xxx', quals=4, kwquals=dict(), trace=True)
       nodestub(ns, 'xxx', quals=[], kwquals=dict(), trace=True)
       nodestub(ns, 'xxx', quals=(3,4,5), kwquals=dict(), trace=True)
       # Errors?
       nodestub(ns, 'xxx', kwquals=15, trace=True)
       nodestub(ns, 'xxx', quals=dict(a=5), trace=True)

   #------------------------------------------------

   if 1:
       quals = [5,-7]
       kwquals = dict(c=8, h=9)
       stub = nodestub(ns,'xxx', quals, kwquals, trace=True)
       stub << 5.6
       stub = unique_stub(ns,'xxx', quals, kwquals, trace=True)
       if 1:
           if 1:
               print '\n dir(stub):',dir(stub),'\n'
           print '- stub.name:',stub.name
           print '- stub.basename:',stub.basename
           print '- stub.classname:',stub.classname
           print '- stub.quals:',stub.quals
           print '- stub.kwquals:',stub.kwquals
           print '- stub.initialized():',stub.initialized()
       if 1:
           node = stub << 3.4
           print '\n node = stub << 3.4   ->',str(node),type(node)
           if 1:
               print '\n dir(node):',dir(node),'\n'
           print '- node.name:',node.name
           print '- node.basename:',node.basename
           print '- node.classname:',node.classname
           print '- node.quals:',node.quals
           print '- node.kwquals:',node.kwquals
           print '- node.initialized():',node.initialized()

       if 1:
           print
           print '.nodename() ->',nodename(ns,'xxx', quals, kwquals)
           print '.unique_name() ->',unique_name(ns,'xxx', quals, kwquals)



   if 0:
       ss = range(4)
       ss.extend([1,'a'])
       ss.extend([1,1,3,7,'a',2,2,2])
       print unique_list(ss, trace=True)
       print 'ss (after) =',ss

   print '\n** End of standalone test of: EasyNode.py:\n' 

#=====================================================================================



