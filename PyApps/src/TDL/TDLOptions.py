from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
import ConfigParser

import traceback
import inspect
import sys
import os.path 
import re
import glob


# import Qt but ignore failures since we can also run stand-alone
try:
  from qt import *
except:
  pass;

_dbg = verbosity(0,name='tdlopt');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# current config section, this is set to the script name by init_options()
config_section = "default";
# config file
config_file = ".tdl.conf";
# flag: write failed (so that we only report it once)
_config_write_failed = False;

class _OurConfigParser (ConfigParser.RawConfigParser):
  """extend the standard ConfigParser with a 'sticky' filename""";
  def __init__ (self,*args):
    ConfigParser.RawConfigParser.__init__(self,*args);
    self._file = config_file;
  def read (self,filename):
    self._file = filename;
    self.reread();
  def reread (self):
    _dprint(1,"reading config file",self._file);
    ConfigParser.RawConfigParser.read(self,self._file);
  def rewrite (self):
    ConfigParser.RawConfigParser.write(self,file(self._file,"w"));

# create global config object
config = _OurConfigParser();

def save_config ():
  global _config_write_failed;
  try:
    config.rewrite();
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

compile_options = [];
runtime_options = [];

def clear_options ():
  global compile_options;
  global runtime_options;
  compile_options = [];
  runtime_options = [];
  
