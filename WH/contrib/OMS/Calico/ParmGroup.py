from Timba.TDL import *
from Meow import Context

# make sure solvables is a list of names
def namify (arg):
  if isinstance(arg,str):
    return arg;
  elif is_node(arg):
    return arg.name;
  else:
    raise TypeError,"node name or node object expected, got '%s'"%str(type(arg));

class ParmGroup (object):
  def __init__ (self,label,name=None,nodes=[],solver_control=None):
    self.label = label;
    self.tdloptions_namespace = label;
    self.name  = name or label;
    self.nodes = nodes; 
    # create TDLOptions for this parameter group
    self._option_list = [
      TDLOption('initial_value','Initial value',0.,more=float,namespace=self),
      TDLOption('time_deg','Polynomial degree, time',0,more=int,namespace=self),
      TDLOption('freq_deg','Polynomial degree, freq',0,more=int,namespace=self),
      TDLOption('subtile_time','Solution subinterval (subtile), time',[None],more=int,namespace=self),
      TDLOption('subtile_freq','Solution subinterval (subtile), freq',[None],more=int,namespace=self),
      TDLOption('use_previous','Use fit from previous time interval as initial guesses',True,namespace=self),
      TDLOption('use_mep','Use solutions from MEP table as initial guesses',True,namespace=self),
      TDLOption('ignore_time',"...even if time domains don't match (e.g. in case of calibrators)",True,namespace=self),
      TDLOption('save_all','Save solutions to MEP table even if not converged',True,namespace=self),
      TDLOption('table_name','MEP table name',TDLDirSelect("*.mep"),namespace=self),
      TDLMenu('Parameter constraints (the HMS Suicidal Insanity submenu)',
        TDLOption('force_positive','Force parameters (or c00) to stay positive',False,namespace=self),
        TDLOption('constrain_min','Lower bound for parameter (or c00)',
                [None],more=float,namespace=self),
        TDLOption('constrain_max','Upper bound for parameter (or c00)',
                [None],more=float,namespace=self)
      )
    ];
    # create our own solver control if none is supplied
    if solver_control is None:
      solver_control = SolverControl(label,name);
    self.solver_control = solver_control;
    
  def add (self,*nodes):
    self.nodes += nodes;
    
  def runtime_options (self,submenu=True):
    if submenu:
      return [ TDLMenu("Parameter options for %s"%self.name,*self._options_list) ];
    else:
      return self._option_list;
    
  def make_state_record (self):
    state = record();
    state.solvable = True;
    # transfer current option settings
    state.default_value = self.initial_value;
    state.shape         = [time_deg+1,freq_deg+1];
    state.tiling        = record();
    if self.subtile_time:
      state.tiling.time = self.subtile_time;
    if self.subtile_freq:
      state.tiling.freq = self.subtile_freq;
    # these get transferred as is
    state.use_previous  = self.use_previous;
    state.reset_funklet = not self.use_mep;
    state.ignore_time   = self.ignore_time;
    state.save_all      = self.save_all;
    state.table_name    = self.table_name;
    # state.force_positive = self.force_positive;
    # state.constrain_min  = self.constrain_min;
    # state.constrain_max  = self.constrain_max;
    return state;
    
  def make_cmdlist_record (self):
    """Makes a record suitbale for inclusion in a request command_by_list entry""";
    state = self.make_state_record();
    return record(
      name=[node.name for node in self.nodes],
      state=state);
      
  def run_solution (self,mqs,mssel=None,vdm=None,wait=False):
    """Starts a solution, setting the group to soolvable""";
    mssel = mssel or Context.mssel;
    # update solver with our settings
    self.solver_control.update_state(mqs,cmdlist=self.make_cmdlist_record());
    # run the VisDataMux
    vdm = namify(vdm or Context.vdm or 'VisDataMux')
    mqs.execute(vdm,mssel.create_io_request(),wait=wait);
