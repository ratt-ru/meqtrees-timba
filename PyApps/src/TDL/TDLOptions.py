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

from Timba.dmi import *
from Timba.utils import *
from Kittens.pixmaps import pixmaps
import configparser

import traceback
import inspect
import sys
import os.path
import time
import re
import glob
import pwd
import socket


# import Qt but ignore failures since we can also run stand-alone
try:
  from qtpy.QtCore import Signal, QObject
  from qtpy.QtWidgets import QFileDialog
  OptionObject = QObject();
except:
  OptionObject;
  pass;

_dbg = verbosity(0,name='tdlopt');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# current config section, this is set to the script base filename by init_options()
config_section = "default";
# current script name
current_scriptname = None;
# config file
config_file = ".tdl.conf";

# flag: write failed (so that we only report it once)
_config_write_failed = False;
# flag: save changes to config
_config_save_enabled = True;

class OptionConfigParser (configparser.RawConfigParser):
  """extend the standard ConfigParser with a 'sticky' filename""";
  mandatoryOptionsSet = Signal()

  def __init__ (self,*args):
    configparser.RawConfigParser.__init__(self,*args);
    self._readfile = self._writefile = config_file;
  def read (self,filename):
    self._readfile = filename;
    self.reread(filename);
  def reread (self,filename=None):
    filename = filename or self._readfile;
    _dprint(1,"reading config file",filename);
    configparser.RawConfigParser.read(self,filename);
  def set_save_filename (self,filename):
    """Sets filename that config is to be saved to. If None, config will not be written out""";
    self._writefile = filename;
  def rewrite (self,filename=None):
    filename = filename or self._writefile;
    if filename:
      _dprint(1,"writing config file",filename);
      ## ConfigParser.RawConfigParser.write(self,file(filename,"w"));
      # write the thing ourselves, as we like to keep things sorted
      ff = open(filename,'wt');
      for section in sorted(self.sections()):
        ff.write("[%s]\n"%section);
        for name,value in sorted(self.items(section)):
          ff.write("%s = %s\n"%(name.lower(),value));
        ff.write("\n");
    else:
      _dprint(1,"not writing config file, as saving is disabled");



# create global config object
config = OptionConfigParser();

def enable_save_config (enable=True):
  """Enables/disables auto-saving of config file every time an option is set.
  TDL.Compile() (among others) calls this to accelerate recompilation."""
  global _config_save_enabled;
  _config_save_enabled = enable;

def save_config ():
  """Saves current option settings to config file."""
  global _config_save_enabled;
  if not _config_save_enabled:
    return;
  global _config_write_failed;
  try:
    config.rewrite();
    _config_write_failed = False;
  except IOError:
    if not _config_write_failed:
      _config_write_failed = True;
      _dprint(0,"WARNING: error writing to file",config_file);
      _dprint(0,"TDL options will not be saved");

def clear_options ():
  """Clears and removes all options."""
  # list of root-level compile-time options
  global compile_options;
  # list of root-level runtime options
  global runtime_options;
  # dict of all options (key is config_name)
  global _all_options;
  # list of all TDL Jobs
  global _job_options;
  # set of mandatory options that are not yet initialized
  global _unset_mandatory_options;
  compile_options = [];
  runtime_options = [];
  _all_options = {};
  _job_options = [];
  _unset_mandatory_options = set();

clear_options();

def _set_config (option,value,save=True):
  """Sets option value in configuration file""";
  if not config.has_section(config_section):
    config.add_section(config_section);
  config.set(config_section,option,value);
  _dprint(1,"setting",option,"=",value,"in config",config_section);
  if save:
    save_config();

def _set_mandatory_option (name,value):
  """Callback function, called when a mandatory option has been set. Checks if all
  mandatory options are set, and emits signals accordingly.""";
  if value is None:
    if not _unset_mandatory_options and OptionObject:
      OptionObject.mandatoryOptionsSet.emit(False)
    _unset_mandatory_options.add(name);
  else:
    _unset_mandatory_options.discard(name);
    if not _unset_mandatory_options and OptionObject:
      OptionObject.mandatoryOptionsSet.emit(True)

def init_script (filename):
  """Initializes the option mechanism in preparation for compilation.
  Clears current options, etc. Note that this funcrtion does NOT cause the config file
  to be read, or a section to be assigned. The latter is done by the init_options() call below.
  This allows batch-mode operation where a script is recompiled without rereading its
  options."""
  clear_options();
  global current_scriptname;
  current_scriptname = filename;

def init_options (section=None,save=True):
  """initializes option list for given script. Reloads the current config file, and attaches to the specified section.
  If section is None, uses the basename of the current script filename as a section.
  If save=False, updated options will never be saved.
  """
  # re-read config file
  global config;
  config.reread();
  global _config_write_failed;
  _config_write_failed = False;
  global _config_save_enabled;
  config_save_enabled = save;
  # init stuff
  global config_section;
  filename = section or current_scriptname;
  config_section = os.path.splitext(os.path.basename(filename))[0];
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

def set_option (name,value,save=True,strict=False,from_str=False):
  """Sets the named option (using its config_name) to the given value.
  If option is not found (which may be the case if the script is not yet compiled), sets it in the current
  config anyway if strict=False, else raises a NameError.
  If from_str=True, uses item.from_str() to convert value from string to a valid option setting. This
  may result in a ValueError if string is not legal.""";
  global _all_options;
  item = _all_options.get(name.lower());
  if item:
    if from_str:
      value = item.from_str(value);
    _dprint(2,"setting existing item:",name,value);
    item.set_value(value,save=save);
    return;
  else:
    _dprint(2,"setting config item for later:",name,value);
    if strict:
      raise NameError("Option '%s' not found"%name);
    # Perhaps the script hasn't been compiled yet, so pre-set it in config
    _set_config(name,str(value),save=save);

def save_to_config (conf,section):
  """Saves all options to given ConfigParser object 'conf', section 'section''""";
  values = [];
  for item in compile_options + runtime_options:
    item.collect_values(values);
  for name,value in values:
    conf.set(section,name,value);

