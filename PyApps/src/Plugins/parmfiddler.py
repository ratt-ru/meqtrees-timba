#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
import Timba.GUI.browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.treebrowser import NodeAction


from qt import *
import weakref
from qttable import *



_dbg = verbosity(0,name='node_fiddle');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



class editParm(QDialog):
    def __init__(self, parent):
      self.parent = parent;
      self.parentname=parent._nodename;
      funklet=parent._funklet;
      self._coeff=funklet.coeff;
      #print self._coeff;
      if is_scalar(self._coeff):
          self._coeff=[[self._coeff]]
      if is_scalar(self._coeff[0]):
          self._coeff=[self._coeff];
          
      self._nx=len(self._coeff);
      self._ny=len(self._coeff[0]);
      #print "new:";
      #print self._coeff;
        
      QDialog.__init__(self, parent, 'TEST', 0, 0)
      self.setCaption('Funklet of '+self.parentname);
      self.v = QVBoxLayout(self, 10, 5)

      self.funkgrid=QTable(self);
      self.funkgrid.setCaption("funklet values")

      self.funkgrid.setNumRows(self._nx);
      self.funkgrid.setNumCols(self._ny);

      self.horh = self.funkgrid.horizontalHeader()
      self.verth = self.funkgrid.verticalHeader()
      
      self.updategrid();

      self.v.addWidget(self.funkgrid);

      self.Bh = QHBoxLayout(self.v, 5)
      
      self.cmdAddRow = QPushButton('Add Row', self)
      QObject.connect(self.cmdAddRow, SIGNAL('clicked()'), self.slotcmdAddRow)
      self.Bh.addWidget(self.cmdAddRow)
      self.cmdRemoveRow = QPushButton('Remove Row', self)
      QObject.connect(self.cmdRemoveRow, SIGNAL('clicked()'), self.slotcmdRemoveRow)
      self.Bh.addWidget(self.cmdRemoveRow)
      self.cmdAddCol = QPushButton('Add Column', self)
      QObject.connect(self.cmdAddCol, SIGNAL('clicked()'), self.slotcmdAddCol)
      self.Bh.addWidget(self.cmdAddCol)
      self.cmdRemoveCol = QPushButton('Remove Column', self)
      QObject.connect(self.cmdRemoveCol, SIGNAL('clicked()'), self.slotcmdRemoveCol)
      self.Bh.addWidget(self.cmdRemoveCol)
      self.Bh2 = QHBoxLayout(self.v, 5)
      
      self.cmdOK = QPushButton('Update', self)
      QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
      self.Bh2.addWidget(self.cmdOK)
      self.cmdCancel = QPushButton('Cancel', self)
      QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.slotcmdCancel)
      self.Bh2.addWidget(self.cmdCancel)

      QObject.connect(self.funkgrid,SIGNAL('valueChanged(int,int)'),self.updateCoeff);
      
      
      self.show()
      

    def slotcmdAddRow(self):
        array1=self._coeff;
        array2=numarray.resize(array1,(self._nx+1,self._ny));
#       something I have to do , since increasing size of a numarray does strange things with values
        for i in range(self._nx):
            for j in range(self._ny):
                array2[i,j]=self._coeff[i][j];
        self._coeff=array2;
        for i in range(self._ny):
            self._coeff[self._nx][i]=0.0;
        self._nx+=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();



    def slotcmdAddCol(self):
        array1=self._coeff;
        array2=numarray.resize(array1,(self._nx,self._ny+1));
        for i in range(self._nx):
            for j in range(self._ny):
                array2[i,j]=self._coeff[i][j];
        self._coeff=array2;
        for i in range(self._nx):
            self._coeff[i][self._ny]=0.0;
        self._ny+=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();

    def slotcmdRemoveRow(self):
        if self._nx<=1:
            return;
        array1=self._coeff;
        array2=numarray.resize(array1,(self._nx-1,self._ny));
        self._coeff=array2;
        self._nx-=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();
       
        

    def slotcmdRemoveCol(self):
        if self._ny<=1:
            return;
        array1=self._coeff;
        array2=numarray.resize(array1,(self._nx,self._ny-1));
        self._coeff=array2;
        self._ny-=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();

    def slotcmdCancel(self):
#        self.parent._dorefresh();
        self.close();

    def slotcmdOK(self):
#        print self.parent._funklet.coeff;
        array1=numarray.resize(self.parent._funklet.coeff,(self._nx,self._ny));
        self.parent._funklet.coeff=array1;
        for i in range(self._nx):
            for j in range(self._ny):
                
                self.parent._funklet.coeff[i][j] = float(str(self.funkgrid.text(i,j)));
#        print self.parent._funklet.coeff;
#       self.updategrid();
        self.parent.updatechange();
                
                
    def updategrid(self):
        maxc=1;
        for j in range(self._ny):
            self.horh.setLabel(j,"");
            for i in range(self._nx):
                if j==0 : self.verth.setLabel(i,""); 
                self.funkgrid.setText(i,j,str(self._coeff[i][j]));
                width= len(self.funkgrid.text(i,j));
                if width>maxc : maxc =width;
            self.funkgrid.setColumnWidth(j,maxc*15);
            maxc=1;
        self.horh.setLabel(0,"t");
        self.verth.setLabel(0,"f");
 
    def updateCoeff(self,row,col):
        self._coeff[row][col]= float(str(self.funkgrid.text(row,col)));

    def updateCoeff_fromparent(self):
        funklet=self.parent._funklet;
        self._coeff=funklet.coeff;
        self.updategrid();

