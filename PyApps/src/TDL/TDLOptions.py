from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
import ConfigParser

import traceback
import inspect
import sys
import os.path 
import re

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
_config_write_failed = False;

def save_config ():
  global _config_write_failed;
  try:
    config.write(file(config_file,"w"));
    _config_write_failed = False;
  except IOError:
    if not _config_write_failed:
      _config_write_failed = True;
      _dprint(0,"WARNING: error writing to file",config_file);
      _dprint(0,"TDL options will not be saved");
  
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
  """initializes option list for given script. 
  This also reads in the config file specified by filename. The basename of filename
  is taken, and the .py extension is stripped"""
  global _config_write_failed;
  _config_write_failed = False;
  clear_options();
  global config_section;
  config_section = re.sub('\.py[co]?','',os.path.basename(filename));
  _dprint(1,"config section is now",config_section);
  # for the sake of backwards compatibility, check if there's no config section 
  # corresponding to the base name, but there is one for the full filename, and
  # copy it over if so
  if not config.has_section(config_section) and config.has_section(filename):
    _dprint(0,"you seem to have an old-style tdlconf section named '%s'"%filename);
    _dprint(0,"migrating it to new-style section '%s'"%config_section);
    config.add_section(config_section);
    for option,value in config.items(filename):
      config.set(config_section,option,value);
      _dprint(1,"migrated",option,value);
    config.remove_section(filename);
    save_config();
  
def get_compile_options ():
  return compile_options;
  
def get_runtime_options ():
  return runtime_options;
  
class _TDLBaseOption (object):
  """abstract base class for all option entries""";
  def __init__ (self,name,namespace=None,doc=None):
    self.name    = name;
    self.doc     = doc;
    self.enabled = True;
    self.visible = True;
    # namespace to which this option belongs
    self.namespace = namespace;
    # is this a runtime or a compile-time option?
    self.is_runtime = None;
    # most options have an associated widget or QAction. This is stored here.
    self._qa      = None;
    self._lvitem  = None;
    
  def set_runtime (self,runtime):
    """marks the option as run-time. This is called as soon as it is known
    whether the option is going to be run-time or compile-time.""";
    self.is_runtime = runtime;
    
  def set_qaction (self,qa):
    """sets the option's QAction. Makes it enabled or disabled as appropriate""";
    self._qa = qa;
    if self.doc:
      qa.setToolTip(self.doc);
      qa.setWhatsThis(self.doc);
    qa.setEnabled(self.enabled);
    qa.setVisible(self.visible);
    return qa;
    
  def set_listview_item (self,item):
    """sets the option's QListViewItem. Makes it enabled or disabled as appropriate""";
    self._lvitem = item;
    if self.doc:
      item.setText(2,"     "+self.doc);
    item.setEnabled(self.enabled);
    item.setVisible(self.visible);
    return item;
    
  def enable (self,enabled=True):
    """enables/disables the option. Default behaviour enables/disables the QAction""";
    self.enabled = enabled;
    self._qa and self._qa.setEnabled(enabled);
    self._lvitem and self._lvitem.setEnabled(enabled);
    return enabled;
    
  def disable (self,disabled=True):
    """disables/enables the option. Default behaviour calls enable() with opposite flag""";
    return self.enable(not disabled);
  
  def show (self,visible=True):
    """shows/hides the option. Default behaviour shows/hides the QAction""";
    self.visible = visible;
    self._qa and self._qa.setVisible(visible);
    self._lvitem and self._lvitem.setVisible(visible);
    return visible;
    
  def hide (self,hidden=True):
    """hides/shows the option. Default behaviour calls show() with opposite flag""";
    return self.show(not hidden);
    
  def set_name (self,name):
    """Changes option name""";
    self.name = name;
    
  def set_doc (self,doc):
    """Changes option documentation string""";
    self.doc = doc;

class _TDLOptionSeparator (_TDLBaseOption):
  """This option simply inserts a separator into a menu""";
  def __init__ (self,namespace=None):
    _TDLBaseOption.__init__(self,name=None,namespace=namespace,doc=None);
    
  def add_to_menu (self,menu,executor):
    if not getattr(menu,'_ends_with_separator',True):
      menu.insertSeparator();
    menu._ends_with_separator = True;
    
  def make_listview_item (self,parent,after,executor=None):
    if not getattr(parent,'_ends_with_separator',True):
      item = QListViewItem(parent,after);
      item.setText(0,"-----------");
      item.setEnabled(False);
      parent._ends_with_separator = True;
      return item;
    return None;
  
