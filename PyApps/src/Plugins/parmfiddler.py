#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.Meq import meq
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
    def __init__(self, parent,grandparent):
      self.parent = parent;
      self.grandparent = grandparent;
      self.parentname=parent._nodename;
      funklet=self.parent._funklet;
      self._coeff=funklet.coeff;
      if is_scalar(self._coeff):
          self._coeff=[[self._coeff]]
      if is_scalar(self._coeff[0]):
          self._coeff=[self._coeff];
      self._nx=len(self._coeff);
      self._ny=len(self._coeff[0]);

      QDialog.__init__(self,grandparent,"Test",0,0);
      self.setCaption('Funklet of '+self.parentname);
      self.v = QVBoxLayout(self, 10, 5)

      self.funkgrid=QTable(self);
      self.funkgrid.setCaption("funklet values")

      self.horh = self.funkgrid.horizontalHeader()
      self.verth = self.funkgrid.verticalHeader()

#      self.updateCoeff_fromparent();

      
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
      
      self.cmdOK = QPushButton('Apply', self)
      QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
      self.Bh2.addWidget(self.cmdOK)
      self.cmdCancel = QPushButton('Cancel', self)
      QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.slotcmdCancel)
      self.Bh2.addWidget(self.cmdCancel)

      self.cmdCancel.setIconSet(pixmaps.cancel.iconset());
      self.cmdOK.setIconSet(pixmaps.check.iconset());

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
        self.reject();

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
        self.reject();
                
                
    def updategrid(self):
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
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
        if is_scalar(self._coeff):
            self._coeff=[[self._coeff]]
        if is_scalar(self._coeff[0]):
            self._coeff=[self._coeff];
        self._nx=len(self._coeff);
        self._ny=len(self._coeff[0]);
        self.updategrid();


class NA_ParmFiddler(NodeAction):
  text = "ParmFiddler";
  nodeclass = meqds.NodeClass('MeqNode');
  iconset= pixmaps.fiddler.iconset;
  def activate (self,node):
    try: dialog = self.item.tb._node_parmfiddler_dialog;
    except AttributeError:
      self.item.tb._node_parmfiddler_dialog = dialog = ParmFiddlerDialog(self.item.tb.wtop());
    dialog.show(node);
  def is_enabled (self,node):
    # available in idle mode, or when stopped at a debugger. 
    # If debug_level is set, node must be idle (otherwise, we can't trust the
    # node control status to be up-to-date)
    return ( self.tb.is_stopped or not self.tb.is_running ) and \
           ( not self.tb.debug_level or node.is_idle() );


class ParmFiddlerDialog (QDialog):

  def __init__(self,parent = None,name = None,modal = 0,fl = 0):
    QDialog.__init__(self,parent,name,modal,fl)
    if not name:
        self.setName("ParmFiddlerDialog")
    ParmFiddlerDialogLayout = QVBoxLayout(self,11,6,"ParmFiddlerDialogLayout")
    self.edit=None;
    self._node=None;
    self.rid=0;
    reqFrame = QVBox(self);
    reqFrame.setFrameShape(QFrame.Panel+QFrame.Sunken);
    reqFrame.setMargin(10);
    reqCtrlFrame = QHBox(reqFrame);
    # Create a list box
    self.lb = QListBox(reqCtrlFrame , "listBox" );

    #on double click:
    self.connect( self.lb, SIGNAL("selected(int)"), self.parmSelected )
    self.connect( self.lb, SIGNAL("clicked(QListBoxItem *)"), self.parmSetIndex )
    
    reqVFrame = QVBox(reqCtrlFrame);
