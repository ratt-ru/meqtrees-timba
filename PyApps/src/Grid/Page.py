#!/usr/bin/env python3
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

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Grid.Debug import *
from Timba import *

import weakref
import re
import gc
import types

from PyQt4.Qt import *
import Kittens.widgets
from Kittens.widgets import PYSIGNAL
    
# ====== Grid.Page ===========================================================
# manages one page of a gridded workspace
#
class Page (object):
  class GridRow (QSplitter):
    def __init__(self,parent):
      QSplitter.__init__(self,Qt.Horizontal,parent);
      self._cells = [];
    def cells (self):
      return self._cells;
      
  def __init__ (self,gw,parent_widget,max_nx=5,max_ny=5,fixed_cells=False):
    self._topgrid = QSplitter(Qt.Vertical,parent_widget);
    self._gw = gw;
    self.max_nx     = max_nx;
    self.max_ny     = max_ny;
    self.max_items  = max_nx*max_ny;
    self._rows      = [];
    self._frag_tag = None;
    self._pagename = self._autoname = '';
    self._icon = QIcon();
    self._icon_cou = False;
    # possible layout formats (nrow,ncol)
    self._layouts = [(1,1)];
    for i in range(2,self.max_nx+1):
      self._layouts += [(i,i-1),(i,i)];
    # create cells matrix
    for irow in range(self.max_ny):
      row = self.GridRow(self._topgrid);
      row.hide();
      self._rows.append(row);
      for icol in range(self.max_nx):
        pos = (self,irow,icol);
        cell = Timba.Grid.Cell(row,pos,fixed_cell=fixed_cells,page=self);
        row._cells.append(cell);
        cell._clear_slot = curry(self._clear_cell,cell);
        QWidget.connect(cell.wtop(),PYSIGNAL("closed()"),cell._clear_slot);
        cell._drop_slot = curry(self.drop_cell_item,cell);
        QWidget.connect(cell.wtop(),PYSIGNAL("itemDropped()"),
                        cell._drop_slot);
        cell._cv_slot = curry(self.change_viewer,cell);                
        QWidget.connect(cell.wtop(),PYSIGNAL("changeViewer()"),cell._cv_slot);
        # cell._display_slot = curry(self._display_data_item,parent=weakref.ref(cell));
        # QWidget.connect(cell.wtop(),PYSIGNAL("displayDataItem()"),
        #                cell._display_slot);
    # prepare layout
    self.set_layout(0);
    
  def set_icon (self,icon,clear_on_update=False):
    _dprint(2,icon);
    self._icon = icon or QIcon();
    self._icon_cou = clear_on_update;
    self.wtop().emit(SIGNAL("setIcon"),self._icon,);
    
  def clear_icon (self):
    self.set_icon(None);
    
  def clear_name (self):
    self.set_name(self._autoname);
    
  def get_icon (self):
    return self._icon;
    
  def set_name (self,name,auto=False):
    _dprint(2,name,auto);
    self._pagename = name;
    if auto:
      self._autoname = name;
    self.wtop().emit(SIGNAL("setName"),name,);
  
  def get_name (self):
    return self._pagename;
    
  def is_auto_name (self):
    return self._autoname == self._pagename;
    
  def gw (self):
    """returns parent Grid.Workspace object""";
    return self._gw;
    
  def set_fragile_tag (self,tag=None):
    """A "fragile tag" disappears whenever a page is updated with anything.
    This is useful for, e.g., keeping track of whether a page has been loaded
    from a pagemark and not modified since, etc.""";
    if tag is None:
      self._frag_tag = None;
    else:
      self._frag_tag = weakref.ref(tag);
      
  def get_fragile_tag (self):
    if self._frag_tag is None:
      return None;
    return self._frag_tag();
      
  def updated (self):
    _dprint(3,'page updated');
    self._frag_tag = None;
    if self._icon_cou:
      self.clear_icon();
    self.wtop().emit(SIGNAL("updated"));
    
  def change_viewer (self,cell,dataitem,viewer):
    self.updated();
    dataitem.cleanup();
    cell.wipe();
    Timba.Grid.Services.addDataItem(dataitem,viewer=viewer,
                  gw=self._gw,position=cell.grid_position());
                  
  def drop_cell_item (self,cell,item,event):
    source_cell = getattr(event.source(),'_grid_cell',None);
    if not isinstance(source_cell,Timba.Grid.Cell):
      source_cell = None;
    our_content = cell.content_dataitem();
    # figure out if we need to swap source/destination cells
    action = None;
    # dropping item from another cell: show menu for move/swap
    if source_cell:
      try: menu = self._cell_swap_menu;
      except AttributeError:
        menu = self._cell_swap_menu = QMenu(self.wtop());
        self._menu_slab = Kittens.widgets.addMenuLabel(menu,"");
        self._qa_move_cell   = menu.addAction(pixmaps.slick_redo.icon(),"Move cell");
        self._qa_dup_cell    = menu.addAction(pixmaps.slick_editcopy.icon(),"Duplicate cell");
        self._qa_swap_cells  = menu.addAction(pixmaps.slick_reload.icon(),"Swap cells");
        self._qa_cancel_drop = menu.addAction(pixmaps.red_round_cross.icon(),"Cancel drop");
      self._menu_slab.setText("<nobr>dragging "+item.caption+"</nobr>");
      self._qa_swap_cells.setVisible(our_content is not None); 
      pos = cell.wtop().mapToGlobal(event.pos());
      action = menu.exec_(pos);
      # cancel selected or menu closed, do nothing
      if not action or action is self._qa_cancel_drop:
        return;
    else:
      # assign 1,2,3 to these if menu is not createed (for comparisons below)
      self._qa_move_cell,self._qa_dup_cell,self._qa_swap_cells = 1,2,3;
    # clear our own cell
    if our_content:
      our_content.cleanup();
      cell.wipe();
    # if duplicate cell is selected, create a new data item
    if action is self._qa_dup_cell:
      item = Timba.Grid.DataItem(item);
    # move cell is selected, clear source cell completely
    elif action is self._qa_move_cell:
      if source_cell:
        source_cell.close();
    # swap is selected, move our content to source cell
    elif action is self._qa_swap_cells:
      item.cleanup();
      source_cell.wipe();
      source_pos = source_cell.grid_position();
      Timba.Grid.Services.addDataItem(our_content,
          gw=source_pos[0].gw(),position=source_pos);
    # add content for this cell
    Timba.Grid.Services.addDataItem(item,gw=self.gw(),position=cell.grid_position());
  
  def num_layouts (self):
    return len(self._layouts);
    
  def current_layout (self):
    return (self._cur_layout_num,) + self._cur_layout;
    
  def has_content (self):
    """returns True if page has content on it""";
    (nrow,ncol) = self._cur_layout;
    for row in self._rows[:nrow]:
      for cell in row._cells[:ncol]:
        if cell.content_udi():
          return True;
    return False;
  
  def get_cell (self,row,col):
    return self._rows[row]._cells[col];
  
  # changes current layout scheme
  def set_layout (self,nrow,ncol=None):
    """set_layout(n) sets layout #n. set_layout(nr,nc) sets minimal layout 
    to display nr x nc cells""";
    self.updated();
    if ncol is None:
      nlo = nrow;
    else:
      for (i,(nr,nc)) in enumerate(self._layouts):
        if nr >= nrow and nc >= ncol:
          nlo = i;
          break;
    (nrow,ncol) = self._cur_layout = self._layouts[nlo];
    self._cur_layout_num = nlo;
    _dprint(4,"setting layout:",self._cur_layout);
    for row in self._rows[:nrow]:
      for cell in row.cells()[:ncol]: 
        # if not cell.is_empty(): 
        cell.show();
      for cell in row.cells()[ncol:]: cell.hide();
      row.show();
    for row in self._rows[nrow:]:
      row.hide();
    self.align_layout();
    # emit signal for change of layout
    self.wtop().emit(SIGNAL("layoutChanged"),nlo,len(self._layouts),nrow,ncol);
    return self._cur_layout;
    
  # increments current layout scheme by one (i.e. adds more windows)
  def next_layout (self):
    try: return self.set_layout(self._cur_layout_num+1);
    except IndexError: 
      return None;
      
  def align_layout (self):
    xsizes = [1000]*self.max_nx;
    list(map(lambda row:row.setSizes(xsizes),self._rows));
    self._topgrid.setSizes([1000]*self.max_ny);
    
  # returns top-level widget
  def wtop   (self):
    return self._topgrid;
    
  def clear (self):
    _dprint(2,'GriddedPage: clearing');
    self.updated();
    self.set_layout(0);
    for row in self._rows:
      _dprint(2,'GriddedPage: clearing row',row);
      list(map(lambda cell:cell.close(),row.cells()));
    self.clear_icon();
    self.clear_name();
    
  def find_cells (self,udi,new=False,avoid_pos=None,nrow=1,ncol=1):
    """Finds a free cell if one is available, switches to the next layout
    as needed. Returns Cell object, or None if everything is full.
    If new=False, tries to reuse unpinned cells before switching layouts.
    When picking a cell to reuse, avoids the following cells:
      * pinned cells
      * cells with a leader (so that blocks of cells are never broken up)
      * cell at position avoid_pos
        (this option is specified when a viewer in a cell is used to launch
        another viewer, e.g. for a sub-data item -- in this case the "child"
        viewer shouldn't reuse the cell of the parent).
      * cells whose contents are "parents" of this one
        (i.e. whose UDI is a prefix of this UDI) 
    If new=True, always allocates a new cell.
    """;
    _dprint(2,udi);
    (avx,avy) = avoid_pos or (-1,-1);
    # loop over layouts until we find a cell (or run out of layouts)
    while True:
      (nrow,ncol) = self._cur_layout;
      # find free space in layout
      for icol in range(ncol):
        for (irow,row) in enumerate(self._rows[:nrow]):
          if icol != avx or irow != avy:
            cell = row.cells()[icol];
            if cell.is_empty():
              return (cell,);
      # no free space, try to find an unpinned cell (starting from the back)
      if not new:
        for icol in range(ncol-1,-1,-1):
          for irow in range(nrow-1,-1,-1):
            cell = self._rows[irow].cells()[icol];
            # avoid: pinned cells, follower cells (leader not None),
            # parents of our udi, and cells speciified by the avoid position
            _dprint(5,cell.is_pinned(),cell.leader(),icol,irow);
            if ( not cell.is_pinned() ) and          \
               ( cell.leader() is None ) and     \
               ( not ( icol == avx and irow == avy) ) and \
               ( not cell.is_parent_of(udi) ):
              cell.wipe();
              return (cell,);
      # current layout is full: proceed to next layout
      if not self.next_layout():
        return None;
        
  def alloc_cells (self,pos,nrow=1,ncol=1):
    self.updated();
    (row,col) = pos;
    _dprint(2,row,col);
    # increment layout until we can house the cell position
    while col >= self._cur_layout[1] or row >= self._cur_layout[0]:
      if not self.next_layout():
        return None;
    row = self._rows[row];
    cell = row.cells()[col];
    if not cell.is_empty():
      cell.wipe();
    return (cell,);

  def _clear_cell (self,cell):
    # if a cell is closed and layout is not empty, rearrange the layout
    if self._cur_layout_num:
      self.rearrange_cells();
      
  # rearranges cells by getting rid of empty rows and columns
  def rearrange_cells (self):
    nrow = 0;
    ncol = 0;
    # find max dimensions of non-empty cells
    for (irow,row) in enumerate(self._rows):
      for (icol,cell) in enumerate(row.cells()):
        if not cell.is_empty():
          nrow = max(nrow,irow);
          ncol = max(ncol,icol);
    nrow += 1;
    ncol += 1;
    # are they good for the current layout?
    if nrow == self._cur_layout[0] and ncol == self._cur_layout[1]:
      return;
    # find suitable layout
    for (i,(nr,nc)) in enumerate(self._layouts):
      if nr >= nrow and nc >= ncol:
        self.set_layout(i);
        break;
    else:
      raise Grid.Error("failed to find a suitable layout");

