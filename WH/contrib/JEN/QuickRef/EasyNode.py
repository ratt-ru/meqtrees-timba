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
# Functions for (unique) node/stub generation:
#====================================================================================

def unique_stub (ns, rootname, *quals, **kwquals):
    """
    Syntax:
    .    stub = EeasyNode.unique_stub (ns, rootname, *quals, **kwquals)
    Return a unique (i.e. uninitialized) nodestub with the speciified
    rootname and qualifiers. If one already exists, modify the rootname
    (or the qualifiers?) until the resulting stub-name does not exist yet.
    
    NB: Checking whether the proposed node has already been initialized
    in the given nodescope (ns) may be not an entirely safe method,
    when using unqualified nodes....
    """
    
    # First make a nodestub:
    stub = nodestub(ns, rootname, *quals, **kwquals)

    # Decode the uniquifying parameter from the rootname (see below):
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

    # Check whether the node already exists (i.e. initialized...):
    if stub.initialized():
        # Recursive: Try again with a modified rootname.
        # (using the incremented uniquifying parameter n)
        newname = nameroot+'|'+str(n+1)+'|'
        return unique_stub(ns, newname, *quals, **kwquals)

    # Return the unique (!) nodestub:
    return stub

#-------------------------------------------------------------------------

def unique_node (ns, rootname, assign, *quals, **kwquals):
    """
    Syntax:
    .    node = EeasyNode.unique_node (ns, rootname, assign, *quals, **kwquals)
    Return a unique node with the specified rootname and qualifiers,
    and assigned (<<) with the specified NodeDef object (assign).
    If one already exists, modify the rootname (or the qualifiers?)
    until the resulting stub does not exist yet.
    """
    stub = unique_stub (ns, rootname, *quals, **kwquals)
    node = stub << assign             
    return node

#-------------------------------------------------------------------------

def check_quals(quals=None, kwquals=None, *args, **kwargs):
    """
    Syntax:
    .     [quals, kwquals] = EasyNode.check_quals(quals[=None], kwquals[=None], *args, **kwargs)
    Helper function to make sure that quals is a list, and kwquals is a dict.
    This is used in functions that have arguments quals=None, kwquals=None,
    but which call functions like reusenode(..., *quals, **kwquals).
    - Any extra keyword arguments are added to kwquals (via **kwargs)
    .   (NB: If trace=True, the a progress message is printed,
    .        but there will be no keyword named 'trace' in kwquals)
    - Extra quals can be appended via args. In this case, both quals and
    .   kwquals must be specified (without =), e.g. check_quals([quals], None, 2,3,4)
    """

    s = '** EasyNode.check_quals('+str(quals)+','+str(kwquals)+','+str(args)+','+str(kwargs)+'):'

    # Unnamed qualifiers (quals and args):
    if not isinstance(quals,(list,tuple)):
        if quals==None:
            quals = []
        else:
            quals = [quals]

    if len(args)>0:
        quals.extend(args)

    # Keyword qualifiers (kwquals and kwargs):
    if not isinstance(kwquals,dict):
        kwquals = dict()

    trace = False
    if kwargs.has_key('trace'):
        trace = kwargs['trace']
        kwargs.__delitem__('trace')
    
    if len(kwargs)>0:
        kwquals.update(kwargs)

    # Finished:
    result = [quals, kwquals]
    if trace:
        print s,'  ->',result
    return result

#-------------------------------------------------------------------------

