
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

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from Timba.Grid import DataItem
from Timba.Grid import Services

from pycasatable import *;
from numarray import *;
import os;
import time;
import qt;
import qttable;

class ParmTable:
    def __init__(self,name,ns=None,parms="*",fit=False):
        self.reopen(name);
        self._parms=parms;
        self._fit=fit;
        self._tablename = name;
        self._keyname = name.replace('/',':');
        self._newtablename = self._tablename+"_"+ time.strftime("%a_%d_%b_%Y_%H:%M:%S",time.localtime())
        #get parms
        self._start_t=1e90;
        self._start_f=1e90;
        self._end_t=0;
        self._end_f=0;
        self._nr_funklets = self._n_t = self._n_f = 0;
        self._db=self.getNames(parms);
        self._rqid=0;
        self._rank_f=1;
        self._rank_t=1;
        if(ns):
            if(fit):
                self.create_solver_trees(ns);
                bm = record(name='SolvedParmInspector '+self._keyname,page=
                            [record(viewer='Collections Plotter',udi='/node/ParmInspector:'+self._keyname, publish=True, pos=(0,0)),
                             record(viewer='Collections Plotter',udi='/node/SolvedParmInspector:'+self._keyname, publish=True, pos=(1,0)),
                             record(viewer='Collections Plotter',udi='/node/ResidualInspector:'+self._keyname, publish=True, pos=(0,1))]);
                Settings.forest_state.bookmarks.append(bm);
            
            else:
                self.create_parm_tree(ns);
            bm = record(name='ParmTableInspector '+self._keyname,page=
                        [record(viewer='Collections Plotter',udi='/node/ParmInspector:'+self._keyname, publish=True, pos=(0,0)),
                         record(viewer='Result Plotter',udi='/node/ParmInspector:'+self._keyname, publish=True, pos=(1,0))]);
            Settings.forest_state.bookmarks.append(bm);
        self.close(); # close in case the rest of the tree wants access too

    def getTableName(self):
        return self._tablename;
        
    def getNames(self,pattern="*"):
        if not self._db:
            self.reopen(self._tablename);

        parmname ="\'"+pattern+"\'";
        select = 'NAME='+"pattern("+parmname+")";
        newtab = self._db.query(select);

        names=set(newtab.getcol('NAME')); #unique list of names
        # sort
        self._parmnames=list(names);
        self._parmnames.sort();
        #create dictionary
        self._parms={};
        for parm  in names:
            select = "NAME==\'"+parm+"\'";
            tab2=newtab.query(select);
            st = tab2.getcol("STARTTIME");
            nr_funklets = len(st);
            start_t = min(st);
            end_t = max(tab2.getcol("ENDTIME"));
            start_f = min(tab2.getcol("STARTFREQ"));
            end_f = max(tab2.getcol("ENDFREQ"));
            if self._nr_funklets < nr_funklets:
                self._nr_funklets = nr_funklets;
            if self._start_t > start_t:
                self._start_t = start_t;
            if self._end_t < end_t:
                self._end_t = end_t;
            if self._start_f > start_f:
                self._start_f = start_f;
            if self._end_f < end_f:
                self._end_f = end_f;
            self._parms[parm]={'start_t':start_t,'end_t':end_t,
                               'start_f':start_f,'end_f':end_f,
                               'nr_funklets':nr_funklets,'funklist':[]}
        return newtab;


    def getFunklets(self,name):
        if not self._db:
            self.reopen(self._tablename);
        funklets=[];
        select = "NAME==\'"+name+"\'";
        tab2=self._db.query(select);
        types = tab2.getcol('FUNKLETTYPE');
        if not tab2.isvarcol('VALUES'):
            coeff = tab2.getcol('VALUES');
        else:
            coeff = tab2.getvarcol('VALUES');
        st_t = tab2.getcol('STARTTIME');
        e_t = tab2.getcol('ENDTIME');
        st_f = tab2.getcol('STARTFREQ');
        e_f = tab2.getcol('ENDFREQ');

        n_f = len(set(st_f));
        n_t = len(set(st_t));
        if self._n_t  < n_t:
            self._n_t = n_t;
        if self._n_f  < n_f:
            self._n_f = n_f;


        self._parms[name]['n_f']=n_f;#store number of freq and nr of time funklets.
        self._parms[name]['n_t']=n_t;

        for i in range(len(types)):
            if isinstance(coeff,dict):
                key = 'r'+str(i+1);
                co=coeff[key];
            else:
                co=coeff[i];

            # get max rank
            rank_f = shape(co)[1];
            rank_t = shape(co)[0];
            if rank_f > self._rank_f:
                self._rank_f = rank_f;
            if rank_t > self._rank_t:
                self._rank_t = rank_t;
            funklet={'ftype':types[i],'coeff':co,
                     'st_t':st_t[i],'end_t':e_t[i],
                     'st_f':st_f[i],'end_f':e_f[i],
                     'rank_t':rank_t,'rank_f':rank_f};
            funklets.append(funklet);
        return funklets;


    def Inspector(self,mqs,parent):
        if not self._db:
            self.reopen(self._tablename);
        for parm in self._parms:
            self.getFunklets(parm);
        self._mqs=mqs;
        inspect = Inspector(self,mqs,parent); 
