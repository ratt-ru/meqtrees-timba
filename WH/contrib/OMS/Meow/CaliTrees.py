from Timba.TDL import *
import Context
import Jones
import Utils

def create_spigots (spigots,ifrs,flag_bit=1):
  for p,q in ifrs:
    spigots(p,q) << Meq.Spigot(station_1_index=p-1,
                               station_2_index=q-1,
                               flag_bit=flag_bit,
                               input_col='DATA');
  return spigots;

def create_sinks (sinks,children,ifrs,flag_bit=1):
  for p,q in ifrs:
    sinks(p,q) << Meq.Sink(children=children(p,q),
                           station_1_index=p-1,
                           station_2_index=q-1,
                           flag_bit=flag_bit,
                           corr_index=[0,1,2,3],
                           flag_mask=-1,
                           output_col='DATA',
                           );
  return sinks;


TDLCompileOption('output_type',"Output visibilities",["residual","corrected"]);

def define_solve_correct_tree (ns,predict,
    array=None,observation=None,
    corrections=[],
    inspect_output=True):
  # check that array and observation have been set up
  array = array or Context.array;
  observation = observation or Context.observation;
  if not array or not observation:
    raise ValueError,"array or observation not specified in global Meow.Context, or in this function call";
  # create spigots for input data
  spigot = create_spigots(ns.spigot,array.ifrs());
  # create solver node ahead of time
  ns.solver << Meq.Solver();
  # select output node 
  if output_type == "residual":
    output_nodes = ns.residual;
  else:
    output_nodes = spigot;
  # create condeqs, residuals and request sequencers
  for p,q in array.ifrs():
    spig = spigot(p,q);
    pred = predict(p,q);
    ns.ce(p,q) << Meq.Condeq(spig,pred);
    # output is either spigot itself, or uncorrected residuals.
    # in the latter case, we also have to define them
    if output_nodes is ns.residual:
      output = output_nodes(p,q) << spig - pred;
    else:
      output = spig;
    # attach output to request sequencer
    ns.reqseq(p,q) << Meq.ReqSeq(ns.solver,output,result_index=1);
    # adjust number of parents for node cache
    pred.set_options(cache_num_active_parents=pred.num_parents()-1);
    
  # create optimal poll order for condeqs, for efficient parallelization
  # (i.e. poll child 1:2, 3:4, 5:6, ..., 13:14,
  # then the rest)
  cpo = [];
  for i in range(len(array.stations())/2):
    (p,q) = array.stations()[i*2:(i+1)*2];
    cpo.append(ns.ce(p,q).name);
  # add condeqs to solver
  ns.solver.set_options(child_poll_order=cpo);
  ns.solver.add_children(*[ns.ce(p,q) for p,q in Context.array.ifrs()]);

  # now apply corrections in the given order
  output_nodes = ns.reqseq;
  if corrections:
    output_nodes = Jones.apply_correction(ns.corrected,output_nodes,corrections,array.ifrs());

  # create output inspector, if needed
  if inspect_output:
    inspector = ns.inspect_output << Meq.Composer(
      dims=(len(array.ifrs()),2,2),
      *[ ns.inspect_output(p,q) << Meq.Mean(output_nodes(p,q),reduction_axes="freq")
          for p,q in array.ifrs()
       ]
    );
  else:
    inspector = None;
    
  # create sinks and visdatamux
  sink = create_sinks(ns.sink,output_nodes,Context.array.ifrs());
  
  vdm = ns.VisDataMux << Meq.VisDataMux(post=inspector,*[ns.sink(p,q) for p,q in array.ifrs()]);
  vdm.add_stepchildren(*[ns.spigot(p,q) for p,q in array.ifrs()]);
  
  return vdm;

def define_solve_job (jobname,jobid,solvables,tile_sizes=[1,10,100]):
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

  # define TDL job to run this solve job
  def run_solve_job (mqs,parent,**kw):
    # put together list of enabled solvables
    Utils.run_solve_job(mqs,solvables,tiling=globals()[tiling],options=getattr(Utils,solver_opts));
    
  # define submenu
  TDLRuntimeMenu(jobname,
    TDLOption(tiling,"Tile size",tile_sizes,more=int),
    TDLMenu("Solver options",*Utils.solver_options(solver_opts)),
    TDLJob(run_solve_job,"Run solution")
  );
