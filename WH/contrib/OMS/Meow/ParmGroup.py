from Timba.TDL import *
from Meow import Context
from Meow import Bookmarks
from SolverControl import SolverControl

import os.path
import os
try:
  from qt import QMessageBox
except:
  QMessageBox = None;

# converts argument to a name
def namify (arg):
  if isinstance(arg,str):
    return arg;
  elif is_node(arg):
    return arg.name;
  else:
    raise TypeError,"node name or node object expected, got '%s'"%str(type(arg));

_all_parmgroups = [];

class ParmGroup (object):
  class Controller (object):
    """A ParmGroup Controller implements a number of TDLOptions associated with the ParmGroup,
    and provides methods for changing the state of the parms"""
    def __init__ (self,pg,label,solvable=False,
                  **kw):
      self.pg = pg;
      self.label = label = "%s.%s"%(label,self.pg.label);
      self.tdloption_namespace = label.replace(":","_").replace(" ","_");
      # this will need to be manipulated from _select_new_ms() below
      self._table_name_option = \
        TDLOption('table_name','MEP table name',TDLDirSelect("*.mep",default=pg.table_name),namespace=self);
      # build up list of options
      self._option_list = [];
      # make individual solvability tdloptions for every parm, if so asked
      self._individual = pg._individual;
      sopts = [];  # these will need to be shown/hidden with the solvability control
      if self._individual:
        self._parm_opts = {};
        for parm in self.pg.nodes:
          opts = self._parm_opts[parm.name] = record();
          opts.tdloption_namespace = (label+"."+parm.name).replace(":","_");
          # solvable parm options
          parm_sopts = [
                TDLOption('time_deg','Polynomial degree, time',[0,1,2,3],more=int,namespace=opts),
                TDLOption('freq_deg','Polynomial degree, freq',[0,1,2,3],more=int,namespace=opts),
                TDLOption('subtile_time','Solution subinterval (subtile), time',[None],more=int,namespace=opts),
                TDLOption('subtile_freq','Solution subinterval (subtile), freq',[None],more=int,namespace=opts)
          ];
          parm_solv = TDLMenu("Solve for %s"%parm.name,
                TDLOption('initial_value','Override initial value',[None,0.],more=float,namespace=opts),
                toggle='solvable',open=True,namespace=opts,
                *parm_sopts
              )
          # hide solvables
          def show_hide_sopts (show):
            print 'showing',show,parm_sopts;
            for opt in parm_sopts:
              opt.show(show);
          parm_solv.when_changed(show_hide_sopts);
          self._option_list.append(parm_solv);
      # else provide a common equivalent applying to all parms
      else:  
        self._option_list.append(TDLOption('initial_value',
                                  'Override initial value',[None,0.],more=float,namespace=self));
        so = [  TDLOption('time_deg','Polynomial degree, time',[0,1,2,3],more=int,namespace=self),
                TDLOption('freq_deg','Polynomial degree, freq',[0,1,2,3],more=int,namespace=self),
                TDLOption('subtile_time','Solution subinterval (subtile), time',[None],more=int,namespace=self),
                TDLOption('subtile_freq','Solution subinterval (subtile), freq',[None],more=int,namespace=self) 
        ];
        sopts += so;
        self._option_list += so;
      # now, more common options which are the same for individual/non-individual parms
      self._option_list += [
        self._table_name_option,
        TDLOption('use_mep','Initialize with solution from MEP table',True,namespace=self),
        TDLOption('ignore_time',"...even if time domains don't match (e.g. in case of calibrators)",False,namespace=self)
      ];
      so = [  TDLOption('use_previous','Start from solution of previous time interval',True,namespace=self),
              TDLOption('save_all','Save solutions to MEP table even if not converged',True,namespace=self),
              TDLMenu('Parameter constraints (the HMS Suicidal Insanity submenu)',
                TDLOption('force_positive','Force parameters (or c00) to stay positive',False,namespace=self),
                TDLOption('constrain_min','Lower bound for parameter (or c00)',
                    [None],more=float,namespace=self),
                TDLOption('constrain_max','Upper bound for parameter (or c00)',
                    [None],more=float,namespace=self)
              )
      ];
      sopts += so;
      self._option_list += so;
      self._option_list.append(TDLJob(self._clear_mep_tables,"Clear out all previous solutions from MEP tables"));
      # update option values from keyword arguments
      for opt in self._option_list:
        if hasattr(opt,'symbol') and opt.symbol in kw:
          opt.set_value(kw[opt.symbol]);
      # register callback with the MS selector
      if Context.mssel and pg._table_in_ms:
        Context.mssel.when_changed(self._select_new_ms);
      # now make menu
      self._optmenu = TDLMenu("Solve for %s"%pg.name,
                        toggle='solvable',open=solvable,namespace=self,
                        *self._option_list);
      # show/hide solvability-related options
      def show_hide_sopts (show):
        for opt in sopts:
          opt.show(show);
      self._optmenu.when_changed(show_hide_sopts);
        
    def runtime_options (self,submenu=True):
      return [ self._optmenu ];
      
    def _select_new_ms (self,msname):
      if msname:
        self.table_name = os.path.join(msname,os.path.basename(self.table_name));
        self._table_name_option.set_value(self.table_name);
      
    def _fill_state_record (self,state):
      """Fills a state record with common options""";
      state.table_name    = self.table_name;
      state.reset_funklet = not self.use_mep;
      state.ignore_time   = self.ignore_time;
      state.use_previous  = self.use_previous;
      state.save_all      = self.save_all;
  
    def make_cmdlist (self,solvable=True):
      """Makes a record suitbale for inclusion in a request command_by_list entry.
      If 'solvable' is True, solvability is determined by parm options.
      If 'solvable' is False, solvability is always False.
      """;
      solvable = solvable and self.solvable;
      if self._individual:
        cmdlist = [];
        deferred = [];
        for parm in self.pg.nodes:
          opts = self._parm_opts[parm.name];
          # if solvable, make a full record for this parm
          if solvable and opts.solvable:
            state = record(solvable=True);
            if opts.initial_value is not None:
              state.default_value = opts.initial_value;
            state.shape         = [opts.time_deg+1,opts.freq_deg+1];
            state.tiling        = record();
            if opts.subtile_time:
              state.tiling.time = opts.subtile_time;
            if opts.subtile_freq:
              state.tiling.freq = opts.subtile_freq;
            self._fill_state_record(state);
            cmdlist.append(record(name=[parm.name],state=state));
          # else if value is overridden, also make a full record
          elif opts.initial_value is not None:
            state = record(solvable=False);
            state.default_value = opts.initial_value;
            self._fill_state_record(state);
            cmdlist.append(record(name=[parm.name],state=state));
          # else include in list of other parms to be initialized with a single record later
          else:
            deferred.append(parm);
        # and now make an entry for the non-solvables
        if deferred:
          state = record(solvable=False);
          self._fill_state_record(state);
          cmdlist.append(record(name=[parm.name for parm in deferred],state=state));
        return cmdlist;
      # else all parms are treated together, so make one state record for everything
      else:
        state = record();
        if self.initial_value is not None:
          state.default_value = self.initial_value;
        state.solvable = solvable;
        if solvable:
          state.shape         = [self.time_deg+1,self.freq_deg+1];
          state.tiling        = record();
          if self.subtile_time:
            state.tiling.time = self.subtile_time;
          if self.subtile_freq:
            state.tiling.freq = self.subtile_freq;
        self._fill_state_record(state);
        return [ record(
          name=[node.name for node in self.pg.nodes],
          state=state) ];
          
    def _clear_mep_tables (self,mqs,parent,**kw):
      if parent and QMessageBox:
        if QMessageBox.warning(parent,"Clearing solutions","This will clear out <b>all</b> previous solutions from table '%s'. Are you sure you want to do this?"%self.table_name,
            QMessageBox.Yes,QMessageBox.No|QMessageBox.Default|QMessageBox.Escape) != QMessageBox.Yes:
          return;
      try:    os.system("rm -fr "+self.table_name);
      except: pass;
  
  def __init__ (self,label,nodes=[],name=None,
                     individual=False,bookmark=None,
                     table_name="calibration.mep",table_in_ms=True,
                     **kw):
    self.label = label;
    self.name  = name or label;
    self.nodes = nodes;
    # various properties
    self.table_name = table_name;
    self._table_in_ms = table_in_ms;
    self._individual = individual;
    # create bookmarks (if specified as an int, it gives the number of parms to bookmark)
    if bookmark:
      if isinstance(bookmark,bool):
        bookmark = len(nodes);
      pg = Bookmarks.Page("Parameters: %s"%label);
      for parm in nodes[0:bookmark]:
        pg.add(parm);
    # add ourselves to global list of parmgroups
    global _all_parmgroups;
    _all_parmgroups.append(self);

  def add (self,*nodes):
    self.nodes += nodes;
    
  def make_controller (self,label=None,**kw):
    return self.Controller(self,label,**kw);

