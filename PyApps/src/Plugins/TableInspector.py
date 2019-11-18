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

import Timba
from Timba.dmi import *

from Timba.GUI.pixmaps import pixmaps

from Timba.GUI.treebrowser import NodeAction


import Timba.GUI.app_proxy_gui


from Timba import Grid

from Timba.GUI import browsers

from Timba.ParmDB import *

from qt import *
from qttable import *
import os


_dbg = verbosity(0,name='TableInspector');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class TableInspector(browsers.GriddedPlugin):
    viewer_name = "TableInspector";
    _icon = pixmaps.table;
    """GUI to inspect contents of a ParmDB"""
    def is_viewable (data):
        return True;
    
    is_viewable = staticmethod(is_viewable);

    def __init__(self,gw,dataitem,cellspec={},**opts):
        
        browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec,**opts);
        self._db=None;
        self._mainbox = QHBox(self.wparent());
#        self._mainbox = self.wparent();
        self._mainbox.setSpacing(6);
        self._wtop= self._mainbox;

        self._mainvbox = QVBox(self._mainbox);

        #table name menu
        self._tabbox= QVBox(self._mainvbox);
        self._tabbox.setSpacing(6);
        self._table_name=None;
        self._name_label = QLabel("Table Name",self._tabbox);
        self._name_edit = QLineEdit(self._tabbox,"test");
        self._browse_button = QPushButton(self._tabbox);
        self._browse_button.setText("Browse...");
        QObject.connect(self._browse_button,SIGNAL("clicked()"),self._browse);

        #domain buttons menu
        self._axesbox = QVBox(self._mainvbox);
        self._axesbox.setSpacing(6);
        self._get_axis_list();
        self._axes =[];
        self.dim=[];
        self.xfrom=[];
        self.xto=[];
        self.nsteps=[];
        for axis in self._axis_list:
            self._add_axis(str(axis));
            
        #self._buttonbox = QHBox(self._mainvbox);
        #self._add_button = QPushButton("Add Axis",self._buttonbox);
        #QObject.connect(self._add_button, SIGNAL('clicked()'), self._add_axis)
        #self._remove_button = QPushButton("Remove Axis",self._buttonbox);
        #QObject.connect(self._remove_button, SIGNAL('clicked()'), self._remove_axis)
        #extra buttons menu
        self._buttonbox2 = QVBox(self._mainvbox);

        #parmnames menu
        self._parmbox= QVBox(self._mainvbox);
        self._parmbox.setSpacing(6);
        self._parm_label = QLabel("Parameters",self._parmbox);
        self.parmtable = QTable(self._parmbox,"parmlist");
        self.parmtable.setShowGrid(False);
        self.parmtable.setFocusStyle(QTable.FollowStyle);
        self.parmtable.setSelectionMode (QTable.SingleRow );
        self.parmtable.setNumCols(2);      
        self.parmtable.horizontalHeader () .setLabel(0,"name");
        self.parmtable.horizontalHeader () .setLabel(1,"nr. funklets");
        self.parmtable.setColumnWidth(0,200);
        self.parmtable.setColumnWidth(1,150);

        QObject.connect(self.parmtable,SIGNAL("selectionChanged()"),self._get_selected);


        self._parm_button = QPushButton(self._parmbox);
        self._parm_button.setText("Get Parms");

        self._parmlist = [];
        self._funklist = {};
        self._Comp_funklet={};
        QObject.connect(self._parm_button,SIGNAL("clicked()"),self._get_parms);

        self._domain = meq.domain(0,1,0,1);
        
        self._plot_button = QPushButton(self._parmbox);
        self._plot_button.setText("Plot Selection");

        QObject.connect(self._plot_button,SIGNAL("clicked()"),self._plot_parms);
       

        caption = "Inspect Table";
        self.set_widgets(self.wtop(),caption);
  

    def wtop(self):
        return self._wtop;

    def _get_table_name(self):
        name = str(self._name_edit.text());
        self._table_name=name;


    def _get_axis_list(self):

        forest_state=meqds.get_forest_state();
        axis_map=forest_state.axis_map;
        self._axis_list=[];
        for i in axis_map:
            if 'id' in i:
                if i.id:
                    self._axis_list.append(i.id);


    def _add_axis(self,axisnr=0):
        if isinstance(axisnr,int):
            axis_name=self._axis_list[axisnr];
        else:
            axis_name=axisnr;
        
        axis= QHBox(self._axesbox);
        axis.setSpacing(4);
        nr=0;
        nr=len(self._axes);
        if nr>= len(self._axis_list):
            #max number of axes reached
            return;
        self.dim.append(QLabel(axis_name,axis));
        textfrom = QLabel("from",axis);
        self.xfrom.append(QLineEdit(axis));

        textto = QLabel("to",axis);
        self.xto.append(QLineEdit(axis));
        textsteps = QLabel("steps",axis);
        self.nsteps.append(QLineEdit(axis));
        self._axes.append(axis)
        axis.show();


    def _get_range(self,pattern="*"):
        #gets the total domain for a given (sest of)parm(s) and fills the axes wiht these as default values
        self._domain = self._db.getRange(pattern);
        #TESTTESTTESTTEST
        #        self._domain['l'] = [-0.057,0.043];
        #        self._domain['m'] = [-0.038,0.062];


    def setDefaultNaxis(self):
        self._Naxis=[];
        for n in range(len(self._axes)):
             self._Naxis.append(10);


    def _get_selected(self,parm=None):
        if parm == None:
            row = self.parmtable.currentRow();
            parm = str(self.parmtable.item(row,0).text());
        self._get_range(parm);
        if parm not in self._funklist:
            self._get_funklets(parm=parm);
        if parm not in self._Comp_funklet:
            if(len(self._funklist[parm])>1):
                self._Comp_funklet[parm]=ComposedFunklet(self._funklist[parm]);
            else:
                self._Comp_funklet[parm]=self._funklist[parm][0];
                

        self._Comp_funklet[parm].setDomain(self._domain);
        self._Comp_funklet[parm].getNX();
        self._Naxis=self._Comp_funklet[parm].getNAxis();

        if not self._Naxis:
            self.setDefaultNaxis();
        #TESTTESTTESTTEST
