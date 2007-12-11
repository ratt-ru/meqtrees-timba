from Timba.TDL import *
from Timba.Meq import meq
from Timba import pynode
import pyfits

import Meow
import math
import os
from Timba import mequtils

import DigestifBeam

Settings.forest_state.cache_policy = 1;

TDLCompileOption("pointing_nsteps","Number of pointing steps along one radius",[15],more=int);
TDLCompileOption("pointing_dlm","Size of one pointing step, in arcmin",[2],more=float);
TDLCompileOption("grid_nsteps","Number of grid steps along one radius",[45],more=int);
TDLCompileOption("grid_dlm","Size of one grid step, in arcmin",[1],more=float);
TDLCompileOption("table_name","Weights table",TDLDirSelect("*.fmep *.mep",default="weights.fmep",exist=False));

TDLCompileMenu("Element beam patterns",
  TDLOption("elem_n0","First element number",[0,1],more=int),
  TDLOption("elem_num","Number of elements",[1,2,20],more=int),
  TDLOption("elem_filename_x","Filenames",["elementbeam_%d.bin"],more=str)
);

TDLCompileMenu("Phase-conjugate beam fit options",
    TDLOption("conj_filename","Output filename for phase-conjugate beams",
              TDLFileSelect("*.beam",default="digestif-conj.beam",exist=False)));

TDLCompileMenu("Gaussian beam fit options",
    TDLOption("gauss_filename","Output filename for gaussian-fitted beams",
              TDLFileSelect("*.beam",default="digestif-gauss.beam",exist=False)),
    TDLOption("gauss_fwhm","FWHM, in arcmin",[30],more=float),
#    TDLOption("gauss_fwhm_solvable","Make FWHM solvable (won't work anyway)",False),
);
gauss_fwhm_solvable = False;

ARCMIN = math.pi/(180*60);

gridding = DigestifBeam.Gridding(pointing_nsteps,pointing_dlm,grid_nsteps,grid_dlm);

class WriteBeamImage (pynode.PyNode):
  """PyNode to write out a beam image""";
  def update_state (self,mystate):
    mystate('file_name','beam.fits');

  def get_result (self,request,*children):
    result = children[0];
    hdu = pyfits.PrimaryHDU(result.vellsets[0].value.real);
    hdulist = pyfits.HDUList([hdu]);
    hdulist.writeto("real-"+self.file_name+".fits",clobber=True);
    hdu = pyfits.PrimaryHDU(result.vellsets[0].value.imag);
    hdulist = pyfits.HDUList([hdu]);
    hdulist.writeto("imag-"+self.file_name+".fits",clobber=True);
    return result;

