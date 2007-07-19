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

script_name = 'MG_JEN_util.py'

# Short description:
#   A collection of 'useful' utility functions 

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 



#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
# from Timba.Contrib.JEN import MG_JEN_forest_state



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   rr = {}
   history (rr, 'item1', 'item2', 4, 5, show=True, trace=1)
   history (rr, show=True, trace=1)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)








#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

 
#--------------------------------------------------------------------------------
# Deal with input arguments (pp):

def inarg (pp={}, _funcall='<funcall>', _help={}, _prompt={}, **default):

    # Create missing fields in pp with the default values given in **default:
    for key in default.keys():
        if not pp.has_key(key): pp[key] = default[key]

    # Identifying info:
    pp['_funcall'] = _funcall
    
    # Eventually, this record may evolve into a input GUI:
    # NB: This field appears to be dropped in pp = record(pp)....?
    # print '_help =',_help
    if len(_help) > 0: pp['_help'] = _help
    if len(_prompt) > 0: pp['_prompt'] = _prompt

    # Make sure of some default fields:
    if not pp.has_key('trace'):
        pp['trace'] = 0
        if pp.has_key('_help'): pp['_help']['trace'] = 'if >0, trace execution'

    # if pp['trace']: display(pp, 'pp', txt='exit of inarg()')
    return pp

#-----------------------------------------------------------------------------------------
# use: if no arguments, return inarg_noexec(pp)
# NB: After record(inarg()), _help etc have disappeared.....!

def inarg_noexec (pp={}, txt='util.inarg_noexec(pp)', trace=0):
    # if trace: display(pp, 'pp', txt=txt)
    return pp



#--------------------------------------------------------------------------------
# Append an log/error/warning message to the given dict/record

def history (rr=0, *item, **pp):
    
    # Deal with input arguments (pp):
    pp = record(inarg (pp, 'MG_JEN_util.history(ns, *item, **pp)',
                        _help=dict(error='if True, an error has occured',
                                   warning='if True, issue a warning',
                                   show='if True, show the accumulated history',
                                   hkey='field-name in rr',
                                   htype='if record, fill a record',
                                   level='indentation level'),
                        error=False, warning=False, show=False,
                        level=1, hkey='_history', htype='dict')) 
    if isinstance(rr, int): return inarg_noexec(pp, trace=pp.trace)
    
    print '*item =',type(item),len(item),item
    print 'str(item) =',str(item)
    return
    
    indent = pp.level*'..'
    if not isinstance(pp.hkey, str): pp.hkey = '_history'
    s1 = '** '+pp.hkey+':'

    if not rr.has_key(pp.hkey):
        if pp.htype=='record':
            rr[pp.hkey] = record(log=record(), ERROR=record(), WARNING=record())
        else:
            rr[pp.hkey] = dict(log={}, ERROR={}, WARNING={})

    if isinstance(item, str):
        s = indent+str(item)
        if trace: print s1,s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s

    if isinstance(pp.error, str):
        s2 = ' ** ERROR ** '
        s = indent+str(pp.error)
        n = len(rr[pp.hkey]['ERROR'])
        print s1,s2,s
        rr[hkey]['ERROR'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[hkey]['log'][n] = s+s2

    if isinstance(pp.warning, str):
        s2 = ' ** WARNING ** '
        s = indent+str(pp.warning)
        n = len(rr[pp.hkey]['WARNING'])
        print s1,s2,s
        rr[hkey]['WARNING'][n] = s
        n = len(rr[pp.hkey]['log'])
        rr[pp.hkey]['log'][n] = s+s2

    if pp.show:
        display (rr[pp.hkey], pp.hkey, pp.hkey)
    return rr


#--------------------------------------------------------------------------------
# Display the contents of a given class

def display_class (klass, txt='<txt>', trace=1):
    print '\n***** Display of class(',txt,'):'
    print '** - klass.__class__ ->',klass.__class__
    rr = dir(klass)
    for attr in rr:
        v = klass[attr]
        print '** - ',attr,':',type(v),':',v
        v = eval('klass.'+attr)
        print '** - ',attr,':',type(v),':',v
    print '***** End of class\n'
    



#-----------------------------------------------------------------------

def get_initrec (node, trace=0):
    initrec = node.initrec()
    if trace: print '\n** JEN_get_initrec(',node.name,'):',initrec,'\n'
    return initrec

#-----------------------------------------------------------------------

def get_dims (node, trace=0):
    initrec = JEN_get_initrec (node)
    if not isinstance(initrec, record):
        dims = [-1]
    elif initrec.has_key('dims'):
        dims = initrec.dims
    elif node.classname == 'MeqSpigot':
        dims = [2,2]
    elif node.classname == 'MeqParm':
        dims = [1]
    elif node.classname == 'MeqConstant':
        dims = list(initrec.value.shape);
    elif node.classname == 'MeqComposer':
        dims = [len(node.children)];
    elif node.classname == 'MeqSelector':
        dims = [1]
        # if initrec.has_key('multi') and initrec.multi:
        if initrec.has_key('index'):
            dims = [len(initrec.index)];
    else:
        dims = [-1]
    if trace: print '\n** JEN_get_dims(',node.name,'): ->',dims,'\n'
    return dims

#------------------------------------------------------------------
# Extract kwquals and quals from lists of nodes

def kwquals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    kwquals = {}
    for i in range(len(cc)):
       kwquals.update(cc[i].kwquals)
       if trace: print '-',i,cc[i],': kwquals =',kwquals
    return kwquals

def quals (cc=[], trace=0):
    if isinstance(cc, tuple): cc = list(cc)
    if not isinstance(cc, list): cc = [cc]
    quals = []
    for i in range(len(cc)):
       quals.extend(list(cc[i].quals))
       if trace: print '-',i,cc[i],': quals =',quals
    return JEN_unique(quals)

#------------------------------------------------------------------
# Make sure that the elements of the list cc are unique 

def unique (cc=[], trace=0):
    if not isinstance(cc, list): return cc
    bb = []
    for c in cc:
        if not bb.__contains__(c): bb.append(c)
    if trace: print '** JEN_unique(',cc,') -> ',bb
    return bb




#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

# MG_JEN_forest_state.init(script_name)



#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   # The following call shows the default settings explicity:
   # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 

   # There are some predefined domains:
   # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)
   # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)

   # NB: It is also possible to give an explicit request, cells or domain
   # NB: In addition, qualifying keywords will be used when sensible

   # If not explicitly supplied, a default request will be used.
   return MG_JEN_exec.meqforest (mqs, parent)



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   # Generic test:
   MG_JEN_exec.without_meqserver(script_name)

   # Various specific tests:
   ns = TDL.NodeScope()

   if 1:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




