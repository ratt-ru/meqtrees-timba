from Timba import dmi
from Timba.TDL import TDLimpl
from TDLimpl import *
from Timba.Meq import meq
import sys
import traceback


_dbg = TDLimpl._dbg;
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

_NodeDef = TDLimpl._NodeDef;

_MODULE_FILENAME = traceback.extract_stack()[-1][0];

class _MeqGen (TDLimpl.ClassGen):
  """This class defines the standard 'Meq' class generator. Having a 
  specialized generator for the Meq classes (as opposed to using a generic 
  ClassGen object) allows us to implement specific constructors for 
  complicated nodes such as Meq.Parm and Meq.Solver.""";
  def __init__ (self):
    TDLimpl.ClassGen.__init__(self,'Meq');
    
  def Constant (self,value):
    return _NodeDef('Meq','Constant',value=value);
    
  def Parm (self,funklet=None,**kw):
    if funklet is not None:
      if isinstance(funklet,dmi.dmi_type('MeqFunklet')):
#        kw['default_funklet'] = funklet;
        kw['init_funklet'] = funklet;
      else:
        try:
#          kw['default_funklet'] = meq.polc(funklet,shape=kw.get('shape',None));
          kw['init_funklet'] = meq.polc(funklet,shape=kw.get('shape',None));
        except:
          if _dbg.verbose>0:
            traceback.print_exc();
          return _NodeDef(NodeDefError("illegal funklet argument in call to Meq.Parm"));
    return _NodeDef('Meq','Parm',**kw);
    
  def Constant (self,value,**kw):
    if isinstance(value,(list,tuple)):
      if filter(lambda x:isinstance(x,complex),value):
        value = dmi.array(map(complex,value));
      else:
        value = dmi.array(map(float,value));
    elif isinstance(value,(int,long)):
      value = float(value);
    elif not isinstance(value,(float,complex,dmi.array_class)):
      raise TypeError,"can't create Meq.Constant from value of type "+type(value).__name__;
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
            raise TypeError,"can't specify a solvable as something of type "+type(s).__name__;
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
    return Meq.Constant(value=dmi.array(children,shape=[2,2]));
    
  def ConjTranspose (self,arg,**kw):
    "conjugate (hermitian) transpose";
    kw['conj'] = True;
    return self.Transpose(arg,**kw);
    
Meq = _MeqGen();
