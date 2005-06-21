from Timba import dmi
from Timba.TDL import TDLimpl
from Timba.Meq import meq
import sys
import traceback

_dbg = TDLimpl._dbg;
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class _MeqGen (TDLimpl.ClassGen):
  """This class defines the standard 'Meq' class generator. Having a 
  specialized generator for the Meq classes (as opposed to using a generic 
  ClassGen object) allows us to implement specific constructors for 
  complicated nodes such as Meq.Parm and Meq.Solver.""";
  def __init__ (self):
    TDLimpl.ClassGen.__init__(self,'Meq');
    
  def Parm (self,funklet=None,**kw):
    if funklet is not None:
      if isinstance(funklet,dmi.dmi_type('MeqFunklet')):
        kw['default_funklet'] = funklet;
      else:
        try:
          kw['default_funklet'] = meq.polc(funklet,shape=kw.get('shape',None));
        except:
          if _dbg.verbose>0:
            traceback.print_exc();
          raise TDLimpl.NodeDefError,"illegal funklet argument in call to Meq.Parm at "+TDLimpl._identifyCaller();
    return TDLimpl._NodeDef('MeqParm',**kw);
    
  def Solver (self,*childlist,**kw):
    solvables = kw.get('solvable',None);
    if solvables:
      # convert to list if a single string is specified
      if isinstance(solvables,str):
        solvables = (solvables,);
      # create solvable command
      kw['solvable'] = dmi.record(
        command_by_list=[dmi.record(name=solvables,state=dmi.record(solvable=True)),
                         dmi.record(state=dmi.record(solvable=False))]);
    return TDLimpl._NodeDef('MeqSolver',*childlist,**kw);
    
  # now for some aliases
  def Matrix22 (self,a,b,c,d,**kw):
    "composes a 2x2 matrix as [[a,b],[c,d]]";
    kw['dims'] = [2,2];
    return self.Composer(a,b,c,d,**kw);
    
  def ConjTranspose (self,arg,**kw):
    "conjugate (hermitian) transpose";
    kw['conj'] = True;
    return self.Transpose(arg,**kw);
    
Meq = _MeqGen();
