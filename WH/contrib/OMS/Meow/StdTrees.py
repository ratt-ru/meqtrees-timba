from Timba.TDL import *
import Context
import Jones
import Utils
import Bookmarks

class _BaseTree (object):
  def __init__ (self,ns,array=None,observation=None):
    self.ns = ns;
    self.array = array or Context.array;
    self.observation = observation or Context.observation;
    if not self.array or not self.observation:
      raise ValueError,"array or observation not specified in global Meow.Context, or in this function call";
    self._inputs = self._outputs = None;

  def set_inputs (self,inputs):
    if self._inputs is not None:
      if inputs is not None and inputs is not self._inputs:
        raise ValueError,"this tree is already using a different set of inputs";
    else:
      self._inputs = inputs or self.array.spigots(flag_bit=1);
    
  def inputs (self):
    return self._inputs;

class SolveTree (_BaseTree):
  def __init__ (self,ns,predict,array=None,observation=None,residuals=None):
    _BaseTree.__init__(self,ns,array,observation);
    self._predict = predict;
    self._make_residuals = residuals;
    
  def outputs (self,inputs=None):
    # figure out our inputs
    self.set_inputs(inputs);
    # select output node type
    if self._make_residuals:
      outputs = self.ns.residual;
    else:
      outputs = self._inputs;
    # now initialize our tree
    reqseq = self._outputs = self.ns.reqseq;
    if not reqseq(*self.array.ifrs()[0]).initialized():
      # create solver node ahead of time
      solver = self.solver() << Meq.Solver();
      self._solver_name = solver.name;
      # create condeqs and request sequencers
      for p,q in self.array.ifrs():
        inp  = self._inputs(p,q);
        pred = self._predict(p,q);
        self.ns.ce(p,q) << Meq.Condeq(inp,pred);
        # output is either spigot itself, or uncorrected residuals.
        # in the latter case, we also have to define them
        if outputs is not self._inputs:
          outp = outputs(p,q) << inp - pred;
        else:
          outp = inp;
        # attach output to request sequencer
        reqseq(p,q) << Meq.ReqSeq(solver,outp,result_index=1);
        # adjust number of parents for node cache
        pred.set_options(cache_num_active_parents=1);
      # create optimal poll order for condeqs, for efficient parallelization
      # (i.e. poll child 1:2, 3:4, 5:6, ..., 13:14,
      # then the rest)
      cpo = [];
      for i in range(len(self.array.stations())/2):
        (p,q) = self.array.stations()[i*2:(i+1)*2];
        cpo.append(self.ns.ce(p,q).name);
      # add condeqs to solver
      solver.set_options(child_poll_order=cpo);
      solver.add_children(*[self.ns.ce(p,q) for p,q in self.array.ifrs()]);
      
    # our output node is the reqseq
    return reqseq;
    
  def solver (self):
    """Returns solver node for this tree""";
    return self.ns.solver;
      
  def define_solve_job (self,jobname,jobid,solvables,tile_sizes=[1,10,100],vdm=None):
    # make sure solvables is a list of names
    def namify (arg):
      if isinstance(arg,str):
        return arg;
      elif is_node(arg):
        return arg.name;
      else:
        raise TypeError,"'solvables' contains an object of illegal type '"+str(type(arg))+"'";
    solvables = [ namify(x) for x in solvables ];

    # init option vars
    tiling = 'tiling_'+jobid;
    solver_opts = '_solver_'+jobid;
    globals()[tiling] = 1;
    
    # figure out VDM name
    vdm = vdm or Context.vdm;
    if vdm is None:
      vdm = 'VisDataMux';
    elif is_node(vdm):
      vdm = vdm.name;
    elif not isinstance(vdm,str):
      raise TypeError,"'vdm' argument must be a node or a node name";

    # define TDL job to run this solve job
    def run_solve_job (mqs,parent,**kw):
      # put together list of enabled solvables
      Utils.run_solve_job(mqs,solvables,
          solver_node=self.ns.solver.name,
          vdm_node=vdm,
          tiling=globals()[tiling],
          options=getattr(Utils,solver_opts));

    # define submenu
    TDLRuntimeMenu(jobname,
      TDLOption(tiling,"Tile size",tile_sizes,more=int),
      TDLMenu("Solver options",*Utils.solver_options(solver_opts)),
      TDLJob(run_solve_job,"Run solution")
    );
    
def vis_inspector (outnode,visnodes,array=None,bookmark=True):
  array = array or Context.array;
  if not array:
    raise ValueError,"array not specified in global Meow.Context, or in this function call";
  outnode << \
    Meq.Composer(
      dims=(len(array.ifrs()),2,2),
      plot_label=[ "%s-%s"%(p,q) for p,q in array.ifrs() ],
      mt_polling=True,
      *[ outnode(p,q) << Meq.Mean(visnodes(p,q),reduction_axes="freq")
         for p,q in array.ifrs() ]
    );
  if bookmark is True:
    bookmark = outnode.name;
  if bookmark:
    Bookmarks.Page(bookmark).add(outnode,viewer="Collections Plotter");
  return outnode;
    

def jones_inspector (outnode,jones,array=None,bookmark=True):
  array = array or Context.array;
  if not array:
    raise ValueError,"array not specified in global Meow.Context, or in this function call";
  outnode << \
    Meq.Composer(
      dims=(len(array.stations()),2,2),
      plot_label=[ str(p) for p in array.stations() ],
      mt_polling=True,
      *[ outnode(p) << Meq.Mean(jones(p),reduction_axes="freq")
         for p in array.stations() ]
    );
  if bookmark is True:
    bookmark = outnode.name;
  if bookmark:
    Bookmarks.Page(bookmark).add(outnode,viewer="Collections Plotter");
  return outnode;  
    
    
      
def make_sinks (ns,outputs,array=None,
                post=None,
                vdm=None,
                spigots=True,
                flag_bit=1,output_col='DATA',**kw):
  array = array or Context.array;
  if not array:
    raise ValueError,"array not specified in global Meow.Context, or in this function call";
  # make sinks
  sink = array.sinks(children=outputs,flag_bit=flag_bit,output_col=output_col,**kw);
  # make vdm
  if vdm is None:
    vdm = ns.VisDataMux;
  elif not is_node(vdm):
    raise TypeError,"'vdm' argument should be a node";

  # check 'post' argument, if it's a list, make a ReqMux called vdm:post
  # to process these guys
  if isinstance(post,(list,tuple)):
    post = vdm('post') << Meq.ReqMux(*post);
  elif not is_node(post):
    raise TypeError,"'post' argument should be a node or a list of nodes";

  # now make the vdm
  vdm << Meq.VisDataMux(post=post,*[sink(p,q) for p,q in array.ifrs()]);
  if spigots:
    if spigots is True:
      spigots = array.spigots();
    vdm.add_stepchildren(*[spigots(p,q) for p,q in array.ifrs()]);

  return vdm;
      
