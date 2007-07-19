#!/usr/bin/python

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


# Short description:
#  A script to simulate daily variations in the gains of a focal plane array

# History:
# - 23 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random
import os

from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq

import Meow

from Meow import Bookmarks
from Meow import Utils

Utils.include_ms_options(tile_sizes=[30,48,60,96,192,480,960]);

TDLRuntimeMenu("Solver options",*Utils.solver_options());

# define antenna stuff
ANTENNAS = range(1,31);
xntd_list = [ str(i) for i in ANTENNAS]
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ]

# default flux
I = 1; Q = .0; U = .0; V = .0

# we'll put the sources on a 5x5 grid (positions relative to 
# the phase centre, in radians)

LM = []
delta = 0.0035
l = -3.0 * delta
#l = 3.0 * delta
for i in range(5):
  m = -0.0105
  l = l + delta
  for j in range(5):
    m = m + delta
    LM.append((l,m))
SOURCES = range(len(LM));       # 0...N-1

def create_polc_ft(degree_f=0, degree_t=0, c00=0.0):
    polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0)
    polc.coeff[0,0] = c00
    return polc

def create_constant_nodes(ns):
# numeric constants
    ns.one << Meq.Constant(1.0)
    ns.half << Meq.Constant(0.5)
    ns.ln_16 << Meq.Constant(-2.7725887)

def create_solvable_beam_parms(ns):

# we want to solve for an elliptical gaussian beam that can have
# its peak offset from the field centre and can be rotated
# by an angle with respect to L,M frame
# HPBW of 30 arcmin = 0.0087266 radians 
# HPBW of 36 arcmin = 0.010472 radians 
# 3 arcmin = 0.00087266 radians 

# define parameters for which we want solutions 
# along with initial guesses
  beam_widthl_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.00872)
  beam_widthm_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.00872)
  beam_angle_polc = create_polc_ft(degree_f=0, degree_t=0, c00=0.9)
  beam_offset_l = create_polc_ft(degree_f=0, degree_t=0, c00=0.0008)
  beam_offset_m = create_polc_ft(degree_f=0, degree_t=0, c00=0.0008)
  ns.widthl << Meq.Parm(beam_widthl_polc, node_groups='Parm')
  ns.widthm << Meq.Parm(beam_widthm_polc, node_groups='Parm')
  ns.beam_angle << Meq.Parm(beam_angle_polc, node_groups='Parm')
  ns.offset_l << Meq.Parm(beam_offset_l, node_groups='Parm')
  ns.offset_m << Meq.Parm(beam_offset_m, node_groups='Parm')

# ns.widthl << Meq.Constant(0.010472)
# ns.widthm << Meq.Constant(0.010000)
# ns.offset_l << Meq.Constant(0.00087266)
# ns.offset_m << Meq.Constant(0.00087266)
# ns.beam_angle = Meq.Constant(1.0)

  ns.width_l_sq << Meq.Sqr(1.0 / ns.widthl)
  ns.width_m_sq << Meq.Sqr(1.0 / ns.widthm)

  # rotation matrix for the elliptical beam
  ns.beam_cos << Meq.Cos(ns.beam_angle);
  ns.beam_sin << Meq.Sin(ns.beam_angle);


def source_EJ_tree(ns):
# We now calculate the expected beam response for a given
# source. We assume that there's no station dependence

# we build up the mathematical expression of a voltage
# pattern for a source using the equations
# log16 =  (-1.0) * log(16.0)
# L,M give direction cosines of the source wrt field centre 
# L_gain = (L * L) / (widthl_ * widthl_)
# M_gain = (M * M ) / (widthm_ * widthm_)
# voltage_gain = sqrt(exp(log16 * (L_gain + M_gain)))
  for src in SOURCES:

    # first generate some basic stuff for a source
    l,m = LM[src];
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # define source brightness B0 (unprojected)
    ns.B0(src) << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q)
    # don't really need to use the following for a point source
    ns.B(src) << ns.B0(src) / n;
    ns.lm(src) << Meq.Composer(l,m)

    # convert L,M of source to L',M' in beam coordinate system
    l_prime = l - ns.offset_l
    m_prime = m - ns.offset_m
    # now convert to rotated reference frame of beam
    m_dprime = m_prime * ns.beam_cos - l_prime * ns.beam_sin
    l_dprime = l_prime * ns.beam_cos + m_prime * ns.beam_sin

    ns.l_sq(src) << Meq.Sqr(l_dprime)
    ns.m_sq(src) << Meq.Sqr(m_dprime)

    # then multiply by width squared, for L, M
    ns.l_vpsq(src) << Meq.Multiply(ns.l_sq(src), ns.width_l_sq)
    ns.m_vpsq(src) << Meq.Multiply(ns.m_sq(src), ns.width_m_sq)

    # add L and M gains together
    ns.l_and_m_sq(src) << Meq.Add(ns.l_vpsq(src), ns.m_vpsq(src))
    # then multiply by log 16
    ns.v_gain(src) << Meq.Multiply(ns.l_and_m_sq(src), ns.ln_16)
    # raise to exponent
    ns.exp_v_gain(src) << Meq.Exp(ns.v_gain(src))
    # take square root to get voltage response
    ns.exp_v_gain(src) << Meq.Exp(ns.v_gain(src))
    ns.E(src) << Meq.Sqrt(ns.exp_v_gain(src))
    ns.Et(src) << Meq.ConjTranspose(ns.E(src))

