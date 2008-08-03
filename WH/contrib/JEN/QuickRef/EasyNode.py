# file: ../JEN/demo/EasyNode.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for dealing with nodes (stubs, names, etc)
#
# History:
#   - 22 jun 2008: creation (from EasyTwig.py)
#   - 26 jul 2008: implemented .get_quickref_help(node)
#   - 28 jul 2008: moved format_record() etc to EasyFormat.py
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

# from Timba.Meq import meqds
# from Timba.meqkernel import set_state    # no module meqserver_interface

Settings.forest_state.cache_policy = 100

from Timba.Contrib.JEN.QuickRef import EasyFormat as EF
from Timba.Contrib.JEN.QuickRef import QuickRefNodeHelp as QRNH

import copy
import math
import pylab       




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

def append2quals (q, quals=None):
    """
    Helper function that appends the given qualifier (q) to quals.
    """
    if quals==None:
        quals = []
    if isinstance(q,(list,tuple)):
        return quals+q
    else:
        return quals+[q]

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
                 full=False, trace=False):
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
    postfix = ''
    if mode=='html':
        prefix = '\n'+(level*' |......')+' '
        postfix = '<br>'
    
    if trace:
        print prefix+str(node)+postfix,node
        # print dir(node)

    finished = False
    if level==0:
        nodenames = []
        basenames = dict()
        if isinstance(node,list):
            # Special case (see MeqNode()): Start with a list of children:
            ss += prefix+'List of '+str(len(node))+' nodes/subtrees (e.g. children):'+postfix
            for c in node:
                ss = format_tree(c, ss=ss, recurse=recurse, mode=mode,
                                 nodenames=nodenames, basenames=basenames,
                                 full=full, level=level+1, trace=trace)
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
                ss += '   (value='+str(EF.format_value(v))+')'
            tags = getattr(initrec,'tags',None)
            if tags:
                ss += '   (tags='+str(tags)+')'

        # Some clutter-avoiding:
        slevel = str(level)
        basenames.setdefault(slevel,[])
        stophere = False
        s1 = ''

        # Stop if a similar node (same basename, same level):
        if not full:
            if node.basename in basenames[slevel]:
                stophere = True
                s1 = '... {similar to earlier nodes at this level}'
                # with basename: '+node.basename
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
                ss += '       ' + s1
            elif level>=recurse:                         # only to the specified recursion depth
                ss += prefix + '   .....'                # indicate that the subtree is deeper
            else:
                for c in node.children:
                    ss += postfix
                    ss = format_tree(c[1], ss=ss, recurse=recurse, mode=mode,
                                     nodenames=nodenames, basenames=basenames,
                                     full=full, level=level+1, trace=trace)

    # Finished:
    if level==0:
        ss += '\n'
        if mode=='list':                # option: return a list of strings
            ss = ss.split('\n')         # (split on '\n')
    return ss

#----------------------------------------------------------------------------

def node_help (node, rider, new=None, severe=False, trace=False):
    """
    Append the given string as a comment to the node quickref_help.
    This is a low-threshold function, to be used extensively in QR_... modules.
    to add help (including standard node-help) to existing nodes, and to make
    sure that they are added to the hierarchical help in the rider.
    """
    return QRNH.node_help (node, detail=1, rider=rider, comment=new,
                           mode='html', trace=False)

#----------------------------------------------------------------------------

def quickref_help (node, append=None, new=None, prepend=None,
                   severe=False, trace=False):
    """
    Get/set the contents of its quickref_help field, if any.
    """
    qhelp = '** not a node **'
    if is_node(node):
        rr = node.initrec()
        key = 'quickref_help'
        if new:                         # a new quickref_help (string)
            node.initrec()[key] = str(new)
        elif append:                    # append quickref_help (string)
            if rr.has_key(key):
                node.initrec()[key] += str(append)
            else:
                node.initrec()[key] = str(append)
        elif prepend:                   # prepend quickref_help (string)
            if rr.has_key(key):
                node.initrec()[key] = str(prepend) + str(node.initrec()[key])
            else:
                node.initrec()[key] = str(prepend)
        qhelp = getattr(rr,key,'** no quickref_help available **')
    elif severe:
        raise ValueError,qhelp
    if trace:
        print '** EN.quickref_help(',str(node),', new=',type(new),') ->',qhelp
    return qhelp


#----------------------------------------------------------------------------

