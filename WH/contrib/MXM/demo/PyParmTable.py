
from Timba.TDL import *
from Timba.Meq import meq
from Timba.Grid import DataItem
from Timba.Grid import Services


from pycasatable import *;
import os;

class ParmTable:
    def __init__(self,name,ns=None,parms="*",fit=False):
        self.reopen(name);
        self._parms=parms;
        self._fit=fit;
        self._tablename = name;
        #get parms
        self._start_t=1e90;
        self._start_f=1e90;
        self._end_t=0;
        self._end_f=0;
        self._nr_funklets = self._n_t = self._n_f = 0;
        self._db=self.getNames(parms);

        if(ns):
            if(fit):
                self.create_solver_trees(ns);
                bm = record(name='SolvedParmInspector '+name,page=
                            [record(viewer='Collections Plotter',udi='/node/SolvedParmInspector', publish=True, pos=(0,0))]);
                Settings.forest_state.bookmarks.append(bm);
            
            else:
                self.create_parm_tree(ns);
            bm = record(name='ParmTableInspector '+name,page=
                        [record(viewer='Collections Plotter',udi='/node/ParmInspector', publish=True, pos=(0,0)),
                         record(viewer='Result Plotter',udi='/node/ParmInspector', publish=True, pos=(1,0))]);
            Settings.forest_state.bookmarks.append(bm);
        self.close(); # close in case the rest of the tree wants access too

        
    def getNames(self,pattern="*"):
        if not self._db:
            self.reopen(self._tablename);

        parmname ="\'"+pattern+"\'";
        select = 'NAME='+"pattern("+parmname+")";
        newtab = self._db.query(select);
        names=set(newtab.getcol('NAME')); #unique list of names
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
                co=coef[i];
            funklet={'ftype':types[i],'coeff':co,
                     'st_t':st_t[i],'end_t':e_t[i],
                     'st_f':st_f[i],'end_f':e_f[i]};
            funklets.append(funklet);
        return funklets;


    def Inspector(self,mqs):
        if not self._db:
            self.reopen(self._tablename);
        for parm in self._parms:
            self.getFunklets(parm);
            
        self.plot(mqs);
        self.fit_all(mqs,shape=[1,2]);
        self.close();
        
    def create_parm_tree(self,ns):
        parms=();
        for parm in self._parms:

            if not ns[parm].initialized():
                ns[parm]<<Meq.Parm(table_name=self._tablename);
            parms+=(ns[parm],);
        ns.ParmInspector<<Meq.Composer(children = parms);

    def create_solver_trees(self,ns):
        solvers = parms=solved_parms=();
        for parm in self._parms:
            if not ns[parm].initialized():
                ns[parm]<<Meq.Parm(table_name=self._tablename);
            new_parm_name = parm +":NEW";
            new_parm = ns[new_parm_name] << Meq.Parm();
            condeq = ns.condeq(parm,'TI') << Meq.Condeq(ns[parm],new_parm);
            solver = ns.solver(parm,'TI')<< Meq.Solver(condeq,solvable = new_parm,
                                                       epsilon=1e-4,
                                                       num_iter=15);

            solved_parm=Meq.ToComplex(ns[parm],new_parm);
            solvers+=(solver,);
            solved_parms+=(solved_parm,);
            parms+=(ns[parm],);
            
        ns.ParmInspector<<Meq.Composer(children = parms);
        ns.SolvedParmInspector<<Meq.Composer(children = solved_parms);
        ns.SolverInspector<<Meq.ReqSeq(children = solvers + (ns.SolvedParmInspector,));



    def plot(self,mqs):
        domain  = meq.domain(self._start_f,self._end_f,
                             self._start_t,self._end_t);    # (f1,f2,t1,t2)
        cells = meq.cells(domain, num_freq=self._n_f, num_time=self._n_t);
        request = meq.request(cells, rqtype='ev');
        result = mqs.meq('Node.Execute',record(name='ParmInspector', request=request))
        return result;



    def fit(self,mqs,parm,shape=[1,1]):
        newparm = parm+":NEW";
        result = mqs.meq('Node.SetState',record(name=newparm, shape=shape));
        solver = "solver:"+parm+":TI";
        domain  = meq.domain(self._start_f,self._end_f,
                             self._start_t,self._end_t);    # (f1,f2,t1,t2)
        cells = meq.cells(domain, num_freq=self._n_f, num_time=self._n_t);
        request = meq.request(cells, rqtype='ev');
        result = mqs.meq('Node.Execute',record(name=solver, request=request))
        return result;
        
        
    def fit_all(self,mqs,shape=[1,1]):
        for parm in self._parms:
            newparm = parm+":NEW";
            result = mqs.meq('Node.Set.State',record(name=newparm, state=record(shape=shape)));
        domain  = meq.domain(self._start_f,self._end_f,
                             self._start_t,self._end_t);    # (f1,f2,t1,t2)
        cells = meq.cells(domain, num_freq=self._n_f, num_time=self._n_t);
        request = meq.request(cells, rqtype='ev');
        result = mqs.meq('Node.Execute',record(name='SolverInspector', request=request));
        return result;
    
   
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