def dump_log (message=None,filename='meqtree.log',filemode='a'):
  """Dumps a message to the indicated logfile, followed by all current option settings."""
  try:
    try:
      fileobj = open(filename,filemode);
    except IOError:
      oldfile = filename;
      filename = os.path.expanduser("~/"+filename);
      _dprint(0,"Error opening %s, will try %s instead"%(oldfile,filename));
      fileobj = open(filename,filemode);
    fileobj.write("\n###  %s\n"%time.asctime());
    fileobj.write("### user %s on host %s\n"%(pwd.getpwuid(os.getuid())[0],socket.gethostname()));
    fileobj.write("### script: %s\n"%current_scriptname);
    fileobj.write("### cwd: %s\n"%os.getcwd());
    if message:
      fileobj.write("### %s\n"%message);
    dump_options(fileobj);
  except IOError:
    _dprint(0,"Error writing to %s. No log will be written."%filename);


def dump_options (fileobj):
  """Dumps all current option settings into the file given by fileobj""";
  fileobj.write("[%s]\n"%config_section);
  fileobj.write('# compile-time options follow\n');
  values = [];
  for item in compile_options:
    item.collect_values(values);
  for name,value in values:
    fileobj.write("%s = %s\n"%(name,value));
  fileobj.write('# runtime options follow\n');
  values = [];
  for item in runtime_options:
    item.collect_values(values);
#  lines.sort();
  for name,value in sorted(values):
    fileobj.write("%s = %s\n"%(name,value));

def get_compile_options ():
  """Returns list of all compile-time options."""
  return compile_options;

def get_runtime_options ():
  """Returns list of all runtime options."""
  return runtime_options;

def get_job_func (name):
  """Find the TDL job with the given name or ID. Raises a NameError if job is not found.""";
  global _job_options;
  for item in _job_options:
    if item.name == name or item.job_id == name:
      return item.func;
  raise NameError("Job '%s' not found"%name);

def is_jobfunc_defined (func):
  global _job_options;
  for item in _job_options:
    if item.func is func:
      return True;
  return False;

def get_all_jobs ():
  global _job_options;
  return [ (item.name,item.job_id) for item in _job_options ];

class _TDLBaseOption (object):
  """abstract base class for all option entries""";
  def __init__ (self,name,namespace=None,owner=None,doc=None):
    if not isinstance(name,str):
      raise TypeError("option name must be a string");
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
    self._twitem  = None;
    self.initialized = False;

  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu. owner is the name of a module to
    which this option belongs, or None for the top-level script.
    runtime is True if option is runtime.""";
    _dprint(2,"item '%s' owner '%s' runtime %d"%(self.name,owner,int(runtime)));
    self.owner = owner;
    self.is_runtime = runtime;
    self.initialized = True;

  def collect_values (self,values):
    """called to collect a list of (name,value) tuples. Should append (name,value) to end of values list.
    Default version collects nothing.""";
    pass;

  def set_qaction (self,qa):
    """sets the option's QAction. Makes it enabled or disabled as appropriate""";
    self._qa = qa;
    if self.doc:
      qa.setToolTip(self.doc);
      qa.setWhatsThis(self.doc);
    qa.setEnabled(self.enabled);
    qa.setVisible(self.visible);
    return qa;

  def set_treewidget_item (self,item):
    """sets the option's QTreeWidgetItem. Makes it enabled or disabled as appropriate""";
    self._twitem = item;
    if self.doc:
      self.set_doc(self.doc);
    item.setDisabled(not self.enabled);
    item.setHidden(not self.visible);
    return item;

  def enable (self,enabled=True):
    """enables/disables the option. Default behaviour enables/disables the QAction""";
    _dprint(3,"enable item",self.name,":",enabled);
    self.enabled = enabled;
    self._qa and self._qa.setEnabled(enabled);
    self._twitem and self._twitem.setDisabled(not enabled);
    return enabled;

  def disable (self,disabled=True):
    """disables/enables the option. Default behaviour calls enable() with opposite flag""";
    return self.enable(not disabled);

  def show (self,visible=True):
    """shows/hides the option. Default behaviour shows/hides the QAction""";
    _dprint(3,"show item",self.name,":",visible);
    self.visible = visible;
    self._qa and self._qa.setVisible(visible);
    self._twitem and self._twitem.setHidden(not visible);
    return visible;

  def hide (self,hidden=True):
    """hides/shows the option. Default behaviour calls show() with opposite flag""";
    return self.show(not hidden);

  def set_name (self,name):
    """Changes option name""";
    self.name = name;
    self._twitem and self._twitem.setText(0,name);

  def set_doc (self,doc):
    """Changes option documentation string""";
    self.doc = doc;
    if self._twitem:
      if self.doc:
        icon = pixmaps.info_blue_round.icon();
        # add body tags to convert documentation to rich text
        doc = "<body>"+self.doc+"</body>";
      else:
        icon,doc = QIcon(),"";
      # set as tooltip
      self._twitem.setIcon(1,icon);
      for col in range(3):
        self._twitem.setToolTip(col,doc);

class _TDLOptionSeparator (_TDLBaseOption):
  """This option simply inserts a separator into a menu""";
  def __init__ (self,name=None,namespace=None,doc=None):
    _TDLBaseOption.__init__(self,name=name or "",namespace=namespace,doc=doc);

  def make_treewidget_item (self,parent,after,executor=None):
    # do not insert an empty separator after another separator
    if not self.name and after and getattr(after,'_is_separator',False):
      return None;
    item = QTreeWidgetItem(parent,after);
    tw = item.treeWidget();
    if self.name:
      widget = QWidget(tw);
      lo = QHBoxLayout(widget);
      lo.setContentsMargins(0,0,0,0);
      label = QLabel(widget);
      label.setFrameStyle(QFrame.Sunken|QFrame.HLine)
      label.setMinimumSize(QSize(64,0));
      lo.addWidget(label,0);
      label = QLabel(widget);
      label.setText("<NOBR><B>%s</B></NOBR>"%self.name);
      lo.addWidget(label,0);
      label = QLabel(widget);
      label.setFrameStyle(QFrame.Sunken|QFrame.HLine)
      lo.addWidget(label,1);
    else:
      widget = QLabel(tw);
      widget.setFrameStyle(QFrame.Sunken|QFrame.HLine)
    tw.setItemWidget(item,0,widget);
    # item.setFlags(Qt.NoItemFlags);  # Qt.NoItemFlags only defined after 4.4
    item.setFirstColumnSpanned(True);
    item._is_separator = True;
    return self.set_treewidget_item(item);

