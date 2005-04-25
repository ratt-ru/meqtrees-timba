#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.Meq import meq
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.treebrowser import NodeAction
import Timba.GUI.app_proxy_gui
from Timba.GUI.meqserver_gui import makeNodeDataItem
from Timba import Grid


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
      if funklet:
          self._coeff=funklet.coeff;
      else:
          self._coeff=0;

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
#        self.reject();
        self.parent.rejectedit();
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
#        self.reject();
                
                
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
        if funklet:
            self._coeff=funklet.coeff;
        else:
            self._coeff=0;
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
  iconset= pixmaps.fiddle.iconset;
  def activate (self,node):
      Grid.Services.addDataItem(makeNodeDataItem(node,viewer=ParmFiddler));

  def is_enabled (self,node):
    # available in idle mode, or when stopped at a debugger. 
    # If debug_level is set, node must be idle (otherwise, we can't trust the
    # node control status to be up-to-date)
    return ( self.tb.is_stopped or not self.tb.is_running ) and \
           ( not self.tb.debug_level or node.is_idle() );


_request_type = dmi_type('MeqRequest',record);



class ParmFiddler (browsers.GriddedPlugin):
  viewer_name = "ParmFiddler";
  _icon = pixmaps.fiddle;

  def is_viewable (data):
    return isinstance(data,_request_type) or \
      isinstance(getattr(data,'request',None),_request_type);
  is_viewable = staticmethod(is_viewable);


  def __init__(self,gw,dataitem,cellspec={},**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    _dprint(1,"started with",dataitem.udi,dataitem.data);
    self._has_data = False;

    self.rid=0;
    self._wtop = QVBox(self.wparent());
#    self._wtop.setFrameShape(QFrame.Panel+QFrame.Sunken);
#    self._wtop.setMargin(10);

    udi_root = dataitem.udi;
    reqCtrlFrame = QHBox(self.wtop());
    # Create a list box
    self.lb = QListBox(reqCtrlFrame , "listBox" );
    

    #on double click:
    QObject.connect( self.lb, SIGNAL("selected(int)"), self.parmSelected )
    #    QObject.connect( self.lb, SIGNAL("selected(int)"), self.parmSetIndex )
    QObject.connect( self.lb, SIGNAL("clicked(QListBoxItem *)"), self.parmSetIndex )
    
    reqVFrame = QVBox(reqCtrlFrame);
    self.labelParm = QLabel("c00: 0", reqVFrame ,"labelParm");
    reqSlideFrame = QHBox(reqVFrame);

    reqButtonFrame = QHBox(reqVFrame);
        
    self.buttonOk = QPushButton(reqButtonFrame,"buttonOk")
#    self.buttonOk.setIconSet(pixmaps.check.iconset());
    self.buttonOk.setText('Funklet');

    self.buttonReset = QPushButton(reqButtonFrame,"buttonReset")
    self.buttonReset.setText('Zero');


    self.slider1 = QSlider (reqSlideFrame,"slider1");
    self.slider1.setMinValue ( -20 );
    self.slider1.setMaxValue ( 20 );
    self.slider2 = QSlider (reqSlideFrame,"slider2");
    self.slider2.setMinValue ( -99 );
    self.slider2.setMaxValue ( 99 );

    self.slider1.setTickInterval(5);
    self.slider2.setTickInterval(2);
    self.slider1.setTickmarks(QSlider.Both);
    self.slider2.setTickmarks(QSlider.Both);
    
    self.slider1.setTracking(True);
    self.slider2.setTracking(True);

    QObject.connect(self.slider1,SIGNAL("valueChanged(int)"),self.changeGrof);
    QObject.connect(self.slider2,SIGNAL("valueChanged(int)"),self.changeFine);
    QObject.connect(self.slider1,SIGNAL("sliderReleased()"),self.updateC00);
    QObject.connect(self.slider2,SIGNAL("sliderReleased()"),self.updateC00);
    


 
    QObject.connect(self.buttonOk,SIGNAL("clicked()"),self.getparms);
    QObject.connect(self.buttonReset,SIGNAL("clicked()"),self.resetfunklet);

    self._request = [];
    self._parmlist= [];
    self._currentparm=None;
    self._parmindex=-1;
    self.c00=0.0;
    # find parms
    #self.getparms();
    # set data
    # form a caption and set contents
    (name,ni) = meqds.parse_node_udi(dataitem.udi);
    caption = "Fiddle from <b>%s</b>" % (name or '#'+str(ni),);
    self._node = ni;
    # setup widgets
    self.set_widgets(self.wtop(),caption,icon=self.icon());

    if dataitem.data is not None:
        self.set_data(dataitem);


  def wtop(self):
      return self._wtop;


  def changeGrof(self,value):
      fine=self.slider2.value()/100.;
      sign = 1;
      if not value == 0:
          sign = abs(value)/value;

          
      self.c00=sign*(abs(value)+fine);
      self.changeCaption(self.c00);

  def changeFine(self,value):
      grof=self.slider1.value();
      self.c00=value/100.+grof;
      self.changeCaption(self.c00);
      

  def changeCaption(self,value):
      self.labelParm.setText("c00: " + str(value))



  def resetfunklet(self):
      if not self._currentparm:
          return;
      self._currentparm.resettozero();


  def updateC00(self):
      if not self._currentparm:
          return;
      self._currentparm.setc00(self.c00);
      
  def changeC00(self, value=0.00):

      sign=1;
      if not value == 0:
          sign = abs(value)/value;

      value=int(abs(value)*100+0.5);
      value=sign*value/100.;
      min=self.slider1.minValue();
      max=self.slider1.maxValue();

      if (value-min)<5 or (max-value)<5:
          self.slider1.setRange(value-20,value+20);
      self.changeCaption(value);
      
      self.c00 = value;
      grof=int(abs(value)+0.5);
      fine=(abs(value)-grof)*100;
      grof =sign*grof;
      self.slider1.setValue(grof)
      self.slider2.setValue(fine)


  def parmSetIndex(self,item=None):
      if item:
          self._parmindex = self.lb.currentItem();
      self.buttonOk.setEnabled(True);
      self.buttonReset.setEnabled(True);
      changenode=self._parmlist[self._parmindex];
      if self._currentparm:
          self._currentparm.reject();
#          del self._currentparm;
      self._currentparm = ParmChange(self,changenode);


  def parmSelected(self,index):
      self._parmindex = index;
      self.buttonOk.setEnabled(True);
      self.buttonReset.setEnabled(True);
      changenode=self._parmlist[self._parmindex];
      if self._currentparm:
          self._currentparm.reject();
#          del self._currentparm;
      self._currentparm = ParmChange(self,changenode);


      self.getparms();

      


  def getparms(self):
    if not self._parmlist:
        QMessageBox.warning(self.wtop(),
                            "Warning",
                            "No parameters found");
        return;
    
    if self._parmindex >= len(self._parmlist) or self._parmindex< 0 :
        QMessageBox.warning(self.wtop(),
                            "Warning",
                            "No parameter selected");
        return;




    changenode=self._parmlist[self._parmindex];
    if not self._currentparm:
        self._currentparm = ParmChange(self,changenode);
    if self._currentparm.edit_parm :
        self._currentparm.rejectedit();
    # create new editor
    self._currentparm._edit();
    self.changeC00(self._currentparm.getc00());
    

  def set_data (self,dataitem,**opts):
    if not self._has_data:
      self._has_data = True;
      state = dataitem.data;
      request = getattr(state,'request',None);
      if not request:
          QMessageBox.warning(self.wtop(),
                              "Warning",
                            "No request found in Node, Please specify request first via Reexecute");
          self.buttonOk.setEnabled(False);          
          self.buttonReset.setEnabled(False);
      else:
          #
          #      print self._node;
          self._request = request;
          self._parmlist= [];
          self.getnodelist(meqds.nodelist[self._node]);
          # fill listbox with MeqParm names
          self.lb.clear();
          if self._currentparm:
              self._currentparm.reject();
              self._currentparm=None;
          self._parmindex=-1;
          for parm in self._parmlist:
              self.lb.insertItem( parm.name )
          self.buttonOk.setEnabled(False);
          self.buttonReset.setEnabled(False);
        
          if not self._parmlist:
              QMessageBox.warning(self.wtop(),
                                  "Warning",
                                  "No parameters found");
              self.buttonOk.setEnabled(False);
              self.buttonReset.setEnabled(False);
        
      self.enable();
      self.flash_refresh();

    
  def _refresh (self):
    # clear the has_data flag, so that set_data above will accept new data
    _dprint(2,'refresh expected now');
    self._has_data = False;
        

  def getnodelist(self,node):
      if node.classname == 'MeqParm':
          self.checkparm(node);
          
      else:
          # loop over chilren          
          if node.children:
              for (key,ni) in node.children:
                  child = meqds.nodelist[ni];
           
                  self.getnodelist(child);
          

  def checkparm(self,node):
      for i in range(len(self._parmlist)):
          checknode=self._parmlist[i];
          if checknode.name==node.name:
              return False;
          if(checknode.name>node.name):
              # store in alphabetic order
              self._parmlist.insert(i,node);
              return True;

      self._parmlist.append(node);
          
      return True;


  def reexecute(self):
      if not self._request:
          return;
      _dprint(1,'accepted: ',self._request);
      self.rid+=1;
      reqid=hiid(self.rid,self.rid,self.rid,self.rid);
      self._request.request_id = reqid;
      cmd = record(nodeindex=self._node,request=self._request,get_state=True);
      mqs().meq('Node.Execute',cmd,wait=False);

  def cleanup (self):
      if self._currentparm:
          self._currentparm.reject();
          del self._currentparm;
      


class ParmChange:
  def __init__(self,parent,node):
      self._parent=parent;
      self._node=node;
      self._nodename=node.name;      
#      self._callback = curry(self._update_state);
#      self._node.subscribe_state(self._callback);
#      meqds.request_node_state(self._node);
      self.edit_parm=None;
      self._funklet=None;
      self._dorefresh();

  def _dorefresh (self):
    # request node state, and subscribe to it via the curried callback
    # the curry() is handy because it will automatically disconnect the
    # subscription when deleted
    self._callback = curry(self._update_state);
    self._node.subscribe_state(self._callback);
    meqds.request_node_state(self._node);
      
  def _update_state(self,node,state,event=None):
      try: funklet = state.funklet;
      except AttributeError: #pass
          #      QListViewItem(self.reqView.wlistview(),'','','(no funklet found in node)');
          
          #pop up
          #        self.buttonOk.setEnabled(False);
          #          print "no funklet found in node";
          QMessageBox.warning(None,
                              "Warning",
                              "No funklet found in Node");

      else:
          #print funklet;
          #      print self._node;
          #      self.buttonOk.setEnabled(True);
          self._funklet = state.funklet;
          self._parent.changeC00(self.getc00());
          if self.edit_parm:
              self.edit_parm.updateCoeff_fromparent();

  def _edit(self):
      if self.edit_parm:
          self.reject();
      self.edit_parm=editParm(self,self._parent.wtop());

  def getc00(self):
      if not self._funklet:
          return 0.;
      coeff = self._funklet.coeff;
      if is_scalar(coeff):
          return self._funklet.coeff;
      else:
          if is_scalar(coeff[0]):
              return self._funklet.coeff[0];
      return self._funklet.coeff[0][0];

  def setc00(self,value):
      if not self._funklet:
          return 0.;
      if is_scalar(self._funklet.coeff):
          self._funklet.coeff=value;
      else:
          if is_scalar(self._funklet.coeff[0]):
              self._funklet.coeff[0]=value;
          else:
              self._funklet.coeff[0][0]=value;
      self.updatechange();
      if self.edit_parm:
          self.edit_parm.updateCoeff_fromparent();



  def resettozero(self):
      if not self._funklet:
          return 0;
      if is_scalar(self._funklet.coeff):
          self._funklet.coeff=0;
      else:
          if is_scalar(self._funklet.coeff[0]):
              for i in range(len(self._funklet.coeff)):
                  self._funklet.coeff[i]=0;
          else:
              for i in range(len(self._funklet.coeff)):
                  for j in range(len(self._funklet.coeff[i])):
                                 self._funklet.coeff[i][j]=0;
      self.updatechange();
      if self.edit_parm:
          self.edit_parm.updateCoeff_fromparent();






  def updatechange (self):
      if not self._funklet:
          return;
      if not self._parent:
          self.reject();
      meqds.set_node_state(self._node,funklet=self._funklet);

      self._parent.changeC00(self.getc00());
      
      self._parent.reexecute();

  def rejectedit(self):
       if self.edit_parm:
          self.edit_parm.reject();
          self.edit_parm=None;
     

  def reject(self):
      self._node = self._callback = None; # this will disconnect the Qt signal
      self.rejectedit();

def define_treebrowser_actions (tb):
  _dprint(1,'defining parm fiddling treebrowser actions');
  tb.add_action(NA_ParmFiddler,30,where="node");

Grid.Services.registerViewer(meqds.NodeClass(),ParmFiddler,priority=25);