class _TDLJobItem (_TDLBaseOption):
  def __init__ (self,func,name=None,namespace=None,doc=None):
    _TDLBaseOption.__init__(self,name or func.__name__.replace('_',' '),
                            namespace=namespace,doc=doc);
    self.func = func;
    self.symbol = func.__name__;
    
  def add_to_menu (self,menu,executor):
    """adds entry for job to menu object (usually of class QPopupMenu).
    """
    # create toggle action for bool options
    qa = QAction(self.name,0,menu);
    self.set_qaction(qa);
    qa.setIconSet(pixmaps.gear.iconset());
    self._exec = curry(executor,self.func,self.name);
    QObject.connect(qa,SIGNAL("activated()"),self._exec);
    qa.addTo(menu);
    menu._ends_with_separator = False;
    
  def make_listview_item (self,parent,after,executor=None):
    item = QListViewItem(parent,after);
    item.setText(0,self.name);
    item.setPixmap(0,pixmaps.gear.pm());
    item._on_click = curry(executor,self.func,self.name);
    item._close_on_click = True;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
  
class _TDLOptionItem(_TDLBaseOption):
  def __init__ (self,namespace,symbol,value,config_name=None,name=None,doc=None):
    _TDLBaseOption.__init__(self,name,namespace=namespace,doc=doc);
    # config_name specifies the configuration file entry
    self.config_name = config_name or symbol;
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
    self._when_changed_callbacks = [];
    
  def _set (self,value):
    self.value = self.namespace[self.symbol] = value;
    # be anal about whether the _when_changed_callbacks attribute is initialized,
    #as _set may have been called before the constructor
    for callback in getattr(self,'_when_changed_callbacks',[]):
      callback(value);
    
  def get_str (self):
    return self.item_str(self.value);
      
  def item_str (item):
    """converts item to string representation.
    If item is a named symbol, uses the name, else uses str()""";
    return getattr(item,'__name__',None) or str(item);
  item_str = staticmethod(item_str);
  
  def when_changed (self,callback):
    """registers a callback which will be called whenever the item is changed.
    Immediately calls the callback as well""";
    self._when_changed_callbacks.append(callback);
    callback(self.value);

class _TDLBoolOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,config_name=None,name=None,doc=None):
    _TDLOptionItem.__init__(self,namespace,symbol,value,config_name=config_name,name=name,doc=doc);
    try:
      value = bool(config.getint(config_section,self.config_name));
      self._set(value);
      _dprint(1,"read",symbol,"=",value,"from config");
    except:
      _dprint(1,"error reading",symbol,"from config");
      if _dbg.verbose > 0:
        traceback.print_exc();
    
  def set (self,value):
    value = bool(value);
    set_config(self.config_name,int(value));
    self._set(value);

  def add_to_menu (self,menu,executor=None):
    """adds entry for option to menu object (usually of class QPopupMenu).
    """
    # create toggle action for bool options
    qa = QAction(self.name or self.symbol,0,menu);
    self.set_qaction(qa);
    qa.setToggleAction(True);
    qa.setOn(self.value);
    QObject.connect(qa,SIGNAL("toggled(bool)"),self.set);
    qa.addTo(menu);
    menu._ends_with_separator = False;
    
  def make_listview_item (self,parent,after,executor=None):
    item = QCheckListItem(parent,after,self.name,QCheckListItem.CheckBox);
    item.setText(0,self.name);
    item.setOn(self.value);
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
    
