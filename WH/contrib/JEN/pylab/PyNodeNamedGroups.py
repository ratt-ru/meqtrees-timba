# file: ../contrib/JEN/pylab/PyNodeNamedGroups.py

# Author: J.E.Noordam
# 
# Short description:
#   Baseclass for a zoo of PyNode classes.
#   It contains functions that manipulate named groups of values,
#   which are derived from the results of its children.
#   The named groups can be turnrd into other named groups
#   by means of python mathematical expressions, in which the
#   names of the groups serve as variables.
#
# History:
#   - 12 apr 2008: creation (from PyPlot.py)
#   - 17 may 2008: stddev() -> std() (numpy)
#   - 02 jul 2008: use of EasyNode/EasyTwig
#   - 02 jul 2008: pynode_NamedGroup() etc
#   - 03 jul 2008: removed default group 'allvells'
#   - 04 jul 2008: implemented string2groupspecs()
#   - 06 jul 2008: implemented string2record_VIS22()
#   - 17 jul 2008: allowed values i.s.o. nodes
#
# Remarks:
#
# Description:
#

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

from math import *   # for ._evaluate()
from Timba.Contrib.JEN.pylab import ChildResult
from Timba.Contrib.JEN.QuickRef import EasyNode as EN
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyBundle as EB

import inspect
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyNodeNamedGroups base class:
#=====================================================================================

