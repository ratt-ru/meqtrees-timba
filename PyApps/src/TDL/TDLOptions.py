from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
import ConfigParser

import traceback

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
_dprint(1,"read config file",config_file);

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
  _dprint(1,"config section is now",filename);
  
def get_compile_options ():
  return compile_options;
  
def get_runtime_options ():
  return runtime_options;
  
class _TDLJobItem (object):
  def __init__ (self,func,name=None,doc=None):
    self.func = func;
    self.symbol = func.__name__;
    self.name = name or func.__name__.replace('_',' ');
    self.doc = doc;
    
  def add_to_menu (self,menu,executor):
    """adds entry for job to menu object (usually of class QPopupMenu).
    """
    # create toggle action for bool options
    qa = QAction(self.name,0,menu);
    if self.doc:
      qa.setToolTip(self.doc);
    qa.setIconSet(pixmaps.gear.iconset());
    self._exec = curry(executor,self.func,self.name);
    QObject.connect(qa,SIGNAL("activated()"),self._exec);
    qa.addTo(menu);
    menu._ends_with_separator = False;
  
class _TDLOptionItem(object):
  def __init__ (self,namespace,symbol,value):
    self.full_symbol = symbol;
    # symbol may have nested namespaces specified with '.'
    syms = symbol.split('.');
    symbol = syms[-1];
    while len(syms) > 1:
      name = syms.pop(0);
      namespace = namespace.setdefault(name,{});
      if not isinstance(namespace,dict):
        namespace = getattr(namespace,'__dict__',None);
        if namespace is None:
          raise TypeError,"'"+name+"' does not refer to a valid namespace";
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
    set_config(self.full_symbol,int(value));
    self._set(value);

  def add_to_menu (self,menu,executor=None):
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
  def __init__ (self,namespace,symbol,value,default=None,more=None):
    if more not in (None,int,float,str):
      raise ValueError,"'more' argument to list options must be 'None', 'int', 'float' or 'str'"
    self._more = more;
    if isinstance(value,(list,tuple)):
      self.option_list = list(value);
      self.option_list_str = map(lambda x:self.item_str(x),value);
      self.option_list_desc = list(self.option_list_str);
    elif isinstance(value,dict):
      self.option_list = list(value.iterkeys());
      self.option_list_str = map(lambda x:self.item_str(x),value.iterkeys());
      self.option_list_desc = map(lambda x:str(x),value.itervalues());
    else:
      raise TypeError,"TDLListOptionItem: list or dict of options expected";
    self.inline = False;
    # if 'more' is specified, add a placeholder in the list for the custom value
    if more is not None:
      self.option_list.append(None);
      self.option_list_str.append('');
      self.option_list_desc.append('');
    # verify default arg
    if default is None:
      default = 0;
    if not isinstance(default,int):
      raise TypeError,"'default': list index expected";
    elif default < 0 or default >= len(value):
      raise ValueError,"'default': index out of range";
    # try to read value from config file
    try:
      def1 = config.get(config_section,symbol);
      # look up value in list
      _dprint(1,"read",symbol,"=",def1,"from config");
      try:
        self.selected = self.option_list_str.index(def1);
      except:
        if more is None:
          _dprint(1,def1,"is an illegal value for",symbol);
          self.selected = default;
        # add configured symbol to list of values
        else:
          self.set_custom_value(more(def1));
          self.selected = len(self.option_list) - 1;
    except:
      _dprint(1,"error reading",symbol,"from config");
      if _dbg.verbose > 0:
        traceback.print_exc();
      self.selected = default;
    _TDLOptionItem.__init__(self,namespace,symbol,self.option_list[self.selected]);

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
    set_config(self.full_symbol,self.get_option_str(value));
    
  def set_custom_value (self,value):
    if self._more is None:
      raise TypeError,"can't set custom value for this option list, since it was not created with a 'more' argument";
    self.option_list[-1] = value;
    self.option_list_str[-1] = self.option_list_desc[-1] = str(value);
    
  def add_to_menu (self,menu,executor=None):
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
      is_custom = self._more is not None and ival == self.num_options()-1;
      name = self.get_option_desc(ival);
      if is_custom:
        name += '...';
      if self.inline:
        name = groupname + ": " + name;
      qa = QAction(name,0,qag);
      qa.setToggleAction(True);
      if self.doc:
        qa.setToolTip(self.doc);
      if ival == self.selected:
        qa.setOn(True);
      if is_custom:
        qa._togglefunc = curry(self._set_custom_menu_option,qag,qa,ival);
      else:
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

  def _set_custom_menu_option (self,qag,qa,ivalue,toggled):
    if not toggled:
      return;
    ok = False;
    # show input dialog, if the "Other" option was selected
    if self._more is int:
      value,ok = QInputDialog.getInteger(qag._groupname,qag._groupname,self.option_list[-1] or 0);
    elif self._more is float:
      value,ok = QInputDialog.getDouble(qag._groupname,qag._groupname,self.option_list[-1] or 0,-2147483647,2147483647,6);
    elif self._more is str:
      value,ok = QInputDialog.getText(qag._groupname,qag._groupname,QLineEdit.Normal,self.option_list[-1] or '');
    if ok:
      self.set_custom_value(value);
    self.set(ivalue);
    txt = self.get_option_desc(ivalue);
    if self.inline:
      qa.setMenuText(qag._groupname+": "+txt+'...');
    else:
      qa.setMenuText(txt+'...');
      qag.setMenuText(qag._groupname+": "+txt);
  
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
    self.name = self._title = title;
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
    
  def add_to_menu (self,menu,executor=None):
    """adds submenu to menu object (usually of class QPopupMenu).
    """
    submenu = QPopupMenu(menu);
    menu.insertItem(self._title,submenu);
    # create entries for sub-items
    for item in self._items:
      _dprint(3,"adding",item,item.name,"to submenu");
      item.add_to_menu(submenu,executor=executor);