#        self._Naxis[2]=10;
#        self._Naxis[3]=10;
        
        for n in range(len(self._axes)):
            axis_name = str(self._axis_list[n]).lower(); 
            if axis_name not in self._domain:
                break;
            self.xfrom[n].setText(str(self._domain[axis_name][0]));
            self.xto[n].setText(str(self._domain[axis_name][1]));
            self.nsteps[n].setText(str(self._Naxis[n]));
        return;
        

    def _remove_axis(self):
        if len(self._axes)<=1:
            return;
        nr=len(self._axes)-1;
        self._axes[nr].close();
        self._axes.pop();
        self.dim.pop();
        self.xfrom.pop();
        self.xto.pop();


    def _browse(self):
        fn = self.open_browse();
        if fn is None:
            return;
        self._table_name=fn;
        self._name_edit.setText(fn);
        self._get_parms();
    
    def open_browse(self):
        """Read a saved inarg record from a file, using a file browser"""
        filename = QFileDialog.getExistingDirectory("", self._wtop);
        if filename == QString.null:
            return None;
        filename = str(filename);
        return filename;


    def _get_parms(self):
        self._get_table_name();
        if not os.path.isdir(self._table_name):
            QMessageBox.warning(self.wtop(),
                                "Warning",
                                "Table not found, Please specify existing table");
            return;
        
        self._db = Parmdb(self._table_name);
        self._parmlist = self._db.getParmNames();
        self._funklist = {};
        #        if self._parmlist:
        self._update_parmtable();

    def _update_parmtable(self):
        if self._parmlist:
            self.parmtable.setNumRows(len(self._parmlist));
        else:
            self.parmtable.setNumRows(0);
            return;
        parmnr=0;
        for parm in self._parmlist:
            self.parmtable.setText(parmnr,0,parm);
            if parm in self._funklist:
                nr_funklets = len(self._funklist[parm]);
                self.parmtable.setText(parmnr,1,str(nr_funklets));
            else:
                self.parmtable.clearCell(parmnr,1);
            parmnr+=1;
        self._get_range();

    def _get_all_funklets(self):
        self._funklist = {};
        for parm in self._parmlist:
            self._funklist[parm] = self._db.getFunklets(parm);
            self._helplist=[];
            for funk in self._funklist[parm]:
                # convert  to evaluatable Funklet:
                self._helplist.append(Funklet(funklet = funk,name=parm));
            self._funklist[parm] = self._helplist;
        #print "all funklets",self._funklist;

    def _get_funklets(self,parm="all"):
        if parm == "all":
            self._get_all_funklets();
        else:
            #print "getting funklets",parm;
            self._funklist[parm] = self._db.getFunklets(parm);
            self._helplist=[];
            for funk in self._funklist[parm]:
                # convert  to evaluatable Funklet:
                self._helplist.append(Funklet(funklet = funk,name=parm));
                self._funklist[parm] = self._helplist;
           
        self._update_parmtable();        
    
    def _plot_parms(self,parm=None):
        if parm == None:
            row = self.parmtable.currentRow();
            parm = str(self.parmtable.item(row,0).text());
        #print "plotting",parm
        if parm is None:
            return;
        if parm not in self._funklist:
            self._get_funklets(parm);
            #print "plotting",self._funklist[parm];
        
            self._Comp_funklet[parm] =  ComposedFunklet(self._funklist[parm]);
        #print self._Comp_funklet[parm].eval({'x0':.4,'x1':.2,'x2':3,'x5':4});
        cells = self._getCells();

        #print cells;
        self._Comp_funklet[parm].plot(cells=cells,parent=self._wtop);
        

    def _getCells(self):
      dom = self._domain;
      cells = meq.cells(dom,num_time=self._Naxis[0],num_freq=self._Naxis[1]);
      #add more axes here...
      #print "domain",dom
      for dim in range(2,len(self._axis_list)):
          id = str(self._axis_list[dim]).lower();
          if id in dom:
              step_size=float(dom[id][1]-dom[id][0])/self._Naxis[dim];
              #print "steP", step_size,self._Naxis[dim],dom;
              startgrid=0.5*step_size+dom[id][0];
              grid = [];
              cell_size=[];
              for i in range(self._Naxis[dim]):
                  grid.append(i*step_size+startgrid);
                  cell_size.append(step_size);
              cells.cell_size[id]=array(cell_size);
              cells.grid[id]=array(grid);
              cells.segments[id]=record(start_index=0,end_index=self._Naxis[dim]-1);

      cells.domain=dom;

      
      return cells;