class PyNodeNamedGroups (pynode.PyNode):
  """
  Base class for a category of pyNodes.
  It contains functions that manipulate named groups of values,
  which are derived from the results of its children.
  The named groups can be turned into other named groups
  by means of python mathematical expressions, in which the
  names of the groups serve as variables.

  The groupspecs record (gs) contains one or more fields, whose names
  are the names of the specified groups. The field values may be either
  a record (see below) or a string. In the latter case, it is assumed
  to be a valid python expression, in which the available groups may be
  variables (see below).

  .   gs =  record(name1=record(children=... [, vells=...]),
  .                name2=record(children=... [, vells=...]),
  .                name3='({name1}+5)*{name2}',
  .               )

  .   from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
  .   ns[nodename] << Meq.PyNode(children=[nodes],
  .                              child_labels=[strings],
  .                              class_name='PyNodeNamedGroups',
  .                              module_name=PNNG.__file__,
  .                              groupspecs=gs)

  For each call .get_result() to this PyNode, the results of its children
  are extracted and stored as vectors in the named groups. This is controlled
  by the group specification records, which may have the following fields:
  - children = '*'           (default) all its children
  .          = '2/3'         the second third of its chidren (etc)
  .          = [0,2,7,5,...] any vector of child indices
  - vells    = '*'           (default) all vells of each child result
  .          = [1,2,2,1,3]   any vector of vells indices
  .          = 0             an integer vells index
  .          = None          the group will contain entire result objects
  - expr     = None          (default) no math operation on vells/results
  .          = 'mean()'      take the mean of each vells
  """

  def __init__ (self, *args, **kwargs):
    # print '\n** entering PyNodeNamedGroups.__init__()\n'
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = -1
    self.groupspecs = record()
    self._gs_order = []
    self._namedgroups = record()
    self._ng_order = []
    self.testeval = None   
    # print '\n** leaving PyNodeNamedGroups.__init__()\n'
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    """
    ss = self.attach_help(ss, PyNodeNamedGroups.__doc__,
                          classname='PyNodeNamedGroups',
                          level=level, mode=mode)
    return ss


  #...................................................................

  def attach_help(self, ss, s, classname='PyNodeNamedGroups',
                  level=0, mode=None, header=True):
    """
    This is the generic routine that does all the work for .help(). 
    It attaches the given help-string (s, in triple-quotes) to ss.
    The following modes are supported:
    - mode=None: interpreted as the default mode (e.g. 'list').
    - mode='list': ss is a list of strings (lines), to be attached to
    the node state. This is easier to read with the meqbrowser.
    - mode='str': ss is a string, in which lines are separated by \n.
    This is easier for just printing the help-text.
    """
    if mode==None:           # The default mode is specified here
      mode = 'str'
    if mode=='list':  
      if not isinstance(ss,(list,tuple)): ss = []
    else:                    # e.g. mode=='str'
      if not isinstance(ss,str): ss = ''
    sunit = '**'             # prefix unit string

    if header:
      h = sunit+(level*sunit)+'** Help for class: '+str(classname)
      if mode=='list':
        ss.append(h)
      else:
        ss += '\n'+h

    prefix = sunit+(level*sunit)+'   '
    cc = s.split('\n')
    bb = []
    for c in cc:
      if mode=='list':
        bb.append(prefix+c)
      else:
        ss += '\n'+prefix+c
    if mode=='list':
      ss.append(bb)
    return ss
    
  #-------------------------------------------------------------------

  def update_state_derived (self, mystate):
    """
    Example re-implementation of .update_state(), for use in
    derived classes (without '_derived' in the name, of course).
    """
    # First call the generic function of the base class:
    # PyNodeNamedGroups.update_state(self, mystate)
    #
    # The class-specific part:
    # mystate('someting',None)
    # ...
    return None

  #-------------------------------------------------------------------
    
  def update_state (self, mystate):
    """
    in PyNodeNamedGroups.py
    Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

    # print '\n** PNNG.update_state(mystate=',type(mystate),'):\n'
    trace = False
    # trace = True

    if True:
      # Attach the help for this class to the state record.
      # This may then be read with the meqbrowser after building the tree.
      if getattr(self, 'help', None):
        ss = self.help(mode='list')
        mystate('pynode_help',ss)
        if trace:
          print '\n** Help attached to node state record:'
          print '\n** self.help(mode=list):\n'
          for s in ss:
            print s
          print '\n** self.help(mode=str):\n'
          print self.help(mode='str')
          print ' '

    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    if isinstance(self.child_indices,int):
      self.child_indices = [self.child_indices]
    string_indices = []
    for i in self.child_indices:
      string_indices.append(str(i))           # default label: node index 


    # It is usually a good idea to specify labels for the
    # 'regular' children (these may be used for plotting etc).
    # NB: Since we only need labels for the 'regular' children,
    # the number of labels is not necessarily equal to the number
    # of children (there might be some PyNodeNamedGroups children)
    undef = None
    undef = '**undef**'
    mystate('child_names', undef)               #  default None not possible....?
    mystate('child_labels', undef)              #  default None not possible....?
    # print '\n** self.child_labels =',self.child_labels,type(self.child_labels)

    if self.child_labels in [None,undef]:
      self.child_labels = string_indices
    elif not isinstance(self.child_labels, (list,tuple)):
      self.child_labels = [str(self.child_labels)]
    self.child_labels = list(self.child_labels) # Tuple does not support item assignment
    for i,s in enumerate(self.child_labels):
      self.child_labels[i] = str(s)             # make sure the labels are strings

    if self.child_names in [None,undef]:
      self.child_names = string_indices
    elif not isinstance(self.child_names, (list,tuple)):
      self.child_names = [str(self.child_names)]
    self.child_names = list(self.child_names)   # Tuple does not support item assignment
    for i,s in enumerate(self.child_names):
      self.child_names[i] = str(s)              # make sure the names are strings

    if trace:
      print '\n*******************************************'
      print '** .update_state()',self.class_name,self.name,self.child_indices
      print '*******************************************\n'
    
    # Read the groupspecs record, and check it:
    mystate('groupspecs', None)
    # print '\n**',self.class_name,self.name,': input self.groupspecs =',self.groupspecs,type(self.groupspecs),'\n'
    if isinstance(self.groupspecs,(int,bool)):      # e.g. False
      self.groupspecs = record()               # make sure it is a record
      self.define_specific_groupspecs()        # (re-implemented) class-specific function 
      self._check_groupspecs()                 # if empty, do nothing
    elif self.groupspecs==None:
      self.groupspecs = record()               # make sure it is a record
      self.define_specific_groupspecs()        # (re-implemented) class-specific function
      self._check_groupspecs()                 # if empty, do nothing  
    elif isinstance(self.groupspecs, record):
      self.define_specific_groupspecs()        # (re-implemented) class-specific function 
      self._check_groupspecs()
    else:
      s = '\n** groupspecs type not recognized: '+str(type(self.groupspecs)) 
      raise ValueError,s

    # Optional: test-evaluation (see .get_result()):
    mystate('testeval', undef)               # only used if it is a string (expr)
    if self.testeval==undef:
      self.testeval = None                   # temporary kludge, until None recognized...

    # Finished
    return None

  #===================================================================
  # Functions dealing with group specifications:
  #===================================================================

  def define_specific_groupspecs(self, trace=False):  
    """
    Placeholder for class-specific function, to be redefined by classes
    that are derived from PyNodeNamedGroups. 
    It allows the specification of one or more specific groupspecs.
    """
    return None

  #-------------------------------------------------------------------

  def _check_groupspecs (self, trace=False):
    """
    Helper function to check the user-specified groupspecs.
    """
    trace = True
    if trace:
      self.display('_check_groupspecs() input')

    self._gs_order = []                      # make the order user-specifiable?
    for key in self.groupspecs.keys():
      rr = self.groupspecs[key]
      lowerkey = key.lower()                 # meqbrowser only transmits lowercase....
      self._gs_order.append(lowerkey)    

      if isinstance(rr, str):                # assume python expression (string)
        self.groupspecs[lowerkey] = rr

      elif isinstance(rr, record):           # children/vells etc
        rr.key = lowerkey                    # attach the key (group name)
        self.groupspecs[lowerkey] = self._check_groupspec(rr)

      elif isinstance(rr, (list,tuple)):     # assume a list of values
        self.groupspecs[lowerkey] = list(rr) # make sure it is a list

      elif isinstance(rr, (int,float,complex)):  # a single value
        self.groupspecs[lowerkey] = [rr]     # make a list of one value

      else:                                  # ...error...?
        rr = record()                        # make sure it is a record
        rr.key = lowerkey                    # attach the key (group name)
        self.groupspecs[lowerkey] = self._check_groupspec(rr)

    # Finished
    if trace:
      self.display('_check_groupspecs() output')
    return True

  #-------------------------------------------------------------------

  def _check_groupspec(self, rr, trac=True):
    """
    Helper function to check the validity of the given group
    specification (rr), which will be used to extract information
    from its children. Called by .update_state().
    """

    # Deal with the selection of children:
    # NB: String specs are not converted to child index vectors, because this can
    # only be done when the nr of 'used' children is known (see .get_result()).
    rr.setdefault('children','*')               # default: all
    s = str(rr.key)+': child spec error: '
    if isinstance(rr.children, (list,tuple)):
      pass                                      # assume OK
    elif isinstance(rr.children, str):
      if rr.children=='*':                      # all
        pass                                    # converted later
      elif '/' in rr.children:                  # e.g. '2/3'
        ss = rr.children.split('/')
        rr.part = int(ss[0])                    # e.g. 2
        rr.nparts = int(ss[1])                  # e.g. 3
      else:
        s += str(rr.children)
        raise ValueError(s)
    else:
      s += str(type(rr.children))
      raise ValueError(s)

    # Deal with the selcetion of vells:
    # rr.setdefault('vells',[0])                  # default: 1st vells
    rr.setdefault('vells','*')                  # default: all vells
    s = str(rr.key)+': vells spec error: '
    if isinstance(rr.vells, int):               # vells index, e.g. 0
      rr.vells = [rr.vells]                     # e.g. 0 -> [0]
    elif isinstance(rr.vells, str):
      if rr.vells=='*':                         # all vells
        pass                                    # converted later
      else:
        s += str(rr.vells)
        raise ValueError(s)
    elif isinstance(rr.vells, (list,tuple)):
      pass                                      # assume ok
    elif rr.vells==None:                        # extract entire child result(s)
      pass
    else:
      s += str(type(rr.vells))
      raise ValueError(s)

    # Misc
    rr.setdefault('expr',None)                  # python math expression (e.g. mean)
    return rr


  #===================================================================
  # Functions dealing with named groups:
  #===================================================================

  def _extract_namedgroups(self, children, child_indices,
                           child_labels=None, trace=False):
    """
    Helper function to extract named groups from the
    given child-results (children). Called by .get_result().
    NB: The 'children' are NOT nodes!
    """

    # trace = True
    if trace:
      print '\n** _extract_namedgroups():'
    
    # import ChildResult
    nc = len(children)

    # First do the groupspecs that are records (they extract values from children):
    for key in self._gs_order:
      rr = self.groupspecs[key]                                 # convenience
      if isinstance(rr,record):

        iic = self._make_child_selection (nc, rr, trace=False)  # child indices
        cindices = []
        for i in iic:
          cindices.append(child_indices[i])
          
        # The child result(s) are read by a special object: 
        extend_labels = True                                    # -> label[ivells] 
        if isinstance(rr.vells,(list,tuple)) and len(rr.vells)==1:
          extend_labels = False                                 # 
        rv = ChildResult.ResultVector(children, select=iic,
                                      extend_labels=extend_labels,
                                      labels=child_labels)
        if trace:
          rv.display(self.class_name)

        # Make/attach a new namedgroup record (object?):
        if rr.vells==None:
          vv = rv.results()                         # <----- !!
          s = 'Extracted:'
          s += '  entire result(s)'
          self._create_namedgroup (key=key, vv=vv, dvv=None,
                                   vells=rr.vells, children=rr.children,
                                   childnos=iic, nodes=cindices,
                                   labels=child_labels, 
                                   history=s)

        else:
          index = rr.vells
          if rr.vells=='*': index = None
          s = 'Extracted:'
          s += '  mean of'                          # <---- !!
          s += '  vells('+str(rr.vells)+')'
          vv = rv.VV(index=index)                   # <---- !!
          dvv = rv.dvv(index=index)                 # <---- !!
          self._create_namedgroup (key=key, vv=vv, dvv=dvv,
                                   vells=rr.vells, children=rr.children,
                                   childnos=rv.expand(iic, index=index),
                                   nodes=rv.expand(cindices, index=index),
                                   labels=rv.labels(index=index), 
                                   history=s)

    #....................................................................
    # Then do the groupspecs that are lists (of values)
    for key in self._gs_order:
      rr = self.groupspecs[key]                                 # convenience
      if isinstance(rr,list):
        dvv = len(rr)*[0.0]
        s = str(len(rr))+' values (nonodes)'
        self._create_namedgroup (key=key, nonodes=True,
                                 vv=rr, dvv=dvv, 
                                 labels=child_labels,
                                 history=s)

    #....................................................................
    # Finally do the groupspecs that are strings (python extressions)
    # They are derived groups:
    # self.display('_extract_namedgroups()')
    for key in self._gs_order:
      rr = self.groupspecs[key]                                 # convenience
      if isinstance(rr,str):
        expr = rr
        s = 'Derived: '+expr
        self._create_namedgroup (key=key, derived=True, expr=expr,
                                 vv=self._evaluate(expr, trace=trace),
                                 dvv=self._expr2dvv(expr, trace=trace),
                                 labels=self._expr2labels(expr, trace=trace),
                                 childnos=self._expr2childnos(expr, trace=trace),
                                 history=s)


    # Finished:
    if trace:
      self.display('_extract_namedgroups()')
    return None
    

  #-------------------------------------------------------------------

  def _create_namedgroup (self, key, vv, dvv=None,
                          children=None, vells=None,
                          childnos=None, nodes=None,
                          labels=None,
                          derived=False, expr=None,
                          nonodes=False,
                          history='History',
                          trace=False):
    """
    Helper function to create a new namedgroup record.
    Called (only) from ._extract_namedgroups(). 
    """
    # Finishing touches on its history (list of strings)
    if isinstance(nodes,(list,tuple)):
      nn = []
      for n in nodes:
        if not n in nn:
          nn.append(n)
      history += '  from '+str(len(nn))+' node(s): '+str(nn)
    history = [history]

    # The group names are lower-key, because the meqbrowser only
    # transmits lowerkey names. 
    lowerkey = key.lower()   

    # Name clashes are more likely with concatenated pynodes....
    if self._namedgroups.has_key(lowerkey):
      s = '** namedgroup name clash: '+lowerkey+' (overwritten)'
      history.append(s)
      print s

    # Extract the largest common string (lcs) from the relevant
    # selection (childnos) of child nodenames:
    lcs = None
    if not (derived or nonodes):
      ss = EN.get_node_names(self.child_names, select=childnos, trace=False) 
      lcs = EN.get_largest_common_string(ss, trace=False) 

    # Make a one-line group summary string: 
    ss = '{'+str(lowerkey)+'}:'
    ss += ' lcs='+str(lcs)
    if derived:
      ss += ' n='+str(len(childnos))
      ss += ' (derived)'
      ss += ' expr='+str(expr)
    elif nonodes:
      ss += ' (nonodes)'
    else:
      ss += ' n='+str(len(childnos))
      ss += ' ('+str(children)+')'
      ss += ' vells='+str(vells)
    
    # Create and attach the new record:
    rr = record(vv=vv, dvv=dvv,
                key=lowerkey,
                derived=derived, expr=expr,
                vells=vells, children=children,
                childnos=childnos, nodes=nodes,
                labels=labels, lcs=lcs,
                summary=ss,
                history=history)
    self._namedgroups[lowerkey] = rr

    # The groups order is important for derived groups, i.e. groups
    # that depend on the values of others (which should be read first).
    self._ng_order.append(lowerkey)
    
    # Finished:
    if trace:
      print '\n** _create_named_group(',key,'): ->',self._ng_order,'\n'
    return True


  #-------------------------------------------------------------------

  def _make_child_selection (self, nc, rr, trace=False):
    """
    Helper function that returns a list of indices for a subset
    of the nc child nodes. Called from _extract_named_groups()
    """
    
    iic = []
    if isinstance(rr.children, (list,tuple)):
      iic = rr.children

    elif rr.children=='*':
      iic = range(nc)

    elif rr.has_field('part'):
      npp = nc/rr.nparts              # nr per part (should be integer...)
      s = '** '+rr.key+' (children='+rr.children+'): '
      if not (npp*rr.nparts)==nc:
        s += 'nc(='+str(nc)+') not divisable by '+str(rr.nparts)
        raise ValueError(s)
      offset = (rr.part-1)*npp
      for i in range(npp):
        iic.append(i+offset)
    else:
      s += ' not recognized'
      raise ValueError(s)
        
    if trace:
      print '** _make_child_selection(',nc,rr.key,rr.children,') ->',iic,'\n'
    return iic


  #===================================================================
  # Display related functions (also used in derived classes):
  #===================================================================

  def oneliner(self):
    """
    Helper function to show a one-line summary of this object
    """
    ss = '** '+self.class_name+' '+self.name+':'
    ss += '  count='+str(self._count)
    if not len(self._ng_order)==len(self._gs_order):
      ss += '  ('+str(len(self._gs_order))+')'
      ss += str(self._gs_order)                        # ....?
    ss += '  groups:'+str(self._ng_order)
    return ss


  def _prefix(self, level=0):
    """
    Helper function to generate prefix string for display.
    """
    return level*'... '

  
  def _preamble(self, level, txt=None, classname='<classname>'):
    """
    Helper function, called at start of .display()
    """
    prefix = self._prefix(level)
    if level==0:
      print prefix,'\n'
      print prefix,self.oneliner()
      if not txt==None: print prefix,' * (',str(txt),'):'
    else:
      print prefix
      print prefix,' **** Inherited from class: '+str(classname)+' ****'
    return prefix


  def _postamble(self, level, txt=None):
    """
    Helper function, called at end of .display()
    """
    prefix = self._prefix(level)
    if level>0:
      pass
      # print prefix,' ****'
      # print prefix
    else:
      if not txt==None: print prefix,' * (',str(txt),'):'
      print prefix,'\n'
    return None