_all_solvejobs = [];

class SolveJob (object):
  def __init__ (self,label,name,*active_parmgroups):
    self.label = label;
    self.name  = name;
    self.tdloption_namespace = label.replace(":","_").replace(" ","_");
    self.active_parmgroups = active_parmgroups;
    # menu is only made on-demand
    self._jobmenu = None;
    # add to global list
    _all_solvejobs.append(self);
    
  def runtime_options (self):
    if self._jobmenu is None:
      opts = [ TDLOption('tile_size',"Solution interval (aka tile size), in timeslots",
                                    [1,10,100],more=int,namespace=self) ];
      # add options from parmgroups
      global _all_parmgroups;
      self.pg_controllers = [];
      for pg in _all_parmgroups:
        controller = pg.make_controller(self.label,solvable=(pg in self.active_parmgroups));
        opts += controller.runtime_options();
        self.pg_controllers.append(controller);
      
      # add solver control
      self.solver_control = SolverControl(self.label);
      opts.append(TDLMenu("Solver options (for the brave)",*self.solver_control.runtime_options()));
      # add solve job
      opts.append(TDLJob(self._run_solve_job,self.name or "Run solution"));
      # now make a runtime menu
      self._jobmenu = TDLMenu(self.name or "Solve for %s"%self.label,*opts);
    return [ self._jobmenu ];
    
  def run_solution (self,mqs,mssel=None,vdm=None,tiling=None,wait=False):
    """Helper function to put together TDL jobs.
    Starts a solution, setting the group to solvable""";
    mssel = mssel or Context.mssel;
    # make command lists for our parameters
    cmdlist = [];
    for pgc in self.pg_controllers:
      cmdlist += pgc.make_cmdlist();
    self.solver_control.update_state(mqs,cmdlist=cmdlist);
    # run the VisDataMux
    vdm = namify(vdm or Context.vdm or 'VisDataMux')
    mqs.execute(vdm,mssel.create_io_request(tiling),wait=wait);

  def _run_solve_job (self,mqs,parent,wait=False,**kw):
    self.run_solution(mqs,tiling=self.tile_size,wait=wait);
    
def num_solvejobs ():
  global _all_solvejobs;
  return len(_all_solvejobs);
  
def get_solvejob_options ():
  global _all_solvejobs;
  opts = [];
  for job in _all_solvejobs:
    opts += job.runtime_options();
  return opts;