##            #self.draw_domains(parm);
            
##        self.plot(mqs);
##        self.fit_all(mqs,shape=[1,2]);
        self.close();
        
    def create_parm_tree(self,ns):
        parms=();
        for parm in self._parmnames:

            if not ns[parm].initialized():
                ns[parm]<<Meq.Parm(table_name=self._tablename);
            parms+=(ns[parm],);
        ns.ParmInspector(self._keyname)<<Meq.Composer(children = parms,plot_label=[ parm for parm in self._parmnames]);

    def create_solver_trees(self,ns):
        solvers = parms=solved_parms=subtracts=();
        for parm in self._parmnames:
            if not ns[parm].initialized():
                ns[parm]<<Meq.Parm(table_name=self._tablename);
            new_parm_name = parm +":NEW";

            new_parm = ns[new_parm_name] << Meq.Parm(parm_name=parm);
            condeq = ns.condeq(parm,'TI',self._keyname) << Meq.Condeq(ns[parm],new_parm);
            solver = ns.solver(parm,'TI',self._keyname)<< Meq.Solver(condeq,solvable = new_parm,
                                                                     epsilon=1e-4,
                                                                     num_iter=15,
                                                                     last_update=True,
                                                                     save_funklets=False);


            subtract=ns.subtract(parm,'TI',self._keyname)<<Meq.Subtract(ns[parm],new_parm);
            solvers+=(solver,);
            subtracts+=(subtract,);
            solved_parms+=(new_parm,);
            parms+=(ns[parm],);
            
        PI = ns.ParmInspector(self._keyname)<<Meq.Composer(children = parms,plot_label=[ parm for parm in self._parmnames]);
        RI = ns.ResidualInspector(self._keyname)<<Meq.Composer(children = subtracts,plot_label=[ "res:"+parm for parm in self._parmnames]);
        SPI = ns.SolvedParmInspector(self._keyname)<<Meq.Composer(children = solved_parms,plot_label=[ parm.name for parm in solved_parms]);
        SI = ns.SolverInspector(self._keyname)<<Meq.ReqSeq(children = solvers + (RI,PI,SPI));



    def plot(self,mqs,domain=None):
        if not domain or len(domain)<6:
            domain = [self._start_t,self._start_f,self._end_t,self._end_f,self._n_t*self._rank_t,self._n_f*self._rank_f];
            
        dom  = meq.domain(domain[1],domain[3],
                             domain[0],domain[2]);    # (f1,f2,t1,t2)
        cells = meq.cells(dom, num_freq=domain[5], num_time=domain[4]);
        request = meq.request(cells, rqtype='ev');
        request.request_id = hiid('ev',self._rqid,self._rqid,self._rqid,self._rqid,self._rqid);
        result = mqs.meq('Node.Execute',record(name='ParmInspector:'+self._keyname, request=request),wait=True)
        self._rqid=self._rqid+1;
        return result;



    def fit(self,mqs,parm,shape=[1,1],domain=None):
        newparm = parm+":NEW";
        result = mqs.meq('Node.SetState',record(name=newparm, shape=shape));
        solver = "solver:"+parm+":TI";
        if not domain or len(domain)<6:
            domain = [self._start_t,self._start_f,self._end_t,self._end_f,self._n_t*self._rank_t,self._n_f*self._rank_f];
            
        dom  = meq.domain(domain[1],domain[3],
                             domain[0],domain[2]);    # (f1,f2,t1,t2)
        cells = meq.cells(dom, num_freq=domain[5], num_time=domain[4]);
        request = meq.request(cells, rqtype='ev');
        request.request_id = hiid('ev',self._rqid,self._rqid,self._rqid,self._rqid,self._rqid);
        result = mqs.meq('Node.Execute',record(name=solver, request=request),wait=True)
        self._rqid=self._rqid+1;
        return result;
        
        
    def fit_all(self,mqs,shape=[1,1],domain=None,save_funklets=False):
        nparm_state=record(shape=shape);
        if save_funklets:
            nparm_state['table_name']=self._newtablename;
        for parm in self._parmnames:
            newparm = parm+":NEW";
            result = mqs.meq('Node.Set.State',record(name=newparm, state=nparm_state));
            result = mqs.meq('Node.Set.State',record(name="solver:"+parm+":TI:"+self._keyname, state=record(save_funklets=save_funklets)));
        if not domain or len(domain)<6:
            domain = [self._start_t,self._start_f,self._end_t,self._end_f,self._n_t,self._n_f];
            
        dom  = meq.domain(domain[1],domain[3],
                             domain[0],domain[2]);    # (f1,f2,t1,t2)
        cells = meq.cells(dom, num_freq=domain[5], num_time=domain[4]);
        request = meq.request(cells, rqtype='ev');
        request.request_id = hiid('ev',self._rqid,self._rqid,self._rqid,self._rqid,self._rqid);
        result = mqs.meq('Node.Execute',record(name='SolverInspector:'+self._keyname, request=request),wait=True);
        self._rqid=self._rqid+1;
        return result;
    
   
    def draw_domains(self,parm):
        if not self._parms[parm][funklist]:
            self.getFunklets(parm);
        funklist = self._parms[parm][funklist];
        rects=[];
        for funk in funklist:
            rect = qwt.rect(funk[st_t],funk[st_f],funk[end_t] - funk[st_t],funk[end_f]-funk[st_f]);
            rects.append(rect);
        


    def select_parms(self,mqs,parmlist='all'):
        if parmlist == 'all':
            parmlist = self._parmnames;
        cs = meqds.CS_ACTIVE;
        for name in parmlist:
            mqs.meq('Node.Set.State',
                      record(name=name,state=record(control_status=cs)));
            # print "selected the state of parm",name
            # also select the solver
            if self._fit:
                sname= "solver:"+name+':TI:'+self._keyname;
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));
                # and the subtract nodes
                sname = "subtract:"+name+":TI:"+self._keyname;
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));
                # and the new parms
                sname = name+":NEW";
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));
                
        # also reset node_list in inspectors for correct naming
        mqs.meq('Node.Set.State',
                record(name='ParmInspector:'+self._keyname,state=record(plot_label=[ parm for parm in parmlist])));
        if self._fit:
            mqs.meq('Node.Set.State',
                    record(name='ResidualInspector:'+self._keyname,state=record(plot_label=[ "res:"+parm for parm in parmlist])));
            



    def deselect_parms(self,mqs,parmlist='all'):
        if parmlist == 'all':
            parmlist = self._parmnames;
        cs = not(meqds.CS_ACTIVE);
        for name in parmlist:
            mqs.meq('Node.Set.State',
                      record(name=str(name),state=record(control_status=cs)));
            
            # also deselect the solver
            if self._fit:
                sname= "solver:"+name+':TI:'+self._keyname;
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));
                # and the subtract nodes
                sname = "subtract:"+name+":TI:"+self._keyname;
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));
                # and the new parms
                sname = name+":NEW";
                mqs.meq('Node.Set.State',
                        record(name=sname,state=record(control_status=cs)));

    def reopen(self,name="test"):
        self._name=name;
        if os.path.isdir(name):
            
            self._db=table(name);
        if not self._db:
            print "Opening db",name,"FAILED";

    def close(self):
        if not self._db:
            print "Closing db",self._tablename,"FAILED";
        else:
            self._db.close();
        self._db=None;