#---------------------------------------------------------------------

  def display (self, txt=None, full=False, level=0):
    """
    Helper function to show the contents of this object
    """
    prefix = self._preamble(level, txt=txt, classname='PyNodeNamedGroups')
    n = len(self.child_indices)
    print prefix,' * child_indices ('+str(len(self.child_indices))+' nodes):',self.child_indices
    print prefix,' * child_labels  ('+str(len(self.child_labels))+'/'+str(n)+'):',self.child_labels

    if isinstance(self.testeval, str):
      print prefix,' * testeval =',self.testeval

    n = len(self._gs_order)
    print prefix,' * Group specifications (n='+str(n)+'):'    
    for key in self._gs_order:
      rr = self.groupspecs[key]
      print prefix,'   - '+key+':  '+str(rr)

    n = len(self._ng_order)
    print prefix,' * Defined namedgroups (new and copied from children) (n='+str(n)+'):'    
    for key in self._ng_order:
      rr = self._namedgroups[key]
      qq = record()
      shortlists = []
      longlists = []
      for key1 in rr.keys():
        if key1 in ['history']:
          pass
        elif not isinstance(rr[key1],(list,tuple)):
          qq[key1] = rr[key1]
        elif len(rr[key1])<5:
          shortlists.append(key1)
        else:
          longlists.append(key1)
      print prefix,'   - '+key+':  '+str(qq)    # qq is record of small (non-list) items 
      for key1 in shortlists:
        print prefix,'       > '+key1+'('+str(len(rr[key1]))+'):  '+str(rr[key1])
      for key1 in longlists:
        # print prefix,'       > '+key1+': '+format_vv(rr[key1])
        print prefix,'       > '+key1+': '+EN.format_value(rr[key1])
      for i,s in enumerate(rr.history):
        print prefix,'       > history['+str(i)+']:  ',s

    # Finished:
    self._postamble(level)
    return True


  #-------------------------------------------------------------------
  #-------------------------------------------------------------------

  def group_history (self, key, append=None, clear=False, trace=False):
    """
    Helper function to interact with the history of the specified group.
    """
    hist = self._namedgroups[key]['history']  
    if isinstance(append,str):
      if isinstance(hist,tuple):
        hist = hist.__add__((append,))
      elif isinstance(hist,list):
        hist.append(append)
      self._namedgroups[key]['history'] = hist  
    return hist

  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """
    Required pyNode function.
    """

    trace = False
    # trace = True
    
    self._count += 1

    # There are two classes of children:
    # - Those that are derived from PyNodeNamedGroups have a
    #   'namedgroups' field in their result.
    # - The others are 'regular' children whose results are used
    #   to extract results/vells, which are turned into new named groups.
    # Thus, nodes derived from PyNodeNamedGroups may be concatenated
    # to produce complicated results.
    # But they can also be used by themselves.
    
    self._namedgroups = record()     
    self._ng_order = []
    cc = []
    ii = []
    for i,child in enumerate(children):            # child results
      if child.has_key('namedgroups'):
        # Copy the PyNodeNamedGroups namedgroup definitions:
        # NB: The order is not important here, because the
        # group values have all been calculated by the child.
        rr = child['namedgroups']
        for key in rr.keys():
          self._namedgroups[key] = rr[key]  
          self._ng_order.append(key)
          self.group_history(key, append='copied from child pynode')
      else:
        # Append child to the list of 'regular' children.
        cc.append(child)
        ii.append(self.child_indices[i])
    
    # Extract new namedgroup definitions from its 'regular' children (if any),
    # or from string groupspecs (i.e. math expressions of existing groups),
    # and append them to the list self._namedgroups:
    # if len(cc)>=0:
    self._extract_namedgroups(cc, child_indices=ii,
                              child_labels=self.child_labels,
                              trace=trace)
    if False:
      self.display('PyNodeNamedGroups.get_result()')

    if isinstance(self.testeval, str):
      self._evaluate(self.testeval, trace=True)
      self._expr2labels(self.testeval, trace=True)
      self._expr2childnos(self.testeval, trace=True)
      self._expr2dvv(self.testeval, trace=True)

    # Make an empty result record
    result = meq.result()

    # Always attach the accumulated namedgroups to the result:
    result['namedgroups'] = self._namedgroups

    # Finished:
    return result


  #-------------------------------------------------------------------
  # Functions dealing with (python, string) expressions:
  #-------------------------------------------------------------------

  def _evaluate(self, expr, trace=False):
    """
    Evaluate the given (python, string) expression, in which the
    names of the namedgroups (enclosed in {}) are variables.
    The groups must have values, and the result is a list/vector.
    """
    # trace = True
    if trace:
      print '\n** _evaluate(',expr,'):'

    # First collect the relevant groups, and count the elements:
    rr = record()
    nv = None
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        rr[kenc] = self._namedgroups[key].vv
        n = len(rr[kenc])
        if nv==None: nv = n
        if trace: print '-',kenc,' in expr, n=',n
        if not nv==n:
          s = '** '+kenc+': evaluation length mismatch: '+str(n)+' != '+str(nv)
          raise ValueError,s
      elif trace:
        print '-',kenc,' not in expr'

    # Evaluate element-by-element:
    vv = []
    for i in range(nv):
      seval = expr
      for kenc in rr.keys():                           # all {var}
        seval = seval.replace(kenc,str(rr[kenc][i]))   # replace all with str(number)
      v = eval(seval)                                  # evaluate

      # If the result of the evaluation is boolean, it may be used to select
      # values, e.g. from the first (?) group in the expression....
      # Obviously this is a bit of a kludge (...to be implemented...)
      if isinstance(v,bool):
        vv.append(v)                         # temporary: do nothing special....                           
      else:
        vv.append(v)                       

      if trace:
        print '-',i,seval,'->',type(v),v

    # Finished:
    if trace:
      # print '->',format_vv(vv),'\n'
      print '->',EN.format_value(vv),'\n'
    return vv

  #-------------------------------------------------------------------

  def _expr2dvv(self, expr, trace=False):
    """
    Return the dvv (stddev) of the first (!?) namedgroup that appears as
    a variable {<name>} in the given expression.
    NB: This is just a placeholder, until it is done properly....
    """
    if trace:
      print '\n** _expr2dvv(',expr,'):'
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        dvv = self._namedgroups[key].dvv
        if trace:
          print '-',kenc,len(dvv),'->',dvv,'\n'
        return dvv                             # for the moment: return the first...!
    return None

  #-------------------------------------------------------------------

  def _expr2labels(self, expr, trace=False):
    """
    Return the labels of the first (!?) namedgroup that appears as
    a variable {<name>} in the given expression. 
    """
    if trace:
      print '\n** _expr2labels(',expr,'):'
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        ss = self._namedgroups[key].labels
        lcs = self._namedgroups[key].lcs
        ss = EN.get_plot_labels(ss, lcs=lcs)
        if trace:
          print '-',kenc,lcs,len(ss),'->',ss,'\n'
        return ss                              # for the moment: return the first...!
    return None


  #-------------------------------------------------------------------

  def _expr2keys(self, expr, trace=False):
    """
    Return a list of keys of the existing named group(s) that appear as
    variable(s) {<name>} in the given expression. 
    """
    keys = []
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        keys.appens(key)
    if trace:
      print '\n** _expr2keys(',expr,') ->',keys
    return keys


  #-------------------------------------------------------------------

  def _expr2lcs(self, expr, trace=False):
    """
    If the given expression contains a variable {<name>}, return the
    expr in which {<name>} is raplaced by the largest_common_string (lcs)
    field of the relevant named group.
    This is used for xlabel/ylabel (see PyNodePlot.py)
    """
    # trace = True
    if trace:
      print '\n** _expr2lcs(',expr,'):'
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        ss = expr.replace(kenc, str(self._namedgroups[key].lcs))
        if trace:
          print '-',kenc,expr,'->',ss,'\n'
        return ss
    # If none found, return the input expr:
    return expr


  #-------------------------------------------------------------------

  def _expr2childnos(self, expr, trace=False):
    """
    Return the child numbers of the first (!?) namedgroup that appears as
    a variable {<name>} in the given expression. To be used as xx. 
    """
    if trace:
      print '\n** _expr2childnos(',expr,'):'
    for key in self._namedgroups.keys():
      kenc = '{'+key+'}'
      if kenc in expr:
        ii = self._namedgroups[key].childnos
        if trace:
          print '-',kenc,len(ii),'->',ii,'\n'
        return ii                             # for the moment: return the first...!
    return None