def nodestub (ns, rootname, *quals, **kwquals):
    """
    Syntax:
    .    stub = EeasyNode.nodestub (ns, rootname, *quals, **kwquals)
    Return a nodestub with the given rootname and any qualifiers.
    """
    s = '\n** EasyNode.nodestub('+str(rootname)+','+str(quals)+','+str(kwquals)+')'
    stub = ns[rootname]
    
    if not isinstance(kwquals,dict):
        kwquals = dict()

    # quals may also be specified as quals=[...]
    if kwquals.has_key('quals'):
        if not kwquals['quals']==None:
            quals = kwquals['quals']
            if not isinstance(quals,(list,tuple)):
                quals = [quals]
        kwquals.__delitem__('quals')

    # Look for a specific keword argument(s):
    trace = True
    trace = False
    if kwquals.has_key('trace'):
        trace = kwquals['trace']
        kwquals.__delitem__('trace')

    # kwquals may also be specified as kwquals=dict()
    # Do this one last (modifies kwquals):
    if kwquals.has_key('kwquals'):
        kwquals = kwquals['kwquals']
        if not isinstance(kwquals,dict):
            kwquals = dict()
    
    # Attach the list of un-named qualifiers (quals):
    if len(quals)>0:
        stub = stub(*quals)

    # Attach the dict of keyword qualifiers:
    # print '-',rootname,': kwquals=',kwquals,len(kwquals)
    if len(kwquals)>0:
        stub = stub(**kwquals)

    # Finished:
    if trace:
        s += ' -> '+str(stub)
        print s
    return stub

#-----------------------------------------------------------------------------------

def reusenode (ns, rootname, assign, *quals, **kwquals):
    """
    Syntax:
    .    node = EeasyNode.reusenode (ns, rootname, assign, *quals, **kwquals)
    Return a node with the specified rootname and qualifiers, assigned
    (i.e. initialized(), <<) with the specified NodeDef object.
    If one already exists in the given nodescope (ns), re-use it.
    Otherwise, create a new one, with a slightly modified rootname.
    """
    trace = False
    s = '\n** reusenode('+str(rootname)+','+str(assign)+','+str(quals)+','+str(kwquals)+'): '
    
    stub = nodestub(ns, rootname, *quals, **kwquals)
    if stub.initialized():                       # node exists (initialized) already
        reused = True
        node = stub                              # re-use it
        # NB: Should we check whether 'assign' is consistent with the existing node? 
        
    else:
        # NB: if assign is a constant, a Meq.Constant is generated, etc
        reused = False
        node = stub << assign                    # create a new one

    if trace:
        print s,'->',str(node),' (re-used=',reused,')'
    return node



#====================================================================================
# Format a multi-line string that that shows the subtree under node,
# to the specified depth.
#====================================================================================

