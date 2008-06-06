# file: ../contrib/JEN/pylab/Baservice.py

# Author: J.E.Noordam
# 
# Short description:
#   Baseclass that provides a range of basic services. 
#
# History:
#   - 23 may 2008: creation (from PyNodeNamedGroups.py)
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


#=====================================================================================
# The Baservice base class:
#=====================================================================================

class Baservice (object):
  """Base class that provides some basic services"""

  def __init__ (self):
    return None

  def classname (self):
    s = str(type(self))
    return s

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class.
    """
    ss = self.attach_help(ss, Baservice.help.__doc__,
                          classname='Baservice',
                          level=level, mode=mode)
    return ss


  #...................................................................

  def attach_help(self, ss, s, classname='<classname>',
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
      if level==0:
        s1 = '** Help for class: '
      else:
        s1 = '** Derived from class: '
      h = sunit+(level*sunit)+s1+str(classname)
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
    

  #===================================================================
  # .oneliner() and .summary():
  #===================================================================

  def oneliner(self):
    """Helper function to show a one-line summary of this object"""
    ss = '** '+str(type(self))
    return ss

  #------------------------------------------------------------------
  #------------------------------------------------------------------

  def summary (self, txt=None, full=False, ss=None, level=0):
    """Return a summary (ss) of the contents of this object
    """
    ss = self._summary_preamble(ss, level, txt=txt,
                                classname='Baservice')
    px = self._summary_prefix(level)

    # The body:
    ss += px+' * '

    # Finished:
    return self._summary_postamble(ss, level)


  #-------------------------------------------------------------------

  def _summary_prefix(self, level=0):
    """Helper function to generate prefix string for summary.
    """
    return '\n'+(level*'... ')+' '

  #-------------------------------------------------------------------
  
  def _summary_preamble(self, ss, level, txt=None,
                        classname='<classname>'):
    """Helper function, called at start of .summary()
    """
    px = self._summary_prefix(level)
    if ss==None:
      ss = ''
    if level==0:
      ss += px+'\n'
      s1 = '** Summary of class: '+str(classname)
      if txt==None:
        ss += px+s1+':'
      else:
        ss += px+s1+' ('+str(txt)+'):'
      ss += px+' * oneliner(): '+self.oneliner()
    else:
      ss += px
      ss += px+' **** Inherited from class: '+str(classname)+' ****'
    return ss

  #-------------------------------------------------------------------

  def _summary_postamble(self, ss, level):
    """Helper function, called at end of .summary()
    """
    px = self._summary_prefix(level)
    if level==0:
      ss += px+'\n'
      print ss
    return ss








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
# Examples of classes derived from Baservice
#=====================================================================================

class ExampleDerivedClass (Baservice):
  """Example of a class derived from Baservice"""

  def __init__ (self):
    Baservice.__init__(self)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    This is an example of a derived class.
    """
    ss = self.attach_help(ss, ExampleDerivedClass.help.__doc__,
                          classname='ExampleDerivedClass',
                          level=level, mode=mode)
    return Baservice.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def summary (self, txt=None, full=False, ss=None, level=0):
    """Return a summary (ss) of the contents of this object
    """
    px = self._summary_prefix(level)
    ss = self._summary_preamble(ss, level, txt=txt,
                                classname='ExampleDerivedClass')
    # The body:
    ss += px+' * D'

    # Finished:
    return Baservice.summary(self, ss=ss, level=level+1)




#=====================================================================================

class ExampleDDerivedClass (ExampleDerivedClass):
  """Example of a class derived from """

  def __init__ (self):
    ExampleDerivedClass.__init__(self)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    This is an example of a derived derived (DD) class.
    """
    ss = self.attach_help(ss, ExampleDDerivedClass.help.__doc__,
                          classname='ExampleDDerivedClass',
                          level=level, mode=mode)
    return ExampleDerivedClass.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def summary (self, txt=None, full=False, ss=None, level=0):
    """Return a summary (ss) of the contents of this object
    """
    px = self._summary_prefix(level)
    ss = self._summary_preamble(ss, level, txt=txt,
                                classname='ExampleDDerivedClass')
    # The body:
    ss += px+' * DD'

    # Finished:
    return ExampleDerivedClass.summary(self, ss=ss, level=level+1)


#=====================================================================================

class ExampleDDDerivedClass (ExampleDDerivedClass):
  """Example of a class derived from """

  def __init__ (self):
    ExampleDerivedClass.__init__(self)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    This is an example of a derived derived derived (DDD) class.
    """
    ss = self.attach_help(ss, ExampleDDDerivedClass.help.__doc__,
                          classname='ExampleDDDerivedClass',
                          level=level, mode=mode)
    return ExampleDDerivedClass.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def summary (self, txt=None, full=False, ss=None, level=0):
    """Return a summary (ss) of the contents of this object
    """
    px = self._summary_prefix(level)
    ss = self._summary_preamble(ss, level, txt=txt,
                                classname='ExampleDDDerivedClass')
    # The body:
    ss += px+' * DDD'

    # Finished:
    return ExampleDDerivedClass.summary(self, ss=ss, level=level+1)






#=====================================================================================
#=====================================================================================
#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

  edc = ExampleDDDerivedClass()
  print edc.oneliner()

  if 1:
    ss = edc.summary('text')
    print ss
  
  if 1:
    print edc.help()

  if 1:
    print '\n** mode=list:'
    ss = edc.help(mode='list')
    for s in ss:
      print s

#=====================================================================================
