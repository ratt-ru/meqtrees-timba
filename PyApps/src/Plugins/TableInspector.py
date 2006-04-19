import Timba
from Timba.dmi import *

from Timba.GUI.pixmaps import pixmaps

from Timba.GUI.treebrowser import NodeAction


import Timba.GUI.app_proxy_gui


from Timba import Grid

from Timba.GUI import browsers

from Timba.ParmDB import *

from Timba.Contrib.MXM.TDL_Funklet import *

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
        self._parm_button = QPushButton(self._parmbox);
        self._parm_button.setText("Get Parms");

        self._parmlist = [];
        self._funklist = {};
        QObject.connect(self._parm_button,SIGNAL("clicked()"),self._get_parms);

        
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
            if i:
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
            if self._funklist.has_key(parm):
                nr_funklets = len(self._funklist[parm]);
                self.parmtable.setText(parmnr,1,str(nr_funklets));
            else:
                self.parmtable.clearCell(parmnr,1);
            parmnr+=1;

    def _get_all_funklets(self):
        self._funklist = {};
        for parm in self._parmlist:
            self._funklist[parm] = self._db.getFunklets(parm);
            self._helplist=[];
            for funk in self._funklist[parm]:
                # convert  to evaluatable Funklet:
                self._helplist.append(Funklet(funklet = funk));
            self._funklist[parm] = self._helplist;
        #print "all funklets",self._funklist;

    def _get_funklets(self,parm="all"):
        if parm == "all":
            self._get_all_funklets();
        else:
            print "getting funklets",parm;
            self._funklist[parm] = self._db.getFunklets(parm);
            self._helplist=[];
            for funk in self._funklist[parm]:
                # convert  to evaluatable Funklet:
                self._helplist.append(Funklet(funklet = funk));
                self._funklist[parm] = self._helplist;
           
        self._update_parmtable();        
    
    def _plot_parms(self,parm=None):
        if parm == None:
            row = self.parmtable.currentRow();
            parm = str(self.parmtable.item(row,0).text());
        #print "plotting",parm
        if parm is None:
            return;
        if not self._funklist.has_key(parm):
            self._get_funklets(parm);
        #print "plotting",self._funklist[parm];
        
        funklet =  ComposedFunklet(self._funklist[parm]);
        print funklet.eval({'x0':.4,'x1':.2,'x2':3,'x5':4});
        dom = meq.domain(0,1,0,1);
        cells = meq.cells(dom,num_time=1,num_freq=25);

        #        print cells;
        funklet.plot(cells=cells,parent=self._wtop);
        

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
  # add ourselves to the MeqTimba menu
  _qa_table.addTo(menu['MeqTimba']);