#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================


def format_float_obsolete(v, name=None, n=2):
  """Helper function to format a float for printing"""
  if isinstance(v, complex):
     s1 = format_float(v.real)
     s2 = format_float(v.imag)
     s = '('+s1+'+'+s2+'j)'
  else:
     q = 100.0
     v1 = int(v*q)/q
     s = str(v1)
  if isinstance(name,str):
    s = name+'='+s
  # print '** format_float(',v,name,n,') ->',s
  return s

#-----------------------------------------------------------

def format_vv_obsolete (vv):
  if not isinstance(vv,(list,tuple)):
    return str(vv)
  elif len(vv)==0:
    return 'empty'
  elif not isinstance(vv[0],(int,float,complex)):
    s = '  length='+str(len(vv))
    s += '  type='+str(type(vv[0]))
    s += '  '+str(vv[0])+' ... '+str(vv[len(vv)-1])
  else:
    import pylab              # must be done here, not above....
    ww = pylab.array(vv)
    s = '  length='+str(len(ww))
    s += format_float(ww.min(),'  min')
    s += format_float(ww.max(),'  max')
    s += format_float(ww.mean(),'  mean')
    if len(ww)>1:                       
      if not isinstance(ww[0],complex):
        s += format_float(ww.std(),'  stddev')
  return s





