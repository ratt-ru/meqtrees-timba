#!/usr/bin/python

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

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Grid.Debug import *
from Timba import *

import weakref
import sets
import re
import gc
import types
from qt import *

# ====== Grid.Workspace ======================================================
# implements a multi-page, multi-panel viewing grid
#
class Workspace (object):
  # define a toolbutton that accepts drops of DataItems
  class DataDropButton(Timba.GUI.widgets.DataDroppableWidget(QToolButton)):
    def accept_drop_item_type (self,itemtype):
      return issubclass(itemtype,Timba.Grid.DataItem);
        
  def __init__ (self,parent,max_nx=4,max_ny=4,use_hide=None):
    # dictionary of UDIs -> list of GridDataItem objects 
    self._dataitems = dict();
    # highlighted item
    self._highlight = None;
    # highlight color
    self._highlight_color = QApplication.palette().active().highlight();
    # currier
    self._currier = PersistentCurrier();
    self.curry = self._currier.curry;
    self.xcurry = self._currier.xcurry;
  
    self._maintab = QTabWidget(parent);
    self._maintab.setTabPosition(QTabWidget.Top);
    QWidget.connect(self._maintab,SIGNAL("currentChanged(QWidget*)"),self._set_layout_button);
    self.max_nx = max_nx;
    self.max_ny = max_ny;
    # set of parents for corners of the maintab (added on demand when GUI is built)
    self._tb_corners = {};
    #------ add page
    newpage = self.add_tool_button(Qt.TopLeft,pixmaps.tab_new_raised.pm(),
        tooltip="open new page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self.add_page);
    newpage._dropitem = xcurry(Timba.Grid.Services.addDataItem,_argslice=slice(0,1),newpage=True);
    QWidget.connect(newpage,PYSIGNAL("itemDropped()"),
        newpage._dropitem);
    #------ new panels button
    self._new_panel = self.add_tool_button(Qt.TopLeft,pixmaps.view_right.pm(),
        tooltip="add more panels to this page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self._add_more_panels);
    self._new_panel._dropitem = xcurry(Timba.Grid.Services.addDataItem,_argslice=slice(0,1),newcell=True);
    QWidget.connect(self._new_panel,PYSIGNAL("itemDropped()"),
        self._new_panel._dropitem);
    #------ align button
    self.add_tool_button(Qt.TopLeft,pixmaps.view_split.pm(),
        tooltip="align panels on this page",
        click=self._align_grid);
    #------ remove page
    self.add_tool_button(Qt.TopRight,pixmaps.tab_remove.pm(),
        tooltip="remove this page",
        click=self.remove_current_page);
    # init first page
    self.add_page();
  
  # adds a tool button to one of the corners of the workspace viewer
  def add_tool_button (self,corner,pixmap,tooltip=None,click=None,
                        leftside=False,class_=QToolButton):
    # create corner box on demand
    layout = self._tb_corners.get(corner,None);
    if not layout:
      parent = QWidget(self._maintab);
      self._tb_corners[corner] = layout = QHBoxLayout(parent);
      layout.setMargin(2);
      self._maintab.setCornerWidget(parent,corner);
    # add button
    button = class_(layout.mainWidget());
    button._gw = weakref.proxy(self);
    if leftside:
      layout.insertWidget(0,button);
    else:
      layout.addWidget(button);
    button.setPixmap(pixmap);
    button.setAutoRaise(True);
    if tooltip:
      QToolTip.add(button,tooltip);
    if callable(click):
      QWidget.connect(button,SIGNAL("clicked()"),click);
    return button;
    
  def wtop (self):
    return self._maintab;
    
  def show (self,shown=True):
    self.wtop().setShown(shown);
    self.wtop().emit(PYSIGNAL("shown()"),(shown,));
  
  def hide (self):
    self.wtop().hide();
    self.wtop().emit(PYSIGNAL("shown()"),(False,));
    
  def isVisible (self):
    return self.wtop().isVisible();
    
  def add_page (self,name=None,iconset=None):
    page = Timba.Grid.Page(self,self._maintab,max_nx=self.max_nx,max_ny=self.max_ny);
    wpage = page.wtop();
    wpage._page = page;
    _dprint(2,'name',name,'iconset',iconset);
    # generate page name, if none is supplied
    if name is None:
      name = 'Page '+str(self._maintab.count()+1);
      page.set_name(name,True); # auto_name = True
    else:
      page.set_name(name);
    page.set_icon(iconset);
    # add page to tab
    iconset = iconset or QIconSet();
    _dprint(2,'addTab:',name,iconset);
    self._maintab.addTab(wpage,iconset,name);
    self._maintab.setCurrentPage(self._maintab.count()-1);
    QWidget.connect(wpage,PYSIGNAL("layoutChanged()"),self._set_layout_button);
    wpage._change_icon = curry(self._maintab.setTabIconSet,wpage);
    QWidget.connect(wpage,PYSIGNAL("setIcon()"),wpage._change_icon);
    wpage._rename = curry(self._maintab.setTabLabel,wpage);
    QWidget.connect(wpage,PYSIGNAL("setName()"),wpage._rename);
    return page;
    
  def remove_current_page (self):
    ipage = self._maintab.currentPageIndex();
    page = self._maintab.currentPage();
    page._page.clear();
    # if more than one page, then remove (else clear and rename only)
    if self._maintab.count()>1:
      self._maintab.removePage(page);
    else:
      page._page.set_name("Page 1",True);
    # renumber remaining pages
    for i in range(ipage,self._maintab.count()):
      wpage = self._maintab.page(i);
      page = wpage._page;
      if page.is_auto_name():
        page.set_name('Page '+str(i+1),True);
      
  def current_page (self):
    return self._maintab.currentPage()._page;
    
  def _align_grid (self):
    self.current_page().rearrange_cells();
    self.current_page().align_layout();
  def _add_more_panels (self):
    _dprint(5,"adding more panels");
    self.current_page().next_layout();
  def _set_layout_button (self):
    page = self.current_page();
    (nlo,nx,ny) = page.current_layout();
    self._new_panel.setDisabled(nlo >= page.num_layouts());
  def clear (self):
    _dprint(5,'GriddedWorkspace: clearing');
    self._maintab.page(0)._page.clear();
    for p in range(1,self._maintab.count()):
      page = self._maintab.page(p);
      page._page.clear();
      self._maintab.removePage(page);
      
  def set_current_page (self,page):
    self._maintab.showPage(page.wtop());
    
  def allocate_cells (self,nrow=1,ncol=1,position=None,avoid_pos=None,
                           newcell=False,newpage=False,udi=''):
    """allocates cell or block of cells""";
    # is an explicit cell specified?
    if position:
      (page,x,y) = position;
      if isinstance(page,Timba.Grid.Page):
        self.set_current_page(page);
      else:  # if page specified, create new one, else use current
        if page:
          page = self.add_page();
        else:
          page = self.current_page();
      return page.alloc_cells((x,y),nrow=nrow,ncol=ncol);
    # no, do we need a new page?
    elif newpage:
      self.add_page();
    # find suitable cell(s) and return
    if avoid_pos is not None:
      if avoid_pos[0] is self.current_page():
        avoid_pos = avoid_pos[1:];
      else:
        avoid_pos = None;
    return self.current_page().find_cells(udi,avoid_pos=avoid_pos,new=newcell,nrow=nrow,ncol=ncol) \
            or self.add_page().find_cells(udi,nrow=nrow,ncol=ncol);