def _define_forest (ns,**kwargs):
  ELEMS = range(elem_n0,elem_n0+elem_num);
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

  # add up contributions of elements -- use nested trees for more efficient parallelization
  PF = 4; # parallelization factor -- max # of branches in one Add node
  # list of all beams to be added
  sums = [ ns.weighted_beam(p) for p in ELEMS ];
  depth = 1;
  while len(sums) > 1:
    new_sums = [];
    # name the sum nodes something sensible, and once we're down to the
    # upper level (one final sum), just call it "phased_beam"
    if len(sums) <= PF:
      out = ns.phased_beam;
    else:
      out = ns.phased_beam_sum(depth);
    # make Add nodes to add up PF branches at a time
    for i0 in range(0,len(sums),PF):
      i1 = min(i0+PF,len(sums));
      new_sums.append(out(i0) << Meq.Add(cache_policy=100,mt_polling=True,
                                         cache_num_active_parents=1,
                                         *sums[i0:i1]));
    sums = new_sums;
    depth += 1;
  out_beam = phased_beam = sums[0];
  Meow.Bookmarks.Page("Phased beam").add(phased_beam);

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

  # now make trees to write the resulting beam pattern to FITS and .beam files
  conj_beam = out_beam;
  if conj_filename:
    conj_beam = ns.writer('conj') << Meq.PyNode(conj_beam,
                      class_name="DigestifBeamWriterNode",module_name="DigestifBeam",
                      file_name=conj_filename);
    conj_beam = ns.image('conj') << Meq.PyNode(conj_beam,
                      class_name="WriteBeamImage",module_name=__file__,
                      file_name=conj_filename);
  # insert sequencer: first solve, then recompute & write
  ns.reqseq('conj') << Meq.ReqSeq(ns.solver('conj'),conj_beam);

  if gauss_fwhm_solvable:
    fwhm = ns.gauss_fwhm << Meq.Parm(gauss_fwhm,tags="fwhm solvable",
                                      tiling=record(time=1,freq=1),
                                      table_name=table_name,save_all=True,
                                      use_mep=True,use_previous=False,constrain_min=5.,constrain_max=45.);
  else:
    fwhm = gauss_fwhm;
  # now make a tree to fit optimized gaussian beams
  ns.l << Meq.Grid(axis="l");
  ns.m << Meq.Grid(axis="m");
  ns.l0 << Meq.Time();
  ns.m0 << Meq.Freq();
  ns.rad << Meq.Sqrt(Meq.Sqr(ns.l-ns.l0)+Meq.Sqr(ns.m-ns.m0));
  ns.gauss_a << (-2*math.log(2)/ARCMIN)/fwhm;
  ns.gauss_beam << Meq.Exp(ns.gauss_a*ns.rad);
  Meow.Bookmarks.Page("Gaussian beam").add(ns.gauss_beam);
  if gauss_fwhm_solvable:
    Meow.Bookmarks.Page("Gaussian beam FWHM").add(fwhm);

  # and fit the weights
  ns.condeq('gauss') << Meq.CondEq(ns.gauss_beam,phased_beam);
  ns.solver('gauss') << Meq.Solver(solvable=ns.condeq('gauss').search(tags="solvable"),
                                lm_factor=0,num_iter=5,convergence_quota=1,
                                save_funklets=True,last_update=True,
                                children=[ns.condeq('gauss')]);
  # and compute residuals
  ns.diff('gauss') << Meq.Subtract(ns.gauss_beam,out_beam);

  # now make trees to write the resulting beam pattern to FITS and .beam files
  gauss_beam = out_beam;
  if gauss_filename:
    gauss_beam = ns.writer('gauss') << Meq.PyNode(gauss_beam,
                      class_name="DigestifBeamWriterNode",module_name="DigestifBeam",
                      file_name=gauss_filename);
    gauss_beam = ns.image('gauss') << Meq.PyNode(gauss_beam,
                      class_name="WriteBeamImage",module_name=__file__,
                      file_name=gauss_filename);
  # insert sequencer: first solve, then recompute & write, then compute residuals
  ns.reqseq('gauss') << Meq.ReqSeq(ns.solver('gauss'),ns.diff('gauss'),gauss_beam);

  Meow.Bookmarks.Page("Gaussian beam residuals").add(ns.diff('gauss'));

  # add separate sequencer for simply recomputing the residuals
  ns.reqseq('recompute') << Meq.ReqSeq(ns.diff('gauss'));

def _job_1_compute_conjugate_beams (mqs,parent,**kwargs):
  from Timba.Meq import meq
  os.system("rm -fr "+table_name);
  cells = gridding.compute_cells();
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq:conj',request);

def _job_2_fit_gaussian_beams (mqs,parent,**kwargs):
  os.system("rm -fr "+table_name);
  from Timba.Meq import meq
  cells = gridding.compute_cells(solve_nrow);
  if not solve_nrow:
    cells = [cells];
  dom = 1;
  for c in cells:
    mqs.execute('solver:gauss',meq.request(c,rqid=meq.requestid(domain_id=dom)));
    dom += 1;
  cells = gridding.compute_cells();
  mqs.execute('diff:gauss',meq.request(cells,rqid=meq.requestid(domain_id=dom)));

def _job_3_recompute_phased_beam (mqs,parent,**kwargs):
  from Timba.Meq import meq
  cells = gridding.compute_cells();
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

