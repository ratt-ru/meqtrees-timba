from Timba.dmi import *
from Timba.utils import *
import ConfigParser

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

# config file for script options
config_file = ".tdl.conf";
config = ConfigParser.RawConfigParser();
config.read(config_file);

def save_config ():
  config.write(file(config_file,"w"));
  
def set_config (option,value):
  if not config.has_section(config_section):
    config.add_section(config_section);
  config.set(config_section,option,value);
  _dprint(1,"setting",option,"=",value,"in config",config_section);
  save_config();

# current config section, this is set to the script name by init_options()
config_section = "default";

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
  
class _TDLOptionItem(object):
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

class _TDLBoolOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value):
    try:
      value = bool(config.getint(config_section,symbol));
    except:
      _dprint(1,"error reading",symbol,"from config");
      if _dbg.verbose > 0:
        traceback.print_exc();
    _dprint(1,"read",symbol,"=",value,"from config");
    _TDLOptionItem.__init__(self,namespace,symbol,value);
    
  def set (self,value):
    value = bool(value);
    set_config(self.symbol,int(value));
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
    
    
class _TDLListOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,default=None):
    if isinstance(value,(list,tuple)):
      self.option_list = value;
      self.option_list_str = self.option_list_desc = map(lambda x:self.item_str(x),value);
    elif isinstance(value,dict):
      self.option_list = list(value.iterkeys());
      self.option_list_str = map(lambda x:self.item_str(x),value.iterkeys());
      self.option_list_desc = map(lambda x:str(x),value.itervalues());
    else:
      raise TypeError,"TDLListOptionItem: list or dict of options expected";
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
      def1 = config.get(config_section,symbol);
      _dprint(1,"read",symbol,"=",def1,"from config");
      default = self.option_list_str.index(def1);
    except:
      _dprint(1,"error reading",symbol,"from config");
      if _dbg.verbose > 0:
        traceback.print_exc();
      default = 0;
    self.selected = default;
    _TDLOptionItem.__init__(self,namespace,symbol,self.option_list[default]);
    
  def num_options (self):
    return len(self.option_list);
    
  def get_option (self,num):
    return self.option_list[num];
    
  def get_option_str (self,num):
    return self.option_list_str[num];
    
  def get_option_desc (self,num):
    return self.option_list_desc[num];
    
  def set (self,value):
    self.selected = value = int(value);
    self._set(self.get_option(value));
    set_config(self.symbol,self.get_option_str(value));
    
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
      name = self.get_option_desc(ival);
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
      qag.setMenuText(groupname + ": " + self.get_option_desc(self.selected));
      menu._ends_with_separator = False;
      
  def _set_menu_option (self,qag,ivalue,toggled):
    if not toggled:
      return;
    self.set(ivalue);
    if not self.inline:
      qag.setMenuText(qag._groupname+": "+self.get_option_desc(ivalue));
      
class _TDLSubmenu (object):
  def __init__ (self,title,*items):
    """Creates a submenu from the given list of options.
    Note that an option may be specified as False or None to skip it.""";
    self._title = title;
    self._items = filter(lambda x:bool(x),items);
    # check the runtime and compiletime option lists and remove item
    # from them, if found. This allows us to include items with
    # TDLCompileOption or TDLRuntimeOption directly
    for item in self._items:
      for option_list in (compile_options,runtime_options):
        for i,item0 in enumerate(option_list):
          if item is item0:
            del option_list[i];
            break;
    
  def add_to_menu (self,menu):
    """adds submenu to menu object (usually of class QPopupMenu).
    """
    submenu = QPopupMenu(menu);
    menu.insertItem(self._title,submenu);
    # create entries for sub-items
    for item in self._items:
      _dprint(3,"adding",item,"to submenu");
      item.add_to_menu(submenu);

def _make_option_item (namespace,symbol,name,value,default=None,inline=False,doc=None):
  # if namespace is not specified, set it to 
  # the globals() of the caller of our caller
  if namespace is None:
    namespace = inspect.stack()[2][0].f_globals;
  elif inspect.ismodule(namespace):
    namespace = namespace.__dict__;
  # boolean option
  if isinstance(value,bool):
    item = _TDLBoolOptionItem(namespace,symbol,value);
  # list of options
  elif isinstance(value,(list,tuple,dict)):
    item = _TDLListOptionItem(namespace,symbol,value,default=default);
    setattr(item,'inline',inline);
  else:
    raise TypeError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
  return item;

def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None):
  """this creates an option object and adds it to the compile-time list""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc);
  compile_options.append(opt);
  return opt;

def TDLRuntimeOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None):
  """this creates an option object and adds it to the runtime list""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc);
  runtime_options.append(opt);
  return opt;
  
def TDLCompileMenu (title,*items):
  compile_options.append(_TDLSubmenu(title,*items));

def TDLRuntimeMenu (title,*items):
  runtime_options.append(_TDLSubmenu(title,*items));

def TDLMenu (title,*items):
  return _TDLSubmenu(title,*items);

def TDLOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None):
  """this creates and returns an option object. Should be used
  with TDLCompileMenu/TDLRuntimeMenu.""";
  return _make_option_item(namespace,symbol,name,value,default,inline,doc);
