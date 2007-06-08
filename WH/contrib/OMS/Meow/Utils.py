from Timba.TDL import *
from Timba.Meq import meq
import numarray
import math
import random
import Meow

input_column = output_column = imaging_column = None;
tile_size = None;
ddid_index = None;
ms_channels = None;
msname = '';
ms_write_flags = False;
ms_input_flag_bit = 1;
ms_has_output = False;

def include_ms_options (
    has_input=True,
    has_output=True,
    tile_sizes=[1,5,10,20,30,60],
    ddid=[0,1],
    channels=None,
    flags=False
  ):
  """Instantiates MS input/output options""";
  TDLRuntimeOptions(*ms_options(has_input,has_output,tile_sizes,ddid,channels,flags));

def ms_options (
    has_input=True,
    has_output=True,
    tile_sizes=[1,5,10,20,30,60],
    ddid=[0,1],
    channels=None,
    flags=False
  ):
  """Returns list of MS input/output options""";
  ms_list = filter(lambda name:name.endswith('.ms') or name.endswith('.MS'),os.listdir('.'));
  if not ms_list:
    ms_list = [ "no MSs found" ];
  opts = [ TDLOption('msname',"MS",ms_list) ];
  if has_input:
    opts.append(TDLOption('input_column',"Input MS column",["DATA","MODEL_DATA","CORRECTED_DATA"],default=0));
  if has_output:
    global ms_has_output;
    ms_has_output = True;
    opts.append(TDLOption('output_column',"Output MS column",["DATA","MODEL_DATA","CORRECTED_DATA",None],default=2));
  if tile_sizes:
    opts.append(TDLOption('tile_size',"Tile size (timeslots)",tile_sizes,more=int));
  if ddid:
    opts.append(TDLOption('ddid_index',"Data description ID",ddid,more=int,
      doc="""If the MS contains multiple spectral windows, etc., then use this option to select different DATA_DESCRIPTION_IDs. Default is 0."""));
  if channels:
    opts.append(TDLOption('ms_channels',"Channel selection",channels));
  if flags:
    opts.append(TDLOption('ms_write_flags',"Write flags to output",False));
  return opts;
  
imaging_npix = 256;
imaging_cellsize = '1arcsec';
imaging_arcmin = None;
imaging_channels = [32,1,1];
imaging_channels_specified = False;

def include_imaging_options (npix=None,arcmin=5,cellsize=None,channels=None):
  """Instantiates imager options""";
  TDLRuntimeOptions(*imaging_options(npix,arcmin,cellsize,channels));

def imaging_options (npix=None,arcmin=5,cellsize=None,channels=None):
  """Instantiates imager options""";
  opts = [
    TDLOption('imaging_mode',"Imaging mode",["mfs","channel"]),
    TDLOption('imaging_weight',"Imaging weights",["natural","uniform","briggs"]),
    TDLOption('imaging_stokes',"Stokes parameters to image",["I","IQUV"]) 
  ];
  if npix:
    if not isinstance(npix,(list,tuple)):
      npix = [ npix ];
    opts.append(TDLOption('imaging_npix',"Image size, in pixels",npix,more=int));
  if arcmin:
    if cellsize:
      raise ValueError,"include_imaging_options: specify cellsize or arcmin, not both";
    if not isinstance(arcmin,(list,tuple)):
      arcmin = [ arcmin ];
    opts.append(TDLOption('imaging_arcmin',"Image size, in arcmin",arcmin,more=float));
  elif cellsize:
    if not isinstance(cellsize,(list,tuple)):
      cellsize = [ cellsize ];
    opts.append(TDLOption('imaging_cellsize',"Pixel size",cellsize,more=str));
  if channels:
    opts.append(TDLOption('imaging_channels',"Imaging channels selection",channels));
    imaging_channels_specified = True;
  def job_make_image (mqs,parent,**kw):
    make_dirty_image();
  if ms_has_output:
    opts.append(TDLJob(job_make_image,"Make image from MS output column"));
  else:
    opts.append(TDLOption('imaging_column',"MS column to image",["DATA","MODEL_DATA","CORRECTED_DATA"]));
    opts.append(TDLJob(job_make_image,"Make image"));
  return opts;  
  

source_table = "sources.mep";
mep_table = "calib.mep";

def get_source_table ():
  return msname + "/" + source_table;

def get_mep_table ():
  return msname + "/" + mep_table;

_solver_opts = dict(
  debug_level  = 0,
  colin_factor = 1e-6,
  lm_factor    = .001,
  balanced_equations = False,
  epsilon      = 1e-4,
  num_iter     = 30,
  convergence_quota = 0.8
);