class Inspector(qt.QDialog):
    def __init__(self,parmtable,mqs=None,parent = None,name = None,modal = 0,fl = 0):
        if not isinstance(parmtable,ParmTable):
            print "Inspector should be initilaized with a ParmTable";
            return;
        
        
        self.parmTable=parmtable;
        self._mqs=mqs;
        self._parent=parent;
        self._shape=[1,1];
        # open user interface
        qt.QDialog.__init__(self,parent);
        self.setCaption('Inspector '+self.parmTable.getTableName());
        self.v = qt.QVBoxLayout(self, 10, 5)
        self.parms=qttable.QTable(self);
        self.parms.setSelectionMode (qttable.QTable.MultiRow );
        self.parms.setCaption("Parms")
        self.init_table();
        self.v.addWidget(self.parms);
        
        # add domain box
        axis= qt.QHGroupBox("Domain",self);
        self.xfrom = [];
        self.xto = [];
        self.nsteps = [];
        for ax in ['Time','Freq']:
            time = qt.QLabel(ax,axis)
            textfrom = qt.QLabel("from",axis);
            self.xfrom.append(qt.QLineEdit(axis));

            textto = qt.QLabel("to",axis);
            self.xto.append(qt.QLineEdit(axis));
            textsteps = qt.QLabel("steps",axis);
            self.nsteps.append(qt.QLineEdit(axis));

        self.cmdDefault = qt.QPushButton('Default', axis);
        qt.QObject.connect(self.cmdDefault,qt.SIGNAL("clicked()"),self.init_axes);
            
        self.init_axes();
        self.v.addWidget(axis);
        
        if self.parmTable._fit:
            self.rank=[];
            #create fit paramaeter screen
            fitparms = qt.QHGroupBox("Fit Parameters",self);
            rankt = qt.QLabel("Rank Time",fitparms);
            self.rank.append(qt.QLineEdit("1",fitparms));
            rankf = qt.QLabel("Rank Freq",fitparms);
            self.rank.append(qt.QLineEdit("1",fitparms));
            self._save = qt.QCheckBox("save",fitparms);
            self.v.addWidget(fitparms);
        
        self.Bh = qt.QHBoxLayout(self.v, 5)
        self.cmdPlotParms = qt.QPushButton('Plot Selection', self)
        qt.QObject.connect(self.cmdPlotParms,qt.SIGNAL("clicked()"),self.plot);
        self.Bh.addWidget(self.cmdPlotParms)

        if self.parmTable._fit:
            self.cmdFitParms = qt.QPushButton('Fit Selection', self)
            qt.QObject.connect(self.cmdFitParms,qt.SIGNAL("clicked()"),self.fit);
            self.Bh.addWidget(self.cmdFitParms)


      
        self.show();

    def plot(self):
        self.get_selected();
        dom = self.getdomain();
        self.parmTable.deselect_parms(self._mqs);
        self.parmTable.select_parms(self._mqs, self._selected);
        result = self.parmTable.plot(self._mqs,domain=dom);
        self.reset();

    def fit(self):
        self.get_selected();
        dom = self.getdomain();
        shape = self.getshape();
        save = self._save.isChecked();
        self.parmTable.deselect_parms(self._mqs);
        self.parmTable.select_parms(self._mqs, self._selected);
        
        result=self.parmTable.fit_all(self._mqs,shape = shape,domain=dom,save_funklets=save);
        self.reset();

    def init_table(self):
        self.parms.setNumCols(6);
        self.parms.setNumRows(len(self.parmTable._parms));
        self.parms.setReadOnly(True);
        self.parms.horizontalHeader () .setLabel(0,"name");
        self.parms.horizontalHeader () .setLabel(1,"nr funklets");
        self.parms.horizontalHeader () .setLabel(2,"start time");
        self.parms.horizontalHeader () .setLabel(3,"end time");
        self.parms.horizontalHeader () .setLabel(4,"start freq");
        self.parms.horizontalHeader () .setLabel(5,"end freq");
        self.parms.setColumnWidth(0,100);
        self.parms.setColumnWidth(0,10);
        self.parms.setColumnWidth(0,100);
        self.parms.setColumnWidth(0,100);
        self.parms.setColumnWidth(0,100);
        tooltip="click to sort";
        qt.QToolTip.add(self.parms.horizontalHeader (),tooltip);
        self._swapsort=True;
        qt.QObject.connect( self.parms.horizontalHeader (),qt.SIGNAL("released(int)"),self.sortColumn);
        parmnr=0;
        for parm in self.parmTable._parms:
            self.parms.setText( parmnr,0,parm );
            self.parms.setText( parmnr,1,str(self.parmTable._parms[parm]['nr_funklets']) );
            self.parms.setText( parmnr,2,str(self.parmTable._parms[parm]['start_t'] ));
            self.parms.setText( parmnr,3,str(self.parmTable._parms[parm]['end_t'] ));
            self.parms.setText( parmnr,4,str(self.parmTable._parms[parm]['start_f'] ));
            self.parms.setText( parmnr,5,str(self.parmTable._parms[parm]['end_f'] ));
            parmnr=parmnr+1;
        
    def sortColumn(self,col):
        swapsort = not self._swapsort;
        
        self.parms.sortColumn ( col,swapsort,True);
        self._swapsort=swapsort;


    def get_selected(self):
        self._selected=[];
        for i in range(len(self.parmTable._parms)):
            if self.parms.isRowSelected(i):
                self._selected.append( str(self.parms.text(i,0)));

                # print "selected",i, str(self.parms.text(i,0));
    def init_axes(self):
        self.xto[0].setText(str(self.parmTable._start_t));
        self.xto[1].setText(str(self.parmTable._start_f));
        self.xfrom[0].setText(str(self.parmTable._end_t));
        self.xfrom[1].setText(str(self.parmTable._end_f));
        self.nsteps[0].setText(str(self.parmTable._n_t*self.parmTable._rank_t));
        self.nsteps[1].setText(str(self.parmTable._n_f*self.parmTable._rank_f));


    def getdomain(self):
        dom=[float(str(self.xto[0].text())),
             float(str(self.xto[1].text())),
             float(str(self.xfrom[0].text())),
             float(str(self.xfrom[1].text())),
             int(str(self.nsteps[0].text())),
             int(str(self.nsteps[1].text()))
             ]; #[start_t,start_f, end_t,end_f,_n_t, _n_f;
        return dom;

    def getshape(self):
        shape=[int(str(self.rank[0].text())),
               int(str(self.rank[1].text()))
               ]; #n_t, n_f;
        return shape;
    
    def reset(self):
        self.parmTable.select_parms(self._mqs);