class _TDLJobItem (_TDLBaseOption):
  closeWindow = Signal()

  def __init__ (self,func,name=None,namespace=None,doc=None,job_id=None):
    _TDLBaseOption.__init__(self,name or func.__name__.replace('_',' '),
                            namespace=namespace,doc=doc);
    self.func = func;
    self.job_id = job_id;
    self.symbol = func.__name__;
    global _job_options;
    _job_options.append(self);

  def make_treewidget_item0 (self,parent,after,executor=None):
    item = QTreeWidgetItem(parent,after);
    item.setText(0,self.name);
    item.setIcon(0,pixmaps.gear.icon());
    font = item.font(0);
    font.setBold(True);
    item.setFont(0,font);
    item._on_click = curry(executor,self.func,self.name,self.job_id);
    item._close_on_click = True;
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

  def make_treewidget_item (self,parent,after,executor=None):
    item = QTreeWidgetItem(parent,after);
    tw = item.treeWidget();
    button = QToolButton(tw);
    button.setText(self.name);
    button.setIcon(pixmaps.gear.icon());
    button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    if self.doc:
      button.setToolTip("<body>%s</body>"%self.doc);
    # item.setFirstColumnSpanned(True);
    tw.setItemWidget(item,0,button);
    button._on_click = curry(executor,self.func,self.name,self.job_id);
    button.clicked.connect(button._on_click)
    button.clicked.connect(tw.closeWindow)
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

class _TDLOptionItem(_TDLBaseOption):
  """Abstract base class for options with a value""";
  def __init__ (self,namespace,symbol,value,config_name=None,name=None,doc=None,mandatory=False):
    _TDLBaseOption.__init__(self,name or symbol,namespace=namespace,doc=doc);
    # config_name specifies the configuration file entry
    if config_name is None:
      config_name = symbol;
    self.config_name = config_name and config_name.lower();
    # symbol may have nested namespaces specified with '.'
    syms = symbol.split('.');
    symbol = syms[-1];
    while len(syms) > 1:
      name = syms.pop(0);
      namespace = namespace.setdefault(name,{});
      if not isinstance(namespace,dict):
        namespace = getattr(namespace,'__dict__',None);
        if namespace is None:
          raise TypeError("'"+name+"' does not refer to a valid namespace");
    self.namespace = namespace;
    self.symbol = symbol;
    self.mandatory = mandatory;
    self._set(value);
    self._when_changed_callbacks = [];

  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLBaseOption.init(self,owner,runtime);
    if owner and self.config_name is not None:
      self.config_name = '.'.join((owner,self.config_name));
    global _all_options;
    _dprintf(3,"initializing %s %s (namespace %X)\n",self.name,self.config_name,id(self.namespace));
    if self.config_name:
      self.config_name = self.config_name.lower();
      _all_options[self.config_name] = self;
    else:
      _dprint(1,"no config name for ",self.name);

  def collect_values (self,values):
    """called to collect a list of (name,value) tuples. Appends (name,value) to end of values list.""";
    if self.visible and self.enabled and self.config_name:
      values.append((self.config_name,self.get_str()));

  def _set (self,value,callback=True):
    """private method for changing the internal value of an option"""
    _dprintf(2,"setting '%s' %s=%s in namespace %X\n"%(self.name,self.symbol,value,id(self.namespace)));
    self.value = self.namespace[self.symbol] = value;
    # add/remove to mandatory set
    if self.mandatory:
      _set_mandatory_option(self.config_name,value);
    # be anal about whether the _when_changed_callbacks attribute is initialized,
    # as _set may have been called before the constructor
    if callback:
      for cb in getattr(self,'_when_changed_callbacks',[]):
        try:
          cb(value);
        except:
          print("Error calling when_changed callback (%s) for option '%s'"%(getattr(cb,'__name__',''),self.name));
          traceback.print_exc();

  def set (self,value,**kw):
    """public method for changing the internal value of an option. Must be implemented
    in child classes""";
    raise TypeError("set() not implemented in child class""");

  def set_value (self,value,**kw):
    """set_value() is by default an alias for set()"""
    self.set(value,**kw);

  def from_str (self,value,**kw):
    """Converts string to legal value of option. Raises ValueError if string is invalid.""";
    raise TypeError("from_str() not implemented in child class""");

  def get_str (self):
    """Returns string representation of option""";
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
    try:
      callback(self.value);
    except:
      print("Error calling when_changed callback (%s) for option '%s'"%(getattr(callback,'__name__',''),self.name));
      traceback.print_exc();

class _TDLBoolOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,config_name=None,name=None,doc=None,nonexclusive=False):
    _TDLOptionItem.__init__(self,namespace,symbol,value,config_name=config_name,name=name,doc=doc);
    self.nonexclusive = nonexclusive;
    self._set(value);

  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    if self.config_name:
      try:
        value = self.from_str(config.get(config_section,self.config_name));
        self._set(value);
        _dprint(2,"read",self.config_name,"=",value,"from config");
      except:
        _dprint(2,"error reading",self.config_name,"from config");
        if _dbg.verbose > 2:
          traceback.print_exc();

  def from_str (self,strval):
    if strval == 'false' or strval == 'False':
      return False;
    elif strval == 'true' or strval == 'True':
      return True;
    else:
      return bool(int(strval));

  def get_str (self):
    """Returns string representation of option""";
    return str(int(self.value));

  def set (self,value,save=True,callback=True,set_twitem=True):
    value = bool(value);
    if self.initialized and self.config_name:
      _set_config(self.config_name,int(value),save=save);
    if self._twitem and set_twitem:
      self._twitem.setCheckState(0,(value and Qt.Checked) or Qt.Unchecked);
    self._set(value,callback=callback);

  def make_treewidget_item (self,parent,after,executor=None):
    item = QTreeWidgetItem(parent,after);
    item.setText(0,self.name);
    item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
    item.setCheckState(0,(self.value and Qt.Checked) or Qt.Unchecked)
    item._on_click = item._on_press = self._check_item;
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

  def _check_item (self):
    self.set(self._twitem.checkState(0) == Qt.Checked,set_twitem=False);

