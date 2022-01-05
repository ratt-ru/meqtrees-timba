#!/usr/bin/env python3

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

solverstart =5;


parmfiddler_instructions = \
                         '''The Parmfiddler shows all the MeqParms as well as all solvers in the tree below the node it is started from.<br> 
                         The funklet/default_funklet/solvability/scales and offsets for the selected Parm(s) can be adjusted via the fiddler. The first coefficient of the funklet of the selected Parm(s) can be easily changed with the slider. The <b>Zero</b> button is a shortcut to reset all coefficients of the selected Parm(s) to 0. <br>To allow for  multiple selection use the <b>multi</b> checkbox, if checked all changes are applied to any selected (highlighted) Parm.  If the <b>reexecute</b> box is checked, the node from which the fiddler is started is reexecuted automatically after each change.<br> Use the right mouse button for extra options.'''





class NA_ParmFiddler(NodeAction):
  text = "ParmFiddler";
  nodeclass = meqds.NodeClass('MeqNode');
  iconset = pixmaps.fiddle.iconset;
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
    self.c00=0.;
    self._wtop = QHBox(self.wparent());
    self._parmlist= [];
    self._solverdict= {};
    self._parmdict= {};
    #all names off the nodes except parms
    self._nodedict= {};
    self._currentparm = None;
    self._request = None;
    self.swapsort=True;
    self.sorted=0; 
    # Initialize subscribe state
    self._callbackparm = curry(self._update_parmlist);
    self._callbacksolver = curry(self._update_solverlist);


    self.parmtable = QTable(self._wtop , "parmtable" );

    QWhatsThis.add(self._wtop,parmfiddler_instructions);



    self.parmtable.setShowGrid(False);
    self.parmtable.setFocusStyle(QTable.FollowStyle);
    self.parmtable.setSelectionMode (QTable.MultiRow );




    self._menu=QPopupMenu(self.parmtable);
    self._menu.insertItem(pixmaps.publish.iconset(),"Publish",self.publish_selected);
    self._menu.insertItem(pixmaps.table.iconset(),"Funklet",self.parmSelected);
    tooltip="invert publishing of all selected rows";
    QToolTip.add(self._menu,tooltip);
   
    tooltip="Double Click to get complete funklet, right mouse for more options";
    QToolTip.add(self.parmtable,tooltip);
    QObject.connect( self.parmtable, SIGNAL("selectionChanged()"), self.parmSetIndex )
    QObject.connect( self.parmtable, SIGNAL("doubleClicked(int, int, int, const QPoint &)"), self.parmSelected )
    QObject.connect( self.parmtable, SIGNAL("clicked(int, int, int, const QPoint &)"), self.parmClicked)
    QObject.connect( self.parmtable, SIGNAL("contextMenuRequested ( int, int, const QPoint &)"), self.rightMouse);
    self.sliderframe = QVBox(self.wtop());