def _start_table_inspector ():
  _dprint(2,'adding a table inspector');
  # Create a 'data item', which represents our box in the grid.
  # The first argument is a UDI, we only need to ensure it is unique
  # so that it doesn't get confused with other data items in the system
  item = Grid.DataItem('/TableInspector',                    # UDI
                        name='Table Inspector',         # name
                        caption='<b>Table Inspector</b>',       # caption for GUI -- note use of Rich Text markup
                        desc='Table inspector plug-in',
                        data=None,refresh=None,             # no data and no refresh function
                        viewer=TableInspector);           # viewer class
  # this registers us with the grid and creates a viewer
  Grid.addDataItem(item);



# this is called automatically by the browser to populate the tree browser
# context menus and toolbar
def define_treebrowser_actions (tb):
  #return;  # temporary while this plugin is broken
  _dprint(1,'defining table inspector treebrowser actions');
  parent = tb.wtop();
  # create QAction for the Stream control plugin
  global _qa_table;
  _qa_table = QAction("Table Inspector",pixmaps.table.iconset(),"Table Inspector",0,parent);
  _qa_table.setMenuText("Table Inspector");
  # make sure it's enabled/disabled as appropriate
  _qa_table._is_enabled = lambda tb=tb: tb.is_connected;
  # "45" is priority of action, determining its place in the toolbar
  tb.add_action(_qa_table,45,callback=_start_table_inspector);





def define_mainmenu_actions (menu,parent):
  #return;  # temporary while this plugin is broken
  _dprint(1,'defining table inspector menu actions');
  global _qa_table;
  # add ourselves to the MeqTrees menu
  _qa_table.addTo(menu['MeqTrees']);