class TDLFileSelect (object):
  def __init__ (self,filenames="",default=None,exist=True):
    self.filenames  = str(filenames);
    self.exist      = exist;
    self.default    = default;

class TDLDirSelect (TDLFileSelect):
  def __init__ (self,filenames="",default=None,exist=True):
    TDLFileSelect.__init__(self,filenames,default,exist);

class _TDLFileOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,filespec,
                default=None,config_name=None,name=None,doc=None,mandatory=False):
    _TDLOptionItem.__init__(self,namespace,symbol,'',
                            config_name=config_name,name=name,doc=doc,mandatory=mandatory);
    self._filespec = filespec;
    self._validator = lambda dum:True;
    self._file_dialog = None;
    # no value in config -- try default
    if isinstance(filespec.default,str):
      self._set(str(filespec.default));
    else:
      self._set(None);

  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    if self.config_name:
      try:
        value = config.get(config_section,self.config_name);
        if self._validator(value):
          _dprint(2,"read",self.config_name,"=",value,"from config");
          self._set(value);
        else:
          _dprint(2,"read",self.config_name,"=",value,"from config, but validation failed");
          self._set(None);
      except:
        _dprint(2,"error reading",self.config_name,"from config");
        if _dbg.verbose > 2:
          traceback.print_exc();
        # no value in config -- try default, if supplied a string
        if isinstance(self._filespec.default,str):
          self._set(str(self._filespec.default));
        # else try to find first matching file (default=True)
        elif self._filespec.default:
          for pattern in self._filespec.filenames.split(" "):
            for filename in glob.glob(pattern):
              if self._validator(filename):
                self._set(filename);
                return;

  def from_str (self,value):
    value = str(value);
    if not self._validator(value):
      raise ValueError("value '%s' does not pass validation for %s"%(value,self.name));
    return value;

  def set_validator (self,validator):
    self._validator = validator;
    if self.value and not self._validator(self.value):
      self.set(None);

  def set (self,value,save=True,callback=True):
    value = str(value);
    # strip off CWD from path
    cwd = os.getcwd() + "/";
    if value.startswith(cwd):
      value = value[len(cwd):];
    if self.initialized and self.config_name:
      _set_config(self.config_name,value,save=save);
    if self._twitem:
      self._twitem.setText(2,value);
    self._set(value,callback=callback);

  def enable (self,enabled=True):
    _TDLOptionItem.enable(self,enabled);
    if not enabled and self._file_dialog:
      self._file_dialog.hide();

  def show (self,visible=True):
    _TDLOptionItem.show(self,visible);
    if not visible and self._file_dialog:
      self._file_dialog.hide();

  class FileDialog (QFileDialog):
    selectedFile = Signal()

    def done (self,result):
      if result:
        self.selectedFile.emit(self.selectedFiles()[0])
      QFileDialog.done(self,result);

  def make_treewidget_item (self,parent,after,executor=None):
    item = QTreeWidgetItem(parent,after);
    item.setText(0,self.name+":");
    if self.value:
      item.setText(2,os.path.basename(self.value.rstrip("/")));
    else:
      item.setText(2,"<none>");
    # create file dialog
    self._file_dialog = file_dialog = \
        self.FileDialog(item.treeWidget(),self.name,".",self._filespec.filenames);
    if isinstance(self._filespec,TDLDirSelect):
      file_dialog.setFileMode(QFileDialog.DirectoryOnly);
    elif self._filespec.exist:
      file_dialog.setFileMode(QFileDialog.ExistingFile);
    else:
      file_dialog.setFileMode(QFileDialog.AnyFile);
    file_dialog.selectedFile.connect(self._select_file)
    # make file selection dialog pop up when item is pressed
    item._on_click = item._on_press = self._show_dialog;
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

  def _show_dialog (self):
#    self._file_dialog.setDirectory(self._file_dialog.directory());
    self._file_dialog.show();

  def _select_file (self,name):
    name = str(name);
    if self._validator(name):
      self._twitem.setText(2,os.path.basename(name.rstrip("/")));
      self.set(name);