class _TDLListOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,default=None,more=None,
                     config_name=None,name=None,doc=None):
    _TDLOptionItem.__init__(self,namespace,symbol,None,config_name=config_name,name=name,doc=doc);
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
      def1 = config.get(config_section,self.config_name);
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
      if more is not None:
        self.set_custom_value(self.get_option(self.selected));
    # set the value
    self._set(self.get_option(self.selected));

  def num_options (self):
    return len(self.option_list);
    
  def get_option (self,num):
    return self.option_list[num];
    
  def get_option_str (self,num):
    return self.option_list_str[num];
    
  def get_option_desc (self,num):
    return self.option_list_desc[num];
    
  def set (self,ivalue):
    self.selected = value = int(ivalue);
    self._set(self.get_option(value));
    set_config(self.config_name,self.get_option_str(value));
    
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
    self.set_qaction(qag);
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
        qa.setWhatsThis(self.doc);
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

  def make_listview_item (self,parent,after,executor=None):
    """makes a listview entry for the item""";
    item = QListViewItem(parent,after);
    item.setText(0,self.name+":");
    item.setText(1,self.get_option_desc(self.selected));
    # create QPopupMenu for available options
    self._submenu = submenu = QPopupMenu(item.listView());
    submenu.setCheckable(True);
    self._submenu_items = [];
    self._submenu_editor = None;
    for ival in range(self.num_options()):
      if self._more is not None and ival == self.num_options()-1:
        box = QHBox(self._submenu);
        spacer = QLabel("",box);
        spacer.setMinimumWidth(32);
        spacer.setBackgroundMode(Qt.PaletteButton);
        #for color in self._submenu.paletteBackgroundColor(),spacer.paletteBackgroundColor():
        #  print color.red(),color.green(),color.blue();
        self._submenu_editor = QLineEdit(self.get_option_desc(ival),box);
        self._submenu_editor.setBackgroundMode(Qt.PaletteMidlight);
        if self._more is int:
          self._submenu_editor.setValidator(QIntValidator(self._submenu_editor));
        elif self._more is float:
          self._submenu_editor.setValidator(QDoubleValidator(self._submenu_editor));
        # connect signal
        QObject.connect(self._submenu_editor,SIGNAL("returnPressed()"),
                        self._set_submenu_custom_value);
        submenu.insertItem("Custom:",ival);
        submenu.insertItem(box);
      else:
        submenu.insertItem(self.get_option_desc(ival),ival);
      submenu.setItemChecked(ival,ival==self.selected);
    QObject.connect(submenu,SIGNAL("activated(int)"),self._activate_submenu_item);
    # make menu pop up when item is pressed
    item._on_click = self._popup_menu;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
      
  def _popup_menu (self):
    # figure out where to pop up the menu
    listview = self._lvitem.listView();
    pos = listview.itemRect(self._lvitem).topLeft();
    pos.setX(pos.x()+listview.columnWidth(0));    # position in listview
    # now map to global coordinates
    self._submenu.popup(listview.mapToGlobal(pos));
    
  def _activate_submenu_item (self,selected):
    self.set(selected);
    for ival in range(self.num_options()):
      self._submenu.setItemChecked(ival,ival==selected);
    self._lvitem.setText(1,self.get_option_desc(selected));

  def _set_submenu_custom_value (self):
    # get value from editor
    value = self._submenu_editor.text();
    if self._more is int:
      value = int(value);
    elif self._more is float:
      value = float(value);
    # set as custom value
    self.set_custom_value(value);
    # update menu
    self._activate_submenu_item(self.num_options()-1);
    self._submenu.close();

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
      
