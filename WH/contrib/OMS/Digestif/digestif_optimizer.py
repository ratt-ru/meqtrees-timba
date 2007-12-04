from Timba.TDL import *
from Timba.Meq import meq

import Meow
import math
import os
from Timba import mequtils

Settings.forest_state.cache_policy = 1;

TDLCompileOption("pointing_nsteps","Number of pointing steps along one radius",[15],more=int);
TDLCompileOption("pointing_dlm","Size of one pointing step, in arcmin",[2],more=float);
TDLCompileOption("grid_nsteps","Number of grid steps along one radius",[45],more=int);
TDLCompileOption("grid_dlm","Size of one grid step, in arcmin",[1],more=float);
TDLCompileOption("table_name","Weights table",TDLDirSelect("*.fmep *.mep",default="weights.fmep",exist=False));

TDLCompileMenu("Element beam patterns",
  TDLOption("elem_nx","Number of elements",[1,2,20],more=int),
  TDLOption("elem_filename_x","Filenames",["elementbeam_%d.bin"],more=str)
);

TDLCompileMenu("Gaussian beam fit options",
    TDLOption("gauss_fwhm","FWHM, in arcmin",[30],more=float));
      
TDLCompileOption("out_filename","Output filename for phased beams",
                  TDLFileSelect("*.fits",default="digestif-beam.fits",exist=False));
  
ARCMIN = math.pi/(180*60);

def _define_forest (ns,**kwargs):
  ELEMS = range(elem_nx);
  # - axes time/freq are used to represent the phasing-up directions
  # - axes l/m are used to represent the resulting beam patterns
  # This is a temporary kludge, since the current Parm does not allow tiling
  # in anything except time/freq. The proper solution is to use l/m for
  # the phasing-up directions, and l1/m1 for the beam patterns
  mequtils.add_axis('l');
  mequtils.add_axis('m');
  # create nodes to represent the beam patterns
  for p in ELEMS:
    # beam pattern, on a fixed l/m grid determined by input file
    b = ns.beam_unnormalized(p) << Meq.PyNode(class_name="DigestifElementNode",
                      module_name='DigestifElement',
                      file_name=elem_filename_x%p,cache_policy=100,
                      xaxis='l',yaxis='m',freqaxis='freq');
    # normalize gain (make it 1 in max direction)
    ns.beam_max(p) << Meq.Max(Meq.Abs(b));
    ns.beam0(p) << b/ns.beam_max(p);
    # beam pattern resampled to requested l/m grid
    # we use a kludge here to get around a Resampler bug (bug 609):
    # if the resampler is passed a full 4D grid, it does resampling on the 
    # full grid, even if its child only returns a 2D (lm) grid. This is 
    # very wasteful, so we use an AxisFlipper to strip everything except lm from
    # the request given to the resampler.
    ns.beam(p) << Meq.PyNode(ns.beam_resampled(p) << Meq.Resampler(ns.beam0(p)),
                      class_name="AxisFlipper",
                      module_name='DigestifBeam',
                      in_axis_1='l',in_axis_2='m',
                      out_axis_1='l',out_axis_2='m');
    # weight parameter, function of time/freq (see kludge above)
    wr = ns.weight(p,'r') << Meq.Parm(1,tags="beam weight solvable",
                                        tiling=record(time=1,freq=1),
                                        table_name=table_name,save_all=True,
                                        use_mep=True,use_previous=False);
    wi = ns.weight(p,'i') << Meq.Parm(0,tags="beam weight solvable",
                                        tiling=record(time=1,freq=1),
                                        table_name=table_name,save_all=True,
                                        use_mep=True,use_previous=False);
    ns.weight(p) << Meq.ToComplex(wr,wi);
    # phased beams, function of time/freq (see kludge above) and l/m
    ns.weighted_beam(p) << ns.beam(p)*ns.weight(p);
    
  # nodes to compute resulting beam, optionally write to FITS
  out_beam = ns.phased_beam << Meq.Add(cache_policy=100,mt_polling=True,
                               cache_num_active_parents=1,
                               *[ns.weighted_beam(p) for p in ELEMS]);
  if out_filename:
    try: os.remove(out_filename); 
    except: pass;
    out_beam = ns.phased_beam_fits << Meq.FITSWriter(out_beam,filename=out_filename);
  Meow.Bookmarks.Page("Phased beam").add(ns.phased_beam);
    
  # make some bookmarks
  Meow.Bookmarks.make_node_folder("Element beams",
        [ns.beam(p) for p in ELEMS],nrow=2,ncol=2);
  Meow.Bookmarks.make_node_folder("Beam weights",
        [ns.weight(p) for p in ELEMS],nrow=2,ncol=2);
    
  # now make a tree to assign conjugate beam weights
  # we kludge this with a solver, this should solve in 1 iteration
  for p in ELEMS:
    # first, we need to take the incoming time/freq grid, turn it into l/m,
    # and resample the element patterns 
    ns.beam_tf(p) << Meq.PyNode(ns.beam_resampled_tf(p) << Meq.Resampler(ns.beam0(p)),
                      class_name="AxisFlipper",
                      module_name='DigestifBeam',
                      in_axis_1='time',in_axis_2='freq',
                      out_axis_1='l',out_axis_2='m');
    ns.condeq('conj',p) << Meq.CondEq(Meq.Conj(ns.beam_tf(p)),ns.weight(p));
  ns.solver('conj') << Meq.Solver(solvable=ns.weight.search(tags="solvable"),
                                  lm_factor=0,num_iter=3,convergence_quota=1,
                                  save_funklets=True,last_update=True,
                                  children=[ns.condeq('conj',p) for p in ELEMS]);
  # now make trees to compute the resulting beam patterns
  ns.reqseq('conj') << Meq.ReqSeq(ns.solver('conj'),out_beam);
  
  # now make a tree to fit optimized gaussian beams
  ns.l << Meq.Grid(axis="l");
  ns.m << Meq.Grid(axis="m");
  ns.l0 << Meq.Time();
  ns.m0 << Meq.Freq();
  ns.rad << Meq.Sqrt(Meq.Sqr(ns.l-ns.l0)+Meq.Sqr(ns.m-ns.m0));
  ns.gauss_a << 2*math.log(2)/(gauss_fwhm*ARCMIN);
  ns.gauss_beam << Meq.Exp(-ns.gauss_a*ns.rad);
  Meow.Bookmarks.Page("Gaussian beam").add(ns.gauss_beam);
  
  # and fit the weights
  ns.condeq('gauss') << Meq.CondEq(ns.gauss_beam,ns.phased_beam);
  ns.solver('gauss') << Meq.Solver(solvable=ns.weight.search(tags="solvable"),
                                lm_factor=0,num_iter=5,convergence_quota=1,
                                save_funklets=True,last_update=True,
                                children=[ns.condeq('gauss')]);
  ns.diff('gauss') << Meq.Subtract(ns.gauss_beam,out_beam);
  ns.reqseq('gauss') << Meq.ReqSeq(ns.solver('gauss'),ns.diff('gauss'));
  Meow.Bookmarks.Page("Gaussian beam residuals").add(ns.diff('gauss'));

  ns.reqseq('recompute') << Meq.ReqSeq(ns.diff('gauss'));