#    self.c00frame = QHBox(self.sliderframe);

    self.labelParm = QLabel("no parm selected", self.sliderframe ,"labelParm");
    self.c00Text = QLabel(self.sliderframe ,"c00text");
    tooltip="Selected Parm";
    QToolTip.add(self.labelParm,tooltip);
    alignment = Qt.AlignLeft|Qt.SingleLine;
    self.c00Text.setAlignment(alignment);
    self.labelParm.setAlignment(alignment);
    style = QFrame.StyledPanel|QFrame.Sunken;
    self.c00Text.setFrameStyle(style);
    
  
    self.slider1 = QSlider (self.sliderframe,"slider1");
    tooltip="Adjust c00 of selected Parm and reexecute";
    QToolTip.add(self.slider1,tooltip);
    self.slider1.setMinValue ( -50 );
    self.slider1.setMaxValue ( 50 );

    self.slider1.setTickInterval(5);
    self.slider1.setTickmarks(QSlider.Both);
    
    self.slider1.setTracking(True);
    self.slider1.setEnabled(False);
    
    QObject.connect(self.slider1,SIGNAL("valueChanged(int)"),self.changeC00Text);
    QObject.connect(self.slider1,SIGNAL("sliderReleased()"),self.updateC00);

    self.spinframe = QHBox(self.sliderframe);
    self.labelSpin =  QLabel("stepsize:", self.spinframe ,"labelSpin");
    self.stepsizeList = QComboBox(False, self.spinframe ,"stepsizeList");
    tooltip="Adjust stepsize of slider";
    QToolTip.add(self.stepsizeList,tooltip);
    QObject.connect(self.stepsizeList,SIGNAL("activated(int)"),self.changeStepsize);
    self.fillstepsizelist();
    self.stepsize=1.;


    self.enable_exec = QCheckBox("reexecute",self.sliderframe, "enable_exec");
    tooltip="If checked, node is executed after change";
    QToolTip.add(self.enable_exec,tooltip);
    self.enable_exec.setEnabled(False);


    self.enable_multi = QCheckBox("multi",self.sliderframe, "multi");
    tooltip="If checked, multiple parms can be adjusted at the same time";
    QToolTip.add(self.enable_multi,tooltip);
    self.enable_multi.setEnabled(True);
    self.enable_multi.setChecked(True);
    QObject.connect(self.enable_multi,SIGNAL("clicked()"),self.toggle_multi);
    
    
    self.ButtonFrame = QHBox(self.sliderframe);
        
    self.buttonOk = QPushButton(self.ButtonFrame,"buttonOk")
    self.buttonOk.setText('Execute');
    tooltip="executes node";
    QToolTip.add(self.buttonOk,tooltip);

    self.buttonReset = QPushButton(self.ButtonFrame,"buttonReset")
    self.buttonReset.setText('Zero');
    tooltip="sets all coefficients of selected Parm to 0";
    QToolTip.add(self.buttonReset,tooltip);
    self.buttonOk.setEnabled(False);
    self.buttonReset.setEnabled(False);
    QObject.connect(self.buttonOk,SIGNAL("clicked()"),self.do_reexecute);
    QObject.connect(self.buttonReset,SIGNAL("clicked()"),self.resetfunklet);

    # form a caption and set contents
    (name,ni) = meqds.parse_node_udi(dataitem.udi);
    caption = "Fiddle from <b>%s</b>" % (name or '#'+str(ni),);
    self._node = ni;
    self._name = name;
    # setup widgets
    self.set_widgets(self.wtop(),caption,icon=self.icon());

    if dataitem.data is not None:
        self.set_data(dataitem);


   

    
    

  def wtop(self):
      return self._wtop;


  def toggle_multi(self):
    if self.enable_multi.state():
      self.parmtable.setSelectionMode (QTable.MultiRow );
    else:
      self.parmtable.setSelectionMode (QTable.SingleRow );
      

  def fillstepsizelist(self):
      for i in range(-10,11):
        if  abs(i) <4:
          stepsize = pow(10.,i);
          self.stepsizeList.insertItem(str(stepsize));
        else:
          sign = "+";
          if i<0:
            sign = "-";
          
          stpstring = "1e"+sign+str(abs(i));
          self.stepsizeList.insertItem(stpstring);
         
      self.stepsizeList.setCurrentItem(10);
      self.stepsize=1;
      
  def changeStepsize(self,stepnr=10):
    self.stepsize= pow(10.,stepnr-10);


  def set_data (self,dataitem,**opts):
      request = getattr(dataitem.data,'request',None);
      if self._request and request:
        self._request  =  request;
      
      
      if not self._has_data:
        self._has_data = True;
        state = dataitem.data;
        if not request:
            QMessageBox.warning(self.wtop(),
                                "Warning",
                              "No request found in Node, Please specify request first via Reexecute");
            self.enable_exec.setOn(False);
            self.enable_exec.setEnabled (False);
            self.buttonOk.setEnabled(False);          
        else:
            #
            #     #print self._node;
            self.enable_exec.setOn(True);
            self.enable_exec.setEnabled (True);
            self.buttonOk.setEnabled(True);          
            self._request = request;

        self.unsubscribe_all();
        #parmlist is sorted by name.
        self._parmlist= [];
        self._solverdict= {};
        self._parmdict= {};
        #all names off the nodes except parms
        self._nodedict= {};


        # recursively get all parms and solvers behind this node
        if self._node:
          self.getnodelist(meqds.nodelist[self._node]);
        else:
          self.getnodelist(meqds.nodelist[self._name]);          
        #subscribe to solvers
        for solverkey in list(self._solverdict.keys()):
          solver = self._solverdict[solverkey]['node'];
          # subscribe
          solver.subscribe_state(self._callbacksolver);
          meqds.request_node_state(solver);

        # fill listbox with MeqParm names
        self.parmtable.setNumCols(len(list(self._solverdict.keys()))+solverstart);
        self.parmtable.setNumRows(len(self._parmlist));
        self.parmtable.setReadOnly(True);
        self.parmtable.horizontalHeader () .setLabel(0,"name");
        self.parmtable.horizontalHeader () .setLabel(1,"c00");
        self.parmtable.horizontalHeader () .setLabel(2,"shape");
        self.parmtable.horizontalHeader () .setLabel(3,pixmaps.publish.iconset(),"");
        self.parmtable.horizontalHeader () .setLabel(4,"0");
        self.parmtable.setColumnWidth(0,100);
        self.parmtable.setColumnWidth(1,200);
        self.parmtable.setColumnWidth(2,60);
        self.parmtable.setColumnWidth(3,25);
        self.parmtable.setColumnWidth(4,25);
