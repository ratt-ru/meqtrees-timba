#!/usr/bin/python

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file, assign them to a FITSImage, and then solve for
#  the maximum position.

#  It solves for all the x hand and y hand beams separately

# History:
# - 23 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random
import os

from string import split, strip
from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
import Meow.Bookmarks

# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,31);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# default flux
I = 1; Q = .0; U = .0; V = .0

#LM = []
#for i in range(10):
#  l = random.uniform(-0.01,0.01)
#  m = random.uniform(-0.01,0.01)
#  flux = random.randint(1,10)
#  source_parms = (l,m,float(flux))
#  LM.append(source_parms)

# we'll put the sources on a grid (positions relative to beam centre in radians)
#LM = [(-0.007,-0.007),(-0.007,0),(-0.007,0.007),
#      ( 0,-0.007),( 0,0),( 0,0.007),
#      ( 0.007,-0.007),( 0.007,0),( 0.007,0.007)];

# compounder produces NaNs at 
# LM positions [(-0.007,0.0), (0.0,0.0), (0.007,0.0)]

# compounder handles these sources
LM = [(-0.007,-0.007),(-0.007,0.007),
      ( 0,-0.007),( 0,0.007),
      ( 0.007,-0.007),( 0.007,0.007)];

SOURCES = range(len(LM));       # 0...N-1

########################################################
def _define_forest(ns):  

# read in beam images
  home_dir = os.environ['HOME'] + '/Timba/WH/contrib/AGW'
  # read in beam data

  infile_name_re_yx = home_dir + '/veidt_stuff/yx_real.fits'
  infile_name_im_yx = home_dir + '/veidt_stuff/yx_imag.fits'
  infile_name_re_yy = home_dir + '/veidt_stuff/yy_real.fits'
  infile_name_im_yy = home_dir + '/veidt_stuff/yy_imag.fits' 
  ns.image_re_yx << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
  ns.image_im_yx << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
  ns.image_re_yy << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
  ns.image_im_yy << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

  ns.im_sq_y << ns.image_re_yy * ns.image_re_yy + ns.image_im_yy * ns.image_im_yy + ns.image_re_yx * ns.image_re_yx + ns.image_im_yx * ns.image_im_yx
  ns.im_y << Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max << Meq.Max(ns.im_y)

  ns.beam_yx << Meq.ToComplex(ns.image_re_yx, ns.image_im_yx) / ns.im_y_max
  ns.beam_yy << Meq.ToComplex(ns.image_re_yy, ns.image_im_yy) / ns.im_y_max

  infile_name_re_xx = home_dir + '/veidt_stuff/xx_real.fits'
  infile_name_im_xx = home_dir + '/veidt_stuff/xx_imag.fits'
  infile_name_re_xy = home_dir + '/veidt_stuff/xy_real.fits'
  infile_name_im_xy = home_dir + '/veidt_stuff/xy_imag.fits'
  ns.image_re_xx << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
  ns.image_im_xx << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)
  ns.image_re_xy << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
  ns.image_im_xy << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)

  ns.im_sq_x << ns.image_re_xx * ns.image_re_xx + ns.image_im_xx * ns.image_im_xx + ns.image_re_xy * ns.image_re_xy + ns.image_im_xy * ns.image_im_xy
  ns.im_x << Meq.Sqrt(ns.im_sq_x)
  ns.im_x_max << Meq.Max(ns.im_x)

  ns.beam_xx << Meq.ToComplex(ns.image_re_xx, ns.image_im_xx) / ns.im_x_max
  ns.beam_xy << Meq.ToComplex(ns.image_re_xy, ns.image_im_xy) / ns.im_x_max

  # I think the following order is correct!
  ns.E_beam << Meq.Matrix22(ns.beam_xx, ns.beam_xy,ns.beam_yx, ns.beam_yy)

  # resampler for the beam
  ns.resampler_E << Meq.Resampler(ns.E_beam, dep_mask=0xff)

# OK - we have E Jones - now observe sources

 # first set up nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));

  # define source e-Jones matrices
  for src in SOURCES:
    l,m = LM[src];
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # define source brightness B0 (unprojected)
#   ns.B0(src) << 0.5 * Meq.Matrix22(flux+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),flux-Q)
    ns.B0(src) << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q)
    # don't really need to use the following for a point source
    ns.B(src) << ns.B0(src) / n;
    ns.lm(src) << Meq.Composer(l,m)

    ns.E(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_E],common_axes=[hiid('l'),hiid('m')]) 
    ns.Et(src) << Meq.ConjTranspose(ns.E(src)) 

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
    # and sum them up via an Add node
    predict = ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]);
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
      tile_size        = 40,
      selection = record(channel_start_index=0,
                             channel_end_index=0,
                             channel_increment=1,
                             selection_string='')
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


if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
