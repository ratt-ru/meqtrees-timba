#!/usr/bin/python

from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.widgets import *
from Timba.Grid.Debug import *
import Timba.Grid.Cell
from Timba import *

import weakref
import sets
import re
import gc
import types
from qt import *

_reg_viewers = {};

# registers a viewer plug-in for the specified type
#
# a viewer plug-in must provide the following interface:
#

def registerViewer (tp,viewer,priority=0):
  """Registers a viewer for the specified type:
  The 'viewer' argument must be a class (or callable) providing the following 
  interface:
    viewer.viewer_name 
      # (optional static attribute) returns "official name" of this 
      # viewer class, for use in menus and such. If not defined, the classname 
      # (viewer.__name__) will be used instead. 
    viewer.is_viewable(data); 
      # (optional static method) checks if a specific data item (of the 
      # registered type) is viewable in this viewer or not. If not defined, 
      # True is assumed.
    viewer.uses_cells 
      # (optional static attribute) does this viewer uses the workspace at all?
      # True is assumed. (Should be False for viewers creating their own
      # windows).
    viewer.icon(); 
      # (optional static method) returns a QIconSet for this viewer
    vo = viewer(gw,cellspec,dataitem,**opts); 
      # construct a viewer object. The gw argument is its parent 
      # GriddedWorkspace object from which the viewer may allocate cells and 
      # pages as needed. 
      # The cellspec argument should be passed to gw.allocate_cells() when 
      # allocating cell(s). This will contain information on how to allocate 
      # a cell (i.e., if an existing cell should be reused, or a new one 
      # allocated, etc.)
      # A dataitem (GridDataItem class) will be supplied at this 
      # time, although dataitem.data may be None if the object is not yet 
      # populated. 
      # **opts may be used to pass in optional keyword arguments on a 
      # per-viewer basis.
    vo.make_visible();
      # Try to make this viewer visible; return True on success. 
      # Cell-based viewers should simply call make_visible() on their cell; 
      # viewers with their own windows should bring their windows to the 
      # front. Returns True if viewer was made visible, False if not 
      # (i.e. cell is on a non-visible page).
    vo.set_data(dataitem,**opts);
      # sets/updates the content of the viewer. **opts may be used to pass 
      # in optional keyword arguments on a per-viewer basis.
    vo.add_data(dataitem,**opts); 
      # (optional method) adds another data object to the viewer. If 
      # multiple-object viewing is not supported, the viewer class should not
      # define this method. The method must return True if the object is
      # successfully added, or False if this cannot be done.
  The viewer object may also issue one Qt signal: PYSIGNAL("refresh()",(udi,)), 
  which requests a refresh of the data item given by the udi.
  Note that the GridCell interface already provides a refresh button which does 
  the same on behalf of the viewer.
  """;
  global _reg_viewers;
  _dprint(1,"registering",viewer,"for type",tp);
  _reg_viewers.setdefault(tp,[]).append((priority,viewer));

def isViewableWith (arg,viewer):
  if type(arg) is type:
    return True;
  try: checker = viewer.is_viewable;
  except AttributeError: return True; 
  if callable(checker):
    return checker(arg);
  return True;

def isViewable (arg):
  global _reg_viewers;
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
  for (tp,vlist) in _reg_viewers.iteritems():
    # registered type must be a superclass of the supplied type;
    # registered dmi type must be either None or match the argument dmi type
    if issubclass(datatype,tp):
      for (pri,viewer) in vlist:
        if isViewableWith(arg,viewer):
          return True;
  return False;

def getViewerList (arg):
  global _reg_viewers;
  if arg is None:
    return [];
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
  viewer_list = [];
  # resolve data type (argument may be object or type)
  for (tp,vlist) in _reg_viewers.iteritems():
    # find viewers for this class
    if issubclass(datatype,tp):
      if type(arg) is type:  # if specified as type, add all
        viewer_list.extend(vlist);
      else: # if specified as object, check to see which are compatible
        viewer_list.extend([(pri,v) for (pri,v) in vlist if isViewableWith(arg,v)]);
  # sort by priority
  viewer_list.sort();
  return [ v for (pri,v) in viewer_list ];


class Floater (QMainWindow):
  """implements a floating window""";
  def __init__ (self,parent):
    fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
    fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
    QMainWindow.__init__(self,parent,"float",fl);
    self.setIcon(pixmaps.float_window.pm());
  def hideEvent (self,ev):
    _dprint(1,'hideEvent',ev);
    self.emit(PYSIGNAL("hidden()"),());
  def closeEvent (self,ev):
    _dprint(1,'closeEvent',ev);
    self.hide();
    ev.ignore();
    
_dataitems = {};
_current_gw = None;
    
def setDefaultWorkspace (gw):
  global _current_gw;
  _current_gw = gw;