#        self.parmtable.horizontalHeader () .setLabel(3,"i");
        tooltip="click to sort";
        QToolTip.add(self.parmtable.horizontalHeader (),tooltip);
        QObject.connect( self.parmtable.horizontalHeader (),SIGNAL("released(int)"),self.sortColumn);
        if self._currentparm:
            self._currentparm.reject();
            self._currentparm=None;
        self._parmindex=-1;

        self.updateTable();
        for parmkey in self._parmlist:
          parm =self._parmdict[parmkey]['node'];
          parm.subscribe_state(self._callbackparm);
          meqds.request_node_state(parm);


        self.buttonReset.setEnabled(False);

        if not self._parmlist:
            QMessageBox.warning(self.wtop(),
                                "Warning",
                                "No parameters found");
            self.buttonReset.setEnabled(False);

        self.enable();
        self.flash_refresh();





  def getnodelist(self,node):
      if node.classname == 'MeqParm':
          self.checkparm(node);
      else:
          # check if we have been at this node before
          if not self.checknodenew(node):
              # improves speed
              return;
          if node.classname == 'MeqSolver':
              self._solverdict[node.name]={'group':'','node':node,'parms':{},'col':-1};

              
          if node.children:
              for (key,ni) in node.children:
                  child = meqds.nodelist[ni];
           
                  self.getnodelist(child);
                  
          
  def checknodenew(self,node):
      if node.name in self._nodedict:
          return False;
      
      self._nodedict[node.name] = 1; 
      return True;   


      

  def checkparm(self,node):
    for i in range(len(self._parmlist)):
      checknode=self._parmlist[i];
      if checknode==node.name:
        return False;
      if(checknode>node.name):
        # store in alphabetic order
        self._parmlist.insert(i,node.name);
        self._parmdict[node.name] = {'node' : node, 'name': node.name,'solvers':{},'c00':0.,'shape':'','publish':0,'groups':[],'zero':0,'row':-1,'funklet':{},'class':'MeqPolc','defaultclass':'MeqPolc'};
        return True;

    self._parmlist.append(node.name);
  
    self._parmdict[node.name] = {'node':node, 'name': node.name,'solvers':{},'c00':0.,'shape':'','publish':0,'groups':[],'zero':0,'row':-1,'funklet':{},'class':'MeqPolc','defaultclass':'MeqPolc'};
      
          
    return True;



  def updateTable(self): 
      #print "got updateTable ",self._parmdict;
      solvernamelist = list(self._solverdict.keys());
      if solvernamelist:
          n=solverstart;
          for solvernm in solvernamelist:
              self.parmtable.horizontalHeader () .setLabel(n,solvernm);              
              self._solverdict[solvernm]['col']=n;
 #             self.parmtable.setColumnReadOnly(n,True);
              n+=1;
      #QObject.connect(self.parmtable.horizontalHeader (),SIGNAL("clicked(int)"),self.sortbycol)
      parmnr=0;
      for parmkey in self._parmlist:
          
          parm =self._parmdict[parmkey]['node'];
          solvers = self._parmdict[parmkey]['solvers'];
          c00 =  self._parmdict[parmkey]['c00'];
          shape =  self._parmdict[parmkey]['shape'];
          publish =  self._parmdict[parmkey]['publish'];
          zero =  self._parmdict[parmkey]['zero'];
          funkletclass = self._parmdict[parmkey]['class'];
          self.parmtable.setText( parmnr,0,parm.name );
          self.parmtable.setText( parmnr,1,str(c00) );
          self.parmtable.setText( parmnr,2,shape );
          if publish:
            self.parmtable.setPixmap(parmnr,3,pixmaps.publish.pm());
          else:
            self.parmtable.clearCell(parmnr,3);
          if zero:
            self.parmtable.setPixmap(parmnr,4,pixmaps.check.pm());
          else:
            self.parmtable.clearCell(parmnr,4);
          self._parmdict[parmkey]['row']=parmnr;
              
          parmnr+=1;

      self.putcheckboxes();


  def sortColumn(self,col):
    swapsort =True;
    if self.sorted==col:
      swapsort = not self.swapsort;
    
    self.parmtable.sortColumn ( col,swapsort,True);
    self.sorted=col;
    self.swapsort = swapsort;
    #update indices
    for i in range(self.parmtable.numRows()):
      parmkey = str(self.parmtable.text(i,0));
      self._parmdict[parmkey]['row']=i;

    # update selected parm
    self._parmindex=-1;
    self.parmSetIndex();
  
    


  def updateRow(self,row):
    parmkey = str(self.parmtable.text(row,0));
    c00=self._parmdict[parmkey]['c00'];
    shape =  self._parmdict[parmkey]['shape'];
    solvers = self._parmdict[parmkey]['solvers'];
    publish =  self._parmdict[parmkey]['publish'];
    zero =  self._parmdict[parmkey]['zero'];
    funkletclass = self._parmdict[parmkey]['class'];
    