#=====================================================================================
# Example of a class derived from PyNodeNamedGroups
#=====================================================================================

class ExampleDerivedClass (PyNodeNamedGroups):
  """
  Example of a class derived from PyNodeNamedGroups. 
  NB: The (preferred) alternative to a derived class is the use of
  a function like pynode_NamedGroups(), as defined in this module.
  """

  def __init__ (self, *args, **kwargs):
    PyNodeNamedGroups.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Link in the chain to provide hierarchical help for the inheritance tree.
    """
    ss = self.attach_help(ss, ExampleDerivedClass.__doc__,
                          classname='ExampleDerivedClass',
                          level=level, mode=mode)
    return PyNodeNamedGroups.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=False):  
    """
    Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    if True:
      # Used for operations (e.g. plotting) on separate correlations.
      # Its children are assumed to be 2x2 tensor nodes (4 vells each).
      self.groupspecs['XX'] = record(children='2/3', vells=[0])
      self.groupspecs['XY'] = record(children='3/3', vells=[1])
      self.groupspecs['YX'] = record(children='*', vells=[2])
      self.groupspecs['YY'] = record(children='*', vells=[3])
      # Derived groups are specified as (string) python extressions,
      # in which the (lowercase!) group names {a} are variables.
      if True:
        self.groupspecs['stokesI'] = '({yx}+{yy})/2' 
    return None






#=====================================================================================
# pynode_NamedGroup() functions (preferred alternative to derived classes)
#=====================================================================================


#--------------------------------------------------------------------

