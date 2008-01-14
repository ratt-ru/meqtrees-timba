#
# Copyright (C) 2002-2007
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

# a script to generate a sequence of CLAR beam images as a
# function of time

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds

from make_multi_dim_request import *
 
import Meow.Bookmarks

# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("CLAR Beam",["beam_rot"],["AzEl"])
]);

# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
#Settings.forest_state.cache_policy = 100;

# get position of field centre RA DEC
TDLCompileMenu('Field Centre RA and DEC',
  TDLOption('fc_ra','RA of field centre (radians)',[0,1,2,3],more=float),
  TDLOption('fc_dec','DEC of field centre (radians)',[0,1,2,3],more=float),
);

# get telescope location for use in simulation
TDLCompileOption('telescope','Telescope Site',['DRAO','VLA'])

# do fast or slow calculation
TDLCompileOption('pre_rotate','Pre-Rotate L and M frame (fast method)',[True, False])

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;

# we  build up the mathematical expression of a CLAR power
# pattern using the formulae
# log16 =  (-1.0) * log(16.0)
# L,M give direction cosines wrt field centre in
# AzEl coordinate frame
# L_gain = (L * L) / (width * width)
# sin_factor = sqr(sin(field centre elevation))
# M_gain = (sin_factor * M * M ) / (width * width)
# power pattern = exp(log16 * (L_gain + M_gain))

# constant used in beam calculation
  ns.ln_16 << Meq.Constant(-2.7725887)

# CLAR HPBW of 3 arcmin at zenith = 0.00087266 radians 
  ns.HPBW << Meq.Constant(0.00087266)

# beam is centred in L,M grid
  ns.centre << Meq.Constant(0.0)

# create a MeqComposer containing ra dec position
  ns.RADec <<Meq.Composer(fc_ra, fc_dec)

# we create an AzEl node with an Observatory name
  ns.AzEl << Meq.AzEl(radec=ns.RADec, observatory=telescope)

# create a Parallactic angle node
  pa = ns.ParAngle << Meq.ParAngle(radec=ns.RADec, observatory = telescope)
# rotation matrix to go from AzEl to Ra,Dec L,M  
  ns.P << Meq.Matrix22(Meq.Cos(pa),-Meq.Sin(pa),Meq.Sin(pa),Meq.Cos(pa))

# get the elevation
  ns.El << Meq.Selector(ns.AzEl, index=1)

# get sine of elevation - used to get CLAR  beam broadening
  ns.sine_el << Meq.Sin(ns.El)

  # square this sine value
  ns.sine_el_sq << Meq.Sqr(ns.sine_el)

# create L and M axis nodes
  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

# attempt to de-rotate the beam in AzEl coordinates to sky coordinates
  if pre_rotate:
    ns.lm_pre_rot << Meq.Composer(laxis,maxis)    # returns an lm 2-vector

    ns.rot_lm << Meq.MatrixMultiply(ns.P,ns.lm_pre_rot);    # rotated lm
    ns.l_rot << Meq.Selector(ns.rot_lm,index=0)
    ns.m_rot << Meq.Selector(ns.rot_lm,index=1)
  
    ns.l_sq << Meq.Sqr(ns.l_rot - ns.centre)
    ns.m_sq << Meq.Sqr(ns.m_rot - ns.centre)
    ns.m_sq_sin << Meq.Multiply(ns.m_sq, ns.sine_el_sq)

# Add l and m gains
    ns.l_and_m_sq << Meq.Add(ns.l_sq, ns.m_sq_sin)
    ns.beam_rot << Meq.Exp((ns.l_and_m_sq * ns.ln_16) / Meq.Sqr(ns.HPBW))

  else:
    ns.l_sq << Meq.Sqr(laxis - ns.centre)
    ns.m_sq << Meq.Sqr(maxis - ns.centre)
    ns.m_sq_sin << Meq.Multiply(ns.m_sq, ns.sine_el_sq)

# Add l and m gains
    ns.l_and_m_sq << Meq.Add(ns.l_sq, ns.m_sq_sin)
    ns.exp_gain << Meq.Exp((ns.l_and_m_sq * ns.ln_16) / Meq.Sqr(ns.HPBW))

# attempt to de-rotate the beam in AzEl coordinates to sky coordinates
    ns.lm_pre_rot << Meq.Composer(laxis,maxis)    # returns an lm 2-vector

    ns.rot_lm << Meq.MatrixMultiply(ns.P,ns.lm_pre_rot);    # rotated lm
    ns.l_rot << Meq.Selector(ns.rot_lm,index=0)
    ns.m_rot << Meq.Selector(ns.rot_lm,index=1)
    ns.lm_rot << Meq.Composer(Meq.Grid(axis=0),Meq.Grid(axis=1),ns.l_rot,ns.m_rot)

    ns.resampler << Meq.Resampler(ns.exp_gain,dep_mask = 0xff)
    ns.beam_rot << Meq.Compounder(children=[ns.lm_rot,ns.resampler],common_axes=[hiid('l'),hiid('m')])

##################################################
def _test_forest (mqs,parent,wait=False):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;

# any large time range will do: we observe the changes in the beam
# pattern in timesteps of 2400s, or 40 min
  delta_t = 2400.0
  # Approx start of 2001
  t0 = 4485011731.14 - delta_t       
  t1 = t0 + delta_t

# here, any frequency range will do
  f0 = 800.0
  f1 = 1300.0

  m_range = [-0.0025,0.0025];
  l_range = [-0.0025,0.0025];
  lm_num = 31;
  counter = 0
  for i in range(12):
    t0 = t0 + delta_t
    t1 = t0 + delta_t
    request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],l_range,m_range], nr_cells = [1,1,lm_num,lm_num])
    counter = counter + 1
# execute request
    mqs.meq('Node.Execute',record(name='beam_rot',request=request),wait=False);
##################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