def _make_option_item (namespace,symbol,name,value,default=None,inline=False,doc=None,more=None):
  # if namespace is not specified, set it to 
  # the globals() of the caller of our caller
  if namespace is None:
    namespace = sys._getframe(2).f_globals;
  elif not isinstance(namespace,dict):
    namespace = getattr(namespace,'__dict__',None);
    if namespace is None:
      raise TypeError,"invalid namespace specified";
  # boolean option
  if isinstance(value,bool):
    item = _TDLBoolOptionItem(namespace,symbol,value);
  # list of options
  elif isinstance(value,(list,tuple,dict)):
    item = _TDLListOptionItem(namespace,symbol,value,default=default,more=more);
    setattr(item,'inline',inline);
  else:
    raise TypeError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
  return item;

def TDLMenu (title,*items):
  """this creates and returns a submenu object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  return _TDLSubmenu(title,*items);

def TDLOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None,more=None):
  """this creates and returns an option object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  return _make_option_item(namespace,symbol,name,value,default,inline,doc,more);

def TDLJob (function,name=None,doc=None):
  """this creates and returns a TDL job entry, without adding it to
  anu menu. Should be used inside a TDLRuntimeMenu.""";
  return _TDLJobItem(function,name=name,doc=doc);

def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the compile-time menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more);
  compile_options.append(opt);
  return opt;

def TDLRuntimeOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the runtime menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeJob (function,name=None,doc=None):
  """this creates a TDL job entry, and adds it to the runtime menu.""";
  job = _TDLJobItem(function,name=name,doc=doc);
  runtime_options.append(job);
  return job;
  
def TDLCompileOptions (*opts):
  """this adds a number of entires (created with TDLOption) to the
  compile-time menu""";
  global compile_options;
  compile_options += opts;

def TDLRuntimeOptions (*opts):
  """this adds a number of entires (created with TDLOption or TDLJob) to the
  run-time menu""";
  global runtime_options;
  runtime_options += opts;
  
def TDLCompileMenu (title,*items):
  """This creates a submenu inside the compile-time menu, and adds a number
  of entires (created with TDLOption) to it.""";
  compile_options.append(_TDLSubmenu(title,*items));

def TDLRuntimeMenu (title,*items):
  """This creates a submenu inside the run-time menu, and adds a number
  of entires (created with TDLOption or TDLJob) to it.""";
  runtime_options.append(_TDLSubmenu(title,*items));