#    print "updating parm ",self._parmdict[parmkey];
    self.parmtable.setText( row,1,str(c00) );
    self.parmtable.setText( row,2,shape );
    if publish:
      self.parmtable.setPixmap(row,3,pixmaps.publish.pm());
    else:
      self.parmtable.clearCell(row,3);
    if zero:
      self.parmtable.setPixmap(row,4,pixmaps.check.pm());
    else:
      self.parmtable.clearCell(row,4);
 
    for solver in list(self._solverdict.keys()):
      col = self._solverdict[solver]['col'];
      checkbutton = self.parmtable.item(row,col);
      if not checkbutton:
        return;
      if solver in solvers:
        if solvers[solver]:
          checkbutton.setChecked(True);
     

  def putcheckboxes(self):
     for solver in list(self._solverdict.keys()):
         col = self._solverdict[solver]['col'];
         if 'parms' in self._solverdict[solver]:
             for parm in list(self._solverdict[solver]['parms'].keys()):
                 row =  self._parmdict[parm]['row'];
                 solvers = self._parmdict[parm]['solvers'];
                 checkbutton = QCheckTableItem(self.parmtable, "");
                 checkbutton.setChecked(False);
                 if solver in solvers:
                     if solvers[solver]:
                         checkbutton.setChecked(True);
                 self.parmtable.setItem(row,col,checkbutton);
               


  def _update_parmlist(self,node,state,event=None):
      nodegroups=[];
      try: nodegroups=state.node_groups;
      except AttributeError: pass;
      funklet=None;
      try: funklet=state.funklet;
      except AttributeError: pass;
      default_funklet=None;
      try: default_funklet=state.default_funklet;
      except AttributeError: pass;
      coeff=[[0]];
      funkletclass = 'MeqPolc';
      if funklet:
          coeff=funklet.coeff;
          if hasattr(funklet,'class'):
            funkletclass = getattr(funklet,'class');
      defaultfunkclass = 'MeqPolc';
      if default_funklet:
        if hasattr(default_funklet,'class'):
          defaultfunkclass = getattr(default_funklet,'class');
      if is_scalar(coeff):
          coeff=[[coeff]];
      if is_scalar(coeff[0]):
        ncoeff=[];
        for i in range(len(coeff)):
          ncoeff.append([coeff[i]]);
        coeff=ncoeff;
      zero=1;
      shapex= len(coeff);
      shapey=len(coeff[0]);
      for i in range(shapex):
        for j in range(i==0,shapey): #funny way to exclude 0,0
          
          if not coeff[i][j]==0:
            zero=0;
            break;
        if not zero:
          break
      shapestr="["+str(shapex)+","+str(shapey)+"]";
      self._parmdict[node.name]['funklet']=funklet;
      self._parmdict[node.name]['c00']=coeff[0][0];
      self._parmdict[node.name]['shape']=shapestr;
      self._parmdict[node.name]['publish']=node.is_publishing();
      self._parmdict[node.name]['zero']=zero;
      self._parmdict[node.name]['class']=funkletclass;
      self._parmdict[node.name]['defaultclass']=defaultfunkclass;
      nodegroups=make_hiid_list(nodegroups);
      self._update_subscribedsolvers(node,nodegroups);

  def _update_subscribedsolvers(self,node, nodegroups):
      solvers={};
      for solver in list(self._solverdict.keys()):
          solvers[solver]=0;
          if node.name in self._solverdict[solver]['parms']: #if parm in list of solvable parms, 
              for group in nodegroups:
                  if group==self._solverdict[solver]['group']:
                      solvers[solver]=1;
      self._parmdict[node.name]['solvers']=solvers;
      self._parmdict[node.name]['groups']=nodegroups;

      row = self._parmdict[node.name]['row'];
      self.updateRow(row);      


  def _update_solverlist(self,node,state,event=None):

      names={};
      for i in state.solvable['command_by_list']:
          if 'state' in i and i['state']['solvable']  and 'name' in i:
              nameslist=i['name'];
      if isinstance(nameslist,str):
          names[nameslist]=1;
      else:
          for name in nameslist:
              names[name]=1;
      
      try: nodegroups=state.parm_group;
      except AttributeError: return;
      # get solver from dictionary
      if self._solverdict[node.name]['group'] == nodegroups:
          return;
      else:
         self._solverdict[node.name]['group']=  nodegroups;
         self._solverdict[node.name]['parms']=  names;
         for parm in list(self._parmdict.keys()):
             parmnode=self._parmdict[parm]['node'];
             # update parmtable if needed
             meqds.request_node_state(parmnode);
      self.putcheckboxes();

  def changeC00Text(self, value):
    change=self.c00 + value*self.stepsize;
    self.c00Text.setText(str(change));


  def changeC00(self, value=0.00):
    self.c00=value;
    if(self.slider1.value()==0):
      self.changeC00Text(0);
    self.slider1.setValue(0);
    
  def updateC00(self):
    ok = True;
    change = self.c00Text.text().toDouble()[0];
    self.changeC00(change);

     

    if self.enable_multi.state():
      #change all selected
      for parmkey in self._parmlist:
        #      if not self._parmdict[parmkey]['publish']:
        if self.parmtable.isRowSelected(self._parmdict[parmkey]['row']):
          #set c00
          funklet = self._parmdict[parmkey]['funklet'];
          coeff=array([[0.]]);
          if funklet:
            coeff=funklet.coeff;
          if is_scalar(coeff):
            coeff=array([[self.c00]]);
            #            coeff=[[coeff]];
          else:
            if is_scalar(coeff[0]):
              #            ncoeff=[];
              #            for i in range(len(coeff)):
              #              ncoeff.append([coeff[i]]);
              #            coeff=ncoeff;
              coeff[0]=self.c00;
            else:
              if is_scalar(coeff[0][0]):
                coeff[0][0]=self.c00;

          funklet.coeff=coeff;
          self._parmdict[parmkey]['funklet']=funklet;

          meqds.set_node_state(parmkey,funklet=funklet);
      self.reexecute();
    else:
      if not self._currentparm:
        return;
      self._currentparm.setc00(self.c00);
      
 
    


  def resetfunklet(self):
      if self.enable_multi.state():
        #change all selected
        for parmkey in self._parmlist:
          #      if not self._parmdict[parmkey]['publish']:
          if self.parmtable.isRowSelected(self._parmdict[parmkey]['row']):
            #set to 0
            funklet = self._parmdict[parmkey]['funklet'];
            coeff=array([[0.]]);
            if funklet:
              coeff=funklet.coeff;
            if is_scalar(coeff):
              coeff=array([[0.]]);
            else:
              if is_scalar(coeff[0]):
                for i in range(len(coeff)):
                  coeff[i]=0.;
              else:
                for i in range(len(coeff)):
                  for j in  range(len(coeff[0])):

                    coeff[i][j]=0.;
            funklet.coeff=coeff;
            self._parmdict[parmkey]['funklet']=funklet;