_solver_opts = {};

def solver_options (optionset='_solver_opts',namespace=None):
  """Returns list of solver options.
  Default places options into dict at Meow.Utils._solver_opts. To make another set of options,
  supply a different optionset.""";
  optionset += '.';
  return [
    TDLOption(optionset+'debug_level',"Solver debug level",[0,1,10],namespace=namespace),
    TDLOption(optionset+'colin_factor',"Collinearity factor",[1e-8,1e-6,1e-3,1e-1],default=1,more=float,namespace=namespace),
    TDLOption(optionset+'lm_factor',"Initial LM factor",[1,.1,.01,.001],default=3,more=float,namespace=namespace),
    TDLOption(optionset+'balanced_equations',"Assume balanced equations",False,namespace=namespace),
    TDLOption(optionset+'epsilon',"Convergence threshold",[.01,.001,.0001,1e-5,1e-6],default=2,more=float,namespace=namespace),
    TDLOption(optionset+'num_iter',"Max iterations",[10,30,50,100,1000],default=1,more=int,namespace=namespace),
    TDLOption(optionset+'convergence_quota',"Subtiling convergence quota",[.8,.9,1.],namespace=namespace) \
  ];

def parameter_options ():
  return [
    TDLOption('use_previous',"Reuse solution from previous time interval",True,
    doc="""If True, solutions for successive time domains will start with
  the solution for a previous domain. Normally this speeds up convergence; you
  may turn it off to re-test convergence at each domain."""),
    TDLOption('use_mep',"Reuse solutions from MEP table",True,
    doc="""If True, solutions from the MEP table (presumably, from a previous
  run) will be used as starting points. Turn this off to solve from scratch.""")
 ];

def create_solver_defaults (solvables,options=None):
  global _solver_opts;
  opts = dict(_solver_opts);
  if options:
    opts.update(options);
  print opts;
  # copy all options into solver defaults with the same name
  solver_defaults = record(**opts);
  # additionally, set epsilon_deriv
  solver_defaults.epsilon_deriv      = opts["epsilon"];
  solver_defaults.save_funklets    = True
  solver_defaults.last_update      = True
  solver_defaults.solvable         = record(command_by_list=(record(name=solvables,
                                            state=record(solvable=True)),
                                            record(state=record(solvable=False))))
  return solver_defaults

def set_node_state (mqs,node,fields_record):
  """helper function to set the state of a node specified by name or
  nodeindex""";
  rec = record(state=fields_record);
  if isinstance(node,str):
    rec.name = node;
  elif isinstance(node,int):
    rec.nodeindex = node;
  else:
    raise TypeError,'illegal node argument';
  # pass command to kernel
  mqs.meq('Node.Set.State',rec);
  pass

# various global MS I/O options
ms_output = True;
ms_queue_size = 500;
ms_selection = None;


def create_inputrec (tiling=None):
  global tile_size;
  global ddid_index;
  boioname = "boio."+msname+".predict."+str(tiling or tile_size);
  # if boio dump for this tiling exists, use it to save time
  if not ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    if input_column:
      rec.data_column_name = input_column;
    # use global tile_size setting if tiling not specified
    if not tiling:
      tiling = tile_size;
    if isinstance(tiling,(list,tuple)):
      if len(tiling) != 2:
        raise TypeError,"tiling: 2-list or 2-tuple expected";
      (tile_segments,tile_size) = tiling;
      if tile_segments is not None:
        rec.tile_segments    = tile_segments;
      if tile_size is not None:
        rec.tile_size        = tile_size;
    else:  
      rec.tile_size = tiling;
    rec.selection = ms_selection or record();
    if ms_channels is not None:
      rec.selection.channel_start_index = ms_channels[0];
      rec.selection.channel_end_index = ms_channels[1];
      if len(ms_channels) > 2:
        rec.selection.channel_increment = ms_channels[2];
    rec.selection.ddid_index = ddid_index;
    rec = record(ms=rec);
  rec.python_init = 'Meow.ReadVisHeader';
  rec.mt_queue_size = ms_queue_size;
  return rec;

def create_outputrec ():
  rec = record();
  rec.mt_queue_size = ms_queue_size;
  if ms_output:
    rec.write_flags    = ms_write_flags;
    if output_column:
      rec.data_column = output_column;
    return record(ms=rec);
  else:
    rec.boio_file_name = "boio."+msname+".solve."+str(tile_size);
    rec.boio_file_mode = 'W';
    return record(boio=rec);
    