def pynode_NamedGroup (ns, nodes, groupspecs=None, labels=None,
                       nodename=None, quals=None, kwquals=None,
                       **kwargs):
  """
  Create and return a pynode of class PyNodeNamedGroups,
  with the nodes (children) in the groups defined groupspecs.
  Syntax:
  .   import PyNodeNamedGroups as PNNG
  .   pynode = PNNG.pynode_NamedGroup (ns, nodes, groupspecs=None, labels=None,
  .                                    nodename=None, quals=None, kwquals=None,
  .                                    **kwargs)
  Mandatory arguments:
  - ns:          nodescope
  - nodes:       list of (child) nodes whose results are to be used.
  .              NB: Some or all of these child nodes may be other pynodes of
  .              the PyNodeNamedGroups class. The named groups in their results
  .              will be copied to the new pynode. This mechanism allows concatenation
  .              of PyNodeNamedGroups pynodes, which is very powerful.
  Optional arguments:
  - labels:      list of labels for the node results. If not supplied, or the wrong
  .                length, they will be derived from the node names.
  - nodename:    name of the resulting pynode
  - quals:       list of qualifiers
  - kwquals:     dict of keyword qualifiers
  - groupspecs:  group specification(s) (string or record):
  .    - if a string (e.g. 'YY'), make a standard groupspecs record internally
  .              (see PNNG.string2groupspecs() for the various possibilities.      
  .    - if a record, assume a valid groupspecs record (advanced use).
  .              The field-names of the record are the names of the new groups.
  .              The field values may be either a record or a string:
  .              - if a string, it should be a valid math expression, in which
  .                the other groups are variables (e.g. '{a}+{b}')
  .              - if a record, it contains specifications for extracting results
  .                from its 'regular' children (i.e. non-PyNamedGroups children)
  - **kwargs:    additional customizing arguments (..)
  """
  trace = False
  # trace = True

  # Check the name of the new node: 
  if not isinstance(nodename, str):
    nodename = 'pynode_NamedGroup'
  else:
    nodename = 'pynode_NamedGroup_'+nodename
    

  if isinstance(groupspecs, str):
    # Certain standard group-specs may be specified by a string:
    nodename += '_'+str(groupspecs)
    gs = string2groupspecs(groupspecs, nodes=nodes)

  elif isinstance(groupspecs, dict):
    # Assume a valid groupspecs record....? 
    gs = groupspecs

  else:
    # No groupspecs specified (concatenation)
    gs = None

  # Make two vectors of child names and labels (used below):
  [child_names, labels] = child_labels(nodes, labels, trace=False)

  # Make a unique nodestub:
  stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)

  # Make the quickref_help list of strings:
  qhelp = ['']
  qhelp.append('   This pynode has been specified by a convienience function:')
  qhelp.append('     import PyNodeNamedGroups as PNNG')
  qhelp.append('     PNNG.pynode_NamedGroup(ns, nodes,')
  if isinstance(groupspecs, str):
    qhelp.append('                     groupspecs='+str(groupspecs)+',')
  else:
    qhelp.append('                     groupspecs='+str(type(groupspecs))+',')
  qhelp.append('                    )')
  qhelp.append('')
  qhelp.append('   The convenience function has defined the actual MeqPyNode:')
  qhelp.append('     stub = EasyNode.unique_stub(ns,nodename,quals,kwquals) -> '+str(stub))
  qhelp.append('     pynode = stub << Meq.PyNode(')
  qhelp.append('                         children=nodes,')
  qhelp.append('                         child_labels=labels,')
  qhelp.append('                         child_names=child_names,')
  qhelp.append('                         groupspecs=gs,')
  qhelp.append('                         class_name=pyNodeNamedGroups,')
  qhelp.append('                         module_name='+str(__file__)+')')
  qhelp.append('')
  qhelp.append('   in which:')
  qhelp.append('       nodes (list) = '+str(nodes[0])+' ... ('+str(len(nodes))+')')
  qhelp.append('       labels (list) = '+str(labels[0])+' ... ('+str(len(labels))+')')
  qhelp.append('       gs (record) = '+str(gs))
  qhelp.append('')

  # Create the PyNode:
  pynode = stub << Meq.PyNode(children=nodes,
                              child_labels=labels,
                              child_names=child_names,
                              groupspecs=gs,
                              quickref_help=qhelp,
                              class_name='PyNodeNamedGroups',
                              module_name=__file__)
  if trace:
    print '->',str(pynode)
  return pynode


#---------------------------------------------------------------------------------------

def child_labels(nodes, labels, trace=False):
  """
  Return a list of valid lists [child_names, labels] of the same
  length as nodes. Check that nodes is an non-empty list.
  Called from pynode_NamedGroup() and PyNodePlot.pynode_Plot() 
  """
  if not isinstance(nodes,(list,tuple)):
    s = '** nodes is not a list, but: '+str(type(nodes))
    raise ValueError,s

  elif len(nodes)==0:
    s = '** node/value list is empty: '
    raise ValueError,s
    
  elif is_node(nodes[0]):
    # Normal case: a list of nodes. 
    # If no labels specified, derive them from the child nodenames:
    child_names = EN.get_node_names(nodes, select='*', trace=False)
    if (not isinstance(labels,(list,tuple))) or (not len(labels)==len(nodes)):
      lcs = EN.get_largest_common_string(child_names, trace=False)
      labels = EN.get_plot_labels(nodes, lcs=lcs, trace=trace)

  else:
    # Assume that nodes is a list of values:
    child_names = []
    for i,v in enumerate(nodes):
      child_names.append('#'+str(i))
    if (not isinstance(labels,(list,tuple))) or (not len(labels)==len(nodes)):
      labels = child_names

  # Finished:
  return [child_names, labels]
      
#---------------------------------------------------------------------------------------
  