def format_node (node, cut=False, cmax=80, trace=False):
    """
    Format a string that gives information about the given node,
    including the syntax with which it was specified.
    """
    if trace:
        print dir(node)
        print node.name         # '(constant)'
        print node.basename     # '(constant)'
        print node.quals        # tuple ()
        print node.kwquals      # dict {}
        print node.classname    # 'MeqConstant'
        print node.children     # list []
        print node.num_children() # int 0
        print node.num_parents()  # int 0
        print node.parents      # <WeakValueDictionary at -1258575060>
        print node.family()     # [<Timba.TDL.TDLimpl._NodeStub object at 0xb4e06aec>]
        print str(node.family()[0])  # '(constant)(MeqConstant)'
        print node.initrec()    # { class: MeqConstant, value: 4.5, tags: ['test'] }

    # Make the constructor string in 3 parts:
    # 1: node part:
    ss = ''
    ss += '** node:   '
    ss += str(node)
    ss_node = ss

    # 2: stub part:
    ss = ''
    ss += ' = ns'
    ss += '[\''+str(node.basename)+'\']'
    if node.quals:
        ss += '(quals)'
    if node.kwquals:
        ss += '(kwquals)'
    ss_stub = ss

    # 3: init part:
    ss = ''
    ss += ' << Meq.'+node.classname.split('Meq')[1]+'('
    rr = node.initrec()
    nc = node.num_children()
    if nc==1:
        ss += 'child' 
        # ss += str(node.children[0][1]) 
    elif nc>1:
        ss += 'children=['+str(nc)+']'
    if not getattr(rr,'value',None)==None:
        ss += str(getattr(rr,'value'))
    ignore = ['class','value','quickref_help']
    for key in rr.keys():
        v = rr[key]
        if key in ignore:
            pass
        elif isinstance(v,str) and len(v)>20:
            ss += ', '+str(key)+'='+str(v[:5])+'..'
        elif isinstance(v,(list,tuple)) and len(v)>5:
            ss += ', '+str(key)+'=['+str(len(v))+']'
        elif isinstance(v,(int,float,complex)):
            ss += ', '+str(key)+'='+str(v)
        elif isinstance(v,dict):
            ss += ', '+str(key)+'={'+str(v.keys())+'}'
        else:
            ss += ', '+str(key)+'='+str(type(v))   
    ss += ')'
    ss_init = ss

    # Put the final string together:
    ss = ss_node
    ss_line = ss_node

    if cut and (len(ss_line)+len(ss_stub))>cmax:
        ss += '\n.    stub:  '
        ss_line = ''
    ss += ss_stub
    ss_line += ss_stub
    
    if cut and (len(ss_line)+len(ss_init))>cmax:
        ss += '\n.    init:  '
        ss_line = ''
    ss += ss_init
    ss_line += ss_init

    if trace:
        print ss
    return ss


#============================================================================
# Function to format a function call:
#============================================================================

def format_function_call_obsolete (function_name, **kwargs):
    """
    Format a string that summarizes a function call
    """
    ss = '<br><dl><dt><font color="blue">\n'
    ss += 'Call to function: '+str(function_name)+'():'
    ss += '\n</font><dd>\n'

    for key in kwargs.keys():
        if key=='kwargs' and isinstance(kwargs['kwargs'],dict):
            pass
        else:
            s = '- '+str(key)+' = '
            s += EF.format_value(kwargs[key])
            ss += s+'<br>\n'

    if kwargs.has_key('kwargs'):
        kw = kwargs['kwargs']
        if isinstance(kw,dict):
            for key in kw.keys():
                s = '-- '+str(key)+' = '
                s += EF.format_value(kw[key])
                ss += s+'<br>\n'
                
    # Finished:
    ss += '</dl><br>\n'
    # print ss
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

def get_node_names (nodes, select='*', trace=False):
    """
    Return a list of node-names from (a selection of) the given nodes
    or node-names. 
    """
    # trace = True

    # Make sure that the input is a list of nodes:
    expected_type = 'node(s)'
    input_type = expected_type
    if not isinstance(nodes,(list,tuple)):
        if not is_node(nodes):                     # not a node
            input_type = type(nodes)
        else:
            nodes = [nodes]
    elif len(nodes)==0:                            # not nodes
        input_type = 'empty list'
    elif not is_node(nodes[0]):                    # not nodes
        input_type = type(nodes[0])

    if trace:
        print '\n** EN.get_node_names(',len(nodes), input_type, select,'):'
        if input_type==expected_type:             
            for i,node in enumerate(nodes):
                print '-',i,'(',type(node),'):',str(node)

    # Escape gracefully if input not nodes (may be values):
    if not input_type==expected_type:              # not nodes
        return None

    # First make the node selection:
    snodes = []                             
    if isinstance(select,(list,tuple)):
        for i in select:
            if i>=0 and i<len(nodes):
                snodes.append(nodes[i])
    elif select==None:
        snodes = []
    else:
        snodes = nodes                      # default: use all nodes
    if trace:
        print '- selected nodes: ',len(snodes),'/',len(nodes)

    nn = []
    for i,node in enumerate(snodes):
        if is_node(node):
            nn.append(node.name)
        elif isinstance(node,str):
            nn.append(node)
        else:
            nn.append(str(type(node))+'??')
        if trace:
            print '--',i,nn[i]
                
    if trace:
        print '** EN.get_node_names(',len(nodes),') ->',len(nn)
    return nn