def create_io_request (tiling=None):
  req = meq.request();
  req.input  = create_inputrec(tiling);
  if ms_write_flags or output_column is not None:
    req.output = create_outputrec();
  return req;
  
def phase_parm (tdeg,fdeg):
  """helper function to create a t/f parm for phase, including constraints.
  Placeholder until Maaijke implements periodic constraints.
  """;
  polc = meq.polc(numarray.zeros((tdeg+1,fdeg+1))*0.0,
            scale=array([3600.,8e+8,0,0,0,0,0,0]));
  shape = [tdeg+1,fdeg+1];
  # work out constraints on coefficients
  # maximum excursion in freq is pi/2
  # max excursion in time is pi/2
  dt = .2;
  df = .5;
  cmin = [];
  cmax = [];
  for it in range(tdeg+1):
    for jf in range(fdeg+1):
      mm = math.pi/(dt**it * df**jf );
      cmin.append(-mm);
      cmax.append(mm);
  cmin[0] = -1e+9;
  cmax[0] = 1e+9;
  return Meq.Parm(polc,shape=shape,real_polc=polc,node_groups='Parm',
                  constrain_min=cmin,constrain_max=cmax,
                  table_name=get_mep_table());


def perturb_parameters (mqs,solvables,pert="random",
                        absolute=False,random_range=[0.2,0.3],constrain=None):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if absolute:  # absolute pert value given
      polc.coeff[0,0] += pert;
    elif pert == "random":  # else random pert
      polc.coeff[0,0] *= 1 + random.uniform(*random_range)*random.choice([-1,1]);
    else: # else perturb in relative terms
      polc.coeff[0,0] *= (1 + pert);
    parmstate = record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=not use_mep);
    if constrain is not None:
      parmstate.constrain = constrain;
    set_node_state(mqs,name,parmstate);
  return solvables;
    
def reset_parameters (mqs,solvables,value=None,use_table=False,reset=False):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[()] = value;
    reset_funklet = reset or not (use_table or use_mep);
    set_node_state(mqs,name,record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=reset_funklet));
  return solvables;

def run_solve_job (mqs,solvables,tiling=None,solver_node="solver",vdm_node="VisDataMux",
                   options=None):
  """common helper method to run a solution with a bunch of solvables""";
  # set solvables list in solver
  solver_defaults = create_solver_defaults(solvables,options=options)
  set_node_state(mqs,solver_node,solver_defaults)

  req = create_io_request(tiling);
  
  mqs.execute(vdm_node,req,wait=False);
  pass
  
def make_dirty_image (npix=None,cellsize=None,arcmin=None,channels=None,**kw):
  """Runs glish script to make an image
  npix is image size, in pixels
  cellsize is pixel size, as an aips++ Measures string (e.g. "0.5arcsec")
  arcmin is image size, in arcminutes. Either cellsize or arcmin must be 
        specified, but not both.
  """;
  col = output_column or imaging_column;
  if not col:
    raise ValueError,"make_dirty_image: output column not set up";
  if not msname:
    raise ValueError,"make_dirty_image: MS not set up";
  npix = (npix or imaging_npix);
  arcmin = (arcmin or imaging_arcmin);
  if arcmin is not None:
    cellsize = str(float(arcmin*60)/npix)+"arcsec";
  import os
  import os.path
  # if explicit channels are specified, use them 
  if channels:
    nchan,chanstart,chanstep = channels;
  # else if MS channels were specified use them
  elif ms_channels and not imaging_channels_specified:
    nchan = ms_channels[1]-ms_channels[0]+1;
    chanstart = ms_channels[0]+1;
    if len(ms_channels) > 2:
      chanstep = ms_channels[2];
    else:
      chanstep = 1;
  # else use the imaging_channels option
  else:
    nchan,chanstart,chanstep = imaging_channels;
  script_name = os.path.join(Meow._meow_path,'make_dirty_image.g');
  script_name = os.path.realpath(script_name);  # glish don't like symlinks...
  args = [ 'glish','-l',
    script_name,
    col,
    'ms='+msname,'mode='+imaging_mode,
    'weight='+imaging_weight,'stokes='+imaging_stokes,
    'npix='+str(npix),
    'cellsize='+(cellsize or imaging_cellsize),
    'nchan='+str(nchan),
    'chanstart='+str(chanstart),    
    'chanstep='+str(chanstep)
  ];
  print args;
  os.spawnvp(os.P_NOWAIT,'glish',args);
  

