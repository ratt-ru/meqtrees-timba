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
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.widgets import *
import Timba.Grid 
from Timba.Grid.Services import *
from Timba.Grid.Debug import *
from Timba import *

import re
import gc
import types

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

class CellBlock (object):
  """A Grid.CellBlock represents a block of grid cells (1x1 by default) used
  by a viewer-plugin to display data. The block is managed as a whole,
  and takes care of allocating cell widgets, floating/unfloating cells,
  etc.""";
    
  def __init__ (self,gw,dataitem,size=1,cellspec={},floating=False):
    """Initializes a cell block of the given size. Arguments are:
    size:     use (N,M) to allocate N cells across by M high; a single
              integer N is a shortcut for (N,1)
    dataitem: the GridDataItem object associated with the cell block.
              Used within as follows:
                * dataitem._gridded_workspace refers to the GriddedWorkspace
                * the workspace is used to allocate cells
                * the workspace is asked to remove the dataitem (and thus
                  the associated viewer) when the cells are closed.
    cellspec: keyword arguments passed to workspace.allocate_cells(). This
              is to use things such as {newcell:True}, {newpage:True}, etc.
    floating: if True, the cell block starts out floating. Default is
              to start embedded in the grid.
    """
    self._dataitem = dataitem;
    self._gw = gw;
    _dprint(2,id(self),': allocating for',dataitem.udi,'size',size);
    # for callbacks
    self._currier = PersistentCurrier();
    if isinstance(size,int):
      (self._ncol,self._nrow) = (size,1);
    elif len(size) == 2:
      (self._ncol,self._nrow) = size;
    else:
      raise TypeError("illegal size argument");
    self._totsize = self._ncol*self._nrow;
    if self._totsize < 1:
      raise ValueError("illegal size value");
    # init cell grid in floating window or workspace
    if floating:
      self._allocate_float();
    else:
      self._allocate_grid(**cellspec);
      
  def __del__ (self):
    _dprint(2,id(self));
      
  def cleanup (self):
    """Cleanup method.""";
    _dprint(2,id(self));
    # release all refs and signals
    self._dataitem = None;
    self._currier.clear();
    
    
  def wparent (self,offset=0):
    """Returns parent widget (i.e. cell workspaces) for viewers to attach 
    their widget content to. 'offset' specifies the cell in the block:
    for an NxM block, this is either an integer from 0 to N*M-1 (counting
    across, then down), or an (x,y) tuple ranging from (0,0) to (N-1,M-1).
    """;
    if not isinstance(offset,int):
      if len(offset) == 2:
        offset = offset[1]*self._nrow + offset[0];
      else:
        raise TypeError("illegal offset argument");
    if offset<0 or offset >= self._totsize:
      raise ValueError("illegal offset value");
    # return parent
    return self._cells[offset].wtop();
    
  def set_widgets (self,widgets,captions=None,icon=None,enable_viewers=True):
    """Sets widget contents. Should only be called once.
    widgets:    a sequence of one widget per cell, counting across 
                the block, then down. If only a 1x1 block is allocated, 
                content may be a single widget.
    captions:   is an list of captions of the same size as widgets.
                If None is supplied, the dataitem caption is used instead.
    enable_viewers: if False, certain GUI functions will be disabled
    """;
    if isinstance(widgets,QWidget):
      if len(self._cells) != 1:
        raise ValueError("len of widgets argument does not match cell layout");
      widgets = (widgets,);
    else:
      try: n = len(widgets);
      except: raise TypeError("widgets argument must be a QWidget or a list of QWidgets");
      if len(widgets) != len(self._cells):
        raise ValueError("len of widgets argument does not match cell layout");
    self._content = widgets;
    self._icon = icon;
    if captions is None:
      self._captions = getattr(self._dataitem,'caption',self._dataitem.udi);
    else:
      self._captions = captions;
    _dprint(2,id(self),': set content',widgets);
    # initialize cells with contents
    self._init_cells(self._cells,enable_viewers=enable_viewers);
    # connect displayDataItem() signal from contents 
    for w in widgets:
      QWidget.connect(w,PYSIGNAL("displayDataItem()"),self._display_sub_item);
    
  def _allocate_grid (self,**kwds):
    """Allocates self._cells: a grid of cells from a workspace.
    All keywords are passed to gridded_workspace.allocate_cells()."""
    # if a previous position in grid was saved, try to reuse it
    if hasattr(self,'_gridpos'):
      kwds['position'] = self._gridpos;
    self._cells = self._gw.allocate_cells(nrow=self._nrow,ncol=self._ncol,
                                          udi=self._dataitem.udi,**kwds);
    if not self._cells:
      raise Timba.Grid.Error("unable to allocate cells");
    # save new position
    leadcell = self._cells[0];
    self._gridpos = leadcell.grid_position();
    _dprint(2,id(self),': allocated',len(self._cells),'cells at position',self._gridpos);
    # connect signal: remove dataitem when cells are closed
    leadcell.connect(PYSIGNAL("wiped()"),
      self._currier.xcurry(Timba.Grid.Services.removeDataItem,_args=(self._dataitem,),_argslice=slice(0)));
    # connect signal: float cells
    leadcell.connect(PYSIGNAL("float()"),self.float_cells);
    
  def _init_cells (self,cells,enable_viewers=True):
    """initializes cells with captions and dataitem.""";
    cw = list(zip(cells,self._content));
    # init leader cell
    cells[0].set_content(self._content[0],dataitem=self._dataitem,icon=self._icon,enable_viewers=enable_viewers);
    # init other cells as followers
    for (c,w) in cw[1:]:
      c.set_content(w,leader=cells[0],icon=self._icon,enable_viewers=enable_viewers);
    # setup cell captions
    if self._captions is None:
      cells[0].set_caption(self._dataitem.caption);
    elif isinstance(self._captions,str):
      cells[0].set_caption(self._captions);
    elif len(self._captions) == len(cells):
      for (cell,capt) in zip(cells,self._captions):
        cell.set_caption(capt);
                      
  def _display_sub_item (self,dataitem,kwargs):
    Timba.Grid.Services.addDataItem(dataitem,gw=self._gw,avoid_pos=self._gridpos,**kwargs);
        
  def _allocate_float (self):
    """internal helper func: creates a float window when first called.""";
    try: float_window = self._float_window;
    except AttributeError:
      self._float_window = float_window = Timba.Grid.Floater(self._gw.wtop());
      QObject.connect(float_window,PYSIGNAL("closed()"),self._unfloat);
      float_window.setWindowTitle(self._dataitem.name);
      # allocate single cell or grid
      if self._totsize == 1: 
        # notitle=True: do not create cell titlebar
        cell = Timba.Grid.Cell(float_window,(0,0),notitle=True);
        self._float_cells = ( cell, );
        float_window.setCentralWidget(cell.wtop());
      else:
        self._float_grid = Timba.Grid.Page(self._gw,float_window,self._ncol,self._nrow);
        # allocate grid of fixed cells (fixed means no drop support and 
        # no change of viewer allowed)
        self._float_cells = self._float_grid.allocate_cells(nrow=self._nrow,ncol=self._ncol,
                            fixed_cells=True);
        float_window.setCentralWidget(self._float_grid.wtop());
    # connect signal: remove dataitem when cells are closed
    self._float_cells[0].connect(PYSIGNAL("closed()"),self.close);
    return float_window;
    
  def close (self):
    Timba.Grid.Services.removeDataItem(self._dataitem);
    # destroy float, if any
    float_window = getattr(self,'_float_window',None);
    if float_window:
      float_window.hide();
      float_window.reparent(QWidget(),QPoint(0,0));
      self._float_window = None;
    self._dataitem = self._float_grid = self._float_cells = None;
    
  def _unfloat (self):
    _dprint(1,'unfloating cells');
    # if dataitem is None, then we've closed the floating cell so we don't
    # need to deallocate anything
    if self._dataitem is not None:
      # this allocates grid cells into self._cells
      self._allocate_grid(newcell=True);
      # move content widgets back into the grid
      for (w,cell,pos,fcell) in zip(self._content,self._cells,self._content_pos,self._float_cells):
        w.setParent(cell.wtop());
        fcell.release();
      # reinitialize grid cells
      self._init_cells(self._cells);
  
  def float_cells (self,dum=None):
    """floats contents in separate window. dum argument is provided
    for compatibility with the cell's float() signal (which has a single 
    argument)""";
    _dprint(1,'floating cells');
    # allocate float if one is not already created
    float_window = self._allocate_float();
    # store positions of content widgets within their parent cells
    _dprint(2,'content is',self._content);
    self._content_pos = [ c.pos() for c in self._content ];
    # reparent all content widgets into the float cells, release grid cells
    _dprint(2,'float_cells',self._float_cells);
    for (w,cell,fcell) in zip(self._content,self._cells,self._float_cells):
      fcell.wtop().resize(cell.wtop().size());
      # w.reparent(fcell.wtop(),w.pos(),True);
      w.setParent(fcell.wtop());
      cell.release();
    # init float cells
    self._init_cells(self._float_cells);
    # show float window 
    self._cells = self._float_cells;
    # disable drops onto float
    for c in self._float_cells:
      c.wtop().setAcceptDrops(False);
    float_window.show();
    
  # hide the float window, thus causing the __unfloat() func above to be 
  # executed (via the hidden() signal of Floater) to do all the real
  # unfloating
  def unfloat_cells (self):
    """moves contents back to the grid""";
    _dprint(2,'hiding floater, unfloat call expected');
    float_window = getattr(self,'_float_window',None);
    if self.float_window:
      float_window.close();
   
  def grid_page (self):
    return self._cells[0].parent_page();
    
  def cell_menu (self):
    return self._cells[0].cell_menu();
    
  def flash_refresh (self):
    # flash leader cell (all follower cells will respond, see Grid.Cell)
    self._cells[0].flash();
    
  def highlight (self,color=True):
    # highlight leader cell (all follower cells will respond, see Grid.Cell)
    self._cells[0].highlight(color);
    
  def enable (self,enable=True):
    # enable leader cell (all follower cells will respond, see Grid.Cell)
    self._cells[0].enable(enable);
    
  def set_pinned (self,pinned=True):
    self._cells[0].set_pinned(pinned);
    