class _TDLListOptionItem (_TDLOptionItem):
  def __init__ (self,namespace,symbol,value,default=None,more=None,
                     config_name=None,name=None,doc=None,mandatory=False):
    _TDLOptionItem.__init__(self,namespace,symbol,None,config_name=config_name,name=name,doc=doc,mandatory=mandatory);
    if more not in (None,int,float,str,complex):
      raise ValueError("'more' argument to list options must be 'None', 'int', 'float', 'complex' or 'str'")
    if not more and not value:
      raise ValueError("empty option list, and 'more=' not specified");
    self._more = more;
    self._custom_value = ('','','');
    self._submenu = self._submenu_editor = None;
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
          raise TypeError("'default': list index expected");
        elif default < 0 or default >= len(self.option_list):
          raise ValueError("'default': index out of range");
    # set the default value
    self.selected = default;
    self._set(self.option_list[default]);

  def init (self,owner,runtime):
    """initializes the option. This is called when the option is placed into a
    run-time or compile-time menu.""";
    _TDLOptionItem.init(self,owner,runtime);
    select = None;
    try:
      _dprint(2,"reading",self.config_name," from config section",config_section);
      value = self.from_str(config.get(config_section,self.config_name));
      _dprint(2,"read",self.config_name,"=",value,"from config");
      try:
        select = self.option_list.index(value);
      except:  # value not in list, add as custom value (from_str() will have checked that this is allowed)
        self.set_custom_value(value);
        select = len(self.option_list)-1;
    except:
      _dprint(2,"error reading",self.config_name,"from config");
      if _dbg.verbose > 2:
        traceback.print_exc();
    # if select was set, we have a legal value
    if select is not None:
      self.set(select,save=False);

  def from_str (self,value):
    try:
      select = self.option_list_str.index(value);
      return self.option_list[select];
    except:
      if self._more is None:
        raise ValueError("value '%s' is not in the list of valid options for %s"%(value,self.name));
      else:
        value = self._more(value);
        if not self._validator(value):
          raise ValueError("value '%s' does not pass validation for %s"%(value,self.name));
        return value;

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
    _dprint(5,self.symbol,"set_option_list",opts);
    if select is None and conserve_selection:
      try:
        selection = self.get_option_str(self.selected);
      except:
        selection = conserve_selection = None;
      _dprint(5,"trying to conserve previous selection",selection);
    if isinstance(opts,(list,tuple)):
      # check for list of ("key":value) pairs
      if len([ opt for opt in opts if isinstance(opt,(list,tuple)) and len(opt) == 2 ]) == len(opts):
        self.option_list = [ opt[0] for opt in opts ];
        self.option_list_str = [ self.item_str(opt[0]) for opt in opts ];
        self.option_list_desc = [ str(opt[1]) for opt in opts ];
      # else treat as simple list of values
      else:
        self.option_list = list(opts);
        self.option_list_str = [self.item_str(x) for x in opts];
        self.option_list_desc = list(self.option_list_str);
    elif isinstance(opts,dict):
      self.option_list = list(opts.keys());
      self.option_list_str = [self.item_str(x) for x in iter(list(opts.keys()))];
      self.option_list_desc = [str(x) for x in iter(list(opts.values()))];
    else:
      raise TypeError("TDLListOptionItem: list or dict of options expected");
    # add custom value
    if self._more is not None:
      self.option_list.append(self._custom_value[0]);
      self.option_list_str.append(self._custom_value[1]);
      self.option_list_desc.append(self._custom_value[2]);
    # rebuild menus, if already instantiated
    if self._submenu:
      self._rebuild_submenu(self._twitem.treeWidget());
    # re-select previous value, or selected value
    if select is not None:
      self.set(select,save=False);
    elif conserve_selection:
      try:
        index = self.option_list_str.index(selection);
        self.set(index,save=False);
      except:
        # old selection not found in list, so make it a custom value if possible
        if self._more is not None:
          self.set_custom_value(selection);
        # else fall back to selection #0
        else:
          self.set(0);

  def set_value (self,value,save=True,callback=True):
    """selects given value in list. If value is not in list, sets
    custom value if possible"""
    try:
      index = self.option_list.index(value);
      self.set(index,save=save,callback=callback);
    except:
      if self._more is None:
        raise ValueError("%s is not a legal value for option '%s'"%(value,self.name));
      self.set_custom_value(self._more(value),save=save,select=True,callback=callback);

  def set (self,ivalue,save=True,callback=True):
    """selects value #ivalue in list""";
    self.selected = value = int(ivalue);
    _dprint(1,"set %s, #%d (%s), save=%s"%(self.name,value,self.get_option_desc(value),save));
    if self._twitem:
      _dprint(1,"setting twitem text");
      self._twitem.setText(2,self.get_option_desc(value));
    if self._submenu:
      self._submenu_qas[self.selected].setChecked(True);
    if self.initialized and self.config_name:
      _set_config(self.config_name,self.get_option_str(value),save=save);
    self._set(self.get_option(value),callback=callback);

  def set_custom_value (self,value,select=True,save=True,callback=True):
    if self._more is None:
      raise TypeError("can't set custom value for this option list, since it was not created with a 'more' argument");
    self._custom_value = (value,str(value),str(value)); # or "(empty)");
    self.option_list[-1],self.option_list_str[-1],self.option_list_desc[-1] = self._custom_value;
    # copy to editor widget
    if self._submenu_editor is not None:
      self._submenu_editor.setText(self._custom_value[1]);
    # select if needed
    if select:
      self.set(len(self.option_list)-1,save=save,callback=callback);

  def _rebuild_submenu (self,parent):
    # create QMenu for available options
    self._submenu = submenu = QMenu(parent);
    ag = QActionGroup(parent);
    self._submenu_qas = [];
    self._submenu_editor = None;
    for ival in range(self.num_options()):
      if self._more is not None and ival == self.num_options()-1:
        qaw = QWidgetAction(parent);
        box = QWidget(parent);
        qaw.setDefaultWidget(box);
        box_lo = QHBoxLayout(box);
        spacer = QLabel("",box);
        box_lo.addWidget(spacer);
        spacer.setMinimumWidth(32);
        box_lo.setContentsMargins(0,0,0,0);
        box_lo.setSpacing(0);
        #spacer.setBackgroundRole(QPalette.Button);
        #for color in self._submenu.paletteBackgroundColor(),spacer.paletteBackgroundColor():
        self._submenu_editor = QLineEdit(self.get_option_str(ival),box);
        box_lo.addWidget(self._submenu_editor);
        # self._submenu_editor.setBackgroundMode(Qt.PaletteMidlight);
        if self._more is int:
          self._submenu_editor.setValidator(QIntValidator(self._submenu_editor));
        elif self._more is float:
          self._submenu_editor.setValidator(QDoubleValidator(self._submenu_editor));
        # connect signal
        self._submenu_editor.editingFinished.connect(self._set_submenu_custom_value)
        qa = ag.addAction("Custom:");
        qa.setCheckable(True);
        self._submenu.addAction(qa);
        self._submenu.addAction(qaw);
      else:
        qa = ag.addAction(self.get_option_desc(ival));
        self._submenu.addAction(qa);
      qa._ival = ival;
      qa.setCheckable(True);
      self._submenu_qas.append(qa);
      if ival == self.selected:
        qa.setChecked(True);
    ag.triggered[QAction].connect(self._activate_submenu_action)

  def make_treewidget_item (self,parent,after,executor=None):
    """makes a listview entry for the item""";
    _dprint(3,"making listview item for",self.name);
    item = QTreeWidgetItem(parent,after);
    item.setText(0,self.name+":");
    item.setText(2,self.get_option_desc(self.selected));
    # create QPopupMenu for available options
    self._rebuild_submenu(item.treeWidget());
    # make menu pop up when item is pressed
    item._on_click = item._on_press = self._popup_menu;
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

  def _popup_menu (self):
    # figure out where to pop up the menu
    tw = self._twitem.treeWidget();
    pos = tw.visualItemRect(self._twitem).topLeft();
    pos.setX(pos.x()+tw.header().sectionSize(0));    # position in listview
    # now map to global coordinates
    self._submenu.popup(tw.mapToGlobal(pos));
    _dprint(5,"returning from popup");

  def _activate_submenu_action (self,action):
    selected = action._ival;
    # validate custom value
    if self._more is not None and selected == self.num_options()-1:
      if not self._validator(self._custom_value[0]):
        self._popup_menu();
        return;
      self.set(selected);
      # keep menu popped up if selected custom value, but editor is empty