def init_options (filename):
  """initializes option list for given script.""" 
  # re-read config file
  global config;
  config.reread();
  global _config_write_failed;
  _config_write_failed = False;
  # init stuff
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
  def __init__ (self,name,namespace=None,owner=None,doc=None):
    if not isinstance(name,str):
      raise TypeError,"option name must be a string";
    self.name    = name;
    self.doc     = doc;
    self.enabled = True;
    self.visible = True;
    # namespace in which the option's symbol is set
    self.namespace = namespace;
    # name of module that owns this option, or None for the top-level TDL script
    self.owner = None;
    # is this a runtime or a compile-time option?
    self.is_runtime = None;
    # most options have an associated widget or QAction. This is stored here.
    self._qa      = None;
    self._lvitem  = None;
    
  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu. owner is the name of a module to
    which this option belongs, or None for the top-level script.
    runtime is True if option is runtime.""";
    _dprint(3,"item '%s' owner '%s' runtime %d"%(self.name,owner,int(runtime)));
    self.owner = owner;
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
    _dprint(3,"enable item",self.name,":",visible);
    self.enabled = enabled;
    self._qa and self._qa.setEnabled(enabled);
    self._lvitem and self._lvitem.setEnabled(enabled);
    return enabled;
    
  def disable (self,disabled=True):
    """disables/enables the option. Default behaviour calls enable() with opposite flag""";
    return self.enable(not disabled);
  
  def show (self,visible=True):
    """shows/hides the option. Default behaviour shows/hides the QAction""";
    _dprint(3,"show item",self.name,":",visible);
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
    if self._lvitem:
      self._lvitem.setText(2,doc);

class _TDLOptionSeparator (_TDLBaseOption):
  """This option simply inserts a separator into a menu""";
  def __init__ (self,namespace=None):
    _TDLBaseOption.__init__(self,name=None,namespace=namespace,doc=None);
    
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
    _TDLBaseOption.__init__(self,name or symbol,namespace=namespace,doc=doc);
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
    
  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLBaseOption.init(self,owner,runtime);
    if owner:
      self.config_name = '.'.join((owner,self.config_name));
    
  def _set (self,value):
    _dprint(1,"setting",self.name,"=",value);
    self.value = self.namespace[self.symbol] = value;
    # be anal about whether the _when_changed_callbacks attribute is initialized,
    # as _set may have been called before the constructor
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
    self._set(value);
  
  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    try:
      value = bool(config.getint(config_section,self.config_name));
      self._set(value);
      _dprint(1,"read",self.config_name,"=",value,"from config");
    except:
      _dprint(1,"error reading",self.config_name,"from config");
      if _dbg.verbose > 2:
        traceback.print_exc();
    
  def set (self,value,save=True):
    value = bool(value);
    if save:
      set_config(self.config_name,int(value));
    self._set(value);

  def make_listview_item (self,parent,after,executor=None):
    item = QCheckListItem(parent,after,self.name,QCheckListItem.CheckBox);
    item.setText(0,self.name);
    item.setOn(self.value);
    item._on_click = item._on_press = self._check_item;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
  
  def _check_item (self):
    self.set(self._lvitem.isOn());
    
class TDLFileSelect (object):
  def __init__ (self,filenames="",default=None,exist=True):
    self.filenames  = str(filenames);
    self.exist      = exist;
    self.default    = default;
    
class TDLDirSelect (TDLFileSelect):
  def __init__ (self,filenames="",default=None):
    self.filenames  = str(filenames);
    self.default    = default;
    
class _TDLFileOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,filespec,
                default=None,config_name=None,name=None,doc=None):
    _TDLOptionItem.__init__(self,namespace,symbol,'',
                            config_name=config_name,name=name,doc=doc);
    self._filespec = filespec;
    self._validator = lambda dum:True;
    # no value in config -- try default
    if filespec.default:
      self._set(str(filespec.default));
    else:
      self._set(None);
    
  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    try:
      value = config.get(config_section,self.config_name);
      if self._validator(value):
        self._set(value);
      _dprint(1,"read",self.config_name,"=",value,"from config");
    except:
      _dprint(1,"error reading",self.config_name,"from config");
      if _dbg.verbose > 2:
        traceback.print_exc();
      # no value in config -- try default
      if self._filespec.default:
        self._set(str(self._filespec.default));
      # else try to find first matching file
      else:
        for pattern in self._filespec.filenames.split(" "):
          for filename in glob.glob(pattern):
            if self._validator(filename):
              self._set(filename);
              return;
    
  def set_validator (self,validator):
    self._validator = validator;
    if self.value and not self._validator(self.value):
      self.set(None);
      
  def set (self,value,save=True):
    value = str(value);
    if save:
      set_config(self.config_name,value);
    self._set(value);
    
  def enable (enabled=True):
    _TDLOptionItem.enable(enabled);
    if not enabled:
      self._file_dialog.hide();
  
  def show (visible=True):
    _TDLOptionItem.show(visible);
    if not visible:
      self._file_dialog.hide();
      
  class FileDialog (QFileDialog):
    def done (self,result):
      if result:
        self.emit(PYSIGNAL("selectedFile()"),(self.selectedFile(),));
      QFileDialog.done(self,result);

  def make_listview_item (self,parent,after,executor=None):
    item = QListViewItem(parent,after);
    item.setText(0,self.name+":");
    item.setText(1,os.path.basename(self.value.rstrip("/")));
    # create file dialog
    self._file_dialog = file_dialog = \
        self.FileDialog(".",self._filespec.filenames,item.listView());
    if isinstance(self._filespec,TDLDirSelect):
      file_dialog.setMode(QFileDialog.DirectoryOnly);
    else:
      if self._filespec.exist:
        file_dialog.setMode(QFileDialog.ExistingFile);
      else:
        file_dialog.setMode(QFileDialog.AnyFile);
    QObject.connect(file_dialog,PYSIGNAL("selectedFile()"),self._select_file);
    # make file selection dialog pop up when item is pressed
    item._on_click = self._show_dialog;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
      
  def _show_dialog (self):
    self._file_dialog.rereadDir();
    self._file_dialog.show();
    
  def _select_file (self,name):
    name = str(name);
    if self._validator(name):
      self._lvitem.setText(1,os.path.basename(name.rstrip("/")));
      self.set(name);
    
class _TDLListOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,default=None,more=None,
                     config_name=None,name=None,doc=None):
    _TDLOptionItem.__init__(self,namespace,symbol,None,config_name=config_name,name=name,doc=doc);
    if more not in (None,int,float,str):
      raise ValueError,"'more' argument to list options must be 'None', 'int', 'float' or 'str'"
    if not more and not value:
      raise ValueError,"empty option list, and 'more=' not specified";
    self._more = more;
    self._custom_value = (None,'');
    self.set_option_list(value,conserve_selection=False);
    self.inline = False;
    # default validator accepts everything
    self._validator = lambda x:x is not None;
    # verify default arg
    if default is None:
      default = 0;
    else:
      # try to treat as a list value
      try:
        default = self.option_list.index(default);
      except:
      # no, treat as an integer index into the list
        if not isinstance(default,int):
          raise TypeError,"'default': list index expected";
        elif default < 0 or default >= len(self.option_list):
          raise ValueError,"'default': index out of range";
    # set the default value
    self.set(default,save=False);
    
  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    select = None;
    try:
      value = config.get(config_section,self.config_name);
      _dprint(1,"read",self.config_name,"=",value,"from config");
      # look up value in list
      try:
        select = self.option_list_str.index(value);
      except:
        if self._more is None or not self._validator(value):
          _dprint(1,value,"is an illegal value for",self.name);
        # add configured symbol to list of values
        else:
          try:
            value = self._more(value);
          except:
            _dprint(1,value,"is an illegal value for",self.name);
          else:
            self.set_custom_value(value);
            select = len(self.option_list)-1;
    except:
      _dprint(1,"error reading",self.config_name,"from config");
      if _dbg.verbose > 2:
        traceback.print_exc();
    # if select was set, we have a legal value
    if select is not None:
      self.set(select,save=False);
    
  def set_validator (self,validator):
    self._validator = validator;

  def num_options (self):
    return len(self.option_list);
    
  def get_option (self,num):
    return self.option_list[num];
    
  def get_option_str (self,num):
    return self.option_list_str[num];
    
  def get_option_desc (self,num):
    return self.option_list_desc[num];
  
  def set_option_list (self,opts,select=None,conserve_selection=True):
    """changes the option list. If conserve_selection is True, attempts
    to preserve the current selection""";
    if select is None and conserve_selection:
      selection = self.get_option_str(self.selected);
    if isinstance(opts,(list,tuple)):
      self.option_list = list(opts);
      self.option_list_str = map(lambda x:self.item_str(x),opts);
      self.option_list_desc = list(self.option_list_str);
    elif isinstance(opts,dict):
      self.option_list = list(opts.iterkeys());
      self.option_list_str = map(lambda x:self.item_str(x),opts.iterkeys());
      self.option_list_desc = map(lambda x:str(x),opts.itervalues());
    else:
      raise TypeError,"TDLListOptionItem: list or dict of options expected";
    # add custom value
    if self._more is not None:
      self.option_list.append(self._custom_value[0]);
      self.option_list_str.append(self._custom_value[1]);
      self.option_list_desc.append(self._custom_value[1]);
    # re-select previous value, or selected value
    if select is not None:
      self.set(select,save=False);
    elif conserve_selection:
      try:
        index = self.option_list_str.index(selection);
        self.set(index,save=False);
      except:
        self.set(0);
        
  def set_value (self,value,save=True):
    """selects given value in list. If value is not in list, sets
    custom value if possible"""
    try:
      index = self.option_list.index(value);
      self.set(index,save=save);
    except:
      if self._more is None:
        raise ValueError,"%s is not a legal value for option '%s'"%(value,self.name);
      self.set_custom_value(value,select=True);
  
  def set (self,ivalue,save=True):
    """selects value #ivalue in list""";
    self.selected = value = int(ivalue);
    self._set(self.get_option(value));
    if self._lvitem:
      self._lvitem.setText(1,self.get_option_desc(value));
    if save:
      set_config(self.config_name,self.get_option_str(value));
    
  def set_custom_value (self,value,select=True):
    if self._more is None:
      raise TypeError,"can't set custom value for this option list, since it was not created with a 'more' argument";
    self._custom_value = (value,str(value));
    self.option_list[-1] = value;
    self.option_list_str[-1] = self.option_list_desc[-1] = str(value);
    if select:
      self.set(len(self.option_list)-1);
    
  def make_listview_item (self,parent,after,executor=None):
    """makes a listview entry for the item""";
    _dprint(3,"making listview item for",self.name);
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
    # validate custom value
    if self._more is not None and selected == self.num_options()-1:
      if not self._validator(self._custom_value[0]):
        return;
    self.set(selected);
    for ival in range(self.num_options()):
      self._submenu.setItemChecked(ival,ival==selected);
    self._lvitem.setText(1,self.get_option_desc(selected));

  def _set_submenu_custom_value (self):
    # get value from editor
    value = str(self._submenu_editor.text());
    if self._more is int:
      value = int(value);
    elif self._more is float:
      value = float(value);
    if self._validator(value):
      # set as custom value
      self.set_custom_value(value,select=True);
      # update menu
      self._activate_submenu_item(self.num_options()-1);
      self._submenu.close();
    else:  # invalid value
      self._submenu_editor.setText(self._custom_value[1]);
      if self._custom_value[0] is None:
        self.set(0);

