# -*- coding: utf-8 -*-
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

import Timba
from Timba import dmi
from Timba.TDL import TDLimpl
from TDLimpl import *
from Timba.Meq import meq
import sys
import traceback
import numpy
from Timba.array import *

def array_double (value,shape=None):
  arr = Timba.array.array(value,dtype=Timba.array.float64);
  if shape:
    arr.shape = shape;
  return arr;

_dbg = TDLimpl._dbg;
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

_NodeDef = TDLimpl._NodeDef;

_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];

class _MeqGen (TDLimpl.ClassGen):
  """This class defines the standard 'Meq' class generator. Having a 
  specialized generator for the Meq classes (as opposed to using a generic 
  ClassGen object) allows us to implement specific constructors for 
  complicated nodes such as Meq.Parm and Meq.Solver.""";
  def __init__ (self):
    TDLimpl.ClassGen.__init__(self,'Meq');
    
  def Parm (self,funklet=None,**kw):
    if funklet is not None:
#      if isinstance(funklet,TDL_Funklet.Funklet):
#        funklet = funklet.get_meqfunklet();
      if isinstance(funklet,dmi.dmi_type('MeqFunklet')):
        #        kw['default_funklet'] = funklet;
        kw['init_funklet'] = funklet;
      else:
        kw['default_value'] = funklet;
        #try:
          ##          kw['default_funklet'] = meq.polc(funklet,shape=kw.get('shape',None));
          #kw['init_funklet'] = meq.polc(funklet,shape=kw.get('shape',None));
        #except:
          #if _dbg.verbose>0:
            #traceback.print_exc();
          #return _NodeDef(NodeDefError("illegal funklet argument in call to Meq.Parm"));
    if not kw.has_key('node_groups'):
      kw['node_groups']='Parm';
    return _NodeDef('Meq','Parm',**kw);


  def WSum(self,*childlist,**kw):
    #make sure weights is vector of doubles
    if not kw.has_key('weights'):
      wgt=[1.];
    else:
      wgt = kw['weights'];
      if isinstance(wgt,(tuple,list)):
        wgt = array_double(wgt);
      if dmi.is_scalar(wgt):
        wgt = [float(wgt)];
      elif dmi.is_array(wgt):
        wgt= array_double(wgt);
    kw['weights']=wgt;
    return _NodeDef('Meq','WSum',*childlist,**kw);

  def WMean(self,*childlist,**kw):
    #make sure weights is vector of doubles
    if not kw.has_key('weights'):
      wgt=[1.];
    else:
      wgt = kw['weights'];
      if isinstance(wgt,(tuple,list)):
        wgt = array_double(wgt);
      if dmi.is_scalar(wgt):
        wgt = [float(wgt)];
      elif dmi.is_array(wgt):
        wgt= array_double(wgt);
    kw['weights']=wgt;
    
    return _NodeDef('Meq','WMean',*childlist,**kw);
  
  def Constant (self,value,**kw):
    # convert value to array, if it's a list
    if isinstance(value,(list,tuple)):
      value = numpy.array(value);
    # if array, check for type -- must be complex or float
    if isinstance(value,numpy.ndarray):
      if value.dtype not in (numpy.complex128,numpy.float64):
        value = value.astype(complex) if numpy.iscomplexobj(value) else value.astype(float);
    elif numpy.isscalar(value):
      value = complex(value) if numpy.iscomplex(value) else float(value);
    else:
      return _NodeDef(NodeDefError("can't create Meq.Constant from value of type "+type(value).__name__));
    kw['value'] = value;
    return _NodeDef('Meq','Constant',**kw);
    
  def Solver (self,*childlist,**kw):
    solvables = kw.get('solvable',None);
    if solvables:
      # convert to list if a singleton is specified
      if not isinstance(solvables,(list,tuple)):
        solvables = (solvables,);
      # build list of names. Each solvable may be specified by a string name,
      # or by something with a "name" attribute
      solvnames = [];
      for s in solvables:
        if not isinstance(s,str):
          try: s = s.name;
          except AttributeError: 
            return _NodeDef(NodeDefError("can't specify a solvable as something of type "+type(s).__name__));
        solvnames.append(s);
      # create solvable command
      kw['solvable'] = dmi.record(
        command_by_list=[dmi.record(name=solvnames,state=dmi.record(solvable=True)),
                         dmi.record(state=dmi.record(solvable=False))]);
    return _NodeDef('Meq','Solver',*childlist,**kw);
    
  def VisDataMux (self,*childlist,**kw):
    children = [ (nm,kw.get(nm,None)) for nm in ('start','pre','post') ];
    for ch in childlist:
      children.append((len(children),ch));
    # extra children?
    return _NodeDef('Meq','VisDataMux',children=children,**kw);
    
  # now for some aliases
  def Matrix22 (self,*children,**kw):
    "composes a 2x2 matrix as [[a,b],[c,d]]";
    if len(children) != 4:
      return _NodeDef(NodeDefError("Matrix22 takes exactly 4 arguments (%d given)"%(len(children),)));
    # are all children numeric constants?
    for ch in children:
      if not isinstance(ch,(bool,int,long,float,complex)):
        # no, so create a composer node
        kw['dims'] = [2,2];
        return self.Composer(*children,**kw);
    # yes, all constants. Do we have at least one complex?
    for ch in children:
      if isinstance(ch,complex):
        children = map(complex,children);
        break;
    else:
      children = map(float,children);
    return Meq.Constant(value=Timba.array.array(children).reshape((2,2)));
    
  def ConjTranspose (self,arg,**kw):
    "conjugate (hermitian) transpose";
    kw['conj'] = True;
    return self.Transpose(arg,**kw);
    
Meq = _MeqGen();