def addDataItem (item,gw=None,show_gw=True,viewer=None,position=None,avoid_pos=None,newcell=False,newpage=False):
  """Adds a data cell with a viewer the given item.
     viewer:    if not None, must a be a viewer plugion class. Overrides
                the viewer specified by the item.
     gw:        if not None, specifies a non-default gridded workspace to
                display the item on.
     position:  if not None, must be a tuple specifying a cell to allocate, 
                as (gridpage,x,y)
     avoid_pos: if not None, must be a tuple specifying a cell to AVOID
                allocating, as (gridpage,x,y). 
     newpage:   if True, creates a new page with the data cell
     newcell:   if True, uses an empty cell (changing layouts as needed)
                rather than reusing an existing unpinned panel. If False,
                reuses a panel if possible.
     Note that the position, newpage and newcell argument are rolled up into
     a "cell specification" dict, and passed to the viewer object as the 
     cellspec argument. The cellspec is then passed as keyword arguments
     (via **cellspec) to Workspace.allocate_cells() when the viewer goes 
     to allocate cells for itself.
  """;
  _dprint(2,item.udi,item.viewer);
  global _dataitems,_current_gw;
  # if position is specified, select workspace from page
  if position is not None:
    item._gridded_workspace = gw = position[0].gw();
  else:
    item._gridded_workspace = gw = gw or _current_gw;
  viewer = viewer or item.viewer;
  if not viewer:
    if not item.viewer_list:
      raise TypeError,"no viewers registered and none explicitly specified";
    viewer = self.viewer_list[0];
  # Are we already displaying this item? (if not, init with empty list)
  itemlist = _dataitems.setdefault(item.udi,[]);
  # see if we can get away with not adding a viewer at all, because
  # it is already displayed with the same viewer class, and we're
  # not requested to put it into a new cell or a specific cell
  if itemlist and not (position or newcell or newpage):
    _dprint(2,'item already displayed, checking for suitable viewers');
    for item0 in itemlist:
      if item0.viewer == viewer and item0.viewer_obj.make_visible():
        _dprint(2,'found visible viewer');
        # in this case, highligh the data item, ask for a refresh, and
        # let the viewers take care of the rest
        highlightDataItem(item);
        if item.data is not None:
          item0.update(item.data);
        else:
          item0.refresh();
        if show_gw:
          gw.show();
        return;
  # ok, we got to here so we have to create a viewer
  vopts = {};
  vopts.update(item.viewopts.get(None,{}));
  for (vclass,vo) in item.viewopts.iteritems():
    if vclass and issubclass(viewer,vclass):
      vopts.update(vo);
  cellspec = { 'position':position,'avoid_pos':avoid_pos,'newcell':newcell,'newpage':newpage };
  try:
    item.viewer_obj = viewer(gw,dataitem=item,cellspec=cellspec,**vopts);
  except:
    (et,ev,etb) = sys.exc_info();
    errstr = '<qt><center><big>Error creating a plug-in of class <b>%s</b> for item <tt>%s</tt>.</big></center>'%(viewer.__name__,item.udi);
    errstr += '<p><tt>%s</tt>: %s'% \
        (getattr(ev,'_classname',ev.__class__.__name__),getattr(ev,'__doc__',''));
    if hasattr(ev,'args'):
      errstr += '</p><p>("'+' '.join(ev.args)+'")</p>';
    errstr += '</p></qt>';
    _dprint(0,errstr);
    print '======== exception traceback follows:';
    traceback.print_tb(etb);
    QMessageBox.warning(None,'Error initializing plug-in',errstr,QMessageBox.Ok,QMessageBox.NoButton);
    return;
  # add to list
  itemlist.append(item);
  # highlight it
  highlightDataItem(item);
  # ask for a refresh of the item
  item.refresh();
  # show the workspace
  if show_gw:
    gw.show();

def removeDataItem (item):
  global _dataitems;
  itemlist = _dataitems.get(item.udi,[]);
  _dprint(2,item.udi,len(itemlist),'instances');
  for i in range(len(itemlist)):
    if itemlist[i] is item:
      _dprint(2,'removing instance',i);
      del itemlist[i];
      return;
  _dprint(2,'no matching items found');
  
_highlighted_items = [];  
  
def highlightDataItem (item):
  global _highlighted_items;
  # remove highlights from previous cells, if any
  if _highlighted_items:
    map(lambda i:i.highlight(False),_highlighted_items);
  _highlighted_items = _dataitems.get(item.udi,[]);
  map(lambda i:i.highlight(),_highlighted_items);

# updates a data item, if it is known
def updateDataItem (udi,data):
  global _dataitems;
  _dprint(3,udi);
  # scan current data items to see which need updating
  for (u,itemlist) in _dataitems.iteritems():
    if u.startswith(udi):
      _dprint(3,len(itemlist),'items for',u);
      update = True;
      data1 = data;  # data1 may get modified below
      subudi = u[len(udi):];
      if subudi:   # a sub-udi, so we must process it by indexing into the data
        # split into keys and process one by one (first one is empty string)
        for key in subudi.split("/")[1:]:
          try: data1 = data1[key];
          except TypeError: # try to convert key to integer instead
            try: data1 = data1[int(key)];
            except TypeError,KeyError: 
              update = False;
              break;
      # update for all items in list
      if update:
        for item in itemlist:
          _dprint(3,'updating',item);
          item.update(data1);