class _TDLSubmenu (_TDLBoolOptionItem):
  def __init__ (self,title,*items,**kw):
    """Creates a submenu from the given list of option items.
    Note that an item may be specified as None, to get a separator.
    Optional keywords:
      doc: documentation string
      open: if True, menu starts out open (this is only a hint)
      toggle: if to a symbol name, the menu entry itself has an associated
              checkbox, and acts as a TDLBoolItem. Initial state is taken from
              the 'open' keyword.
      namespace: overrides the namespace passed to constructor -- only
              makes sense if toggle is set as well.
    """;
    doc = kw.get('doc');
    self._is_open = kw.get('open',False);
    self._toggle = kw.get('toggle','');
    namespace = kw.get('namespace');
    # depth is 2 (this frame, TDLxxxMenu frame, caller frame)
    namespace,config_name = _resolve_namespace(namespace,self._toggle,calldepth=2);
    # somewhat kludgy, but what the hell: if toggle is set, init our BoolOptionItem
    # parent, else only init the TDLBaseOption parent
    if self._toggle:
      _TDLBoolOptionItem.__init__(self,namespace,self._toggle,self._is_open,
                                  name=title,config_name=config_name,doc=doc);
      self._old_value = self._is_open;
    else:
      _TDLBaseOption.__init__(self,name=title,namespace=namespace,doc=doc);
    self._title = title;
    self._items0 = items;
    self._items  = None;
    
  def init (self,owner,runtime):
    _dprint(3,"menu",self._title,"owner",owner);
    # in toggle mode, init BoolItem parent to read value from config
    if self._toggle:
      _TDLBoolOptionItem.init(self,owner,runtime);
    else:
      _TDLBaseOption.init(self,owner,runtime);
    # if option not previously initialized, then we need to process the items list
    if self._items is None:
      _dprint(3,"menu",self._title,"runtime is",runtime);
      # process the items as follows:
      # 1. If the item is None, it is a separator
      # 2. If the item is an option:
      #    Check the global run-time and compile-time option lists and remove item
      #    from them, if found. This allows us to include items into a menu with
      #    TDLCompileOption or TDLRuntimeOption directly.
      # 3. check if item is a module or a dict. Encapsulate all options
      #    from that module or dict if so. Here we need to know if it is runtime 
      #    or compile-time items that need to be encapsulated.
      self._items = [];
      for item in self._items0:
        # None is a separator
        if item is None:
          _dprint(3,"menu: separator");
          item = _TDLOptionSeparator(namespace=self.namespace);
          item.set_runtime(runtime);
          self._items.append(item);
        # item is an option: add to list, steal from global lists
        elif isinstance(item,_TDLBaseOption):
          _dprint(3,"menu: ",item.name);
          self._steal_items(False,lambda item0:item is item0);
          self._steal_items(True,lambda item0:item is item0);
          item.init(owner,runtime);
          self._items.append(item);
        # item is a module: steal items from that module
        elif inspect.ismodule(item):
          owner = os.path.basename(item.__file__).split('.')[0];
          _dprint(3,"menu: stealing items from module",owner);
          # now steal items from this namespace's runtime or compile-time options
          self._steal_items(runtime,lambda item0:item0.owner == owner);
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
              raise TypeError,"invalid item type '%s' in option menu '%s'"%(type(item),self._title);
          # now steal items from this namespace's runtime or compile-time options
          self._steal_items(runtime,lambda item0:item0.namespace is namespace);
      self._items0 = None;
  
  def _steal_items (self,runtime,predicate):
    """helper function: steals items matching the given predicate""";
    if runtime:
      option_list = runtime_options;
    else:
      option_list = compile_options;
    steal_items = [];
    for i,item0 in enumerate(option_list):
      if isinstance(item0,_TDLBaseOption) and predicate(item0):
        _dprint(3,"menu: stealing ",item0.name);
        steal_items.insert(0,i);
        self._items.append(item0);
    # delete stolen items
    for i in steal_items:
      del option_list[i];
  
  def expand (self,expand=True):
    self._is_open = expand;
    if self._lvitem:
      self._lvitem.setOpen(expand);
      
  def set (self,value):
    _TDLBoolOptionItem.set(self,value);
    # open/close menu when going from unset to set and vice versa
    if self._lvitem and self._old_value != value:
      self._lvitem.setOpen(value);
    self._old_value = value;
    
  def make_listview_item (self,parent,after,executor=None):
    """makes a listview entry for the menu""";
    if self._items is None:
      raise RuntimeError,"option menu '%s' not initialized, this should be impossible!"%self._title;
    if self._toggle:
      item = QCheckListItem(parent,after,self._title,QCheckListItem.CheckBox);
      item.setExpandable(True);
      self._old_value = self.value;
      item.setOn(self.value);
      item.setOpen(self.value);
      item._on_click = item._on_press = self._check_item;
    else:
      item = QListViewItem(parent,after);
      item.setText(0,self._title);
      item.setExpandable(True);
      item.setOpen(self._is_open);
    # loop over items
    previtem = None;
    for subitem in self._items:
      _dprint(3,"adding",subitem,getattr(subitem,'name',''),"to item",self.name);
      subitem = subitem or _TDLOptionSeparator();
      previtem = subitem.make_listview_item(item,previtem,executor=executor) or previtem;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
    item._on_click = item._on_press = self._check_item;
    parent._ends_with_separator = False;
    return self.set_listview_item(item);
    
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
  QObject.connect(listview,SIGNAL("pressed(QListViewItem*)"),_process_listview_press);
  QObject.connect(listview,SIGNAL("returnPressed(QListViewItem*)"),_process_listview_click);
  QObject.connect(listview,SIGNAL("spacePressed(QListViewItem*)"),_process_listview_click);
  QObject.connect(listview,SIGNAL("doubleClicked(QListViewItem*,const QPoint &, int)"),_process_listview_click);
  # add to menu
  menu.insertItem(listview);