########################################################
def _define_forest(ns):  
  # first create constants 
  create_constant_nodes(ns)

  # create solvable beam parameters
  create_solvable_beam_parms(ns)

  # create E-Jones nodes for sources
  source_EJ_tree(ns)

 # now set up nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # set up individual positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));
    # NOTE: in the above lines of code since the ns.radec0 = statement
    # we have been creating nodes with placeholder values of zero. These
    # get set to actual values when the statement 
    # python_init = 'Meow.ReadVisHeader' gets executed during the 
    # _test_forest function is called. The state of the above nodes
    # gets updated by contents read in from the MS
    
# define K-jones matrices - just derive the phase shift, and the
# its complex conjugate for each antenna  / source combination
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));

  # now define predicted visibilities, and attach to sinks for writing out
  # to the measurement set. We just calculate the measurement equation
  # for each source and interferometer pair though the MatrixMultiply
  # node 
  for p,q in IFRS:
    for src in SOURCES:
      ns.predict_ok(p,q,src) << \
        Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
    predict_ok = ns.predict_ok(p,q) << Meq.Add(*[ns.predict_ok(p,q,src) for src in SOURCES]);
    # create the spigots
    spigot = ns.spigot(p,q) << Meq.Spigot( station_1_index=p-1,
                                  station_2_index=q-1,
                                  flag_bit=4,
                                  input_col='DATA');
    # By some unknown means the data_column_name used in forming
    # the request below will be translated to a spigot input_col 
    # in general the spigot input_col should be 'DATA'

    # set up condeqs
    ns.ce(p,q) << Meq.Condeq(spigot,predict_ok)

    # set up residuals
    ns.residual(p,q) << spigot - predict_ok

  # create solver
  ns.solver << Meq.Solver(*[ns.ce(p,q) for p,q in IFRS]);

  # create sequencer and sinks
  for p,q in IFRS:
    ns.sink(p,q) << Meq.Sink(
      ns.reqseq(p,q) << Meq.ReqSeq(ns.solver,ns.residual(p,q),result_index=1),
    station_1_index=p-1,station_2_index=q-1, output_col='PREDICT');

  # create visualizers for spigots and residuals
  ns.inspect_spigots << Meq.Composer(
    dims=[0],
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[ns.spigot(p,q) for p,q in IFRS]
  );
# ns.inspect_residuals << Meq.Composer(
#   dims=[0],
#   plot_label=["%s-%s"%(p,q) for p,q in IFRS],
#   *[ns.residual(p,q) for p,q in IFRS]
# );
  

  # and thats it. Finally we define a VisDataMux node which essentially
  # has the sinks as implicit children. When we send a request
  # to the VisDataMux node in the _test_forest function below, it
  # sends requests to the sinks, which then propagate requests through
  # the tree ....
  # create VisDataMux
# ns.VisDataMux = Meq.VisDataMux(pre=ns.inspect_spigots,post=ns.inspect_residuals,*[ns.sink(p,q) for p,q in array.ifrs()]);
  ns.VisDataMux = Meq.VisDataMux(pre=ns.inspect_spigots,*[ns.sink(p,q) for p,q in IFRS]);
# ns.VisDataMux = Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);

  #add bookmarks
  bk = Bookmarks.Page("Beam Parameters",2,3)
  bk.add(ns.widthl);
  bk.add(ns.widthm);
  bk.add(ns.beam_angle);
  bk.add(ns.offset_l);
  bk.add(ns.offset_m);
  bk.add(ns.solver);
  pg = Bookmarks.Page("Inspectors",1,2);
  pg.add(ns.inspect_spigots,viewer="Collections Plotter");
# pg.add(ns.inspect_residuals,viewer="Collections Plotter");

########################################################################

def _test_forest(mqs,parent):

  # predict visibilities from source and beam parameters
  # then, by comparing with previously observed data,
  # solve for beam parameters
  solvables = [ "widthl","widthm","beam_angle","offset_l", "offset_m" ];
  Utils.run_solve_job(mqs,solvables);


if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