#      if not self._custom_value[1]:
#        _dprint(5,"forcing popup");
#        self._popup_menu();
    else:
      self.set(selected);

  def _set_submenu_custom_value (self):
    # get value from editor
    value = str(self._submenu_editor.text());
#    if value == "(empty)" and self._custom_value[0] == '':
#      value = '';
    if value == "None" and self._custom_value[0] is None:
      value = None;
    if self._more is int:
      value = int(value);
    elif self._more is float:
      value = float(value);
    if self._validator(value):
      # set as custom value
      self.set_custom_value(value,select=True);
      # update menu
      self._activate_submenu_action(self._submenu_qas[self.num_options()-1]);
      self._submenu.close();
    else:  # invalid value
      self._submenu_editor.setText(self._custom_value[1] or "(empty)");
      if self._custom_value[0] is None:
        self.set(0);

class _TDLSubmenu (_TDLBoolOptionItem):
  def __init__ (self,title,*items,**kw):
    """Creates a submenu from the given list of option items.
    Note that an item may be specified as None, to get a separator.
    Optional keywords:
      doc: documentation string
      summary: summary string (optional)
      open: if True, menu starts out open (this is only a hint)
      toggle: if set to a symbol name, the menu entry itself has an associated
              checkbox, and acts as a TDLBoolItem. Initial state is taken from
              the 'open' keyword.
      exclusive: if set to a symbol name, the menu acts like a "radio button"
              controller. All TDLBoolItems (including toggle submenus) within
              the menu become exclusive. That is, checking one un-checks all
              the others. The name of the selected item is stored in the 'exclusive'
              symbol name. The controlled items are no longer saved to the config.
      nonexclusive: setting this attribute to True exempts a toggle submenu from
              the 'exclusivity' behaviour imposed by its parent
      name:   sets the name attribute -- if None, title is used.
      namespace: overrides the namespace passed to constructor -- only
              makes sense if toggle is set as well.
    """;
    doc = kw.get('doc');
    name = kw.get('name',None) or title;
    self._summary = kw.get('summary',None);
    self._is_open = kw.get('open',None);
    self._toggle = kw.get('toggle',None);
    self._exclusive = kw.get('exclusive',None);
    namespace = kw.get('namespace');
    nonexclusive = kw.get('nonexclusive',False);
    # resolve 'exclusive' symbol
    if self._exclusive:
      _dprint(2,"menu",title,"exclusive, symbol is",self._exclusive);
      self.excl_namespace,self.excl_config_name = \
          _resolve_namespace(namespace,self._exclusive,calldepth=2);
      self.excl_config_name = self.excl_config_name and self.excl_config_name.lower();
      self._excl_selected = self.excl_namespace[self._exclusive] = None;
      _dprint(2,"menu",title,"exclusive, config name is",self.excl_config_name);
    # depth is 2 (this frame, TDLxxxMenu frame, caller frame)
    namespace,config_name = _resolve_namespace(namespace,self._toggle or '',calldepth=2);
    # somewhat kludgy, but what the hell: if toggle is set, init our BoolOptionItem
    # parent, else only init the TDLBaseOption parent
    _dprint(2,"creating menu",title,"name",name);
    if self._toggle:
      _TDLBoolOptionItem.__init__(self,namespace,self._toggle,self._is_open or False,
                                  name=name,config_name=config_name,doc=doc,nonexclusive=nonexclusive);
    else:
      _TDLBaseOption.__init__(self,name=name,namespace=namespace,doc=doc);
    self._title = title;
    self._items0 = items;
    self._items  = None;
    self._exclusive_items = {};

  def init (self,owner,runtime):
    _dprint(1,"menu",self._title,"owner",owner);
    # in toggle mode, init BoolItem parent to read value from config
    if self._toggle:
      _TDLBoolOptionItem.init(self,owner,runtime);
    else:
      _TDLBaseOption.init(self,owner,runtime);
    # in exclusive mode, read the exclusive setting from the config
    if self._exclusive:
      self.namespace[self._exclusive] = None;
      try:
        excl_value = config.get(config_section,self.excl_config_name);
      except:
        excl_value = None;
      _dprint(2,"read",self.excl_config_name,"=",excl_value,"from config");
      global _all_options;
      _all_options[self.excl_config_name] = self;
    # if option not previously initialized, then we need to process the items list
    if self._items is None:
      _dprint(1,"menu",self._title,"runtime is",runtime);
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
          self._items += _steal_items(compile_options,lambda item0:item is item0) + \
                         _steal_items(runtime_options,lambda item0:item is item0);
          # append to list, if not stolen
          if not ( self._items and self._items[-1] is item ):
            self._items.append(item);
          # if exclusive, register callback
          if self._exclusive:
            if not (isinstance(item,_TDLSubmenu) and not item._toggle) and \
               isinstance(item,_TDLBoolOptionItem) and not item.nonexclusive:
              self._exclusive_items[item.symbol] = item;
              if excl_value is None:
                excl_value = item.symbol;
                item.set(True);
              else:
                item.set(item.symbol == excl_value);
              item.config_name = None;
              item.when_changed(curry(self._exclusive_item_selected,item));
          # init the item
          item.init(owner,runtime);
        # else try to steal items from the module
        else:
          self._items += TDLStealOptions(item,runtime);
      self._items0 = None;

  def set_exclusive (self,item,setitem=True,save=True):
    if isinstance(item,str):
      item = self._exclusive_items.get(item,None);
      name = item and item.symbol;
    else:
      name = item.symbol;
    _dprint(2,"setting exclusive menu item",name,item);
    self._excl_selected = self.excl_namespace[self._exclusive] = name;
    if item:
      if setitem:
        item.set(True,save=False);
      for other in list(self._exclusive_items.values()):
        if other is not item:
          other.set(False,save=False);
    if self.initialized and self.excl_config_name:
      _set_config(self.excl_config_name,name or '',save=save);

  def _exclusive_item_selected (self,item,value,save=True):
    _dprint(3,"selected exclusive menu item",item,item.symbol,value);
    if value:
      self.set_exclusive(item,setitem=False,save=save);

  def collect_values (self,values):
    """called to collect a list of (name,value) tuples. Appends (name,value) to end of values list.""";
    if self._toggle:
      _TDLBoolOptionItem.collect_values(self,values);
      if not self.value:
        return;
    if self.visible and self.enabled:
      if self._exclusive:
        values.append((self.excl_config_name,self._excl_selected));
      for item in self._items:
        if isinstance(item,_TDLBaseOption):
          item.collect_values(values);

  def expand (self,expand=True):
    self._is_open = expand;
    if self._twitem:
      self._twitem.setExpanded(expand);

  def from_str (self,value):
    if self._exclusive and isinstance(value,str) and value in self._exclusive_items:
      return value;
    elif self._toggle:
      return _TDLBoolOptionItem.from_str(self,value);
    else:
      raise ValueError("can't set %s to %s"%(self.name,value));

  def set (self,value,**kw):
    _dprint(4,"setting menu item",self.name,value);
    if self._exclusive and isinstance(value,str):
      self.set_exclusive(value,save=False);
    elif self._toggle:
      oldval = self.value;
      _TDLBoolOptionItem.set(self,value,**kw);
      # open/close menu when going from unset to set and vice versa
      if self._twitem:
        self._twitem.setCheckState(0,(self.value and Qt.Checked) or Qt.Unchecked);
        if oldval != value:
          self._twitem.setExpanded(value);

  def set_summary (self,summary):
    self._summary = summary;
    if self._twitem:
      self._twitem.setText(2,summary or '');

  def make_treewidget_item (self,parent,after,executor=None):
    """makes a listview entry for the menu""";
    if self._items is None:
      raise RuntimeError("option menu '%s' not initialized, this should be impossible!"%self._title);
    item = QTreeWidgetItem(parent,after);
    item.setText(0,self._title);
    item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled);
    if self._toggle:
      item.setFlags(item.flags()|Qt.ItemIsUserCheckable);
      self._old_value = self.value;
      item.setCheckState(0,(self.value and Qt.Checked) or Qt.Unchecked);
      if self._is_open is None:
        item.setExpanded(self.value);
      else:
        item.setExpanded(self._is_open or False);
      item._on_click = item._on_press = self._check_item;
    else:
      item.setExpanded(self._is_open or False);
    if self._summary:
      item.setText(2,self._summary);
    # loop over items
    previtem = None;
    for subitem in self._items:
      _dprint(3,"adding",subitem,getattr(subitem,'name',''),"to item",self.name);
      subitem = subitem or _TDLOptionSeparator();
      previtem = subitem.make_treewidget_item(item,previtem,executor=executor) or previtem;
    parent._ends_with_separator = False;
    return self.set_treewidget_item(item);

