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

import inspect
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyNodeNamedGroups base class:
#=====================================================================================

class PyNodeNamedGroups (pynode.PyNode):
  """Extract named groups of Vells from its child results."""

  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = -1
    self.groupspecs = record()
    self._namedgroups = record()
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class for a category of pyNodes.
    It contains functions that manipulate named groups of values,
    which are derived from the results of its children.
    The named groups can be turned into other named groups
    by means of python mathematical expressions, in which the
    names of the groups serve as variables.

    First of all, this baseclass contains functions for the
    extraction of named groups from its child results.
    This is specified by attaching a record named 'groupspecs' to
    the constructor, containing zero or more named records:
    .   ns.plot << Meq.PyNode(class_name='PyPlot', module_name=__file__,
    .        groupspecs=record(name1=record(children=... [, vells=...]),
    .                          name2=record(children=... [, vells=...]),
    .                          ...
    .                          ))

    If no groupspecs record has been provided, or if it is empty,
    or if it is not a record, a default record will be assumed:
    .        groupspecs=record(vv=record(children='*', vells=[0]))
    i.e. it will make a single group (named 'allvells') from
    all available vells in the results of all its 'regular' children.

    An extractgroup specification record may have the following fields:
    - children = '*'           (default) all its children
               = '2/3'         the second third of its chidren (etc)
               = [0,2,7,5,...] any vector of child indices
    - vells    = [0]           (default) the first vells of each child result
               = [1,2,2,1,3]   any vector of vells indices
               = None          the group will contain entire result objects
    - expr     = None          (default) python expression
               = 'mean()'      initial operation on each vells
    """
    ss = self.attach_help(ss, PyNodeNamedGroups.help.__doc__,
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
      mode = 'list'
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
    for c in cc:
      if mode=='list':
        ss.append(prefix+c)
      else:
        ss += '\n'+prefix+c
    return ss
    
  #-------------------------------------------------------------------

  def update_state_derived (self, mystate):
    """Example re-implementation of .update_state(), for use in
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
    """Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

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

    # It is usually a good idea to specify labels for the
    # 'regular' children (these may be used for plotting etc).
    # NB: Since we only need labels for the 'regular' children,
    # the number of labels is not necessarily equal to the number
    # of children (there might be some PyNodeNamedGroups children)
    undef = None
    undef = 'undef'
    mystate('child_labels', undef)              #  default None not possible....?
    # print '\n** self.child_labels =',self.child_labels,type(self.child_labels)
    if self.child_labels in [None,undef]:
      string_indices = []
      for i in self.child_indices:
        string_indices.append(str(i))           # default label: node index 
      self.child_labels = string_indices
    elif not isinstance(self.child_labels, (list,tuple)):
      self.child_labels = [str(self.child_labels)]
    self.child_labels = list(self.child_labels) # Tuple does not support item assignment
    for i,label in enumerate(self.child_labels):
      self.child_labels[i] = str(label)         # make sure the labels are strings

    if trace:
      print '\n*******************************************'
      print '** .update_state()',self.class_name,self.name,self.child_indices
      print '*******************************************\n'
    
    # Read the groupspecs record, and check it:
    mystate('groupspecs', None)
    if not isinstance(self.groupspecs, record):
      self.groupspecs = record()             # make sure it is a record

    self.define_specific_groupspecs()        # (re-implemented) class-specific function 
    if len(self.groupspecs)==0:
      self.groupspecs['allvells'] = record() # at least one group (named allvells)

    for key in self.groupspecs.keys():
      rr = self.groupspecs[key]
      if not isinstance(rr, record):
        rr = record()                           # make sure it is a record
      rr.key = key                              # attach the key (group name)
      self.groupspecs[key] = self._check_extractgroup_definition(rr)

    # Finished
    return None


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Placeholder for class-specific function, to be redefined by classes
    that are derived from PyNodeNamedGroups.Called by .update_state().
    It allows the specification of one or more default groupspecs.
    """
    # Example(s):
    if False:
      # Used for operations (e.g. plotting) on separate correlations.
      # Its children are assumed to be 2x2 tensor nodes (4 vells each).
      self.groupspecs['XX'] = record(children='2/3', vells=[0])
      self.groupspecs['XY'] = record(children='3/3', vells=[1])
      self.groupspecs['YX'] = record(children='*', vells=[2])
      self.groupspecs['YY'] = record(children='*', vells=[3])
    return None

  #-------------------------------------------------------------------

  def _check_extractgroup_definition(self, rr, trac=True):
    """Helper function to check the validity of the given definition (rr)
    of an extractgroup (used to extract information from its children).
    Called by .update_state().
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


  #-------------------------------------------------------------------

  def _extract_namedgroups(self, children, child_indices,
                           child_labels=None, trace=True):
    """Helper function to extract named groups from the
    given child-results (children). Called by .get_result().
    """

    import ChildResult
    nc = len(children)

    for key in self.groupspecs.keys():
      rr = self.groupspecs[key]                            # convenience
      lowerkey = key.lower()                                  # use lowercase only...!!  

      iic = self._make_child_selection (nc, rr, trace=False)  # child indices
      cindices = []
      # print '\n iic =',iic,nc,rr.children
      for i in iic:
        # print '-',child_indices,'[',i,']->',child_indices[i]
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
        self._create_namedgroup (key=lowerkey, vells=rr.vells,
                                 children=rr.children,
                                 childnos=iic, nodes=cindices,
                                 labels=child_labels,
                                 history=s, vv=vv)

      else:
        index = rr.vells
        if rr.vells=='*': index = None
        s = 'Extracted:'
        s += '  mean of'                          # <---- !!
        s += '  vells'+str(rr.vells)
        vv = rv.vcx(index=index)                  # <---- !!
        self._create_namedgroup (key=lowerkey, vells=rr.vells,
                                 children=rr.children,
                                 childnos=rv.expand(iic, index=index),
                                 nodes=rv.expand(cindices, index=index),
                                 labels=rv.labels(index=index),
                                 history=s, vv=vv)


    # Finished:
    if trace:
      self.display('_extract_namedgroups()')
    return None
    
      
  #-------------------------------------------------------------------

  def _create_namedgroup (self, key, children, vells,
                          childnos, nodes, labels,
                          history, vv, trace=True):
    """Helper function to create a new namedgroup record.
    Called (only) from ._extract_namedgroups(). 
    """
    # Finishing touches on its history (list of strings)
    nn = []
    for n in nodes:
      if not n in nn:
        nn.append(n)
    history += '  from '+str(len(nn))+' node(s): '+str(nn)
    history = [history]

    # Name clashes are more likely with concatenated pynodes....
    if self._namedgroups.has_key(key):
      s = '** namedgroup name clash: '+key+' (overwritten)'
      history.append(s)
      print s

    # Create and attach the new record:
    rr = record(key=key, vells=vells, children=children,
                childnos=childnos, nodes=nodes, labels=labels,
                history=history, vv=vv)
    self._namedgroups[key] = rr

    # Finished:
    return True


  #-------------------------------------------------------------------

  def _make_child_selection (self, nc, rr, trace=False):
    """Helper function that returns a list of indices for a subset
    of the nc child nodes.
    """

    # trace = True
    
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

  #-------------------------------------------------------------------

  def oneliner(self):
    """Helper function to show a one-line summary of this object"""
    ss = '** PyNodeNamedGroups: '
    ss += self.name+':'
    ss += '  count='+str(self._count)
    ss += '  extract('+str(len(self.groupspecs.keys()))+')'
    ss += str(self.groupspecs.keys())
    ss += '  named('+str(len(self._namedgroups.keys()))+')'
    ss += str(self._namedgroups.keys())
    return ss
  

  def display (self, txt=None, full=False):
    """Helper function to show the contents of this object
    """
    print '\n'
    print self.oneliner()
    print ' * (',txt,'):'
    print ' *',type(self), self.class_name, self.name
    n = len(self.child_indices)
    print ' * child_indices ('+str(len(self.child_indices))+' nodes):',self.child_indices
    print ' * child_labels  ('+str(len(self.child_labels))+'/'+str(n)+'):',self.child_labels

    print ' * Group specifications (by the user):'    
    for key in self.groupspecs.keys():
      rr = self.groupspecs[key]
      print '   - '+key+':  '+str(rr)

    print ' * Total (copied and/or extracted) namedgroups:'    
    for key in self._namedgroups.keys():
      rr = self._namedgroups[key]
      qq = record()
      keys = []
      for key1 in rr.keys():
        if key1 in ['history']:
          pass
        elif not isinstance(rr[key1],(list,tuple)):
          qq[key1] = rr[key1]
        elif len(rr[key1])<5:
          qq[key1] = rr[key1]
        else:
          keys.append(key1)
      print '   - '+key+':  '+str(qq)
      for key1 in keys:
        print '      > '+key1+'('+str(len(rr[key1]))+'):  '+str(rr[key1])
      for i,s in enumerate(rr.history):
        print '      > history['+str(i)+']:  ',s

    print
    return True


  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Required pyNode function."""

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
    
    fieldname = 'namedgroups'                      # name of result field
    self._namedgroups = record()     
    cc = []
    ii = []
    for i,child in enumerate(children):            # child results
      if child.has_key(fieldname):
        # Copy the PyNodeNamedGroups namedgroup definitions:
        rr = child[fieldname]
        for key in rr.keys():
          self._namedgroups[key] = rr[key]  
      else:
        # Append child to the list of 'regular' children.
        cc.append(child)
        ii.append(self.child_indices[i])
    
    # Extract new namedgroup definitions from its 'regular' children (if any),
    # and append them to the list self._namedgroups:
    if len(cc)>0:
      self._extract_namedgroups(cc, child_indices=ii,
                                child_labels=self.child_labels,
                                trace=trace)
    if True:
      self.display('.get_result()')

    # Make an empty result record
    result = meq.result()

    # Always attach the accumulated namedgroups to the result:
    result[fieldname] = self._namedgroups

    # Finished:
    return result


  #-------------------------------------------------------------------
  # Re-implementable functions (for derived classes)
  #-------------------------------------------------------------------