def string2groupspecs(ss, nodes=None, trace=False):
  """
  Make a groupspecs record from the given string spec.
  Recognized strings are:
  - YY:        Take vells[0] for group y
  - CY:        Take (complex) vells[0] for group y 
  - XY:        Assume tensor nodes with vells[0,1] for groups x,y
  - CXY:       Take real,imag part of vells[0] for groups x,y 
  - XYZ:       Assume tensor nodes with vells[0,1,2] for groups x,y,z
  - VELLS_ijk: Assume tensor nodes. Groups x,y,z from vells[i,j,k].
  - XXYY:      Assume single list of equal nrs of x,y nodes
  - XXYYZZ:    Assume single list of equal nrs of x,y,z nodes
  - VIS22...:  Assume 2x2 tensor nodes. See string2record_VIS22()
  - anything else: make a group of that name, with all vells[0]
  .                (NB: group-name will be converted to lowercase...)
  """
  gs = record()

  if ss in ['YY','CY']:
    # Its children are assumed to have a single vells -> group y
    gs.y = record(children='*', vells=[0])
  elif ss in ['XX']:
    # Its children are assumed to have a single vells -> group x
    gs.x = record(children='*', vells=[0])
  elif ss in ['ZZ']:    
    # Its children are assumed to have a single vells -> group z
    gs.z = record(children='*', vells=[0])

  elif ss=='XXYY':
    # Its children are assumed to be in 2 concatenated lists (and have a single vells...)
    gs.x = record(children='1/2', vells=[0])           # the 1st half
    gs.y = record(children='2/2', vells=[0])           # the 2nd half
  elif ss=='XXYYZZ':
    # Its children are assumed to be in 3 concatenated lists (and have a single vells...)
    gs.x = record(children='1/3', vells=[0])           # the 1st third
    gs.y = record(children='2/3', vells=[0])           # the 2nd third
    gs.z = record(children='3/3', vells=[0])           # the 3rd third

  elif ss=='CXY':
    # NB: This does not work, because 'expr' is not used (yet)...................!!
    # Its children are assumed to nodes with complex vells[0]
    gs.x = record(children='*', vells=[0], expr='real()')       # ...?
    gs.y = record(children='*', vells=[0], expr='imag()')       # ...?

  elif ss=='XY':
    # Its children are assumed to be tensor nodes with (at least) 2 vells
    gs.x = record(children='*', vells=[0]) 
    gs.y = record(children='*', vells=[1]) 
  elif ss=='XYZ':
    # Its children are assumed to be tensor nodes with (at least) 3 vells
    gs.x = record(children='*', vells=[0]) 
    gs.y = record(children='*', vells=[1]) 
    gs.z = record(children='*', vells=[2]) 

  elif 'VELLS_' in ss:
    # Its children are assumed to be tensor nodes with at least as
    # many vells as are required by the integers after '_'.
    vv = ss.split('VELLS_')[1]                 # VELLS_34 -> vv = '34'
    if len(vv)==1:
      gs.y = record(children='*', vells=[int(vv[0])])    # [3]
    elif len(vv)>1:
      gs.x = record(children='*', vells=[int(vv[0])])    # [3]
      gs.y = record(children='*', vells=[int(vv[1])])    # [4]
      if len(vv)==3:
        gs.z = record(children='*', vells=[int(vv[2])])  # 

  elif 'VIS22' in ss:
    # Special case: 2x2 cohaerency matrices
    gs = string2groupspecs_VIS22 (ss, trace=trace)

  else:
    # Assume that the string is a groupname....
    # NB: Convert the group-name to lowercase, because the meqbrowser
    #     will converts it in any case....
    gs[ss.lower()] = record(children='*', vells=[0])


  #...............................................................
  # The input 'nodes' may also be a list of values,
  # from which a named group will be formed:
  values = False
  if isinstance(nodes, (int,float,complex)):
    values = True
    gs[ss.lower()] = [nodes]
  elif not isinstance(nodes,(list,tuple)):
    pass
  elif len(nodes)==0:
    pass
  elif is_node(nodes[0]):
    pass
  else:
    values = True
    gs[ss.lower()] = nodes
  #...............................................................


  if trace:
    print '\n** string2groupspecs(',ss,values,'):\n    ',gs,'\n'
  return gs

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

def string2groupspecs_VIS22 (ss, trace=False):
  """
  Special case: visibilities.
  Its children are assumed to be 2x2 tensor nodes (4 vells each).
  See also PyNodePlotVIS22.py
  """
  rr =  string2record_VIS22 (ss, trace=trace)
  gs = record()
  for icorr in rr.corrs:
    gname = rr.groupname[icorr]
    gs[gname] = record(children='*', vells=[icorr])
    if trace:
      print '-',icorr,gname,gs[gname]
  return gs

#.....................................................................

def string2record_VIS22 (ss, trace=False):
  """
  Turns the given string (VIS22...) into a record of polarisation info,
  which is used to define groupspecs and plotspecs for visibility plotting.
  - VIS22C: polrep='circular' (otherwise: polrep='linear')
  - _IQUV: convert to I,Q,U,V (otherwise: visibilities)
  - _QUV: convert to Q,U,V 
  - _DIAG: diagonal terms corrs=[0,3] (e.g. XX,YY')
  - _OFFDIAG: off-diagonal terms corrs=[1,2] (e.g. XY,YX')
  - _annotate: annotate all corrs/stokes
  - _nannotate: annotate none of the corrs/stokes
  NB: This function is also called from module PyNodePlot.py
  """
  rr = record()

  rr.annotate = [True,False,False,False]
  rr.corrs = range(4)
  rr.stokes = []
  rr.mode = 'vis'
  rr.color = ['red','magenta','green','blue']
  rr.marker = ['circle','cross','cross','circle']      
  rr.markersize = [2,3,3,2]
  rr.fontsize = [7,7,7,7]
  rr.xlabel = 'real part (cos) of vis (Jy)'
  rr.ylabel = 'imag part (sin) of vis (Jy)'

  if '_IQUV' in ss:
    rr.mode = 'stokes'
    rr.stokes = range(4)
  elif '_QUV' in ss:
    rr.mode = 'stokes'
    rr.stokes = range(1,4)
    rr.annotate[1] = True
  elif '_DIAG' in ss:
    rr.corrs = [0,3]
  elif '_OFFDIAG' in ss:
    rr.corrs = [1,2]
    rr.annotate[1] = True

  if '_annot' in ss:
    rr.annotate = 4*[True] 
  elif '_nannot' in ss:
    rr.annotate = 4*[False] 

  rr.polrep = 'linear'
  rr.groupname = ['xx','xy','yx','yy']
  if 'VIS22C' in ss:
    rr.polrep = 'circular'
    rr.groupname = ['rr','rl','lr','ll']

  if rr.mode=='stokes':
    rr.marker = ['circle','cross','cross','plus']     
    rr.markersize = [2,3,3,3]                       
    rr.xlabel = 'real part of Stokes (Jy)'
    rr.ylabel = 'imag part of Stokes (Jy)'
    if rr.polrep=='circular':
      rr.name = ['I','Q','iU','V']
      rr.expr = ['({rr}+{ll})/2','({rl}+{lr})/2',
                 '({rl}-{lr})/2','({rr}-{ll})/2']
    else:
      rr.name = ['I','Q','U','iV']
      rr.expr = ['({xx}+{yy})/2','({xy}+{yx})/2',
                 '({xy}-{yx})/2','({xx}-{yy})/2']

  elif rr.polrep=='circular':
    rr.name = ['RR','RL','LR','LL']
    rr.expr = ['{rr}','{rl}','{lr}','{ll}']

  else:
    rr.name = ['XX','XY','YX','YY']
    rr.expr = ['{xx}','{xy}','{yx}','{yy}']


  if trace:
    print rr
  return rr