def _process_listview_click (item,*dum):
  """helper function to process a click on a listview item. Meant to be connected
  to the clicked() signal of a QListView""";
  on_click = getattr(item,'_on_click',None);
  if on_click:
    on_click();
  if getattr(item,'_close_on_click',False):
    item.listView().parent().close();
  
def _process_listview_press (item,*dum):
  """helper function to process a press on a listview item. Meant to be connected
  to the pressed() signal of a QListView""";
  on_click = getattr(item,'_on_press',None);
  if on_click:
    on_click();

def _resolve_owner (calldepth=2):
  filename = inspect.getframeinfo(sys._getframe(calldepth+1))[0];
  filename = os.path.basename(filename).split('.')[0];
  # if owner matches our config section, return None
  if filename == config_section:
    return None;
  else:
    return filename;

def _resolve_namespace (namespace,symbol,calldepth=2):
  # if namespace is not specified, set it to the globals() of the caller of our caller
  if namespace is None:
    # figure out filename of caller frame -- skip frames in this file
    namespace = sys._getframe(calldepth+1).f_globals;
  # else namespace is a dict
  elif isinstance(namespace,dict):
    namespace_name = None;
  # else namespace must have a __dict__ attribute
  else:
    # form options inside an explcit namespace (e.g. inside an object), prepend the 
    # name of the object to the config name
    prefix = getattr(namespace,'tdloption_namespace',None) or \
             getattr(namespace,'__name__',None) or \
             type(namespace).__name__;
    _dprint(2,"option",symbol,"namespace is",namespace,", prefix is",prefix);
    namespace = getattr(namespace,'__dict__',None);
    if namespace is None:
      raise TypeError,"invalid namespace specified";
    # get name for config file, by prepending the namespace name
    if prefix:
      symbol = ".".join((prefix,symbol));
  return namespace,symbol;
  