#            print "setting funklet ",funklet;
            meqds.set_node_state(parmkey,funklet=funklet);
        self.reexecute();

      else:
        if not self._currentparm:
          return;
        self._currentparm.resettozero();



  def parmSetIndex(self ):
      row = self.parmtable.currentRow();
      col = self.parmtable.currentColumn();
     # if col >=solverstart:
      #   return;


      if row>=0 and row <len(self._parmlist) and not row == self._parmindex :
          self._parmindex = row;
      else:
          #nothing
          return;

      self.buttonOk.setEnabled(True);
      self.buttonReset.setEnabled(True);
      self.slider1.setEnabled(True);
      changenodekey=str(self.parmtable.text(row,0));
      changenode=self._parmdict[changenodekey]['node'];
      if self._currentparm:
          self._currentparm.reject();
      #          del self._currentparm;
      self._currentparm = ParmChange(self,changenode);

      label="c00 of "+changenodekey;
      self.labelParm.setText(label);

      
  def parmSelected(self,row=0,col=0,button=0,mousePos=0):
    if col>=solverstart :
      #nothing
      return;

    row = self.parmtable.currentRow();
    if row>=0 and row <len(self._parmlist):
      self._parmindex = row;
    else:
      #nothing
      return;
    self.buttonOk.setEnabled(True);
    self.buttonReset.setEnabled(True);
    self.slider1.setEnabled(True);
    changenodekey=str(self.parmtable.text(row,0));
    changenode=self._parmdict[changenodekey]['node'];
    if self._currentparm:
      self._currentparm.reject();
    #          del self._currentparm;
    self._currentparm = ParmChange(self,changenode);


    self.getparms();


      
  def parmClicked(self,row,col,button,mousePos):
  
    if button == Qt.LeftButton:
      self.leftMouse(row,col);
    if button == Qt.RightButton:
      self.rightMouse(row,col,mousePos);
    if button == Qt.MidButton:
      self.rightMouse(row,col,mousePos);
      

    
  def leftMouse(self,row,col):
    #check if solvable paramters are updated
    if row<0 or row >len(self._parmlist) or col > len(list(self._solverdict.keys()))+solverstart:
      #nothing
      return;
    if col <solverstart :
      if not row == self._parmindex:
        self.parmSetIndex();
      #nothing
      return;
    checkbutton = self.parmtable.item(row,col);
    if not checkbutton:
        return;
    parmkey = str(self.parmtable.text(row,0));
    parm=self._parmdict[parmkey]['node'];    
    solver = str(self.parmtable.horizontalHeader().label(col));
    solvers = self._parmdict[parmkey]['solvers'];
    if checkbutton.isChecked():
      checkbutton.setChecked(False);
    else:
      checkbutton.setChecked(True);
      
    updateneeded = False;
    if solver in solvers:
        if solvers[solver]  and not checkbutton.isChecked():
          solvers[solver]=0;
          self._parmdict[parmkey]['solvers']=solvers;
          updateneeded=True;
        if not solvers[solver]  and checkbutton.isChecked():
          solvers[solver]=1;
          self._parmdict[parmkey]['solvers']=solvers;
          updateneeded=True;
        
          
    if updateneeded:
      nodegroups=[];
      for solver in list(self._solverdict.keys()):
        group = self._solverdict[solver]['group'];
        if solver in solvers:
          if solvers[solver]:
            nodegroups.append(group);
      dmigroups=make_hiid_list(nodegroups);
      if nodegroups:
        meqds.set_node_state(parm,node_groups=dmigroups);
      else:
        meqds.set_node_state(parm,node_groups=hiid(0));
        meqds.set_node_state(parm,solvable=False);
      
  def rightMouse(self,row,col,mousePos):
    self._menu.popup(mousePos);
       
  def publish_selected(self):
    #get selected rows
    for parmkey in self._parmlist:
#      if not self._parmdict[parmkey]['publish']:
        if self.parmtable.isRowSelected(self._parmdict[parmkey]['row']):
          meqds.enable_node_publish(parmkey,enable=not self._parmdict[parmkey]['publish']);


     
  
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




    changenodekey=str(self.parmtable.text(self._parmindex,0));
    changenode=self._parmdict[changenodekey]['node'];
    if not self._currentparm:
      self._currentparm = ParmChange(self,changenode);
    if self._currentparm.edit_parm :
      self._currentparm.rejectedit();
    # create new editor
    self._currentparm._edit();



  def update_default_selected(self,funklet):
    newfunkclass = 'MeqPolc';
    if hasattr(funklet,'class'):
      newfunkclass=getattr(funklet,'class');
    for parmkey in self._parmlist:
      if self.parmtable.isRowSelected(self._parmdict[parmkey]['row']):
        funkletclass = self._parmdict[parmkey]['defaultclass'];
        if not newfunkclass==funkletclass:
          # cannot change class
          continue;
#        print "setting def_funklet ",funklet;
        meqds.set_node_state(parmkey,default_funklet=funklet);    


  def update_selected(self,funklet):
    newfunkclass = 'MeqPolc';
    if hasattr(funklet,'class'):
      newfunkclass=getattr(funklet,'class');
    for parmkey in self._parmlist:
      if self.parmtable.isRowSelected(self._parmdict[parmkey]['row']):
        funkletclass = self._parmdict[parmkey]['class'];
        if not newfunkclass==funkletclass:
          # cannot change class
          continue;
        self._parmdict[parmkey]['funklet']=funklet;
