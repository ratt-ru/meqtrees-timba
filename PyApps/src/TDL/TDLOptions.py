from Timba.dmi import *
from Timba.utils import *
from Timba.Apps.config import Config 

import traceback
import inspect

# import Qt but ignore failures since we can also run stand-alone
try:
  from qt import *
except:
  pass;

_dbg = verbosity(0,name='tdlopt');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# current config section, this is set to the script name by init_options()
config_section = "tdl scripts";

compile_options = [];
runtime_options = [];

def clear_options ():
  global compile_options;
  global runtime_options;
  compile_options = [];
  runtime_options = [];
  
def init_options (filename):
  """initializes option list for given script. This also
  reads in the config file specifiied by filename."""
  clear_options();
  global config_section;
  config_section = filename;
  
def get_compile_options ():
  return compile_options;
  
def get_runtime_options ():
  return runtime_options;
  
class TDLOptionItem(object):
  def __init__ (self,namespace,symbol,value):
    self.namespace = namespace;
    self.symbol = symbol;
    self._set(value);
    self.name = None;
    self.doc = None;
    
  def set_name (self,name):
    self.name = name;
    
  def set_doc (self,doc):
    self.doc = doc;
    
  def _set (self,value):
    self.value = self.namespace[self.symbol] = value;
    
  def get_str (self):
    return self.item_str(self.value);
      
  def item_str (item):
    """converts item to string representation.
    If item is a named symbol, uses the name, else uses str()""";
    return getattr(item,'__name__',None) or str(item);
  item_str = staticmethod(item_str);

class TDLBoolOptionItem (TDLOptionItem):
  def __init__ (self,namespace,symbol,value):
    try:
      value = Config.getbool(symbol,default=value,section=config_section)
    except:
      _dprint(1,"error reading",symbol,"from config");
      if _dbg.verbose > 0:
        traceback.print_exc();
    _dprint(1,"read",symbol,"=",value,"from config");
    TDLOptionItem.__init__(self,namespace,symbol,value);
    
  def set (self,value):
    value = bool(value);
    Config.set(self.symbol,value,section=config_section);
    self._set(value);

  def add_to_menu (self,menu):
    """adds entry for option to menu object (usually of class QPopupMenu).
    """
    # create toggle action for bool options
    qa = QAction(self.name or self.symbol,0,menu);
    if self.doc:
      qa.setToolTip(self.doc);
    qa.setToggleAction(True);
    qa.setOn(self.value);
    QObject.connect(qa,SIGNAL("toggled(bool)"),self.set);
    qa.addTo(menu);
    menu._ends_with_separator = False;
    
    
class TDLListOptionItem (TDLOptionItem):
  def __init__ (self,namespace,symbol,value,default=None):
    self.option_list = value;
    self.option_list_str = map(lambda x:self.item_str(x),value);
    self.inline = False;
    # verify default arg
    if default is None:
      default = 0;
    elif not isinstance(default,int):
      raise TypeError,"'default': list index expected";
    elif default < 0 or default >= len(value):
      raise ValueError,"'default': index out of range";
    # try to read from config
    try:
      def1 = Config.get(symbol,section=config_section);
      _dprint(1,"read",symbol,"=",def1,"from config");
      default = self.option_list_str.index(def1);
    except:
      _dprint(1,"error reading value from configuration file");
      if _dbg.verbose > 0:
        traceback.print_exc();
    self.selected = default;
    TDLOptionItem.__init__(self,namespace,symbol,self.option_list[default]);
    
  def num_options (self):
    return len(self.option_list);
    
  def get_option (self,num):
    return self.option_list[num];
    
  def get_option_str (self,num):
    return self.option_list_str[num];
    
  def set (self,value):
    self.selected = value = int(value);
    self._set(self.get_option(value));
    Config.set(self.symbol,self.get_option_str(value),section=config_section);
    
  def add_to_menu (self,menu):
    """adds entry for option to menu object (usually of class QPopupMenu).
    """
    # create QActionGroup for list items
    groupname = self.name or self.symbol;
    qag = QActionGroup(menu);
    qag._groupname = groupname;
    qag.setExclusive(True);
    if self.inline:
      qag.setUsesDropDown(False);
      if not getattr(menu,'_ends_with_separator',True):
        menu.insertSeparator();
    else:
      qag.setUsesDropDown(True);
    # create QActions within group
    for ival in range(self.num_options()):
      name = self.get_option_str(ival);
      if self.inline:
        name = groupname + ": " + name;
      qa = QAction(name,0,qag);
      qa.setToggleAction(True);
      if self.doc:
        qa.setToolTip(self.doc);
      if ival == self.selected:
        qa.setOn(True);
      qa._togglefunc = curry(self._set_menu_option,qag,ival);
      QObject.connect(qa,SIGNAL("toggled(bool)"),qa._togglefunc);
    # add to menu
    qag.addTo(menu);
    if self.inline:
      menu.insertSeparator();
      menu._ends_with_separator = True;
    else:
      qag.setMenuText(groupname + ": " + self.get_str());
      menu._ends_with_separator = False;
      
  def _set_menu_option (self,qag,ivalue,toggled):
    if not toggled:
      return;
    self.set(ivalue);
    if not self.inline:
      qag.setMenuText(qag._groupname+": "+self.get_str());
    
  

def make_option_item (namespace,symbol,name,value,default=None,inline=False,doc=None):
  # boolean option
  if isinstance(value,bool):
    item = TDLBoolOptionItem(namespace,symbol,value);
  # list of options
  elif isinstance(value,(list,tuple)):
    item = TDLListOptionItem(namespace,symbol,value,default=default);
    setattr(item,'inline',inline);
  else:
    raise TDLError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
  return item;

def _add_option (option_list,namespace,*args,**kwargs):
  if namespace is None:
    namespace = inspect.stack()[2][0].f_globals;
  elif inspect.ismodule(namespace):
    namespace = namespace.__dict__;
  opt = make_option_item(namespace,*args,**kwargs);
  option_list.append(opt);
  return opt;
  


def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None):
  return _add_option(compile_options,namespace,
    symbol,name,value,default=default,inline=inline,doc=doc);


def TDLRuntimeOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None):
  return _add_option(runtime_options,namespace,
    symbol,name,value,default=default,inline=inline,doc=doc);



