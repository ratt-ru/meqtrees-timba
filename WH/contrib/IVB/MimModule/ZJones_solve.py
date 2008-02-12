from Timba.TDL import *
import Meow
from Meow import Context
from Meow import Jones,ParmGroup,Bookmarks
import myPoly_MIM

    

class ZJones(object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def compute_jones (self,jones,sources,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    mim = myPoly_MIM.Poly_MIM(jones.Subscope(),None,sources,Context.array,tags=tags);
    mim.compute_jones(jones,tags=tags);
    return jones;

  def compile_options(self):
    return myPoly_MIM.compile_options();