#    self.dialParm = QDial(0, 255, 1, 0,reqVFrame );
#    self.labelParm = QLabel("c00: 0", reqVFrame );
#    QObject.connect(self.dialParm, SIGNAL("valueChanged(int)"),
#                    self.changeC00);
    
    self.buttonOk = QPushButton(reqVFrame,"buttonOk")
    self.buttonOk.setIconSet(pixmaps.check.iconset());
    self.buttonOk.setText('Funklet');

    ParmFiddlerDialogLayout.addWidget(reqFrame);

    Layout1 = QHBoxLayout(None,0,6,"Layout1")
    Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
    Layout1.addItem(Horizontal_Spacing2)

    self.buttonCancel = QPushButton(self,"buttonCancel")
    Layout1.addWidget(self.buttonCancel)
    ParmFiddlerDialogLayout.addLayout(Layout1)

    self.resize(QSize(511,482).expandedTo(self.minimumSizeHint()))

    self.clearWState(Qt.WState_Polished)

    self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
    self.buttonCancel.setIconSet(pixmaps.cancel.iconset());
    self.buttonCancel.setText('Cancel');


    self.connect(self.buttonOk,SIGNAL("clicked()"),self.getparms);

    self._request = [];
    self._parmlist= [];
    self._currentparm=None;
    self._parmindex=-1;
    self.c00=0;
    # find parms
    #self.getparms();

  def changeC00(self, value):
      self.labelParm.setText("c00: " + str(value))
      self.c00 = value


  def parmSetIndex(self,item=None):
      if item:
          self._parmindex = self.lb.currentItem();
      self.buttonOk.setEnabled(True);


  def parmSelected(self,index):
      self._parmindex = index;
      self.buttonOk.setEnabled(True);
      self.getparms();

      


  def getparms(self):
    if not self._parmlist:
        QMessageBox.warning(self,
                            "Warning",
                            "No parameters found");
        return;
    
    if self._parmindex >= len(self._parmlist) or self._parmindex< 0 :
        QMessageBox.warning(self,
                            "Warning",
                            "No parameter selected");
        return;



    if self._currentparm :
        self._currentparm.reject();

    changenode=self._parmlist[self._parmindex];
    self._currentparm = ParmChange(self,changenode);


  def show (self,node):
    self.setCaption("Fiddle from node: "+node.name);
    self._node = weakref_proxy(node);
    self._nodename=node.name;
    self._dorefresh();
    self._parmlist= [];
    self.getnodelist(self._node);
    #fill listbox with MeqParm names
    self.lb.clear();
    self._parmindex=-1;
    for parm in self._parmlist:
        self.lb.insertItem( parm.name )
    QDialog.show(self);
    if self._parmindex >= 0:
        self.buttonOk.setEnabled(True);
    else:
        self.buttonOk.setEnabled(False);
        
    if not self._parmlist:
        QMessageBox.warning(self,
                            "Warning",
                            "No parameters found");
        self.buttonOk.setEnabled(False);
        

    
  def _dorefresh (self):
    # request node state, and subscribe to it via the curried callback
    # the curry() is handy because it will automatically disconnect the
    # subscription when deleted
    self._callback = curry(self._update_state);
    self._node.subscribe_state(self._callback);
    meqds.request_node_state(self._node);


  def _update_state(self,node,state,event=None):
    try: request = state.request;
    except AttributeError: #pass
        #      QListViewItem(self.reqView.wlistview(),'','','(no funklet found in node)');

        #pop up
        QMessageBox.warning(self,
                            "Warning",
                            "No request found in Node",
                            "Please specify request first via Reexecute");
#        print "no request found in node";
#        self.buttonOk.setEnabled(False);
    else:
        #
        #      print self._node;
        self._request = state.request;
        

  def getnodelist(self,node):
      if node.classname == 'MeqParm':
          self.checkparm=0;
          self._parmlist.append(node);
          
      else:
          # loop over chilren          
          if node.children:
              for (key,ni) in node.children:
                  child = meqds.nodelist[ni];
           
                  self.getnodelist(child);
          


  def reject (self):
    self._node = self._request = self._callback = None; # this will disconnect the Qt signal
    self.killTimers();
    QDialog.reject(self);



  def reexecute(self):
      if not self._request:
          return;
      _dprint(1,'accepted: ',self._request);
      self.rid+=1;
      reqid=hiid(self.rid,self.rid,0,0);
      self._request.request_id = reqid;
      cmd = record(name=self._node.name,request=self._request,get_state=True);
      mqs().meq('Node.Execute',cmd,wait=False);

      


class ParmChange:
  def __init__(self,parent,node):
      self._parent=parent;
      self._node=node;
      self._nodename=node.name;      
      self._callback = curry(self._update_state);
      self._node.subscribe_state(self._callback);
      meqds.request_node_state(self._node);
      self.edit_parm=None;

  def _update_state(self,node,state,event=None):
      try: funklet = state.funklet;
      except AttributeError: #pass
          #      QListViewItem(self.reqView.wlistview(),'','','(no funklet found in node)');
          
          #pop up
          #        self.buttonOk.setEnabled(False);
          print "no funklet found in node";
      else:
          #print funklet;
          #      print self._node;
          #      self.buttonOk.setEnabled(True);
          self._funklet = state.funklet;
          if not self.edit_parm:
              self.edit_parm=editParm(self,self._parent);



  def updatechange (self):
      if not self._funklet:
          return;
      meqds.set_node_state(self._node,funklet=self._funklet);
      meqds.set_node_state(self._node,cacheresult=False);
      
      self._parent.reexecute();

  def reject(self):
      if self.edit_parm:
          self.edit_parm.reject();

def define_treebrowser_actions (tb):
  _dprint(1,'defining parm fiddling treebrowser actions');
  tb.add_action(NA_ParmFiddler,30,where="node");