def _make_option_item (namespace,symbol,name,value,default=None,
                       inline=False,doc=None,more=None,runtime=None):
  # resolve namespace based on caller
  # depth is 2 (this frame, TDLxxxOption frame, caller frame)
  namespace,config_name = _resolve_namespace(namespace,symbol,calldepth=2);
  # boolean option
  if isinstance(value,bool):
    item = _TDLBoolOptionItem(namespace,symbol,value,config_name=config_name);
  # list of options
  elif isinstance(value,(list,tuple,dict)):
    item = _TDLListOptionItem(namespace,symbol,value,
                              default=default,more=more,config_name=config_name);
    setattr(item,'inline',inline);
  elif isinstance(value,TDLFileSelect):
    item = _TDLFileOptionItem(namespace,symbol,value);
  else:
    raise TypeError,"Illegal type for TDL option: "+type(value).__name__;
  item.set_name(name);
  item.set_doc(doc);
  if runtime is not None:
    # resolve owner
    # depth is 2 (this frame, TDLxxxOption frame, caller frame)
    item.init(_resolve_owner(calldepth=2),runtime);
  return item;

def TDLMenu (title,*items,**kw):
  """this creates and returns a submenu object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  return _TDLSubmenu(title,*items,**kw);

def TDLOption (symbol,name,value,default=None,
               inline=False,doc=None,namespace=None,more=None):
  """this creates and returns an option object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  item = _make_option_item(namespace,symbol,name,value,default,inline,doc,more);
  return item;