class NA_ParmFiddler(NodeAction):
  text = "ParmFiddler";
  nodeclass = meqds.NodeClass('MeqParm');
  def activate (self):
    try: dialog = self.item.tb._node_parmfiddler_dialog;
    except AttributeError:
      self.item.tb._node_parmfiddler_dialog = dialog = ParmFiddlerDialog(self.item.tb.wtop());
    dialog.show(self.node);
  def is_enabled (self):
    # available in idle mode, or when stopped at a debugger. 
    # If debug_level is set, node must be idle (otherwise, we can't trust the
    # node control status to be up-to-date)
    return ( self.tb.is_stopped or not self.tb.is_running ) and \
           ( not self.tb.debug_level or self.node.is_idle() );


class ParmFiddlerDialog (QDialog):
  def __init__(self,parent = None,name = None,modal = 0,fl = 0):
    QDialog.__init__(self,parent,name,modal,fl)
    if not name:
        self.setName("ParmFiddlerDialog")
    ParmFiddlerDialogLayout = QVBoxLayout(self,11,6,"ParmFiddlerDialogLayout")
    self.edit=None;
    reqFrame = QVBox(self);
    reqFrame.setFrameShape(QFrame.Panel+QFrame.Sunken);
    reqFrame.setMargin(10);
    reqCtrlFrame = QHBox(reqFrame);
    self.reqRefresh = QToolButton(reqCtrlFrame);
    self.reqRefresh.setIconSet(pixmaps.refresh.iconset());
    self.reqRefresh.setAutoRaise(True);
    self.reqRefresh.setSizePolicy(QSizePolicy(0,0));  # fixed size
    QObject.connect(self.reqRefresh,SIGNAL("clicked()"),self._dorefresh);
    QToolTip.add(self.reqRefresh,"refresh funklet from node state");
    self.reqViewLabel = QLabel(" Funklet:",reqCtrlFrame);
    self.reqView = Timba.GUI.browsers.HierBrowser(reqFrame,"","");
    ParmFiddlerDialogLayout.addWidget(reqFrame);
 


    Layout1 = QHBoxLayout(None,0,6,"Layout1")
    Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
    Layout1.addItem(Horizontal_Spacing2)
    self.buttonOk = QPushButton(self,"buttonOk")
    Layout1.addWidget(self.buttonOk)

    self.buttonCancel = QPushButton(self,"buttonCancel")
    Layout1.addWidget(self.buttonCancel)
    ParmFiddlerDialogLayout.addLayout(Layout1)
    self.resize(QSize(511,482).expandedTo(self.minimumSizeHint()))
    self.clearWState(Qt.WState_Polished)
    self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
    self.connect(self.buttonOk,SIGNAL("clicked()"),self.change)
    self.buttonCancel.setIconSet(pixmaps.cancel.iconset());
    self.buttonOk.setIconSet(pixmaps.check.iconset());
    self.buttonOk.setText('Change');
    self.buttonCancel.setText('Cancel');


    


  def show (self,node):
    self.setCaption("Fiddle node: "+node.name);
    self.reqView.clear();
    self._node = weakref_proxy(node);
    self._funklet = None;
    self._nodename=node.name;
    self._dorefresh();
    QDialog.show(self);
    



  def _dorefresh (self):
    # request node state, and subscribe to it via the curried callback
    # the curry() is handy because it will automatically disconnect the
    # subscription when deleted
    self._callback = curry(self._update_state);
    self._node.subscribe_state(self._callback);
    meqds.request_node_state(self._node);


  def _update_state(self,node,state,event=None):
#    print "updating "
    try: funklet = state.funklet;
    except AttributeError: #pass
      self.reqView.wlistview().setRootIsDecorated(False);
      QListViewItem(self.reqView.wlistview(),'','','(no funklet found in node)');
      self.buttonOk.setEnabled(False);
    else:
#      print funklet;
#      print self._node;
      self.buttonOk.setEnabled(True);
      self._funklet = state.funklet;
      self.reqView.wlistview().setRootIsDecorated(True);
      self.reqView.set_content(self._funklet);
      #      self.reqView.set_open_items(self.defaultOpenItems);
      if self.edit:
          self.edit.updateCoeff_fromparent();
        



  def reject (self):
    self._node = self._funklet = self._callback = None; # this will disconnect the Qt signal
    self.killTimers();
    QDialog.hide(self);


  def change (self):
      if not self._funklet:
          return;
      self.edit=editParm(self);
      
  def updatechange (self):
      if not self._funklet:
          return;
      meqds.set_node_state(self._node,funklet=self._funklet);
      meqds.set_node_state(self._node,CacheResult=False);
      
      
def define_treebrowser_actions (tb):
  _dprint(1,'defining parm fiddling treebrowser actions');
  tb.add_action(NA_ParmFiddler,30,where="node");
