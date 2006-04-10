from Timba.dmi import *
from Timba.utils import *
from Timba.Apps import config 

import traceback
import inspect

_dbg = verbosity(0,name='tdlopt');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


compile_options = [];
runtime_options = [];

Config = None;

def clear_options ():
  compile_options = [];
  runtime_options = [];
  
def init_options (filename):
  """initializes option list for given script. This also
  reads in the config file specifiied by filename."""
  clear_options();
  global Config;
  Config = config.DualConfigParser(filename);
  
class TDLOptionItem(object):
  def __init__ (self,caller,symbol,value):
    self.caller = caller;
    self.symbol = symbol;
    self._set(value);
    
  def set_name (self,name):
    self.name = name;
    
  def set_doc (self,doc):
    self.doc = doc;
    
  def _set (self,value):
    self.value = self.caller[self.symbol] = value;
    
  def get_str (self):
    name = getattr(self.value,'__name__',None);
    if name is None:
      return str(self.value);
    else:
      return name;

class TDLBoolOptionItem (TDLOptionItem):
  def __init__ (self,caller,symbol,value):
    try:
      value = Config.getbool(symbol,default=value)
    except:
      _dprint(0,"error reading value from configuration file");
      traceback.print_exc();
    TDLOptionItem.__init__(self,caller,symbol,value);
    
  def set (self,value):
    value = bool(value);
    Config.set(self.symbol,value);
    self._set(value);
    
class TDLListOptionItem (TDLOptionItem):
  def __init__ (self,caller,symbol,value,default=None):
    self.option_list = value;
    # verify default arg
    if default is None:
      default = 0;
    elif not isinstance(default,int):
      raise TypeError,"'default': list index expected";
    elif default < 0 or default >= len(value):
      raise ValueError,"'default': index out of range";
    # try to read from config
    try:
      def1 = Config.getint(symbol,default=default);
      if def1 >= 0 and def1 < len(self.option_list):
        default = def1;
    except:
      _dprint(0,"error reading value from configuration file");
      traceback.print_exc();
    TDLOptionItem.__init__(self,caller,symbol,self.option_list[default]);
    
  def set (self,value):
    value = int(value);
    Config.set(self.symbol,value);
    self._set(self.option_list[default]);
    
  

def make_option_item (caller,symbol,name,value,default=None,inline=False,doc=None):
  # boolean option
  if isinstance(value,bool):
    item = TDLBoolOptionItem(caller,symbol,value);
  # list of options
  elif isinstance(value,(list,tuple)):
    item = TDLListOptionItem(caller,symbol,value,default=default);
    setattr(item,'inline',inline);
  else:
    raise TDLError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
    

def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None):
  # find calling module
  caller = inspect.stack()[1][0].f_globals;
  # add to list
  opt = make_option_item(caller,symbol,name,value,default=default,inline=inline,doc=doc);
  compile_options.append(opt);
  return opt;


def TDLRuntimeOption (symbol,name,value,default=None,inline=False,doc=None):
  # find calling module
  caller = inspect.stack()[1][0].f_globals;
  # add to list
  opt = make_option_item(caller,symbol,name,value,default=default,inline=inline,doc=doc);
  runtime_options.append(opt);
  return opt;