class _TDLSubmenu (_TDLBaseOption):
  def __init__ (self,title,namespace,*items):
    _TDLBaseOption.__init__(self,name=title,namespace=namespace);
    """Creates a submenu from the given list of options.
    is_runtime is True for runtime options, False for compile-time options.
    Note that an item may be specified as None, to get a separator.""";
    self.name = self._title = title;
    self._items = items;
    self._parent_menu = self._menu_id = None;
    
  def set_runtime (self,runtime):
    # if option not previously marked as runtime or compile-time, then we need to process
    # the items list
    if self.is_runtime is None:
      _dprint(3,"menu",self._title,"runtime is",runtime);
      # process the items as follows:
      # 1. If the item is None, it is a separator
      # 2. If the item is a string, it is a doc string
      # 2. If the item is an option:
      #    Check the global run-time and compile-time option lists and remove item
      #    from them, if found. This allows us to include items into a menu with
      #    TDLCompileOption or TDLRuntimeOption directly.
      # 3. check if item is a module or a dict. Encapsulate all options
      #    from that module or dict if so. Here we need to know if it is runtime 
      #    or compile-time items that need to be encapsulated.
      itemlist = self._items;
      self._items = [];
      for item in itemlist:
        # None is a separator
        if item is None:
          _dprint(3,"menu: separator");
          item = _TDLOptionSeparator(namespace=self.namespace);
          item.set_runtime(runtime);
          self._items.append(item);
        # strings are documentation
        elif isinstance(item,str):
          self.set_doc(item);
        # item is an option: add to list, steal from global lists
        elif isinstance(item,_TDLBaseOption):
          _dprint(3,"menu: ",item.name);
          for option_list in (compile_options,runtime_options):
            steal_items = [];
            for i,item0 in enumerate(option_list):
              if item is item0:
                steal_items.insert(0,i);
            # delete stolen items -- they've been listed in reverse order
            for i in steal_items:
              del option_list[i];
          item.set_runtime(runtime);
          self._items.append(item);
        # item is a namespace: steal items from that namespace
        else:  
          namespace = None;
          if isinstance(item,dict):
            _dprint(3,"menu: stealing items from ",item);
            namespace = item;
          else:
            _dprint(3,"menu: stealing items from ",getattr(item,'__name__','?'));
            namespace = getattr(item,'__dict__',None);
            if not namespace:
              raise TypeError,"invalid item in option menu '%s'"%self._title;
          # now steal items from this namespace's runtime or compile-time options
          if runtime:
            option_list = runtime_options;
          else:
            option_list = compile_options;
          steal_items = [];
          for i,item0 in enumerate(option_list):
            if isinstance(item0,_TDLBaseOption) and item0.namespace is namespace:
              _dprint(3,"menu: stealing ",item0.name);
              steal_items.insert(0,i);
              item0.set_runtime(runtime);
              self._items.append(item0);
          # delete stolen items
          for i in steal_items:
            del option_list[i];
    # call parent's function
    _TDLBaseOption.set_runtime(self,runtime);
  
  def enable (self,enabled=True):
    _TDLBaseOption.enable(self,enabled);
    if self._parent_menu:
      self._parent_menu.setItemEnabled(self._menu_id,enabled);
    return enabled;
    
  def show (self,visible=True):
    _TDLBaseOption.show(self,visible);
    self.visible = visible;
    if self._parent_menu:
      self._parent_menu.setItemVisible(self._menu_id,visible);
    return visible;
    
  def add_to_menu (self,menu,executor=None):
    """adds submenu to menu object (usually of class QPopupMenu)."""
    self._parent_menu = menu;
    submenu = QPopupMenu(menu);
    if self.doc:
      QToolTip.add(submenu,self.doc);
      QWhatsThis.add(submenu,self.doc);
    self._menu_id = menu.insertItem(self._title,submenu);
    self.enable(self.enabled);
    self.show(self.visible);
    populate_option_menu(submenu,self._items,executor=executor);
    menu._ends_with_separator = False;
    
  def make_listview_item (self,parent,after,executor=None):
    """makes a listview entry for the menu""";
    item = QListViewItem(parent,after);
    item.setText(0,self.name);
    item.setExpandable(True);
    # loop over items
    previtem = None;
    for subitem in self._items:
      _dprint(3,"adding",subitem,getattr(subitem,'name',''),"to item",self.name);
      subitem = subitem or _TDLOptionSeparator();
      previtem = subitem.make_listview_item(item,previtem,executor=executor) or previtem;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
        
def populate_option_menu (menu,option_items,executor=None):
  """static helper method to populate a menu with the given list of items""";
  # create entries for sub-items
  for item in option_items:
    _dprint(3,"adding",item,getattr(item,'name',''),"to submenu",menu);
    item = item or _TDLOptionSeparator();
    item.add_to_menu(menu,executor=executor);

def populate_option_listview (menu,option_items,executor=None):
  listview = QListView(menu);
  listview.addColumn("name");
  listview.addColumn("value");
  listview.addColumn("description",100);
  listview.setRootIsDecorated(True);
  listview.setShowToolTips(True);
  listview.setSorting(-1);
  listview.header().hide();
  listview.viewport().setBackgroundMode(Qt.PaletteMidlight);
  # populate listview
  previtem = None;
  for item in option_items:
    previtem = item.make_listview_item(listview,previtem,executor=executor);
  # add callbacks
  QObject.connect(listview,SIGNAL("clicked(QListViewItem*)"),_process_listview_click);
  # add to menu
  menu.insertItem(listview);

