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
  def __init__ (self,label,nodes=[],name=None,
                     solver_control=None,
                     individual=False,bookmark=None,
                     table_name="calibration.mep",table_in_ms=True,
                     **kw):
    self.label = label;
    self.tdloption_namespace = label;
    self.name  = name or label;
    self.nodes = nodes;
    # create bookmarks (if specified as an int, it gives the number of parms to bookmark)
    if bookmark:
      if isinstance(bookmark,bool):
        bookmark = len(nodes);
      pg = Bookmarks.Page("Parameters: %s"%label);
      for parm in nodes[0:bookmark]:
        pg.add(parm);
    # create TDLOptions for this parameter group
    self._table_name_option = \
      TDLOption('table_name','MEP table name',TDLDirSelect("*.mep",default=table_name),namespace=self);
    # make individual tdloptions for every parm if asked
    self._individual = individual;
    if individual:
      self._option_list = [];
      self._parm_opts = {};
      for parm in nodes:
        opts = self._parm_opts[parm.name] = record();
        opts.tdloption_namespace = label+"."+parm.name.replace(":","_");
        self._option_list.append(
          TDLMenu("Solve for %s"%parm.name,
            TDLOption('initial_value','Initial value (None for default)',[None,0.],more=float,namespace=opts),
            TDLOption('time_deg','Polynomial degree, time',[0,1,2,3],more=int,namespace=opts),
            TDLOption('freq_deg','Polynomial degree, freq',[0,1,2,3],more=int,namespace=opts),
            TDLOption('subtile_time','Solution subinterval (subtile), time',[None],more=int,namespace=opts),
            TDLOption('subtile_freq','Solution subinterval (subtile), freq',[None],more=int,namespace=opts),
            toggle='solvable',open=True,namespace=opts
          )
        );
    else:  # common options for all parms
      self._option_list = [
        TDLOption('initial_value','Initial value (None for default)',[None,0.],more=float,namespace=self),
        TDLOption('time_deg','Polynomial degree, time',[0,1,2,3],more=int,namespace=self),
        TDLOption('freq_deg','Polynomial degree, freq',[0,1,2,3],more=int,namespace=self),
        TDLOption('subtile_time','Solution subinterval (subtile), time',[None],more=int,namespace=self),
        TDLOption('subtile_freq','Solution subinterval (subtile), freq',[None],more=int,namespace=self) ];
    self._option_list += [
      TDLOption('use_previous','Initialize with solution from previous time interval',True,namespace=self),
      TDLOption('use_mep','Initialize with solution from MEP table',True,namespace=self),
      TDLOption('ignore_time',"...even if time domains don't match (e.g. in case of calibrators)",True,namespace=self),
      TDLOption('save_all','Save solutions to MEP table even if not converged',True,namespace=self),
      self._table_name_option,
      TDLMenu('Parameter constraints (the HMS Suicidal Insanity submenu)',
        TDLOption('force_positive','Force parameters (or c00) to stay positive',False,namespace=self),
        TDLOption('constrain_min','Lower bound for parameter (or c00)',
                [None],more=float,namespace=self),
        TDLOption('constrain_max','Upper bound for parameter (or c00)',
                [None],more=float,namespace=self)
      )
    ];
    # update option values from keyword arguments
    for opt in self._option_list:
      if hasattr(opt,'symbol') and opt.symbol in kw:
        opt.set_value(kw[opt.symbol]);
    # register callback with the MS selector
    if Context.mssel and table_in_ms:
      Context.mssel.when_changed(self._select_new_ms);
    # create our own solver control if none is supplied
    if solver_control is None:
      self.solver_control = SolverControl(label,name);
      self._private_solver_control = True;
    else:
      self.solver_control = solver_control;
      self._private_solver_control = False;
    # add ourselves to global list of parmgroups
    global _all_parmgroups;
    _all_parmgroups.append(self);

  def _select_new_ms (self,msname):
    if msname:
      self.table_name = os.path.join(msname,os.path.basename(self.table_name));
      self._table_name_option.set_value(self.table_name);

  def add (self,*nodes):
    self.nodes += nodes;

  def runtime_options (self,submenu=True):
    if submenu:
      opts = [ TDLMenu("Parameter options",*self._option_list) ];
    else:
      opts = self._option_list;
    if self._private_solver_control:
      opts.append(TDLMenu("Solver options (for the brave)",*self.solver_control.runtime_options()));
    return opts;

  def _fill_state_record (self,state):
    """Fills a state record with common options""";
    state.use_previous  = self.use_previous;
    state.reset_funklet = not self.use_mep;
    state.ignore_time   = self.ignore_time;
    state.save_all      = self.save_all;
    state.table_name    = self.table_name;

  def make_cmdlist (self,solvable=True):
    """Makes a record suitbale for inclusion in a request command_by_list entry.
    If 'solvable' is True, solvability is determined by parm options.
    If 'solvable' is False, solvability is False""";
    if self._individual:
      cmdlist = [];
      nonsolve = [];
      for parm in self.nodes:
        opts = self._parm_opts[parm.name];
        # build list of full records for solvables
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
        else:
          nonsolve.append(parm);
      # and now make an entry for the non-solvables
      if nonsolve:
        state = record(solvable=False);
        self._fill_state_record(state);
        cmdlist.append(record(name=[parm.name for parm in nonsolve],state=state));
    # else all parms are treated together, so make one state record for everything
      return cmdlist;
    else:
      state = record();
      if solvable:
        state.solvable = True;
        # transfer current option settings
        if self.initial_value is not None:
          state.default_value = self.initial_value;
        state.shape         = [self.time_deg+1,self.freq_deg+1];
        state.tiling        = record();
        if self.subtile_time:
          state.tiling.time = self.subtile_time;
        if self.subtile_freq:
          state.tiling.freq = self.subtile_freq;
      else:
        state.solvable = False;
      self._fill_state_record(state);
      return [ record(
        name=[node.name for node in self.nodes],
        state=state) ];

  def run_solution (self,mqs,mssel=None,vdm=None,tiling=None,wait=False):
    """Helper fuunction to put together TDL jobs.
    Starts a solution, setting the group to solvable""";
    mssel = mssel or Context.mssel;
    # make command lists for our parameters
    cmdlist = self.make_cmdlist();
    # and add commands to init parms from all other parmgroups (as non-solvable)
    global _all_parmgroups;
    for pg in _all_parmgroups:
      if pg is not self:
        cmdlist += pg.make_cmdlist(solvable=False);
    self.solver_control.update_state(mqs,cmdlist=cmdlist);
    # run the VisDataMux
    vdm = namify(vdm or Context.vdm or 'VisDataMux')
    mqs.execute(vdm,mssel.create_io_request(tiling),wait=wait);

  def _run_solve_job (self,mqs,parent,wait=False,**kw):
    self.run_solution(mqs,tiling=self.tile_size,wait=wait);

  def _clear_mep_tables (self,mqs,parent,**kw):
    if parent and QMessageBox:
      if QMessageBox.warning(parent,"Clearing solutions","This will clear out <b>all</b> previous solutions from table '%s'. Are you sure you want to do this?"%self.table_name,
          QMessageBox.Yes,QMessageBox.No|QMessageBox.Default|QMessageBox.Escape) != QMessageBox.Yes:
        return;
    try:    os.system("rm -fr "+self.table_name);
    except: pass;

  def make_solvejob_menu (self,jobname=None,default_tile_size=1):
    self._tile_option = TDLOption('tile_size',"Solution interval (aka tile size), in timeslots",
                                  [1,10,100],more=int,namespace=self);
    opts = [self._tile_option] + self.runtime_options(submenu=True);
    opts.append(TDLJob(self._run_solve_job,"Run solution"));
    opts.append(TDLJob(self._clear_mep_tables,"Clear out all previous solutions from MEP tables"));
    return TDLMenu(jobname or "Solve for %s"%self.label,*opts);

def compose_calibration_menu ():
  # makes options to solve for all ParmGroups