#        print "setting funklet ",funklet;
        meqds.set_node_state(parmkey,funklet=funklet);
 



  def _refresh (self):
    # clear the has_data flag, so that set_data above will accept new data
    _dprint(2,'refresh expected now');
    self._has_data = False;

  def do_reexecute(self):
      self.reexecute(True);

  def reexecute(self,do_execute = False):

    if not self.enable_exec.state () and not do_execute: #reexecute not enabled
      #print "auto execute not eneabled"
      return;
    
    if not self._request:
      _dprint(2,'no request to execute');
      return;
    #check solver status:
    #      self.updateTable();
    _dprint(1,'accepted: ',self._request);
    reqid_old= self._request.request_id;
    if not reqid_old:
      reqid_old=  hiid(1,1,1,1);

    rid0=int(reqid_old[0]);
    rid1=int(reqid_old[1])+1;
    rid2=int(reqid_old[2])+1;
    reqid=hiid(rid0,rid1,rid2,0);


    self._request.request_id = reqid;
    #self._request.cache_override = True;
    if self._node:
      cmd = record(nodeindex=self._node,request=self._request,get_state=True);
    elif self._name:
      cmd = record(name=self._name,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);



  def unsubscribe_all(self):
      for parmkey in list(self._parmdict.keys()):
          parm =  self._parmdict[parmkey]['node'];
          #print "unsubscribe node ", parm.name;
          parm.unsubscribe_state(self._callbackparm);
      #print "unsubscribing solvers", self._solverdict;
      for solverkey in list(self._solverdict.keys()):
          solver = self._solverdict[solverkey]['node'];
          #print "unsubscribe solver ", solver.name;
          solver.unsubscribe_state(self._callbacksolver);

  def cleanup (self):
      browsers.GriddedPlugin.cleanup(self);
      
      #unsubscribe
      
      self.unsubscribe_all();

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
          self._funklet.coeff=array([[0.]]);
      else:
          if is_scalar(self._funklet.coeff[0]):
              for i in range(len(self._funklet.coeff)):
                  self._funklet.coeff[i]=0.;
          else:
              for i in range(len(self._funklet.coeff)):
                  for j in range(len(self._funklet.coeff[i])):
                                 self._funklet.coeff[i][j]=0.;
      self.updatechange();
      if self.edit_parm:
          self.edit_parm.updateCoeff_fromparent();




  def setDefault(self):
      if not self._funklet:
         return;
      if not self._parent:
          self.reject();
      self._parent.update_default_selected(self._funklet);

#      meqds.set_node_state(self._node,default_funklet=self._funklet);


  def updatechange (self):
      if not self._funklet:
         return;
      if not self._parent:
          self.reject();


      self._parent.update_selected(self._funklet);

      self._parent.changeC00(self.getc00());
      
      self._parent.reexecute();

  def rejectedit(self):
       if self.edit_parm:
          self.edit_parm.reject();
          self.edit_parm=None;
     

  def reject(self):
      self._node = self._callback = None; # this will disconnect the Qt signal
      self.rejectedit();


class editParm(QDialog):
    def __init__(self, parent,grandparent):
      self.parent = parent;
      self.grandparent = grandparent;
      self.parentname=parent._nodename;
      funklet=self.parent._funklet;
      if funklet:
          self._coeff=funklet.coeff;
      else:
          self._coeff=[[0.]];

      if is_scalar(self._coeff):
          self._coeff=[[self._coeff]]
      if is_scalar(self._coeff[0]):
        ncoeff=[];
        for i in range(len(coeff)):
          ncoeff.append([coeff[i]]);
        coeff=ncoeff;
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
      self.Bh0 = QHBoxLayout(self.v, 5)
      self.offsLabel = QLabel("Offset (t,f)",self);
      self.Bh0.addWidget(self.offsLabel);
      self.offsF = QLineEdit(self);
#      QObject.connect(self.offsF, SIGNAL(' textChanged(QString)'), self.slotcmdUpdateOffs)
      self.Bh0.addWidget(self.offsF);
      self.offsT = QLineEdit(self);