#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================


def format_float(v, name=None, n=2):
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

def format_vv (vv):
  if not isinstance(vv,(list,tuple)):
    return str(vv)
  elif len(vv)==0:
    return 'empty'
  import pylab              # must be done here, not above....
  ww = pylab.array(vv)
  # print '\n** ww =',type(ww),ww
  s = '  length='+str(len(ww))
  s += format_float(ww.min(),'  min')
  s += format_float(ww.max(),'  max')
  s += format_float(ww.mean(),'  mean')
  if len(ww)>1:                       
    if not isinstance(ww[0],complex):
      s += format_float(ww.stddev(),'  stddev')
  return s



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
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
  # gs = record(gs0=record(children=range(1,3)))
  gs = record(gs0=record(children='2/3', vells='*'))
  # gs = record(gs0=record(children=range(1,3), vells=[0,1]))
  # gs = record(gs0=record(children=range(1,3), vells=2))

  ns['rootnode'] << Meq.PyNode(children=cc,
                               child_labels=labels,
                               class_name='PyNodeNamedGroups',
                               groupspecs=gs,
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

  # run in batch mode?
  if '-run' in sys.argv:
    from Timba.Apps import meqserver
    from Timba.TDL import Compile
    
    # this starts a kernel.
    mqs = meqserver.default_mqs(wait_init=10);

    # This compiles a script as a TDL module. Any errors will be thrown as
    # an exception, so this always returns successfully. We pass in
    # __file__ so as to compile ourselves.
    (mod,ns,msg) = Compile.compile_file(mqs,__file__);
    
    # this runs the _test_forest job.
    mod._test_forest(mqs,None,wait=True);

  elif False:
    pp = PyNodeNamedGroups()
    print pp.help()

  else:
    #  from Timba.Meq import meqds 
    # Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