def _process_listview_click (item):
  """helper function to process a click on a listview item. Meant to be connected
  to the clicked() signal of a QListView""";
  on_click = getattr(item,'_on_click',None);
  if on_click:
    on_click();
  if getattr(item,'_close_on_click',False):
    item.listView().parent().close();
  
  
def _make_option_item (namespace,symbol,name,value,default=None,
                       inline=False,doc=None,more=None,runtime=False):
  # if namespace is not specified, set it to the globals() of the caller of our caller
  if namespace is None:
    # figure out filename of caller frame
    namespace = sys._getframe(2).f_globals;
    filename = inspect.getframeinfo(sys._getframe(2))[0];
    namespace_name = os.path.basename(filename).split('.')[0];
  # else namespace is a dict
  elif isinstance(namespace,dict):
    namespace_name = None;
  # else namespace must have a __dict__ attribute
  else:
    namespace_name = getattr(namespace,'__name__',None);
    namespace = getattr(namespace,'__dict__',None);
    if namespace is None:
      raise TypeError,"invalid namespace specified";
  # get name for config file, by prepending the namespace
  if namespace_name and namespace_name != config_section:
    config_name = ".".join((namespace_name,symbol));
  else:
    config_name = symbol;
  # boolean option
  if isinstance(value,bool):
    item = _TDLBoolOptionItem(namespace,symbol,value,config_name=config_name);
  # list of options
  elif isinstance(value,(list,tuple,dict)):
    item = _TDLListOptionItem(namespace,symbol,value,
                              default=default,more=more,config_name=config_name);
    setattr(item,'inline',inline);
  else:
    raise TypeError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
  item.set_runtime(runtime);
  return item;




def TDLMenu (title,*items):
  """this creates and returns a submenu object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  namespace = sys._getframe(1).f_globals;
  return _TDLSubmenu(title,namespace,*items);

def TDLOption (symbol,name,value,default=None,
               inline=False,doc=None,namespace=None,more=None,runtime=False):
  """this creates and returns an option object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  item = _make_option_item(namespace,symbol,name,value,default,inline,doc,more,runtime);
  return item;

def TDLJob (function,name=None,doc=None):
  """this creates and returns a TDL job entry, without adding it to
  anu menu. Should be used inside a TDLRuntimeMenu.""";
  namespace = sys._getframe(1).f_globals;
  return _TDLJobItem(function,name=name,namespace=namespace,doc=doc);

def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the compile-time menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more,False);
  compile_options.append(opt);
  return opt;

def TDLCompileOptionSeparator ():
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(namespace=namespace);
  compile_options.append(opt);
  return opt;

def TDLRuntimeOption (symbol,name,value,default=None,
                      inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the runtime menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more,True);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeOptionSeparator ():
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(namespace=namespace);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeJob (function,name=None,doc=None):
  """this creates a TDL job entry, and adds it to the runtime menu.""";
  job = _TDLJobItem(function,name=name,doc=doc);
  job.set_runtime(True);
  runtime_options.append(job);
  return job;
  
def TDLCompileOptions (*opts):
  """this adds a number of entries (created with TDLOption) to the
  compile-time menu""";
  for opt in opts:
    opt and opt.set_runtime(False);
  global compile_options;
  compile_options += opts;

def TDLRuntimeOptions (*opts):
  """this adds a number of entries (created with TDLOption or TDLJob) to the
  run-time menu""";
  global runtime_options;
  for opt in opts:
    opt and opt.set_runtime(True);
  runtime_options += opts;
  
def TDLCompileMenu (title,*items):
  """This creates a submenu inside the compile-time menu, and adds a number
  of entires (created with TDLOption) to it.""";
  namespace = sys._getframe(1).f_globals;
  menu = _TDLSubmenu(title,namespace,*items);
  menu.set_runtime(False);
  compile_options.append(menu);
  return menu;

def TDLRuntimeMenu (title,True,*items):
  """This creates a submenu inside the run-time menu, and adds a number
  of entires (created with TDLOption or TDLJob) to it.""";
  namespace = sys._getframe(1).f_globals;
  menu = _TDLSubmenu(title,namespace,*items);
  menu.set_runtime(True);
  runtime_options.append(menu);
  return menu;

