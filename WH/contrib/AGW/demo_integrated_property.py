#!/usr/bin/python

# demonstrates the error: node 'E:0': 'integrated' property of child 
# results is not uniform (while getting result for request ev.0.0.0.1.1)

import math
import random

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,31);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# source flux (same for all sources)
#I = 1; Q = .2; U = .2; V = .2;
I = 1; Q = .0; U = .0; V = .0;

# location of 'phased up' beam
BEAM_LM = [(0.0,0.0)]
# we'll put the sources on a grid (positions relative to beam centre in radians)
LM = [(0.001,0)]
SOURCES = range(len(LM));       # 0...N-1

########################################################
def _define_forest(ns):  

# get the position where we wish to form a beam 
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam  << Meq.Parm(l_beam,node_groups='Parm')
  ns.m_beam  << Meq.Parm(m_beam,node_groups='Parm')
  ns.beam_pos << Meq.Composer(ns.l_beam,ns.m_beam)

# read in beam image (only need one to demo the problem)
  BEAMS = range(0,1)
  infile_name_re_x = 'demo_beam.fits'
  infile_name_im_x = 'demo_beam.dits'
  infile_name_re_y = 'demo_beam.fits'
  infile_name_im_y = 'demo_beam.fits'
  ns.image_re_x << Meq.FITSImage(filename=infile_name_re_x,cutoff=1.0,mode=2)
  ns.image_im_x << Meq.FITSImage(filename=infile_name_im_x,cutoff=1.0,mode=2)
  ns.image_re_y << Meq.FITSImage(filename=infile_name_re_y,cutoff=1.0,mode=2)
  ns.image_im_y << Meq.FITSImage(filename=infile_name_im_y,cutoff=1.0,mode=2)

  ns.beam_x << Meq.ToComplex(ns.image_re_x, ns.image_im_x)
  ns.beam_y << Meq.ToComplex(ns.image_re_y, ns.image_im_y)
  ns.resampler_x << Meq.Resampler(ns.beam_x, dep_mask=0xff)
  ns.resampler_y << Meq.Resampler(ns.beam_y, dep_mask=0xff)

# now create a source and observe it
# nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));

  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);

  # source l,m,n-1 vectors
  for src in SOURCES:
    l_off,m_off = LM[src];
    l = l_beam + l_off
    m = m_beam + m_off
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # and the projected brightness...
    ns.B(src) << ns.B0 / n;
    ns.lm_offset(src) << Meq.Composer(l, m)
    ns.voltage_x(src) <<Meq.Compounder(children=[ns.lm_offset(src),ns.resampler_x],common_axes=[hiid('l'),hiid('m')])
    ns.voltage_y(src) <<Meq.Compounder(children=[ns.lm_offset(src),ns.resampler_y],common_axes=[hiid('l'),hiid('m')])

    ns.E(src) << Meq.Matrix22(ns.voltage_x(src), 0.0+0.0j, ns.voltage_y(src), 0.0+0.0j)
    ns.Et(src) << Meq.ConjTranspose(ns.E(src));

  # define K-jones matrices
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));

  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
    predict = ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES])
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);

########################################################################

def _test_forest(mqs,parent):

# now observe sources
  req = meq.request();
  req.input = record(
    ms = record(
      ms_name          = 'TEST_XNTD_30_960.MS',
      tile_size        = 40
    ),
    python_init = 'Meow.ReadVisHeader'
  );
  req.output = record(
    ms = record(
      data_column = 'CORRECTED_DATA'
    )
  );
  # execute
  mqs.execute('vdm',req,wait=False);

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