def _steal_items (itemlist,predicate):
  """helper function: steals option items matching the given predicate, from the given
  list (which will usuaally be either the global runtime_options or compile_options
  list).
  Returns list of stolen items, or [] if none.
  list.""";
  items = [];
  steal_items = [];  # list of indices of stolen items
  for i,item0 in enumerate(itemlist):
    if isinstance(item0,_TDLBaseOption) and predicate(item0):
      _dprint(3,"menu: stealing ",item0.name);
      steal_items.insert(0,i);
      items.append(item0);
  # delete stolen items
  for i in steal_items:
    del itemlist[i];
  return items;

def TDLStealOptions (obj,is_runtime=False):
  """Steals options from the given object.
  If is_runtime is False, steals compile-time options, else steals runtime options.
  Returns list of stolen options, or [] if none are found."""
  # determine which global list we steal options from
  optlist = (is_runtime and runtime_options) or compile_options;
  # is it a module? Steal options whose owner is the module
  if inspect.ismodule(obj):
    owner = os.path.basename(obj.__file__).split('.')[0];
    _dprint(3,"menu: stealing items from module",owner);
    # now steal items from this namespace's runtime or compile-time options
    return _steal_items(optlist,lambda item:item.owner == owner);
  # else object is a dict, or has a __dict__ attribute: steal items from that dict
  else:
    namespace = None;
    if isinstance(obj,dict):
      _dprint(3,"menu: stealing items from ",obj);
      namespace = obj;
    else:
      _dprint(3,"menu: stealing items from ",getattr(obj,'__name__','?'));
      namespace = getattr(obj,'__dict__',None);
    if namespace:
      return _steal_items(optlist,lambda item:item.namespace is namespace);
  # fall through here on error
  name = getattr(obj,"__name__",None);
  if name:
    name = " '%s'"%name;
  else:
    name = "";
  raise TypeError("cannot steal options from object%s of type %s"%(name,type(obj)));

def populate_option_treewidget (tw,option_items,executor=None):
  tw.clear();
  # populate listview
  previtem = None;
  for item in option_items:
    if item is None:
      item = _TDLOptionSeparator();
    previtem = item.make_treewidget_item(tw,previtem,executor=executor);
  # add callbacks
  # add to menu
  # menu.insertItem(listview);
  return tw;