def compute_cells (rows=None):
  grad = (grid_nsteps+.5)*grid_dlm*ARCMIN;
  gn   = grid_nsteps*2+1;
  prad = (pointing_nsteps+.5)*pointing_dlm*ARCMIN;
  pn   = pointing_nsteps*2+1;
  if rows is None:
    domain = meq.gen_domain(time=[-prad,prad],freq=[-prad,prad],l=[-grad,grad],m=[-grad,grad]);
    cells = meq.gen_cells(domain,num_time=pn,num_freq=pn,num_l=gn,num_m=gn);
  else:
    cells = [];
    for i0 in range(-pointing_nsteps,pointing_nsteps+1,rows):
      i1 = min(pointing_nsteps,i0+rows-1);
      t0 = (i0-0.5)*pointing_dlm*ARCMIN;
      t1 = (i1+0.5)*pointing_dlm*ARCMIN;
      domain = meq.gen_domain(time=[t0,t1],freq=[-prad,prad],l=[-grad,grad],m=[-grad,grad]);
      cells.append(meq.gen_cells(domain,num_time=(i1-i0+1),num_freq=pn,num_l=gn,num_m=gn));
  return cells;

def _job_1_compute_conjugate_beams (mqs,parent,**kwargs):
  from Timba.Meq import meq
  os.system("rm -fr "+table_name);
  cells = compute_cells();
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq:conj',request);

def _job_2_fit_gaussian_beams (mqs,parent,**kwargs):
  os.system("rm -fr "+table_name);
  from Timba.Meq import meq
  cells = compute_cells(solve_nrow);
  if not solve_nrow:
    cells = [cells];
  for c in cells:
    mqs.execute('solver:gauss',meq.request(c,rqtype='ev'));
  cells = compute_cells();
  mqs.execute('diff:gauss',meq.request(cells,rqtype='ev'));
 
def _job_3_recompute_phased_beam (mqs,parent,**kwargs):
  os.system("rm -fr "+table_name);
  from Timba.Meq import meq
  cells = compute_cells();
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq:recompute',request);

TDLRuntimeJob(_job_1_compute_conjugate_beams,"compute phase-conjugate beams");

TDLRuntimeMenu("Fit gaussian beams",
  TDLOption("solve_nrow","Number of rows to solve for at once",[None,5],more=int,
      doc="""Use None to solve for all pointing directions simultaneously.
      With a large grid, you may not have enough memory for this, so use
      a low integer instead to do a stepwise solve."""),
  TDLJob(_job_2_fit_gaussian_beams,"fit gaussian beams"),
  TDLJob(_job_3_recompute_phased_beam,"recompute current phased beam")
);