def TDLJob (function,name=None,doc=None):
  """this creates and returns a TDL job entry, without adding it to
  anu menu. Should be used inside a TDLRuntimeMenu.""";
  namespace = sys._getframe(1).f_globals;
  return _TDLJobItem(function,name=name,namespace=namespace,doc=doc);

def TDLCompileOption (symbol,name,value,default=None,inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the compile-time menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more,runtime=False);
  compile_options.append(opt);
  return opt;

def TDLCompileOptionSeparator ():
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(namespace=namespace);
  # owner is at depth 1 -- our caller
  opt.init(_resolve_owner(calldepth=1),False);
  compile_options.append(opt);
  return opt;

def TDLRuntimeOption (symbol,name,value,default=None,
                      inline=False,doc=None,namespace=None,more=None):
  """this creates an option object and adds it to the runtime menu""";
  opt = _make_option_item(namespace,symbol,name,value,default,inline,doc,more,runtime=True);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeOptionSeparator ():
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(namespace=namespace);
  # owner is at depth 1 -- our caller
  opt.init(_resolve_owner(calldepth=1),True);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeJob (function,name=None,doc=None):
  """this creates a TDL job entry, and adds it to the runtime menu.""";
  job = _TDLJobItem(function,name=name,doc=doc);
  # owner is at depth 1 -- our caller
  opt.init(_resolve_owner(calldepth=1),True);
  runtime_options.append(job);
  return job;
  
def TDLCompileOptions (*opts):
  """this adds a number of entries (created with TDLOption) to the
  compile-time menu""";
  # owner is at depth 1 -- our caller
  owner = _resolve_owner(calldepth=1);
  for opt in opts:
    opt and opt.init(owner,False);
  global compile_options;
  compile_options += opts;

def TDLRuntimeOptions (*opts):
  """this fadds a number of entries (created with TDLOption or TDLJob) to the
  run-time menu""";
  global runtime_options;
  # owner is at depth 1 -- our caller
  owner = _resolve_owner(calldepth=1);
  for opt in opts:
    opt and opt.init(owner,True);
  runtime_options += opts;
  
def TDLCompileMenu (title,*items,**kw):
  """This creates a submenu inside the compile-time menu, and adds a number
  of entires (created with TDLOption) to it.""";
  menu = _TDLSubmenu(title,*items,**kw);
  # owner is at depth 1 -- our caller
  menu.init(_resolve_owner(calldepth=1),False);
  compile_options.append(menu);
  return menu;

def TDLRuntimeMenu (title,*items,**kw):
  """This creates a submenu inside the run-time menu, and adds a number
  of entires (created with TDLOption or TDLJob) to it.""";
  menu = _TDLSubmenu(title,*items,**kw);
  # owner is at depth 1 -- our caller
  menu.init(_resolve_owner(calldepth=1),True);
  runtime_options.append(menu);
  return menu;