#------------------------------------------------------------------------

def get_largest_common_string (ss, trace=False):
    """
    Return the largest common string (starting at the beginning) of the given
    list of strings (ss). Example: a list of nodenames.
    """
    # trace = True
    if trace:
        print '\n** EN.largest_common_string():'
        print '   from:',ss

    if not isinstance(ss,(list,tuple)):
        lcs = 'not a list of strings, but: '+str(type(ss))
        # raise ValueError,s
    elif len(ss)==0:
        lcs = '<empty list of strings>'
        # raise ValueError,lcs        
    elif len(ss)==1:
        lcs = ss[0]
    else:
        ncmin = 10000
        for s in ss:
            ncmin = min(ncmin,len(s))
        for s in ss:
            if len(s)==ncmin:
                smin = s       # smin is the shortest string in ss
        lcs = ''
        ii = range(1,len(ss))
        same = True
        for k,c in enumerate(smin):
            for i in ii:
                same = (c==ss[i][k])
                if not same: break
            if not same: break
            lcs += c
                
    if trace:
        print '** EN.largest_common_string() ->',lcs,'\n'
    return lcs

#-----------------------------------------------------------------------

def get_plot_labels (nodes, lcs=None, trace=False):
    """
    Get a list of plot-labels (strings) for the given nodes,
    by removing the 'largest_common_string' from their node-names.
    """
    # trace = True
    if trace:
        print '\n** EN.get_plot_labels(',len(nodes),lcs,'):'

    names = get_node_names (nodes, trace=trace)
    if not names:
        return None
    
    if not isinstance(lcs,str):
        lcs = get_largest_common_string (names, trace=trace)

    if is_node(nodes):
        ss = names                     # just return the node-names
    elif lcs=='':           
        ss = names                     # just return the node-names
    else:
        ss = []
        char = '#'
        for i,name in enumerate(names):
            label = name.replace(lcs,char)      
            if label==char:                  # the node-name is the entire lcs...
                # This is likely the first node, without qualifiers:
                label = str(name)            # use the entire nodename
            ss.append(label)
            if trace:
                print '-',i,':',name,'->',label
    # Finished:
    if trace:
        print '->',ss,'\n'
    return ss


#================================================================================
# Orphan (node) collection functions:
#================================================================================

orphanodes = []

def orphans (node=None, clear=False, trace=True):
    """
    Add the given node(s) to the orpans list (global orphanodes).
    If clear==True, clear the internal orphanodes list ([]).
    Always return the current contents of the list.
    """
    global orphanodes
    if clear:
        orphanodes = []
    if is_node(node):
        orphanodes.append(node)
    elif isinstance(node,(list,tuple)):
        orphanodes.extend(node)
    if trace:
        print '\n** EN.orphans(',type(node),clear,') -> total =',len(orphanodes),'\n'
    return orphanodes

#-------------------------------------------------------------------------------

def bundle_orphans (ns, parent='Composer', trace=True):
    """
    Bundle the collected orphan nodes (if any) in 'orphanodes' with the specified
    parent node, and return it. If orphanodes is empty, return None.
    The idea is to minimize clutter in the browser.
    This function should be called at the end of all _define_forest() functions.
    """
    global orphanodes
    stub = unique_stub(ns, 'orphans')
    node = None
    if len(orphanodes)>0:
        node = stub << getattr(Meq,parent)(*orphanodes)
    if trace:
        print '\n** EN.bundle_orphans(',parent,') ->',str(node),'\n'
        if node:
            print format_tree(node, full=False)
    return node


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

   if 0:
       check_quals(3, trace=True)
       check_quals(range(3), trace=True)
       check_quals(range(3), aa=3, trace=True)
       print check_quals(range(3), dict(a=3), **dict(b=4))
       check_quals(range(3), None, 6, aa=3, trace=True)

   if 0:
       cc = []
       stub = nodestub(ns, 'test')
       for i in range(6):
           cc.append(stub(i) << Meq.Constant(i))
       select = None
       select = [2,3,4]
       nn = get_node_names(cc, select=select, trace=True)
       lcs = get_largest_common_string(nn, trace=True)
       get_plot_labels(cc, lcs=lcs, trace=True)

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
       node = ns['xxx'](range(2)) << Meq.Constant(4.5, tags='test', k1=4, k2=78)
       print format_node(node, cut=True)
       node = ns << Meq.Cos(node, sss='67')
       print format_node(node, cut=True)
       node = ns['comp'](1,2)(g=6) << Meq.Composer(node,0,1,2, dims=[2,2])
       print format_node(node, cut=True)

   if 1:
       node = ns['xxx'](range(2)) << Meq.Constant(4.5, tags='test', k1=4, k2=78)
       print format_node(node, cut=True)

   print '\n** End of standalone test of: EasyNode.py:\n' 

#=====================================================================================