#      QObject.connect(self.offsT, SIGNAL(' textChanged(QString)'), self.slotcmdUpdateOffs)
      self.Bh0.addWidget(self.offsT);

      self.Bh1 = QHBoxLayout(self.v, 5)
      self.scaleLabel = QLabel("Scale (t,f)",self);
      self.Bh1.addWidget(self.scaleLabel);
      self.scaleF = QLineEdit(self);
      self.Bh1.addWidget(self.scaleF);
      self.scaleT = QLineEdit(self);
      self.Bh1.addWidget(self.scaleT);

      self._offset=array([0.,0.]);
      self._scale=array([1.,1.]);

      self.Bh2 = QHBoxLayout(self.v, 5)
      
      self.cmdOK = QPushButton('Apply', self)
      QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)

      self.cmdOK.setFocus();
      
      self.Bh2.addWidget(self.cmdOK)
      self.cmdCancel = QPushButton('Cancel', self)
      QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.slotcmdCancel)
      self.Bh2.addWidget(self.cmdCancel);
      self.cmdDefault = QPushButton('Set as Default', self)
      QObject.connect(self.cmdDefault, SIGNAL('clicked()'), self.slotcmdDefault)
      self.Bh2.addWidget(self.cmdDefault)

      self.cmdCancel.setIconSet(pixmaps.cancel.iconset());
      self.cmdOK.setIconSet(pixmaps.check.iconset());

      QObject.connect(self.funkgrid,SIGNAL('valueChanged(int,int)'),self.updateCoeff);
      
      self.updategrid();

            
      
      self.show()
      
    def UpdateOffs(self):
#      print "updating offset ",float(str(self.offsF.text()));
      self._offset[0]=float(str(self.offsF.text()));
      self._offset[1]=float(str(self.offsT.text()));
 
    def UpdateScale(self):
#      print "updating scale ",self._scale;
      self._scale[0]=float(str(self.scaleF.text()));
      self._scale[1]=float(str(self.scaleT.text()));
      
    def slotcmdAddRow(self):
        array1=self._coeff;
        array2=Timba.array.resize(array1,(self._nx+1,self._ny));
#       something I have to do , since increasing size of a Timba.array does strange things with values
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
        array2=Timba.array.resize(array1,(self._nx,self._ny+1));
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
        array2=Timba.array.resize(array1,(self._nx-1,self._ny));
        self._coeff=array2;
        self._nx-=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();
       
        

    def slotcmdRemoveCol(self):
        if self._ny<=1:
            return;
        array1=self._coeff;
        array2=Timba.array.resize(array1,(self._nx,self._ny-1));
        self._coeff=array2;
        self._ny-=1;
        self.funkgrid.setNumRows(self._nx);
        self.funkgrid.setNumCols(self._ny);
        self.updategrid();

    def slotcmdCancel(self):
#        self.parent._dorefresh();
#        self.reject();
        self.parent.rejectedit();


    def slotcmdDefault(self):
      self.slotcmdOK(1);

    def slotcmdOK(self, set_default=0):
#       #print self.parent._funklet.coeff;
        array1=Timba.array.resize(self.parent._funklet.coeff,(self._nx,self._ny));
        self.parent._funklet.coeff=array1;
        for i in range(self._nx):
            for j in range(self._ny):
                
                self.parent._funklet.coeff[i][j] = float(str(self.funkgrid.text(i,j)));

        self.UpdateOffs();
        self.UpdateScale();

        offset=self._offset;
        scale = self._scale;

        self.parent._funklet.offset=offset;
        self.parent._funklet.scale=scale;
        if set_default:
          self.parent.setDefault();
        
#       #print self.parent._funklet.coeff;
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
        self.horh.setLabel(0,"f");
        self.verth.setLabel(0,"t");
        self.offsF.setText(str(self._offset[0]));
        self.offsT.setText(str(self._offset[1]));
        self.scaleF.setText(str(self._scale[0]));
        self.scaleT.setText(str(self._scale[1]));

 
    def updateCoeff(self,row,col):
        self._coeff[row][col]= float(str(self.funkgrid.text(row,col)));

    def updateCoeff_fromparent(self):
        funklet=self.parent._funklet;
        self._offset=array([0.,0.]);
        self._scale=array([1.,1.]);
        self._coeff=0.;

        if funklet:
#          print funklet;
          if hasattr(funklet,'coeff'):
            self._coeff=funklet.coeff;
          if hasattr(funklet,'offset'):
            self._offset=funklet.offset;
          if hasattr(funklet,'scale'):
            self._scale = funklet.scale;
        if is_scalar(self._coeff):
            self._coeff=[[self._coeff]]
        if is_scalar(self._coeff[0]):
          ncoeff=[];
          for i in range(len(self._coeff)):
            ncoeff.append([self._coeff[i]]);
          self._coeff=ncoeff;
        self._nx=len(self._coeff);
        self._ny=len(self._coeff[0]);
        self.updategrid();


def define_treebrowser_actions (tb):
  _dprint(1,'defining parm fiddling treebrowser actions');
  tb.add_action(NA_ParmFiddler,30,where="node");

Grid.Services.registerViewer(meqds.NodeClass(),ParmFiddler,priority=25);