#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  cc = []

  nodes = EB.cloud(ns,'n6s2')
  xnodes = EB.cloud(ns,'n6s1')
  ynodes = EB.cloud(ns,'n6s2')
  znodes = EB.cloud(ns,'n6s3')
  cxnodes = EB.cloud(ns,'n6r1')
  viewer = 'Record Browser'

  if True:
    node = pynode_NamedGroup(ns, xnodes, 'XX')
    Meow.Bookmarks.Page('XX').add(node, viewer=viewer)
    cc.append(node)
    node = pynode_NamedGroup(ns, ynodes, 'YY')
    Meow.Bookmarks.Page('YY').add(node, viewer=viewer)
    cc.append(node)

  if True:
    # Concatenate the pynodes in cc (XX and YY):
    node = pynode_NamedGroup(ns, cc, 'concat')
    Meow.Bookmarks.Page('concat').add(node, viewer=viewer)
    cc.append(node)

  if True:
    # A group with an arbitrary name (and complex children)
    node = pynode_NamedGroup(ns, cxnodes, 'complex')
    Meow.Bookmarks.Page('user').add(node, viewer=viewer)
    cc.append(node)

  if True:
    # Concatenate the pynodes in cc (XX, YY, concat, user):
    node = pynode_NamedGroup(ns, cc, 'concat2')
    Meow.Bookmarks.Page('concat2').add(node, viewer=viewer)
    cc.append(node)

  if True:
    node = pynode_NamedGroup(ns, xnodes+ynodes, 'XXYY')
    Meow.Bookmarks.Page('XXYY').add(node, viewer=viewer)
    cc.append(node)

  if True:
    node = pynode_NamedGroup(ns, xnodes+ynodes+znodes, 'XXYYZZ')
    Meow.Bookmarks.Page('XXYYZZ').add(node, viewer=viewer)
    cc.append(node)

   
  # Finished:
  ns['rootnode'] << Meq.Composer(*cc)
  return True

#-------------------------------------------------------------------------------------

def _define_forest_old (ns,**kwargs):
  """Make trees with the various pyNodes"""
  

  cc = []
  labels = []
  n = 6
  for i in range(n):
    vv = []
    for j,corr in enumerate(['XX','XY','YX','YY']):
      v = (j+1)+10*(i+1)
      v = complex(i,j)
      vv.append(ns[corr](i) << v)
    cc.append(ns['c'](i) << Meq.Composer(*vv))
    labels.append('c'+str(i))

  gs = None
  # labels = None

  if False:
    # Optional: make concatenation pynode:
    gs = record(concat=record(vells=[2]))
    ns['concat'] << Meq.PyNode(children=cc, child_labels=labels,
                               class_name='PyNodeNamedGroups',
                               groupspecs=gs,
                               module_name=__file__)
    cc.append(ns['concat'])
    # cc.insert(0,ns['concat'])
    # cc.insert(2,ns['concat'])


  # Make the root pynode:
  # gs = record(gs0=record())
  # gs = record(gs0=record(children=range(1,3)))
  # gs = record(gs0=record(children='2/3', vells='*'))
  # gs = record(gs0=record(children=range(1,3), vells=[0,1]))
  # gs = record(gs0=record(children=range(1,3), vells=2))

  # Optional (testing): Define a test-evaluation expression 
  tv = None
  tv = '{allvells}'
  tv = '{allvells}/2'
  tv = '{allvells}.real + {allvells}.imag'
  tv = 'cos(abs({allvells}))'
  tv = '{allvells}**2'
  # tv = None

  ns['rootnode'] << Meq.PyNode(children=cc,
                               child_labels=labels,
                               # class_name='PyNodeNamedGroups',
                               class_name='ExampleDerivedClass',
                               # groupspecs=gs,
                               # testeval=tv,
                               module_name=__file__)
  # Meow.Bookmarks.Page('pynode').add(rootnode, viewer="Record Viewer")

  # Finished:
  return True
  


#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,wait=False):
  from Timba.Meq import meq
  nf2 = 10
  nt2 = 5
  cells = meq.cells(meq.domain(-nf2,nf2,-nt2,nt2),
                    num_freq=2*nf2+1,num_time=2*nt2+1);
  print '\n-- cells =',cells,'\n'
  request = meq.request(cells,rqtype='e1');
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True

if False:
  def _tdl_job_sequence (mqs,parent,wait=False):
    from Timba.Meq import meq
    for i in range(5):
      cells = meq.cells(meq.domain(i,i+1,i,i+1),num_freq=20,num_time=10);
      rqid = meq.requestid(i)
      print '\n--',i,rqid,': cells =',cells,'\n'
      request = meq.request(cells, rqid=rqid);
      a = mqs.meq('Node.Execute',record(name='rootnode',request=request), wait=wait)
    return True


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

  print '\n** Start of standalone test of: PyNodeNamedGroups.py:\n' 
  ns = NodeScope()

  nodes = EB.cloud(ns,'n6s2')
  cxnodes = EB.cloud(ns,'n6r1', trace=True)

  if 0:
    pynode = pynode_NamedGroup(ns, nodes, 'Y')
    pynode = pynode_NamedGroup(ns, cxnodes, 'complex')

  if 0:
    xx = pynode_NamedGroup(ns, nodes, 'XX')
    yy = pynode_NamedGroup(ns, nodes, 'YY')
    if True:
      concat = pynode_NamedGroup(ns, [xx,yy], 'concat')

  if 0:
    xnodes = EB.cloud(ns,'n6s1')
    ynodes = EB.cloud(ns,'n6s2')
    znodes = EB.cloud(ns,'n6s3')
    pynode = pynode_NamedGroup(ns, xnodes+ynodes, 'XXYY')
    pynode = pynode_NamedGroup(ns, xnodes+ynodes+znodes, 'XXYYZZ')

  if False:
    _define_forest(ns);
    ns.Resolve();

  print '\n** End of standalone test of: PyNodeNamedGroups.py:\n' 

#=====================================================================================