def format_tree (node, ss='', recurse=True,
                 level=0, mode='str',
                 nodenames=None, basenames=None, 
                 trace=False):
    """
    Recursively format the subtree under the given node(s) to the given string (ss).
    If mode='list', return a list of strings (lines).
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

    finished = False
    if level==0:
        nodenames = []
        basenames = dict()
        if isinstance(node,list):
            # Special case (see MeqNode()): Start with a list of children:
            ss += prefix+'Its subtree, starting with its '+str(len(node))+' children:'
            for c in node:
                ss = format_tree(c, ss=ss, recurse=recurse, 
                                 nodenames=nodenames, basenames=basenames,
                                 level=level+1, trace=trace)
            finished = True
        elif not is_node(node):
            s = '** not a node (??) **'         
            raise ValueError,s

    if not finished:
        ss += prefix+str(node)
        if getattr(node,'initrec',None):
            initrec = node.initrec()
            v = getattr(initrec,'value',None)
            if isinstance(v,(int,float,complex)):
                ss += '   (value='+str(v)+')'

        # Some clutter-avoiding:
        slevel = str(level)
        basenames.setdefault(slevel,[])
        stophere = False
        s1 = ''

        # Stop if a similar node (same basename, same level):
        if node.basename in basenames[slevel]:
            stophere = True
            s1 = '... similar to earlier nodes at this level with basename: '+node.basename
        else:
            basenames[slevel].append(node.basename)

        # Stop if this node has already been shown (same node-name):
        if node.name in nodenames:
            stophere = True
            s1 = '... this node/subtree has already been shown above'
        else:
            nodenames.append(node.name)
            
        # Do its children (recursively), if required:
        if getattr(node, 'children', None):
            if stophere:                                 # stop here (see above)
                ss += '       '+s1
            elif level>=recurse:                         # only to the specified recursion depth
                ss += prefix+'   .....'                  # indicate that the subtree is deeper
            else:
                for c in node.children:
                    ss = format_tree(c[1], ss=ss, recurse=recurse, 
                                     nodenames=nodenames, basenames=basenames,
                                     level=level+1, trace=trace)

    # Finished:
    if level==0:
        ss += '\n'
        if mode=='list':                # option: return a list of strings
            ss = ss.split('\n')         # (split on '\n')
    return ss



#============================================================================
# Function to format a (short) string that represent a value:
#============================================================================

def format_value(v, name=None, trace=False):
    """
    Format a string that summarizes the given value (v).
    If v is a node, use its initrec.value field, if any.
    If a name is specified, prepend it.
    """
    if is_node(v):
        ss = '(node)'
        if getattr(v,'initrec',None):
            initrec = v.initrec()
            v1 = getattr(initrec,'value',None)
            if not v1==None:
                ss = format_value(v1)
    elif isinstance(v,(complex)):
        s1 = format_float(v.real)
        s2 = format_float(v.imag)
        ss = '('+s1+'+'+s2+'j)'
    elif isinstance(v,(int)):
        ss = str(v)
    elif isinstance(v,(float)):
        ss = format_float(v)
    elif isinstance(v,(list,tuple)):
        import pylab                        # must be done here, not above....
        vv = pylab.array(v)
        ss = '[length='+str(len(vv))
        ss += format_float(vv.min(),'  min')
        ss += format_float(vv.max(),'  max')
        ss += format_float(vv.mean(),'  mean')
        if len(vv)>1:                       
            if not isinstance(vv[0],complex):
                ss += format_float(vv.std(),'  stddev')
        ss += ']'
    else:
        ss = str(v)

    if isinstance(name,str):
        ss = name+'='+ss

    if trace:
        print '** format_value(',type(v),name,') ->',ss
    return ss

#-----------------------------------------------------------------------

def format_float(v, name=None):
    q = 100.0
    v1 = int(v*q)/q
    ss = str(v1)
    if isinstance(name,str):
        ss = name+'='+ss
    return ss


#====================================================================================
# Functions dealing with finding nodes in a tree:
#====================================================================================

def find_parms (tree, recurse=True, trace=False):
    """
    Get a list of all the MeqParm nodes in the given tree
    """
    return find_nodes (tree, meqtype='MeqParm', recurse=recurse, trace=trace)


def find_nodes (tree, meqtype='MeqParm', level=0, recurse=True, trace=False):
    """
    Get a list of nodes of the specified type from the given tree.
    """
    prefix = level*'..'
    if level==0:
        if isinstance(recurse,bool):
            if not recurse: recurse=0
            if recurse: recurse=1000
        if trace:
            s1 = '** .find_nodes('+str(tree)+','+meqtype+'):'

    # Collect the nodes in nn:
    nn = []
    if level<=recurse and getattr(tree,'children', None):
        for child in tree.children:
            c1 = child[1]
            if c1.classname==meqtype:
                nn.append(c1)
            nn.extend(find_nodes(c1, meqtype=meqtype, level=level+1,
                                 recurse=recurse, trace=trace))

    if level==0:
        if trace:
            print prefix,s1,'found',len(nn),'nodes'
            for i,n in enumerate(nn):
                print '   -',i,':',str(n)
            print

    # Return the list of found nodes:
    return nn
    


#====================================================================================
# Some misc helper fuctions:
#====================================================================================

def unique_list (ss, trace=False):
    """
    Helper function to remove doubles from the given list (ss)
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
       nodestub(ns, 'xxx', 1,2,3, trace=True)
       nodestub(ns, 'xxx', quals=range(3), trace=True)
       nodestub(ns, 'xxx', quals=3, a=4, b=5, trace=True)
       nodestub(ns, 'xxx', kwquals=dict(a=3), trace=True)
       nodestub(ns, 'xxx', quals=4, kwquals=dict(a=3), trace=True)
       if 0:
           # Empty:
           nodestub(ns, 'xxx', quals=4, kwquals=dict(), trace=True)
           nodestub(ns, 'xxx', quals=[], kwquals=dict(), trace=True)
           nodestub(ns, 'xxx', quals=(3,4,5), kwquals=dict(), trace=True)
       if 0:
           # Problems and Errors
           nodestub(ns, 'xxx', range(3), trace=True)     
           # nodestub(ns, 'xxx', *range(3), trace=True)      # syntax error
           nodestub(ns, 'xxx', kwquals=15, trace=True)
           nodestub(ns, 'xxx', quals=dict(a=5), trace=True)

   if 0:
       reusenode(ns, 'xxx', assign=Meq.Constant(1.2))
       reusenode(ns, 'xxx', assign=Meq.Constant(2.2))
       reusenode(ns, 'xxx', assign=Meq.Parm(1.2))
       reusenode(ns, 'xxx', assign=Meq.Parm(1.2))
       if 0:
           # NB: This does NOT produce an error.
           # In a _define_forest() the double MeqParm does....
           # But not the constant, as long as the value is the same...
           print ns.xxxx << Meq.Constant(1.2)
           print ns.xxxx << Meq.Parm(1.2)
           print ns.xxxx << Meq.Parm(1.2)
           print ns.xxxx ** Meq.Parm(1.2)
           ns.resolve()

   if 0:
       reusenode(ns, 'xxx', assign=Meq.Constant(1.2))
       c1 = Meq.Constant(1.2)
       c2 = Meq.Constant(2.3)
       reusenode(ns, 'yyy', assign=(c1+c2))
       reusenode(ns, 'zzz', assign=5.6)

   if 1:
       check_quals(3, trace=True)
       check_quals(range(3), trace=True)
       check_quals(range(3), aa=3, trace=True)
       print check_quals(range(3), dict(a=3), **dict(b=4))
       check_quals(range(3), None, 6, aa=3, trace=True)

   #------------------------------------------------

   if 0:
       quals = [5,-7]
       kwquals = dict(c=8, h=9)
       stub = nodestub(ns,'xxx', quals=quals, kwquals=kwquals, trace=True)
       stub = unique_stub(ns,'xxx', quals=quals, kwquals=kwquals, trace=True)
       stub << 5.6
       stub = unique_stub(ns,'xxx', quals=quals, kwquals=kwquals, trace=True)
       if 1:
           if 1:
               print '\n dir(stub):',dir(stub),'\n'
           print '- stub.name:',stub.name
           print '- stub.basename:',stub.basename
           print '- stub.classname:',stub.classname
           print '- stub.quals:',stub.quals
           print '- stub.kwquals:',stub.kwquals
           print '- stub.initialized():',stub.initialized()
       if 0:
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

   #----------------------------------------------------------------

   if 0:
       c1 = ns << Meq.Constant(1.3)
       c2 = ns << Meq.Constant(2.3)
       c3 = ns << Meq.Constant(3.3)
       node1 = ns.sum(1) << Meq.Add(c1,c2,c3)
       node2 = ns.sum(2) << Meq.Add(c1,c2,node1)
       node = ns.sum(3) << Meq.Add(c1,node1,node2)
       print format_tree(node, 'test', recurse=2)
       if 1:
           print format_tree([c1,c2,c3], recurse=2)
           
   
   if 0:
       format_value(3, 'int', trace=True)
       format_value(3.4, 'float', trace=True)
       format_value(complex(3,4), 'complex', trace=True)
       format_value(range(100), 'list', trace=True)
       format_value(ns << Meq.Constant(4.5), 'node', trace=True)

   if 0:
       ss = range(4)
       ss.extend([1,'a'])
       ss.extend([1,1,3,7,'a',2,2,2])
       print unique_list(ss, trace=True)
       print 'ss (after) =',ss

   print '\n** End of standalone test of: EasyNode.py:\n' 

#=====================================================================================



