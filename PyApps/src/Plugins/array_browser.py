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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from Timba.dmi import *
from Timba import utils
from Timba import dmi_repr
from Timba.GUI.pixmaps import pixmaps
from Timba import Grid
from Timba.GUI.browsers import GriddedPlugin,PrecisionPopupMenu
from qt import *
from qttable import *

_dmirepr = dmi_repr.dmi_repr();

_dbg = utils.verbosity(0,name='array_browser');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class ArrayTable(QTable):
  extra_col_width  = 1;   # extra column margins, in units of a charcter's width
  extra_row_height = .05;  # extra row margin, in units of a character's height

  def __init__(self,parent,**args):
    QTable.__init__(self,parent,*args);
    font = QFont("Fixed",QFontInfo(QApplication.font()).pointSize());
    font.setFixedPitch(True);
    self.setFont(font);
    self.setSelectionMode(QTable.NoSelection);
    self._arr = None;
    self._prec = (None,'f');

  # changes content
  def set_array (self,arr):
    if not 1<=arr.ndim<=2:
      raise TypeError("illegal array dimensionality");
    self._arr = arr;
    self._rank = arr.ndim;
    _dprint(3,"rank is", self._rank);
    if self._rank == 1:   
      ncol = 1;
    else:
      ncol = arr.shape[1];
    self.reset_colsizes(ncol=ncol);
    self.setNumRows(arr.shape[0]);
    self.setNumCols(ncol);
    # self.repaint_cells();
    self.apply_colsizes();

  def reset_colsizes (self,dum=None,ncol=None):
    # this is continuously updated with the minimum column width
    # required to display each column completely
    _dprint(3,ncol,self.numCols());
    self._colwidths = [0] * (ncol or self.numCols());
    self._rowheight = 0;
    self._adjust_cols = False; # True when widths have been adjusted

  def apply_colsizes (self):
    if self._adjust_cols:
      self._adjust_cols = False;
      fm = QFontMetrics(self.font());
      rh = self._rowheight + int(fm.height()*self.extra_row_height);
      dw = int(fm.width("0")*self.extra_col_width); 
      for irow in range(self.numRows()):
        self.setRowHeight(irow,rh);
      self.setTopMargin(rh);
      for (icol,w) in enumerate(self._colwidths):
        self.setColumnWidth(icol,w+dw);

  # changes precision
  def set_precision (self,prec,format):
    self._prec = (prec,format);
    self.reset_colsizes();
    self.repaint_cells();

  def get_prec (self):
    return self._prec;

  def repaint_cells (self):
    cols = list(range(min(self.columnAt(0),0),max(self.columnAt(self.width())+1,self.numCols())));
    rows = list(range(min(self.rowAt(0),0),max(self.rowAt(self.height())+1,self.numRows())));
    self._colsizes = None; # sets paint mode for paintCell
    for row in rows:
      for col in cols:
        self.updateCell(row,col);

  # redefine paintCell method to paint on-the-fly
  def paintCell(self,painter,row,col,cr,selected):
    (txt,inline) = _dmirepr.inline_str(self._arr[(row,col)[:self._rank]],prec=self._prec);
    if txt is None:
      txt = '';
    # compute bounding box of text to work out cell sizes
    rect0 = QRect(0,0,cr.width(),cr.height());
    box = painter.boundingRect(rect0,Qt.AlignLeft,txt);
    if box.width() > self._colwidths[col]:
      self._colwidths[col] = box.width();
      self._adjust_cols = True;
    if box.height() > self._rowheight:
      self._rowheight = box.height();
      self._adjust_cols = True;
    # set color
    cg = QApplication.palette().active();
    if selected:
      painter.fillRect(rect0,QBrush(cg.highlight()));
      painter.setPen(cg.highlightedText());
    else:
      painter.fillRect(rect0,QBrush(cg.base()));
      painter.setPen(cg.text());
    # actually draw text
    painter.drawText(rect0,Qt.AlignLeft,txt);

  def resizeData(self,len):
    pass;

  # redefine paint event to keep column widths correctly adjusted  
  def paintEvent(self,ev):
    # repaint
    QTable.paintEvent(self,ev);
    # will resize row/columns as needed
    self.apply_colsizes();

class ArrayBrowser(GriddedPlugin):
  _icon = pixmaps.matrix;
  viewer_name = "Array Browser";
  def is_viewable (data):
    try: return 1 <= data.ndim <=2;
    except: return False;
  is_viewable = staticmethod(is_viewable);
  
  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._arr = None;
    self._tbl = ArrayTable(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);
    QObject.connect(self._tbl,PYSIGNAL("fontChanged()"),self._tbl.reset_colsizes);
    context_menu = self.cell_menu();
    if context_menu is not None:
      context_menu.insertSeparator();
      menu = PrecisionPopupMenu(context_menu,prec=self._tbl.get_prec());
      context_menu.insertItem(pixmaps.precplus.iconset(),'Number format',menu);
      QWidget.connect(menu,PYSIGNAL("setPrecision()"),\
                      self._tbl.set_precision);
      
  def wtop (self):
    return self._tbl;
  
  def set_data (self,dataitem,**opts):
    # clear everything and reset data as new
    self._tbl.set_array(dataitem.data);
    self.enable();
    self.flash_refresh();
    
# Give ArrayBrowser slightly higher priority for arrays
Grid.Services.registerViewer(array_class,ArrayBrowser,priority=15);