def _resolve_owner (calldepth=2):
  frame = sys._getframe(calldepth+1);
  ## this is kludgy, but psyco understands it:
  # filename = frame.f_code.co_filename;
  ## this way is more portable, but incompatible with psyco:
  filename = inspect.getframeinfo(frame)[0];
  # if owner matches our current script name, return None
  owner = os.path.splitext(os.path.basename(filename))[0];
  if owner == (current_scriptname and os.path.splitext(os.path.basename(current_scriptname))[0]):
    return None;
  else:
    return owner;

def _resolve_namespace (namespace,symbol,calldepth=2):
  # if namespace is not specified, set it to the globals() of the caller of our caller
  if namespace is None:
    # figure out filename of caller frame -- skip frames in this file
    namespace = sys._getframe(calldepth+1).f_globals;
  # else namespace is a dict -- check for tdloption_namespace
  elif isinstance(namespace,dict):
    namespace_name = None;
    prefix = namespace.get('tdloption_namespace',None);
    if prefix:
      symbol = ".".join((prefix,symbol));
  # else namespace must have a __dict__ attribute
  else:
    # form options inside an explcit namespace (e.g. inside an object), prepend the
    # name of the object to the config name
    prefix = getattr(namespace,'tdloption_namespace',None) or \
             getattr(namespace,'__name__',None) or \
             type(namespace).__name__;
    _dprintf(1,"option %s, namespace is %s (%X), prefix is %s\n"%(symbol,namespace,id(namespace),prefix));
    namespace = getattr(namespace,'__dict__',None);
    if namespace is None:
      raise TypeError("invalid namespace specified");
    # get name for config file, by prepending the namespace name
    if prefix:
      symbol = ".".join((prefix,symbol));
  _dprintf(1,"option %s, namespace dict is %X\n"%(symbol,id(namespace)));
  return namespace,symbol;

def _make_option_item (namespace,symbol,name,value,default=None,
                       inline=False,doc=None,mandatory=False,more=None,runtime=None,nonexclusive=False):
  # resolve namespace based on caller
  # depth is 2 (this frame, TDLxxxOption frame, caller frame)
  namespace,config_name = _resolve_namespace(namespace,symbol,calldepth=2);
  _dprintf(1,"option %s, config name is %s, namespace %X\n"%(symbol,config_name,id(namespace)));
  if runtime and mandatory:
    raise TypeError("run-time options cannot be declared mandatory");
  # boolean option
  if isinstance(value,bool):
    item = _TDLBoolOptionItem(namespace,symbol,value,config_name=config_name,nonexclusive=nonexclusive);
  # single number -- convert to list
  elif isinstance(value,(int,float)):
    item = _TDLListOptionItem(namespace,symbol,[value],
                              default=default,more=more,config_name=config_name,mandatory=mandatory);
  # list of options
  elif isinstance(value,(list,tuple,dict)):
    item = _TDLListOptionItem(namespace,symbol,value,
                              default=default,more=more,config_name=config_name,mandatory=mandatory);
    setattr(item,'inline',inline);
  elif isinstance(value,TDLFileSelect):
    item = _TDLFileOptionItem(namespace,symbol,value,config_name=config_name,mandatory=mandatory);
  else:
    raise TypeError("Illegal type for TDL option '%s': %s"%(symbol,type(value).__name__));
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

def TDLOption (symbol,name,value,namespace=None,validator=None,**kw):
  """this creates and returns an option object, without adding it to
  any menu. Should be used inside a TDLCompileMenu/TDLRuntimeMenu.""";
  item = _make_option_item(namespace,symbol,name,value,**kw);
  validator and item.set_validator(validator);
  return item;

TDLOptionSeparator = _TDLOptionSeparator;

def TDLJob (function,name=None,doc=None,job_id=None):
  """this creates and returns a TDL job entry, without adding it to
  any menu. Should be used inside a TDLRuntimeMenu.""";
  namespace = sys._getframe(1).f_globals;
  opt = _TDLJobItem(function,name=name,namespace=namespace,doc=doc,job_id=job_id);
  return opt;

def TDLCompileOption (symbol,name,value,namespace=None,**kw):
  """this creates an option object and adds it to the compile-time menu""";
  opt = _make_option_item(namespace,symbol,name,value,runtime=False,**kw);
  compile_options.append(opt);
  return opt;

def TDLCompileOptionSeparator (name=None,doc=None):
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(name=name,doc=doc,namespace=namespace);
  # owner is at depth 1 -- our caller
  opt.init(_resolve_owner(calldepth=1),False);
  compile_options.append(opt);
  return opt;

def TDLRuntimeOption (symbol,name,value,namespace=None,**kw):
  """this creates an option object and adds it to the runtime menu""";
  opt = _make_option_item(namespace,symbol,name,value,runtime=True,**kw);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeOptionSeparator (name=None,doc=None):
  namespace = sys._getframe(1).f_globals;
  opt = _TDLOptionSeparator(name=name,doc=doc,namespace=namespace);
  # owner is at depth 1 -- our caller
  opt.init(_resolve_owner(calldepth=1),True);
  runtime_options.append(opt);
  return opt;

def TDLRuntimeJob (function,name=None,doc=None,job_id=None):
  """this creates a TDL job entry, and adds it to the runtime menu.""";
  job = _TDLJobItem(function,name=name,doc=doc,job_id=job_id);
  # owner is at depth 1 -- our caller
  job.init(_resolve_owner(calldepth=1),True);
  runtime_options.append(job);
  return job;

def TDLCompileOptions (*opts):
  """this adds a number of entries (created with TDLOption) to the
  compile-time menu""";
  # owner is at depth 1 -- our caller
  owner = _resolve_owner(calldepth=1)
  for opt in opts:
    isinstance(opt,_TDLBaseOption) and opt.init(owner,False)
  global compile_options
  compile_options += opts

def TDLRuntimeOptions (*opts):
  """this fadds a number of entries (created with TDLOption or TDLJob) to the
  run-time menu""";
  global runtime_options;
  # owner is at depth 1 -- our caller
  owner = _resolve_owner(calldepth=1);
  for opt in opts:
    isinstance(opt,_TDLBaseOption) and opt.init(owner,True);
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

